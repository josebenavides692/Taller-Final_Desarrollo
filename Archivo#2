
import hashlib
import os
import hmac


def get_password_hash(password: str) -> str:
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000
    )
    return salt.hex() + ":" + password_hash.hex()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt_hex, stored_hash = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            100_000
        )

        return hmac.compare_digest(
            password_hash.hex(),
            stored_hash
        )

    except (ValueError, TypeError):
        return False
