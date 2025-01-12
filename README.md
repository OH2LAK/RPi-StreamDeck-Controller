> [!NOTE]
> This program is just in its baby steps. Only basic communication between the controller and StreamDeck and behavior control of the buttons have been implemented.
> Next task is to implement the support for all kind of actions based on button press.

# RPi-StreamDeck-Controller

This project is designed to control a StreamDeck device using a Raspberry Pi. It includes a web GUI for managing styles and button configurations stored in an SQLite database.

## Description

This project configures the appearance and functionality of a StreamDeck device. It supports customizable button styles, short and long press actions, and acknowledgment actions (not yet implemented).

## Development Environment

This project is being developed on a **Raspberry Pi Zero W** with the following setup:
- **USB-OTG dongle** to connect the StreamDeck.
- The newest **Raspbian Lite OS**.
- All Python packages are installed via **APT**.

## Files

- `streamdeck.py`: Main script to run the StreamDeck controller.
- `WebGUI.py`: Flask application for managing styles and button configurations.
- `create_db.py`: Script to create the SQLite database and tables.
- `insert_data.py`: Script to insert initial data into the database.
- `templates/`: Directory containing HTML templates for the Flask web GUI.
  - `index.html`: Main page listing styles and button configurations.
  - `add_style.html`: Form to add a new style.
  - `add_button_config.html`: Form to add a new button configuration.
- `static/`: Directory for static files (e.g., CSS, JavaScript).
  - `css/`: Directory for CSS files.
    - `styles.css`: Optional CSS file for custom styles.
- `streamdeck.db`: The SQLite database file.
- `requirements.txt`: List of Python dependencies (e.g., Flask, Pillow, StreamDeck).

## Dependencies

The following packages are required and should be installed via APT:
- `python3`
- `python3-pip`
- `python3-pil` (Pillow library for image processing)
- `python3-flask` (Flask web framework)
- `python3-setuptools`
- `libhidapi-libusb0` (HIDAPI library for StreamDeck)
- `libhidapi-hidraw0` (HIDAPI library for StreamDeck)
- `libusb-1.0-0-dev` (USB library for StreamDeck)
- `python3-streamdeck` (StreamDeck driver package)
- `fonts-roboto` (Roboto font package)
- `python3-netifaces` (Portable library for network interface information)

## Requirements

- Python 3.x
- Flask
- Pillow
- StreamDeck

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/OH2LAK/RPi-StreamDeck-Controller.git
   cd RPi-StreamDeck-Controller
```

2. **Install the required packages using APT:**
   ```sh
sudo apt update
sudo apt install python3 python3-pip python3-pil python3-flask python3-setuptools libhidapi-libusb0 libhidapi-hidraw0 libusb-1.0-0-dev python3-streamdeck fonts-roboto 
```

## Setting up the database
1. **Create the SQLite database and tables:**
```sh
python3 create_db.py
```

2. **Insert initial data into the database:**
```sh
python3 insert_data.py
```

## Running the Flask Web GUI
1. **Start the Flask application:**
```sh
python3 WebGUI.py
```

1. **Access the web GUI:**
Open your web browser and go to ```http://127.0.0.1:5000/```

## Configuration

# Parameters

Set general parameters (like press durations) in `parameters.py`:

```python
parameters = {
    "short_press_duration": 0.5,  # 0.5 seconds for short press
    "long_press_duration": 1.0  # 1.0 seconds for long press
}
```

## Field Definitions
* `short_press_duration`: Duration (in seconds) that constitutes a short press.
* `long_press_duration`: Duration (in seconds) that constitutes a long press.

# Button styles

Add or modify button styles in `styles.py`:

```python
styles = {
    ...
    "new_style": {
        "bg_color": (100, 100, 100),
        "text_color": (255, 255, 255),
        "highlight_bg_color": (200, 200, 200),
        "highlight_text_color": (0, 0, 0),
        "font": ImageFont.truetype("Roboto-Medium.ttf", 14)
    }
}
```
##  Field Definitions
* `bg_color`: Background color of the button in RGB format. Example: (100, 100, 100) for a medium grey color.
* `text_color`: Text color of the button in RGB format. Example: (255, 255, 255) for white text.
* `highlight_bg_color`: Background color of the button when it is highlighted (e.g., pressed) in RGB format. Example: (200, 200, 200) for a lighter grey color.
* `highlight_text_color`: Text color of the button when it is highlighted (e.g., pressed) in RGB format. Example: (0, 0, 0) for black text.
* `font`: The font used for the button text. This is typically defined using the ImageFont.truetype method, specifying the font file and size. Example: ImageFont.truetype("Roboto-Medium.ttf", 14) for the Roboto Medium font at size 14.

You can create new styles or edit existing ones to suit your needs.

# Button Actions

Define button-specific actions and configure buttons in `button_config.py`:

```python
button_config = {
    0: {
        "style": "default",
        "long_press_ack_style": "long_press_ack",
        "text": "Button 0",
        "short_press": short_action_0,  # Replace with the actual function call
        "long_press": long_action_0,  # Replace with the actual function call
        "ack_action": ack_action_0  # Replace with the actual function call
    },
    ...
}
```
## Field Definitions
* `style`: The style applied to the button, referencing a key in the styles dictionary.
* `long_press_ack_style`: The style applied to the button when it is in the long press acknowledgment state, referencing a key in the styles dictionary.
* `text`: The text displayed on the button.
* `short_press`: The function or action called when the button is short-pressed (not yet implemented)
* `long_press`: The function or action called when the button is long-pressed (not yet implemented).
* `ack_action_short_press`: The function or action called for acknowledgment after a short press (not yet implemented).
* `ack_action_long_press`: The function or action called for acknowledgment after a long press (not yet implemented).

# TO-DO
* Implement button actions: web calls, calling scripts to do things, etc.
* Implement image support for the button backgrounds

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.

