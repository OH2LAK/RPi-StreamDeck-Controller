import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('streamdeck.db')
cursor = conn.cursor()

# Add the default column to the styles table
cursor.execute('ALTER TABLE styles ADD COLUMN default INTEGER DEFAULT 0')

# Set the default style
cursor.execute('UPDATE styles SET default = 1 WHERE name = "default"')

# Commit changes and close the connection
conn.commit()
conn.close()