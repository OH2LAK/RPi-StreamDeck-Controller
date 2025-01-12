import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('streamdeck.db')
cursor = conn.cursor()

# Insert styles data
styles_data = [
    ('default', '#000000', '#FFFFFF', 'Roboto-Medium', 14, '#333333', '#FFFFFF'),
    ('highlight', '#FFFFFF', '#000000', 'Roboto-Medium', 14, '#FFFF00', '#000000'),
    # Add more styles as needed
]

cursor.executemany('''
INSERT OR IGNORE INTO styles (name, bg_color, text_color, font_path, font_size, highlight_bg_color, highlight_text_color)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', styles_data)

# Insert button configurations
button_config_data = [
    (0, 'Button 1', 'default'),
    (1, 'Button 2', 'highlight'),
    # Add more button configurations as needed
]

cursor.executemany('''
INSERT OR IGNORE INTO button_config (key, text, style)
VALUES (?, ?, ?)
''', button_config_data)

# Commit changes and close the connection
conn.commit()
conn.close()