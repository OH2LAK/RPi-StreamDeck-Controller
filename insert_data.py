import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('streamdeck.db')
cursor = conn.cursor()

# Insert styles data
styles_data = [
    ('default', '#000000', '#FFFFFF', 'Roboto-Medium.ttf', 14, '#333333', '#FFFFFF'),
    ('highlight', '#FFFFFF', '#000000', 'Roboto-Medium.ttf', 14, '#FFFF00', '#000000'),
    ('long_press_ack', '#FF0000', '#FFFFFF', 'Roboto-Medium.ttf', 14, '#FF0000', '#FFFFFF'),  # Add long_press_ack style
    # Add more styles as needed
]

cursor.executemany('''
INSERT OR IGNORE INTO styles (name, bg_color, text_color, font_path, font_size, highlight_bg_color, highlight_text_color)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', styles_data)

# Insert button configurations
button_config_data = [
    (i, f'Button {i+1}', 'default' if i < 5 or i >= 10 else 'highlight', 'long_press_ack', f'short_action_{i+1}', f'long_action_{i+1}', f'ack_action_{i+1}')
    for i in range(15)
]

cursor.executemany('''
INSERT OR IGNORE INTO button_config (key, text, style, long_press_ack_style, short_press, long_press, ack_action)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', button_config_data)

# Commit changes and close the connection
conn.commit()
conn.close()