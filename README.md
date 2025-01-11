# StreamDeck Controller

A Python script to control a StreamDeck device with customizable button styles and actions.

## Description

This project configures the appearance and functionality of a StreamDeck device. It supports customizable button styles, short and long press actions, and placeholder acknowledgment actions.

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

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.

