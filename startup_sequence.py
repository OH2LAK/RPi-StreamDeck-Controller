# startup_sequence.py
import time
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import datetime  # Import datetime to get the current date

def create_startup_image(size, text, bg_color, text_color, font, line_spacing=10):
    image = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(image)
    
    # Split text into lines
    lines = text.split('\n')
    
    # Calculate text position, centered with line spacing
    total_text_height = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] + line_spacing for line in lines]) - line_spacing
    current_y = (size[1] - total_text_height) // 2

    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_position = ((size[0] - text_width) // 2, current_y)
        draw.text(text_position, line, font=font, fill=text_color)
        current_y += text_bbox[3] - text_bbox[1] + line_spacing

    image = ImageOps.mirror(image)  # Mirror the image to correct text orientation

    image_bytes = io.BytesIO()
    image.save(image_bytes, format='BMP')
    return image_bytes.getvalue()

def show_startup_sequence(deck, styles):
    size = deck.key_image_format()["size"]
    unique_colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
        (255, 0, 255), (0, 255, 255), (192, 192, 192), (128, 0, 0),
        (128, 128, 0), (0, 128, 0), (128, 0, 128), (0, 128, 128), 
        (0, 0, 128), (255, 165, 0), (75, 0, 130)
    ]
    font = ImageFont.truetype("Roboto-Medium.ttf", 12)
    texts = {
        10: "Author:",
        11: "Erik Finskas\nOH2LAK",
        13: "Version:",
        14: "2025\n 0113"
    }

    for key in range(deck.key_count()):
        color = unique_colors[key % len(unique_colors)]
        text = texts.get(key, "")
        image = create_startup_image(size, text, color, (255, 255, 255), font, line_spacing=10)
        deck.set_key_image(key, image)

def run_startup_sequence(deck, styles):
    deck.reset()
    show_startup_sequence(deck, styles)
    time.sleep(2)
