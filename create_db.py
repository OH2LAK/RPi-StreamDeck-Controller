import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('streamdeck.db')
cursor = conn.cursor()

# Create devices table
cursor.execute('''
CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY,
    model TEXT,
    serial_number TEXT UNIQUE
)
''')

# Create styles table with a `default` column
cursor.execute('''
CREATE TABLE IF NOT EXISTS styles (
    id INTEGER PRIMARY KEY,
    device_id INTEGER,
    name TEXT,
    bg_color TEXT,
    text_color TEXT,
    highlight_bg_color TEXT,
    highlight_text_color TEXT,
    `default` INTEGER DEFAULT 0,
    FOREIGN KEY(device_id) REFERENCES devices(id)
)
''')

# Create button_config table
cursor.execute('''
CREATE TABLE IF NOT EXISTS button_config (
    id INTEGER PRIMARY KEY,
    device_id INTEGER,
    key INTEGER,
    text TEXT,
    style TEXT,
    long_press_ack_style TEXT,
    short_press TEXT,
    long_press TEXT,
    ack_action TEXT,
    FOREIGN KEY(device_id) REFERENCES devices(id),
    FOREIGN KEY(style) REFERENCES styles(name),
    FOREIGN KEY(long_press_ack_style) REFERENCES styles(name)
)
''')

# Create parameters table
cursor.execute('''
CREATE TABLE IF NOT EXISTS parameters (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    value TEXT
)
''')

# Create generic_config table
cursor.execute('''
CREATE TABLE IF NOT EXISTS generic_config (
    id INTEGER PRIMARY KEY,
    font_path TEXT,
    font_size INTEGER
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()