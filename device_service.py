from flask import Flask, jsonify
from StreamDeck import DeviceManager
from StreamDeck.Transport.Transport import TransportError
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/device_info', methods=['GET'])
def device_info():
    decks = DeviceManager.DeviceManager().enumerate()
    if not decks:
        app.logger.error('No StreamDeck devices found')
        return jsonify({'error': 'No StreamDeck devices found'}), 404
    deck = decks[0]
    try:
        deck.open()
        device_info = {
            'model': deck.deck_type(),
            'serial_number': deck.get_serial_number(),
            'button_count': deck.key_count()
        }
        deck.close()
        return jsonify(device_info)
    except TransportError as e:
        app.logger.error(f'Could not open StreamDeck device: {e}')
        return jsonify({'error': 'Could not open StreamDeck device'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)