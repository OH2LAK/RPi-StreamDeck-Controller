import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('streamdeck.db')
cursor = conn.cursor()

# Create styles table
cursor.execute('''
CREATE TABLE IF NOT EXISTS styles (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    bg_color TEXT,
    text_color TEXT,
    font_path TEXT,
    font_size INTEGER,
    highlight_bg_color TEXT,
    highlight_text_color TEXT
)
''')

# Create button_config table
cursor.execute('''
CREATE TABLE IF NOT EXISTS button_config (
    id INTEGER PRIMARY KEY,
    key INTEGER UNIQUE,
    text TEXT,
    style TEXT,
    FOREIGN KEY(style) REFERENCES styles(name)
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()