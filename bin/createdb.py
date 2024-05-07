import sqlite3
from passlib.hash import pbkdf2_sha256

class DatabaseSetup:
    def __init__(self, db_name='bank.db'):
        self.db_name = db_name

    def create_connection(self):
        """Create a database connection."""
        try:
            conn = sqlite3.connect(self.db_name)
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return None

    def create_tables(self):
        """Create users and accounts tables if they do not already exist."""
        try:
            conn = self.create_connection()
            if conn is not None:
                c = conn.cursor()
                # Create users table
                c.execute('''
                    CREATE TABLE IF NOT EXISTS users
                    (email TEXT PRIMARY KEY, name TEXT, password TEXT)
                ''')
                # Create accounts table
                c.execute('''
                    CREATE TABLE IF NOT EXISTS accounts
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, account_number TEXT,
                     balance REAL, owner TEXT, FOREIGN KEY (owner) REFERENCES users(email))
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating tables: {e}")
        finally:
            if conn:
                conn.close()

    def insert_sample_data(self):
        """Insert sample user data into the users table."""
        try:
            conn = self.create_connection()
            if conn is not None:
                c = conn.cursor()
                # Use SQL transactions and handle existing data
                with conn:
                    c.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)",
                              ('alice@example.com', 'Alice Xu', pbkdf2_sha256.hash('123456'),
                              ('bob@example.com', 'Bobby Tables', pbkdf2_sha256.hash('123456'))))
        except sqlite3.Error as e:
            print(f"An error occurred while inserting sample data: {e}")
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    db_setup = DatabaseSetup()
    db_setup.create_tables()
    db_setup.insert_sample_data()
