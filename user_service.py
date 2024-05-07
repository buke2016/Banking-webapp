import sqlite3
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from flask import request, g
import jwt

SECRET = 'bfg28y7efg238re7r6t32gfo23vfy7237yibdyo238do2v3'

class UserService:
    def __init__(self):
        self.db_name = 'bank.db'

    def get_user_with_credentials(self, email, password):
        """Fetches a user by their email and password, returning None if no match."""
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute("SELECT email, name, password FROM users WHERE email = ?", (email,))
            row = cur.fetchone()

            if row is None:
                return None

            user_email, name, hashed_password = row
            if pbkdf2_sha256.verify(password, hashed_password):
                return {"email": user_email, "name": name, "token": self.create_token(user_email)}
            else:
                return None

    def get_user_by_email(self, email):
        """Fetches a user by their email, returning None if no match."""
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            cur = conn.cursor()
            cur.execute("SELECT email, name FROM users WHERE email = ?", (email,))
            row = cur.fetchone()

            if row is None:
                return None

            user_email, name = row
            return {"email": user_email, "name": name}

    def logged_in(self):
        """Verifies user's authentication token from the cookies."""
        token = request.cookies.get('auth_token')
        if not token:
            return False

        try:
            data = jwt.decode(token, SECRET, algorithms=['HS256'])
            g.user = data['sub']
            return True
        except jwt.ExpiredSignatureError:
            # Handle expired token
            return False
        except jwt.DecodeError:
            # Handle incorrect token decoding
            return False
        except jwt.InvalidTokenError:
            # Handle invalid token
            return False

    def create_token(self, email):
        """Generates a JWT token for authenticated sessions."""
        now = datetime.utcnow()
        payload = {'sub': email, 'iat': now, 'exp': now + timedelta(minutes=60)}
        token = jwt.encode(payload, SECRET, algorithm='HS256')
        return token
