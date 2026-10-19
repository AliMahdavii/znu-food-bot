import os

from cryptography.fernet import Fernet, InvalidToken


def get_fernet() -> Fernet:
    """Return the Fernet instance configured with the secret key."""

    key = os.getenv("CREDENTIALS_ENCRYPTION_KEY")

    if not key:
        raise RuntimeError(
            "CREDENTIALS_ENCRYPTION_KEY is not configured."
        )

    try:
        return Fernet(key.encode("utf-8"))
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "CREDENTIALS_ENCRYPTION_KEY is invalid."
        ) from exc


def encrypt_password(password: str) -> str:
    """Encrypt a university account password."""

    if not password:
        raise ValueError("Password cannot be empty.")

    encrypted = get_fernet().encrypt(password.encode("utf-8"))

    return encrypted.decode("utf-8")


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt a university account password."""

    try:
        decrypted = get_fernet().decrypt(
            encrypted_password.encode("utf-8")
        )
    except InvalidToken as exc:
        raise RuntimeError(
            "Password decryption failed. Check the encryption key."
        ) from exc

    return decrypted.decode("utf-8")
