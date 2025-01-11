# styles.py
from PIL import ImageFont

styles = {
    "default": {
        "bg_color": (0, 0, 0),
        "text_color": (255, 255, 255),
        "highlight_bg_color": (255, 255, 255),
        "highlight_text_color": (0, 0, 0),
        "font": ImageFont.truetype("Roboto-Medium.ttf", 14)  # Update path
    },
    "style1": {
        "bg_color": (50, 50, 50),
        "text_color": (200, 200, 200),
        "highlight_bg_color": (200, 200, 200),
        "highlight_text_color": (50, 50, 50),
        "font": ImageFont.truetype("Roboto-Medium.ttf", 16)  # Update path
    },
    "long_press_ack": {  # New style for long press acknowledgment
        "bg_color": (0, 128, 0),
        "text_color": (255, 255, 255),
        "highlight_bg_color": (255, 215, 0),
        "highlight_text_color": (0, 0, 0),
        "font": ImageFont.truetype("Roboto-Medium.ttf", 14)  # Update path
    }
}
