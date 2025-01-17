import sys
import os
import time
from StreamDeck import DeviceManager
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

# Ensure the script's directory is in the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

import styles  # Import styles from styles.py
import button_config  # Import button configurations from button_config.py
import parameters  # Import general parameters from parameters.py

# Store images for each key and state
images = {}
key_press_times = {}  # Store the time when a key was pressed
long_press_ack_keys = set()  # Track keys that are in long press acknowledgment state

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

deck = DeviceManager.DeviceManager().enumerate()[0]
deck.open()

try:
    deck.reset()

    for key in range(deck.key_count()):
        style_name = button_config.button_config[key]['style']
        style = styles.styles[style_name]
        original_image = create_image(deck.key_image_format()['size'], 'Key {}'.format(key), style)
        highlighted_image = create_highlighted_image(deck.key_image_format()['size'], 'Key {}'.format(key), style)
        long_press_ack_image = create_image(deck.key_image_format()['size'], 'Key {}'.format(key), styles.styles['long_press_ack'])
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
            if press_duration >= parameters.parameters['long_press_duration']:
                print('Long press detected on key: {}'.format(key))
                long_press_function = button_config.button_config[key].get('long_press')
                if callable(long_press_function):
                    long_press_function()  # Call the long press action, if defined
                long_press_ack_keys.add(key)  # Track long press ack state
            else:
                print('Short press detected on key: {}'.format(key))
                short_press_function = button_config.button_config[key].get('short_press')
                if callable(short_press_function):
                    short_press_function()  # Call the short press action, if defined
                deck.set_key_image(key, images[key]['original'])
            del key_press_times[key]
    
    def main_loop():
        while True:
            current_keys = list(key_press_times.keys())  # Create a list of current keys
            for key in current_keys:
                if time.time() - key_press_times[key] >= parameters.parameters['long_press_duration']:
                    deck.set_key_image(key, images[key]['long_press_ack'])
                    ack_action_function = button_config.button_config[key].get('ack_action')
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

