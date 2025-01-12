import sys
import os
import time
from StreamDeck import DeviceManager
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import sqlite3
import threading
import socket

# Ensure the script's directory is in the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

import startup_sequence  # Import startup sequence

# Store images for each key and state
images = {}
key_press_times = {}  # Store the time when a key was pressed
long_press_ack_keys = set()  # Track keys that are in long press acknowledgment state

# Flag for stopping the main loop
stop_flag = threading.Event()

def create_image(size, text, style, font):
    image = Image.new('RGB', size, style['bg_color'])
    draw = ImageDraw.Draw(image)
    
    # Calculate text position, centered
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw the text on the image
    draw.text(text_position, text, font=font, fill=style['text_color'])
    
    image = ImageOps.mirror(image)  # Flip the image horizontally to fix mirrored text
    
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='BMP')
    return image_bytes.getvalue()

def create_highlighted_image(size, text, style, font):
    return create_image(size, text, {
        'bg_color': style['highlight_bg_color'],
        'text_color': style['highlight_text_color'],
    }, font)

def insert_default_configuration(device_id):
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()

    # Insert default styles
    styles_data = [
        (device_id, 'default', '#000000', '#FFFFFF', '#333333', '#FFFFFF', 1),  # Default style
        (device_id, 'highlight', '#FFFFFF', '#000000', '#FFFF00', '#000000', 0),
        (device_id, 'long_press_ack', '#FF0000', '#FFFFFF', '#FF0000', '#FFFFFF', 0)
    ]

    cursor.executemany('''
    INSERT INTO styles (device_id, name, bg_color, text_color, highlight_bg_color, highlight_text_color, `default`)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', styles_data)

    # Insert default button configurations
    button_config_data = [
        (device_id, i, f'Button {i+1}', 'default' if i < 5 or i >= 10 else 'highlight', 'long_press_ack', f'short_action_{i+1}', f'long_action_{i+1}', f'ack_action_{i+1}')
        for i in range(15)
    ]

    cursor.executemany('''
    INSERT INTO button_config (device_id, key, text, style, long_press_ack_style, short_press, long_press, ack_action)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', button_config_data)

    conn.commit()
    conn.close()

def load_configuration(device_id):
    global styles, button_config, parameters, font

    # Connect to the SQLite database
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()

    # Fetch styles
    cursor.execute('SELECT id, device_id, name, bg_color, text_color, highlight_bg_color, highlight_text_color, `default` FROM styles WHERE device_id = ?', (device_id,))
    styles = {row[2]: {
        'device_id': row[1],
        'bg_color': row[3],
        'text_color': row[4],
        'highlight_bg_color': row[5],
        'highlight_text_color': row[6],
        'default': row[7]
    } for row in cursor.fetchall()}

    # Fetch button configurations
    cursor.execute('SELECT device_id, key, text, style, long_press_ack_style, short_press, long_press, ack_action FROM button_config WHERE device_id = ?', (device_id,))
    button_config = {row[1]: {
        'device_id': row[0],
        'text': row[2],
        'style': row[3],
        'long_press_ack_style': row[4],
        'short_press': row[5],
        'long_press': row[6],
        'ack_action': row[7]
    } for row in cursor.fetchall()}

    # Debugging: Print button_config
    print("Button Configurations Loaded:")
    for key, config in button_config.items():
        print(f"Key {key}: {config}")

    # Fetch parameters
    cursor.execute('SELECT name, value FROM parameters')
    parameters = {row[0]: row[1] for row in cursor.fetchall()}

    # Load font
    font_path = parameters['font_path']
    font_size = int(parameters['font_size'])
    font = ImageFont.truetype(font_path, font_size)

    # Close the database connection
    conn.close()

    # Update button images
    for key in range(deck.key_count()):
        if key not in button_config:
            print(f"Key {key} not found in button_config")
            continue
        style_name = button_config[key]['style']
        style = styles[style_name]
        original_image = create_image(deck.key_image_format()['size'], button_config[key]['text'], style, font)
        highlighted_image = create_highlighted_image(deck.key_image_format()['size'], button_config[key]['text'], style, font)
        long_press_ack_image = create_image(deck.key_image_format()['size'], button_config[key]['text'], styles['long_press_ack'], font)
        images[key] = {
            'original': original_image,
            'highlighted': highlighted_image,
            'long_press_ack': long_press_ack_image
        }
        deck.set_key_image(key, original_image)

def stop_program():
    input("Press X to stop the program...\n")
    stop_flag.set()

def listen_for_updates(device_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 65432))
        s.listen()
        while not stop_flag.is_set():
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if data == b'update':
                    load_configuration(device_id)
                    print("Configuration reloaded")
                else:
                    handle_command(data.decode())

def handle_command(command):
    # Example command: "set_key_image 0 highlighted"
    parts = command.split()
    if parts[0] == "set_key_image":
        key = int(parts[1])
        image_type = parts[2]
        if image_type in images[key]:
            deck.set_key_image(key, images[key][image_type])
            print(f"Set key {key} image to {image_type}")

try:
    threading.Thread(target=stop_program).start()  # Start the stop program thread

    deck = DeviceManager.DeviceManager().enumerate()[0]
    deck.open()
    deck.reset()

    # Get device information
    device_model = deck.deck_type()
    device_serial_number = deck.get_serial_number()

    # Print detected device information
    print(f"Detected device: {device_model} (S/N: {device_serial_number})")

    # Connect to the SQLite database
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()

    # Check if the device is already in the database
    cursor.execute('SELECT id FROM devices WHERE serial_number = ?', (device_serial_number,))
    device = cursor.fetchone()

    if device is None:
        # Insert the device into the database
        cursor.execute('INSERT INTO devices (model, serial_number) VALUES (?, ?)', (device_model, device_serial_number))
        conn.commit()
        device_id = cursor.lastrowid

        # Insert default configuration for the new device
        insert_default_configuration(device_id)
        print(f"Inserted default configuration for new device: {device_model} (S/N: {device_serial_number})")
    else:
        device_id = device[0]
        print(f"Loaded existing configuration for device: {device_model} (S/N: {device_serial_number})")

    conn.close()

    threading.Thread(target=listen_for_updates, args=(device_id,)).start()  # Start the update listener thread

    load_configuration(device_id)  # Load configuration before running the startup sequence

    # Run the startup sequence
    startup_sequence.run_startup_sequence(deck, styles)

    for key in range(deck.key_count()):
        if key not in button_config:
            print(f"Key {key} not found in button_config")
            continue
        style_name = button_config[key]['style']
        style = styles[style_name]
        original_image = create_image(deck.key_image_format()['size'], button_config[key]['text'], style, font)
        highlighted_image = create_highlighted_image(deck.key_image_format()['size'], button_config[key]['text'], style, font)
        long_press_ack_image = create_image(deck.key_image_format()['size'], button_config[key]['text'], styles['long_press_ack'], font)
        images[key] = {
            'original': original_image,
            'highlighted': highlighted_image,
            'long_press_ack': long_press_ack_image
        }
        deck.set_key_image(key, original_image)
    
    def key_change(deck, key, state):
        if state:
            key_press_times[key] = time.time()  # Record the press time
            deck.set_key_image(key, images[key]['highlighted'])
        else:
            press_duration = time.time() - key_press_times[key]  # Calculate the press duration
            if press_duration >= float(parameters['long_press_duration']):
                print('Long press detected on key: {}'.format(key))
                long_press_function = button_config[key].get('long_press')
                if callable(long_press_function):
                    long_press_function()  # Call the long press action, if defined
                long_press_ack_keys.add(key)  # Track long press ack state
            else:
                print('Short press detected on key: {}'.format(key))
                short_press_function = button_config[key].get('short_press')
                if callable(short_press_function):
                    short_press_function()  # Call the short press action, if defined
                deck.set_key_image(key, images[key]['original'])
            del key_press_times[key]
    
    def main_loop():
        while not stop_flag.is_set():
            current_keys = list(key_press_times.keys())  # Create a list of current keys
            for key in current_keys:
                if time.time() - key_press_times[key] >= float(parameters['long_press_duration']):
                    deck.set_key_image(key, images[key]['long_press_ack'])
                    ack_action_function = button_config[key].get('ack_action')
                    if callable(ack_action_function):
                        ack_action_function()  # Call the ack action, if defined
                    long_press_ack_keys.add(key)
            for key in long_press_ack_keys.copy():
                if key not in key_press_times:
                    deck.set_key_image(key, images[key]['original'])
                    long_press_ack_keys.remove(key)
            time.sleep(0.1)  # Small sleep to prevent high CPU usage
    
    deck.set_key_callback(key_change)
    main_loop()

finally:
    deck.close()