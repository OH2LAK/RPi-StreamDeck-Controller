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

def create_image(size, text, bg_color, text_color, font_size):
    font = ImageFont.truetype("Roboto-Medium.ttf", font_size)
    image = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(image)
    
    # Calculate text position, centered
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    
    # Draw the text on the image
    draw.text(text_position, text, font=font, fill=text_color)
    
    image = ImageOps.mirror(image)  # Flip the image horizontally to fix mirrored text
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='BMP')
    return image_bytes.getvalue()

def get_ip_address():
    gws = netifaces.gateways()
    default_interface = gws['default'][netifaces.AF_INET][1]
    ip_address = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]['addr']
    return ip_address

def display_configuration_message(font):
    message = "USE WEB GUI TO CONFIGURE"
    words = message.split()
    ip_address = get_ip_address()
    print(f"IP Address: {ip_address}")  # Debugging: Print the IP address
    ip_parts = ip_address.split('.')

    for i in range(6):
        text = words[i] if i < len(words) else ""
        image = create_image((72, 72), text, '#000000', '#FFFFFF', 14)
        images[i] = image

    images[6] = create_image((72, 72), "IP", '#000000', '#FFFFFF', 14)
    images[7] = create_image((72, 72), "address", '#000000', '#FFFFFF', 14)
    for i in range(4):
        print(f"IP Part {i}: {ip_parts[i]}")  # Debugging: Print each IP part
        images[8 + i] = create_image((72, 72), ip_parts[i], '#000000', '#FFFFFF', 14)

def insert_default_configuration(device_id):
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM button_config WHERE device_id = ?', (device_id,))
    count = cursor.fetchone()[0]
    if count == 0:
        for key in range(32):  # Assuming a default of 32 buttons
            cursor.execute('INSERT INTO button_config (device_id, key, text, style, short_press, long_press, ack_action, image) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (device_id, key, f'Button {key}', 'Default', '', '', '', None))
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

def load_style(style_name):
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM styles WHERE name = ?', (style_name,))
    style = cursor.fetchone()
    conn.close()
    return style

def update_button_images(button_mappings, font):
    for mapping in button_mappings:
        key = mapping['key']
        text = mapping['text']
        style = load_style(mapping['style'])
        image = create_image((72, 72), text, style['normal_bg_color'], style['normal_text_color'], style['normal_font_size'])
        images[key] = image

def handle_key_event(key, state):
    if state:
        key_press_times[key] = time.time()
    else:
        press_duration = time.time() - key_press_times.get(key, time.time())
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

        # Initialize key_press_times for all keys
        for key in range(device_info['button_count']):
            key_press_times[key] = 0

        try:
            while not stop_flag.is_set():
                response = requests.get('http://localhost:5001/api/device_state')
                if response.status_code == 200:
                    device_state = response.json()
                    logging.debug(f"Device state: {device_state}")  # Add logging to verify device state
                    for key, state in device_state.items():
                        if state == "pressed":
                            handle_key_event(key, True)
                        else:
                            handle_key_event(key, False)
                time.sleep(0.1)
        except KeyboardInterrupt:
            stop_flag.set()
    else:
        logging.error("No StreamDeck device connected.")

if __name__ == '__main__':
    main()