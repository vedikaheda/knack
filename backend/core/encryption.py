from cryptography.fernet import Fernet
from .config import get_settings


settings = get_settings()


def _get_fernet() -> Fernet:
    key = settings.encryption_key.encode("utf-8")
    return Fernet(key)


def encrypt_value(value: str) -> str:
    if not value:
        return ""
    token = _get_fernet().encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_value(token: str) -> str:
    if not token:
        return ""
    value = _get_fernet().decrypt(token.encode("utf-8"))
    return value.decode("utf-8")
