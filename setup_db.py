import sqlite3

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
        long_press_ack_style TEXT NOT NULL,
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
        bg_color TEXT NOT NULL,
        text_color TEXT NOT NULL,
        highlight_bg_color TEXT NOT NULL,
        highlight_text_color TEXT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parameters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        value TEXT NOT NULL
    );
    ''')

    # Insert default styles
    cursor.execute('''
    INSERT OR IGNORE INTO styles (name, bg_color, text_color, highlight_bg_color, highlight_text_color)
    VALUES ('default', '#000000', '#FFFFFF', '#FFFFFF', '#000000')
    ''')

    # Insert default button configuration for the maximum number of buttons (32)
    max_buttons = 32
    default_device_id = 'default_device'
    for key in range(max_buttons):
        cursor.execute('''
        INSERT OR IGNORE INTO button_config (device_id, key, text, style, long_press_ack_style, short_press, long_press, ack_action)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (default_device_id, key, f'Button {key}', 'default', 'default', '', '', ''))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()