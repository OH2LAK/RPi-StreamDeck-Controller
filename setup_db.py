import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import sqlite3
import threading
import socket
import netifaces
import requests
import logging

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

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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

def get_ip_address():
    gws = netifaces.gateways()
    default_interface = gws['default'][netifaces.AF_INET][1]
    ip_address = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]['addr']
    return ip_address

def display_configuration_message(deck, font):
    message = "USE WEB GUI TO CONFIGURE"
    words = message.split()
    ip_address = get_ip_address()
    print(f"IP Address: {ip_address}")  # Debugging: Print the IP address
    ip_parts = ip_address.split('.')

    for i in range(6):
        text = words[i] if i < len(words) else ""
        image = create_image(deck.key_image_format()['size'], text, {'bg_color': '#000000', 'text_color': '#FFFFFF'}, font)
        deck.set_key_image(i, image)

    deck.set_key_image(6, create_image(deck.key_image_format()['size'], "IP", {'bg_color': '#000000', 'text_color': '#FFFFFF'}, font))
    deck.set_key_image(7, create_image(deck.key_image_format()['size'], "address", {'bg_color': '#000000', 'text_color': '#FFFFFF'}, font))
    for i in range(4):
        print(f"IP Part {i}: {ip_parts[i]}")  # Debugging: Print each IP part
        deck.set_key_image(8 + i, create_image(deck.key_image_format()['size'], ip_parts[i], {'bg_color': '#000000', 'text_color': '#FFFFFF'}, font))

def insert_default_configuration(device_id):
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM button_config WHERE device_id = ?', (device_id,))
    count = cursor.fetchone()[0]
    if count == 0:
        for key in range(32):  # Assuming a default of 32 buttons
            cursor.execute('INSERT INTO button_config (device_id, key, text, style, long_press_ack_style, short_press, long_press, ack_action) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (device_id, key, f'Button {key}', 'default', 'default', '', '', ''))
    conn.commit()
    conn.close()

def get_device_info():
    try:
        response = requests.get('http://localhost:5001/api/device_info')
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error fetching device info: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
    return None

def load_button_mappings(device_id, button_count):
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM button_config WHERE device_id = ? AND key < ?', (device_id, button_count))
    button_mappings = cursor.fetchall()
    conn.close()
    return button_mappings

def update_button_images(button_mappings, font):
    for mapping in button_mappings:
        key = mapping['key']
        text = mapping['text']
        style = {
            'bg_color': mapping['bg_color'],
            'text_color': mapping['text_color']
        }
        image = create_image((72, 72), text, style, font)
        images[key] = image

def handle_key_event(deck, key, state):
    if state:
        key_press_times[key] = time.time()
    else:
        press_duration = time.time() - key_press_times[key]
        if press_duration > 1.0:  # Long press
            logging.info(f"Key {key} long pressed")
            long_press_ack_keys.add(key)
        else:  # Short press
            logging.info(f"Key {key} short pressed")
            if key in long_press_ack_keys:
                long_press_ack_keys.remove(key)

def main():
    device_info = get_device_info()
    if device_info:
        logging.info(f"Connected to {device_info['model']} with {device_info['button_count']} buttons.")
        font = ImageFont.truetype("Roboto-Medium.ttf", 14)

        button_mappings = load_button_mappings(device_info['serial_number'], device_info['button_count'])
        update_button_images(button_mappings, font)

        # Fetch the device state and update images through device_service.py
        while not stop_flag.is_set():
            try:
                response = requests.get('http://localhost:5001/api/device_state')
                if response.status_code == 200:
                    device_state = response.json()
                    for key, state in device_state.items():
                        if state == "pressed":
                            handle_key_event(None, key, True)
                        else:
                            handle_key_event(None, key, False)
                time.sleep(0.1)
            except KeyboardInterrupt:
                stop_flag.set()
            except requests.exceptions.RequestException as e:
                logging.error(f"RequestException: {e}")
                time.sleep(1)
    else:
        logging.error("No StreamDeck device connected.")

if __name__ == '__main__':
    main()

def initialize_database():
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY,
        model TEXT,
        serial_number TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS styles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        name TEXT NOT NULL,
        bg_color TEXT NOT NULL,
        text_color TEXT NOT NULL,
        highlight_bg_color TEXT NOT NULL,
        highlight_text_color TEXT NOT NULL,
        `default` INTEGER DEFAULT 0,
        FOREIGN KEY(device_id) REFERENCES devices(id)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS button_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        key INTEGER NOT NULL,
        text TEXT NOT NULL,
        style TEXT NOT NULL,
        long_press_ack_style TEXT NOT NULL,
        short_press TEXT NOT NULL,
        long_press TEXT NOT NULL,
        ack_action TEXT NOT NULL,
        image BLOB,
        FOREIGN KEY(device_id) REFERENCES devices(id),
        FOREIGN KEY(style) REFERENCES styles(name),
        FOREIGN KEY(long_press_ack_style) REFERENCES styles(name)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        value TEXT NOT NULL
    );
    ''')

    # Insert devices data
    devices_data = [
        ('StreamDeck Mini', 'ABC123'),
        ('StreamDeck XL', 'XYZ789')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO devices (model, serial_number)
    VALUES (?, ?)
    ''', devices_data)

    # Get device IDs
    cursor.execute('SELECT id FROM devices WHERE serial_number = "ABC123"')
    device_id_mini = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM devices WHERE serial_number = "XYZ789"')
    device_id_xl = cursor.fetchone()[0]

    # Insert styles data with device_id
    styles_data = [
        (device_id_mini, 'default', '#000000', '#FFFFFF', '#333333', '#FFFFFF', 1),  # Default style
        (device_id_mini, 'highlight', '#FFFFFF', '#000000', '#FFFF00', '#000000', 0),
        (device_id_mini, 'long_press_ack', '#FF0000', '#FFFFFF', '#FF0000', '#FFFFFF', 0),
        (device_id_xl, 'default', '#000000', '#FFFFFF', '#333333', '#FFFFFF', 1),  # Default style
        (device_id_xl, 'highlight', '#FFFFFF', '#000000', '#FFFF00', '#000000', 0),
        (device_id_xl, 'long_press_ack', '#FF0000', '#FFFFFF', '#FF0000', '#FFFFFF', 0)
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO styles (device_id, name, bg_color, text_color, highlight_bg_color, highlight_text_color, `default`)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', styles_data)

    # Insert button configurations with device_id
    button_config_data = [
        (device_id_mini, i, f'Button {i+1}', 'default' if i < 5 or i >= 10 else 'highlight', 'long_press_ack', f'short_action_{i+1}', f'long_action_{i+1}', f'ack_action_{i+1}', None)
        for i in range(15)
    ] + [
        (device_id_xl, i, f'Button {i+1}', 'default' if i < 5 or i >= 10 else 'highlight', 'long_press_ack', f'short_action_{i+1}', f'long_action_{i+1}', f'ack_action_{i+1}', None)
        for i in range(15)
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO button_config (device_id, key, text, style, long_press_ack_style, short_press, long_press, ack_action, image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', button_config_data)

    # Insert parameters data
    parameters_data = [
        ('short_press_duration', '0.2'),
        ('long_press_duration', '1.0'),
        ('font_path', 'Roboto-Medium.ttf'),
        ('font_size', '14')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO parameters (name, value)
    VALUES (?, ?)
    ''', parameters_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()