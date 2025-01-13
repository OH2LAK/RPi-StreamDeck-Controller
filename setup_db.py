import sqlite3
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

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

def initialize_database():
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS button_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        key INTEGER NOT NULL,
        text TEXT NOT NULL,
        style TEXT NOT NULL,
        short_press TEXT NOT NULL,
        long_press TEXT NOT NULL,
        ack_action TEXT NOT NULL,
        image BLOB
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS styles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        normal_bg_color TEXT NOT NULL,
        normal_text_color TEXT NOT NULL,
        normal_font_size INTEGER NOT NULL,
        short_press_bg_color TEXT NOT NULL,
        short_press_text_color TEXT NOT NULL,
        short_press_font_size INTEGER NOT NULL,
        long_press_bg_color TEXT NOT NULL,
        long_press_text_color TEXT NOT NULL,
        long_press_font_size INTEGER NOT NULL,
        normal_image BLOB,
        short_press_image BLOB,
        long_press_image BLOB
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        value TEXT NOT NULL
    );
    ''')

    # Create images for the default style variations with the text "Text"
    normal_image = create_image((72, 72), "Text", "#000000", "#AAAAAA", 14)
    short_press_image = create_image((72, 72), "Text", "#555555", "#AAAAAA", 14)
    long_press_image = create_image((72, 72), "Text", "#FFAAAA", "#AAAAAA", 14)

    # Insert default style
    cursor.execute('''
    INSERT OR IGNORE INTO styles (name, normal_bg_color, normal_text_color, normal_font_size, short_press_bg_color, short_press_text_color, short_press_font_size, long_press_bg_color, long_press_text_color, long_press_font_size, normal_image, short_press_image, long_press_image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('Default', '#000000', '#AAAAAA', 14, '#555555', '#AAAAAA', 14, '#FFAAAA', '#AAAAAA', 14, normal_image, short_press_image, long_press_image))

    # Insert default button configuration for the maximum number of buttons (32)
    max_buttons = 32
    default_device_id = 'default_device'
    for key in range(max_buttons):
        cursor.execute('''
        INSERT OR IGNORE INTO button_config (device_id, key, text, style, short_press, long_press, ack_action, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (default_device_id, key, f'Button {key}', 'Default', '', '', '', None))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()