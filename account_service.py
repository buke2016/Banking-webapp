import sqlite3

class Account:
    def __init__(self, id, account_number, balance, owner):
        self.id = id
        self.account_number = account_number
        self.balance = balance
        self.owner = owner

class AccountService:
    def __init__(self):
        self.db_name = 'bank.db'

    def get_accounts_by_user(self, owner):
        """Fetch all accounts for a given user."""
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, account_number, balance, owner FROM accounts WHERE owner=?", (owner,))
            accounts = [Account(*row) for row in cur.fetchall()]
            return accounts

    def get_account_by_id(self, account_number):
        """Retrieve a single account by account number."""
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, account_number, balance, owner FROM accounts WHERE account_number=?", (account_number,))
            row = cur.fetchone()
            return Account(*row) if row else None

    def get_balance(self, account_number, owner):
        """Get the current balance of an account."""
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT balance FROM accounts WHERE account_number=? AND owner=?", (account_number, owner))
            row = cur.fetchone()
            return row[0] if row else None

    def transfer_funds(self, from_account, to_account, amount):
        """Transfer funds between two accounts."""
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            # Ensure both accounts exist and retrieve their balances
            cur.execute("SELECT balance FROM accounts WHERE account_number=?", (from_account,))
            from_balance = cur.fetchone()
            if from_balance is None or from_balance[0] < amount:
                raise ValueError("Insufficient funds or from_account does not exist.")

            cur.execute("SELECT balance FROM accounts WHERE account_number=?", (to_account,))
            to_balance = cur.fetchone()
            if to_balance is None:
                raise ValueError("to_account does not exist.")

            try:
                # Begin transaction
                conn.execute("BEGIN")
                # Update account balances
                cur.execute("UPDATE accounts SET balance = balance - ? WHERE account_number=?", (amount, from_account))
                cur.execute("UPDATE accounts SET balance = balance + ? WHERE account_number=?", (amount, to_account))
                conn.commit()  # Commit the changes
            except sqlite3.Error as e:
                conn.rollback()  # Roll back changes on error
                raise RuntimeError(f"Database transaction failed: {e}")
            return True
