import os
import base64
import hashlib
import hmac
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

load_dotenv()

def _fernet() -> Fernet:
    key = os.getenv("PII_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("Set PII_ENCRYPTION_KEY to a Fernet key in environment/.env")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("PII_ENCRYPTION_KEY must be a valid Fernet key") from exc

def encrypt_pii(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("PII value must be a string")
    return _fernet().encrypt(value.encode("utf-8")).decode("ascii")

def decrypt_pii(value: str) -> str:
    try:
        return _fernet().decrypt(value.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("PII ciphertext is invalid or the encryption key does not match") from exc

def pii_lookup_hash(value: str) -> str:
    """Return a keyed, deterministic lookup token without storing the identifier."""
    key = os.getenv("PII_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError("Set PII_ENCRYPTION_KEY to a Fernet key in environment/.env")
    try:
        raw_key = base64.urlsafe_b64decode(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("PII_ENCRYPTION_KEY must be a valid Fernet key") from exc
    return hmac.new(raw_key, value.encode("utf-8"), hashlib.sha256).hexdigest()
