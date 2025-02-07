from dataclasses import dataclass


@dataclass
class User:
    username: str
    password: bytes
    salt: bytes
