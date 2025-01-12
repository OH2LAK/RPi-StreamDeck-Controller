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

def create_image(size, text, style):
    image = Image.new('RGB', size, style['bg_color'])
    draw = ImageDraw.Draw(image)
    
    # Calculate text position, centered
    text_bbox = draw.textbbox((0, 0), text, font=style['font'])
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw the text on the image
    draw.text(text_position, text, font=style['font'], fill=style['text_color'])
    
    image = ImageOps.mirror(image)  # Flip the image horizontally to fix mirrored text
    
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='BMP')
    return image_bytes.getvalue()

def create_highlighted_image(size, text, style):
    return create_image(size, text, {
        'bg_color': style['highlight_bg_color'],
        'text_color': style['highlight_text_color'],
        'font': style['font'],
    })

def load_configuration():
    global styles, button_config, parameters

    # Connect to the SQLite database
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()

    # Fetch styles
    cursor.execute('SELECT name, bg_color, text_color, font_path, font_size, highlight_bg_color, highlight_text_color FROM styles')
    styles = {row[0]: {
        'bg_color': row[1],
        'text_color': row[2],
        'font': ImageFont.truetype(row[3], row[4]),
        'highlight_bg_color': row[5],
        'highlight_text_color': row[6]
    } for row in cursor.fetchall()}

    # Fetch button configurations
    cursor.execute('SELECT key, text, style, long_press_ack_style, short_press, long_press, ack_action FROM button_config')
    button_config = {row[0]: {
        'text': row[1],
        'style': row[2],
        'long_press_ack_style': row[3],
        'short_press': row[4],
        'long_press': row[5],
        'ack_action': row[6]
    } for row in cursor.fetchall()}

    # Fetch parameters
    cursor.execute('SELECT name, value FROM parameters')
    parameters = {row[0]: row[1] for row in cursor.fetchall()}

    # Close the database connection
    conn.close()

def stop_program():
    input("Press X to stop the program...\n")
    stop_flag.set()

def listen_for_updates():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 65432))
        s.listen()
        while not stop_flag.is_set():
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if data == b'update':
                    load_configuration()
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
    threading.Thread(target=listen_for_updates).start()  # Start the update listener thread

    deck = DeviceManager.DeviceManager().enumerate()[0]
    deck.open()
    deck.reset()

    load_configuration()  # Load configuration before running the startup sequence

    # Run the startup sequence
    startup_sequence.run_startup_sequence(deck, styles)

    for key in range(deck.key_count()):
        style_name = button_config[key]['style']
        style = styles[style_name]
        original_image = create_image(deck.key_image_format()['size'], button_config[key]['text'], style)
        highlighted_image = create_highlighted_image(deck.key_image_format()['size'], button_config[key]['text'], style)
        long_press_ack_image = create_image(deck.key_image_format()['size'], button_config[key]['text'], styles['long_press_ack'])
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
            if press_duration >= parameters['long_press_duration']:
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
                if time.time() - key_press_times[key] >= parameters['long_press_duration']:
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