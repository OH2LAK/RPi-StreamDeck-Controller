import sqlite3

def initialize_database():
    conn = sqlite3.connect('streamdeck.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY,
        model TEXT,
        serial_number TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS styles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        name TEXT NOT NULL,
        bg_color TEXT NOT NULL,
        text_color TEXT NOT NULL,
        highlight_bg_color TEXT NOT NULL,
        highlight_text_color TEXT NOT NULL,
        `default` INTEGER DEFAULT 0,
        FOREIGN KEY(device_id) REFERENCES devices(id)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS button_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER,
        key INTEGER NOT NULL,
        text TEXT NOT NULL,
        style TEXT NOT NULL,
        long_press_ack_style TEXT NOT NULL,
        short_press TEXT NOT NULL,
        long_press TEXT NOT NULL,
        ack_action TEXT NOT NULL,
        image BLOB,
        FOREIGN KEY(device_id) REFERENCES devices(id),
        FOREIGN KEY(style) REFERENCES styles(name),
        FOREIGN KEY(long_press_ack_style) REFERENCES styles(name)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        value TEXT NOT NULL
    );
    ''')

    # Insert devices data
    devices_data = [
        ('StreamDeck Mini', 'ABC123'),
        ('StreamDeck XL', 'XYZ789')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO devices (model, serial_number)
    VALUES (?, ?)
    ''', devices_data)

    # Get device IDs
    cursor.execute('SELECT id FROM devices WHERE serial_number = "ABC123"')
    device_id_mini = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM devices WHERE serial_number = "XYZ789"')
    device_id_xl = cursor.fetchone()[0]

    # Insert styles data with device_id
    styles_data = [
        (device_id_mini, 'default', '#000000', '#FFFFFF', '#333333', '#FFFFFF', 1),  # Default style
        (device_id_mini, 'highlight', '#FFFFFF', '#000000', '#FFFF00', '#000000', 0),
        (device_id_mini, 'long_press_ack', '#FF0000', '#FFFFFF', '#FF0000', '#FFFFFF', 0),
        (device_id_xl, 'default', '#000000', '#FFFFFF', '#333333', '#FFFFFF', 1),  # Default style
        (device_id_xl, 'highlight', '#FFFFFF', '#000000', '#FFFF00', '#000000', 0),
        (device_id_xl, 'long_press_ack', '#FF0000', '#FFFFFF', '#FF0000', '#FFFFFF', 0)
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO styles (device_id, name, bg_color, text_color, highlight_bg_color, highlight_text_color, `default`)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', styles_data)

    # Insert button configurations with device_id
    button_config_data = [
        (device_id_mini, i, f'Button {i+1}', 'default' if i < 5 or i >= 10 else 'highlight', 'long_press_ack', f'short_action_{i+1}', f'long_action_{i+1}', f'ack_action_{i+1}', None)
        for i in range(15)
    ] + [
        (device_id_xl, i, f'Button {i+1}', 'default' if i < 5 or i >= 10 else 'highlight', 'long_press_ack', f'short_action_{i+1}', f'long_action_{i+1}', f'ack_action_{i+1}', None)
        for i in range(15)
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO button_config (device_id, key, text, style, long_press_ack_style, short_press, long_press, ack_action, image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', button_config_data)

    # Insert parameters data
    parameters_data = [
        ('short_press_duration', '0.2'),
        ('long_press_duration', '1.0'),
        ('font_path', 'Roboto-Medium.ttf'),
        ('font_size', '14')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO parameters (name, value)
    VALUES (?, ?)
    ''', parameters_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()