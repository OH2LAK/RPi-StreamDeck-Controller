import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('streamdeck.db')
cursor = conn.cursor()

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
    (device_id_mini, 'default', '#000000', '#FFFFFF', 'Roboto-Medium.ttf', 14, '#333333', '#FFFFFF', 1),  # Default style
    (device_id_mini, 'highlight', '#FFFFFF', '#000000', 'Roboto-Medium.ttf', 14, '#FFFF00', '#000000', 0),
    (device_id_mini, 'long_press_ack', '#FF0000', '#FFFFFF', 'Roboto-Medium.ttf', 14, '#FF0000', '#FFFFFF', 0),
    (device_id_xl, 'default', '#000000', '#FFFFFF', 'Roboto-Medium.ttf', 14, '#333333', '#FFFFFF', 1),  # Default style
    (device_id_xl, 'highlight', '#FFFFFF', '#000000', 'Roboto-Medium.ttf', 14, '#FFFF00', '#000000', 0),
    (device_id_xl, 'long_press_ack', '#FF0000', '#FFFFFF', 'Roboto-Medium.ttf', 14, '#FF0000', '#FFFFFF', 0)
]

cursor.executemany('''
INSERT OR IGNORE INTO styles (device_id, name, bg_color, text_color, font_path, font_size, highlight_bg_color, highlight_text_color, `default`)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', styles_data)

# Insert button configurations with device_id
button_config_data = [
    (device_id_mini, i, f'Button {i+1}', 'default' if i < 5 or i >= 10 else 'highlight', 'long_press_ack', f'short_action_{i+1}', f'long_action_{i+1}', f'ack_action_{i+1}')
    for i in range(15)
] + [
    (device_id_xl, i, f'Button {i+1}', 'default' if i < 5 or i >= 10 else 'highlight', 'long_press_ack', f'short_action_{i+1}', f'long_action_{i+1}', f'ack_action_{i+1}')
    for i in range(15)
]

cursor.executemany('''
INSERT OR IGNORE INTO button_config (device_id, key, text, style, long_press_ack_style, short_press, long_press, ack_action)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', button_config_data)

# Insert parameters data
parameters_data = [
    ('short_press_duration', 0.2),
    ('long_press_duration', 1.0),
    # Add more parameters as needed
]

cursor.executemany('''
INSERT OR IGNORE INTO parameters (name, value)
VALUES (?, ?)
''', parameters_data)

# Commit changes and close the connection
conn.commit()
conn.close()