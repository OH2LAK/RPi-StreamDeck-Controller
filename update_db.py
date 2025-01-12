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

# Commit changes and close the connection
conn.commit()
conn.close()