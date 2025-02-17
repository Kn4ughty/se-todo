from dataclasses import dataclass
import bcrypt
import secrets
import time

import server.database as db


@dataclass
class User:
    username: str
    password: bytes
    token: str | None = None
    token_expiry_time: float | None = None

    def check_passsword(self, password: bytes) -> bool:
        return True if bcrypt.checkpw(password, self.password) else False

    # Expires in 1 day by default
    def create_token(self, expires_in: float = (5)):
        now = time.time()
        self.token_expiry_time = now + expires_in
        self.token = secrets.token_urlsafe(16)
        db.add_token(self)

    def get_token(self):
        # Check if token exists for username in db.
        db_token = db.get_token_from_user(self)
        if db_token is not None:
            # if self.is_token_valid(db_token):
            return db_token

        self.create_token()
        return self.token

        # If not then create one and add to db and return

    @staticmethod
    def is_token_valid(token: float) -> bool:
        now = time.time()
        return True if (token >= now) else False
