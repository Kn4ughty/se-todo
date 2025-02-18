from dataclasses import dataclass, field
import bcrypt
import secrets
import time
from loguru import logger as log

import server.database as db


@dataclass
class Token:
    token: str
    token_expiry_time: float

    @staticmethod
    def is_token_valid(token_expiry_time: float) -> bool:
        now = time.time()

        log.info("ALKSJDLKSADJFKLSDJFLSDJFLKSJDFLkj")
        return True if (token_expiry_time >= now) else False


@dataclass
class User:
    username: str
    password: bytes
    token: None | Token = None

    def check_passsword(self, password: bytes) -> bool:
        return True if bcrypt.checkpw(password, self.password) else False

    # Expires in 1 day by default
    def create_token(self, expires_in: float = (60 * 60)) -> Token:
        now = time.time()
        self.token = Token(secrets.token_urlsafe(16), (now + expires_in))
        db.add_token(self)
        return self.token

    def get_token(self) -> Token:
        # Check if token exists for username in db.
        db_token = db.get_token_from_user(self)
        if db_token is not None:
            if db_token.is_token_valid(db_token.token_expiry_time):
                return db_token
            else:
                db.revoke_token(db_token)

        return self.create_token()

        # If not then create one and add to db and return
