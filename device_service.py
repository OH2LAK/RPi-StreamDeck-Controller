from flask import Flask, jsonify
from StreamDeck import DeviceManager
from StreamDeck.Transport.Transport import TransportError

app = Flask(__name__)

@app.route('/api/device_info', methods=['GET'])
def device_info():
    decks = DeviceManager.DeviceManager().enumerate()
    if not decks:
        return jsonify({'error': 'No StreamDeck devices found'}), 404
    deck = decks[0]
    try:
        deck.open()
        device_info = {
            'model': deck.deck_type(),
            'serial_number': deck.get_serial_number()
        }
        deck.close()
        return jsonify(device_info)
    except TransportError:
        return jsonify({'error': 'Could not open StreamDeck device'}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)