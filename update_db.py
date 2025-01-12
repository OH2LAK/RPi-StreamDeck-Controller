import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('streamdeck.db')
cursor = conn.cursor()

# Check if the `default` column exists
cursor.execute("PRAGMA table_info(styles)")
columns = [column[1] for column in cursor.fetchall()]

# Add the `default` column if it doesn't exist
if 'default' not in columns:
    cursor.execute('ALTER TABLE styles ADD COLUMN `default` INTEGER DEFAULT 0')

# Move font configuration to parameters table
cursor.execute("SELECT font_path, font_size FROM styles LIMIT 1")
font_config = cursor.fetchone()
if font_config:
    cursor.execute('INSERT OR IGNORE INTO parameters (name, value) VALUES (?, ?)', ('font_path', font_config[0]))
    cursor.execute('INSERT OR IGNORE INTO parameters (name, value) VALUES (?, ?)', ('font_size', str(font_config[1])))

# Remove font columns from styles table
cursor.execute('''
CREATE TABLE IF NOT EXISTS styles_new (
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

cursor.execute('''
INSERT INTO styles_new (id, device_id, name, bg_color, text_color, highlight_bg_color, highlight_text_color, `default`)
SELECT id, device_id, name, bg_color, text_color, highlight_bg_color, highlight_text_color, `default`
FROM styles
''')

cursor.execute('DROP TABLE styles')
cursor.execute('ALTER TABLE styles_new RENAME TO styles')

# Commit changes and close the connection
conn.commit()
conn.close()