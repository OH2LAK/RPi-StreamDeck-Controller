# styles.py
from PIL import ImageFont

styles = {
    "default": {
        "bg_color": (0, 0, 0),
        "text_color": (255, 255, 255),
        "highlight_bg_color": (255, 255, 255),
        "highlight_text_color": (0, 0, 0),
        "font": ImageFont.truetype("Roboto-Medium.ttf", 14)
    },
    "style1": {
        "bg_color": (0, 150, 150),
        "text_color": (200, 200, 200),
        "highlight_bg_color": (100, 100, 100),
        "highlight_text_color": (150, 150, 150),
        "font": ImageFont.truetype("Roboto-Medium.ttf", 16)
    },
    "red_button": {
        "bg_color": (200, 0, 0),
        "text_color": (200, 200, 200),
        "highlight_bg_color": (255, 0, 0),
        "highlight_text_color": (255, 255, 255),
        "font": ImageFont.truetype("Roboto-Medium.ttf", 16)
    },
    "long_press_ack": {
        "bg_color": (0, 128, 0),
        "text_color": (255, 255, 255),
        "highlight_bg_color": (255, 215, 0),
        "highlight_text_color": (0, 0, 0),
        "font": ImageFont.truetype("Roboto-Medium.ttf", 14)
    }
}
