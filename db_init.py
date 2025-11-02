import sqlite3
import os

DB = "app.db"
if os.path.exists(DB):
    os.remove(DB)

conn = sqlite3.connect(DB)
c = conn.cursor()

# users table (simple, plaintext password for training only)
c.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    fullname TEXT
)
''')

# accounts table (bank-like)
c.execute('''
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    balance INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# comments table (stored XSS)
c.execute('''
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    comment TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# sample users
c.execute("INSERT INTO users (username, password, role, fullname) VALUES ('alice', 'password123', 'user', 'Alice')")
c.execute("INSERT INTO users (username, password, role, fullname) VALUES ('bob', 'mypassword', 'user', 'Bob')")
c.execute("INSERT INTO users (username, password, role, fullname) VALUES ('admin', 'adminpass', 'admin', 'Administrator')")

# accounts
c.execute("INSERT INTO accounts (user_id, balance) VALUES (1, 1000)")  # Alice
c.execute("INSERT INTO accounts (user_id, balance) VALUES (2, 500)")   # Bob
c.execute("INSERT INTO accounts (user_id, balance) VALUES (3, 10000)") # Admin

conn.commit()
conn.close()
print("Database created: app.db (users: alice, bob, admin)")
