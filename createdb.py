import sqlite3

# Create or connect to the test.db SQLite database
conn = sqlite3.connect('test.db')
c = conn.cursor()

# Create the users table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
''')

# Insert 5 sample entries into the users table
users = [
    ('admin','verysecurepassword')
    ('alice', 'password123'),
    ('bob', 'qwerty456'),
    ('charlie', 'mypassword789'),
    ('david', 'letmein101'),
    ('eve', '12345secure'),
]

# Insert the data into the users table
c.executemany('INSERT INTO users (username, password) VALUES (?, ?)', users)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database created with sample users.")
