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
from flask import Flask, jsonify
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

app = Flask(__name__)

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
        for key in range(15):  # Assuming a default of 15 buttons
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

def main():
    device_info = get_device_info()
    if device_info:
        logging.info(f"Connected to {device_info['model']} with {device_info['button_count']} buttons.")
        # Add your logic to handle button interactions here
    else:
        logging.error("No StreamDeck device connected.")

if __name__ == '__main__':
    main()