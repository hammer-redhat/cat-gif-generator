import os
from cryptography.fernet import Fernet

_fernet = Fernet(Fernet.generate_key())


def encrypt(plaintext: str) -> bytes:
    return _fernet.encrypt(plaintext.encode())


def decrypt(token: bytes) -> str:
    return _fernet.decrypt(token).decode()


def get_session_token() -> str:
    return os.urandom(16).hex()
