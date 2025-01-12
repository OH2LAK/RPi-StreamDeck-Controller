import sys
import os
import time
from StreamDeck import DeviceManager
from PIL import Image, ImageDraw, ImageFont
import io
import startup_sequence  # Import startup sequence
import threading
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Ensure the script's directory is in the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Store images for each key and state
images = {}
key_press_times = {}  # Store the time when a key was pressed
long_press_ack_keys = set()  # Track keys that are in long press acknowledgment state

# Flag for stopping the main loop
stop_flag = threading.Event()

def create_image(size, text, style, line_spacing=10):
    image = Image.new('RGB', size, style['bg_color'])
    draw = ImageDraw.Draw(image)
    
    # Split text into lines
    lines = text.split('\n')
    
    # Calculate text position, centered with line spacing
    total_text_height = sum([draw.textbbox((0, 0), line, font=style['font'])[3] - draw.textbbox((0, 0), line, font=style['font'])[1] + line_spacing 
                            for line in lines]) - line_spacing
    current_y = (size[1] - total_text_height) // 2

    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=style['font'])
        text_width = text_bbox[2] - text_bbox[0]
        text_position = ((size[0] - text_width) // 2, current_y)
        draw.text(text_position, line, font=style['font'], fill=style['text_color'])
        current_y += text_bbox[3] - text_bbox[1] + line_spacing
    
    # Flip the image horizontally before saving
    image = image.transpose(Image.FLIP_LEFT_RIGHT)
    
    # Save the flipped image
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='BMP')
    return image_bytes.getvalue()

def create_highlighted_image(size, text, style):
    return create_image(size, text, {
        'bg_color': style['highlight_bg_color'],
        'text_color': style['highlight_text_color'],
        'font': style['font']
    })

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
cursor.execute('SELECT key, text, style FROM button_config')
button_config = {row[0]: {'text': row[1], 'style': row[2]} for row in cursor.fetchall()}

# Close the database connection
conn.close()

deck = DeviceManager.DeviceManager().enumerate()[0]
deck.open()

def stop_program():
    input("Press X to stop the program...\n")
    stop_flag.set()

try:
    threading.Thread(target=stop_program).start()  # Start the stop program thread

    startup_sequence.run_startup_sequence(deck, styles)  # Run startup sequence

    for key in range(deck.key_count()):
        style_name = button_config[key]['style']
        style = styles[style_name]
        original_image = create_image(deck.key_image_format()['size'], button_config[key]['text'], style, line_spacing=10)
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
            # Handle key release
            pass

    deck.set_key_callback(key_change)

    while not stop_flag.is_set():
        time.sleep(0.1)

finally:
    deck.reset()
    deck.close()

def get_db_connection():
    conn = sqlite3.connect('streamdeck.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    styles = conn.execute('SELECT * FROM styles').fetchall()
    button_configs = conn.execute('SELECT * FROM button_config').fetchall()
    conn.close()
    return render_template('index.html', styles=styles, button_configs=button_configs)

@app.route('/add_style', methods=('GET', 'POST'))
def add_style():
    if request.method == 'POST':
        name = request.form['name']
        bg_color = request.form['bg_color']
        text_color = request.form['text_color']
        font_path = request.form['font_path']
        font_size = request.form['font_size']
        highlight_bg_color = request.form['highlight_bg_color']
        highlight_text_color = request.form['highlight_text_color']

        conn = get_db_connection()
        conn.execute('INSERT INTO styles (name, bg_color, text_color, font_path, font_size, highlight_bg_color, highlight_text_color) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (name, bg_color, text_color, font_path, font_size, highlight_bg_color, highlight_text_color))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('add_style.html')

@app.route('/add_button_config', methods=('GET', 'POST'))
def add_button_config():
    if request.method == 'POST':
        key = request.form['key']
        text = request.form['text']
        style = request.form['style']

        conn = get_db_connection()
        conn.execute('INSERT INTO button_config (key, text, style) VALUES (?, ?, ?)', (key, text, style))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn = get_db_connection()
    styles = conn.execute('SELECT name FROM styles').fetchall()
    conn.close()
    return render_template('add_button_config.html', styles=styles)

if __name__ == '__main__':
    app.run(debug=True)