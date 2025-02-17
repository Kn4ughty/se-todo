from dataclasses import dataclass, field
import bcrypt
import secrets
import time
from loguru import logger as log

import server.database as db


@dataclass
class Token:
    token: str | None = None
    token_expiry_time: float | None = None

    def is_token_valid(self) -> bool:
        now = time.time()
        if self.token_expiry_time is None:
            log.error("Is token valid was asked on uninitialsed token")
            raise Exception
        return True if (self.token_expiry_time >= now) else False


@dataclass
class User:
    username: str
    password: bytes
    token: Token = field(default_factory=Token)

    def check_passsword(self, password: bytes) -> bool:
        return True if bcrypt.checkpw(password, self.password) else False

    # Expires in 1 day by default
    def create_token(self, expires_in: float = (5)):
        now = time.time()
        self.token.token_expiry_time = now + expires_in
        self.token.token = secrets.token_urlsafe(16)
        db.add_token(self)

    def get_token(self):
        # Check if token exists for username in db.
        db_token = db.get_token_from_user(self)
        if db_token is not None:
            if db_token.is_token_valid():
                return db_token
            else:
                db.revoke_token(db_token)

        self.create_token()
        return self.token

        # If not then create one and add to db and return
