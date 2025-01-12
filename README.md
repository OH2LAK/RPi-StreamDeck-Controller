> [!NOTE]
> This program is just in its baby steps. Only basic communication between the controller and StreamDeck and behavior control of the buttons have been implemented.
> Next task is to implement the support for all kind of actions based on button press.

# Python StreamDeck Controller for Raspberry Pi Zero W

A Python script to control a StreamDeck device with customizable button styles and actions. The controller is to sit in a Raspberry Pi Zero W miniature computer which can be attached to the back of the StreamDeck device.

## Description

This project configures the appearance and functionality of a StreamDeck device. It supports customizable button styles, short and long press actions, and acknowledgment actions (not yet implemented).

## Development Environment

This project is being developed on a **Raspberry Pi Zero W** with the following setup:
- **USB-OTG dongle** to connect the StreamDeck.
- The newest **Raspbian Lite OS**.
- All Python packages are installed via **APT**.

## Files

- `streamdeck.py`: Main script to run the StreamDeck controller.
- `styles.py`: Defines button styles (background color, text color, font, etc.).
- `button_config.py`: Defines button-specific styles and actions (short press, long press, acknowledgment).
- `parameters.py`: Defines general parameters (short press duration, long press duration).

## Dependencies

The following packages are required and should be installed via APT:
- `python3`
- `python3-pip`
- `python3-pil` (Pillow library for image processing)
- `streamdeck` (Library to interact with the StreamDeck device)
- `python3-setuptools`

For installing these packages, you can use the following command:
```sh
sudo apt-get install python3 python3-pip python3-pil python3-setuptools
pip3 install streamdeck
```

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

