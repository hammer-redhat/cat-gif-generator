"""
Demonstrates cryptography (Fernet) by encrypting/decrypting a local config token.
Generates a key on first run and stores it in .secret.key.
"""
import os
from cryptography.fernet import Fernet

KEY_FILE = ".secret.key"


def _load_or_create_key() -> bytes:
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key


def encrypt(plaintext: str) -> bytes:
    f = Fernet(_load_or_create_key())
    return f.encrypt(plaintext.encode())


def decrypt(token: bytes) -> str:
    f = Fernet(_load_or_create_key())
    return f.decrypt(token).decode()


def get_session_token() -> str:
    """Returns a stable encrypted session token, creating it on first call."""
    token_file = ".session.token"
    if os.path.exists(token_file):
        with open(token_file, "rb") as f:
            return decrypt(f.read())
    token = "cat-gif-session-v1"
    encrypted = encrypt(token)
    with open(token_file, "wb") as f:
        f.write(encrypted)
    return token
