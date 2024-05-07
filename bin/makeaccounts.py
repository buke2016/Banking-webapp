import sqlite3
from passlib.hash import pbkdf2_sha256

def create_tables(conn):
    cur = conn.cursor()
    # Create the users table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY, 
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create the accounts table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY, 
            owner TEXT NOT NULL, 
            balance INTEGER NOT NULL,
            FOREIGN KEY(owner) REFERENCES users(email)
        )
    ''')
    conn.commit()

def insert_sample_data(conn):
    cur = conn.cursor()
    # Insert sample users with name field added
    users = [
        ('alice@example.com', 'Alice Xu', '123456'),
        ('bob@example.com', 'Bobby Tables', '123456')
    ]
    for email, name, password in users:
        if cur.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone() is None:
            hashed_password = pbkdf2_sha256.hash(password)
            cur.execute("INSERT INTO users(email, name, password) VALUES (?, ?, ?)", (email, name, hashed_password))

    # Insert sample accounts
    accounts = [
        ('100', 'alice@example.com', 7500),
        ('190', 'alice@example.com', 200),
        ('998', 'bob@example.com', 1000)
    ]
    for account_id, owner, balance in accounts:
        if cur.execute("SELECT id FROM accounts WHERE id=?", (account_id,)).fetchone() is None:
            cur.execute("INSERT INTO accounts(id, owner, balance) VALUES (?, ?, ?)", (account_id, owner, balance))

    conn.commit()

def create_sample_accounts():
    with sqlite3.connect('bank.db') as conn:
        create_tables(conn)
        insert_sample_data(conn)

if __name__ == '__main__':
    create_sample_accounts()
    print("Sample accounts and users created successfully!")
