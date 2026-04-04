"""Password hashing using bcrypt.

Centralizing the algorithm here keeps the choice of hash in one
file so any future swap (argon2, scrypt) is a single-module
change. Legacy sha256 hashes coexist via the migration helper.
"""

from __future__ import annotations

import hashlib

import bcrypt

_BCRYPT_ROUNDS = 12
_LEGACY_SHA256_LEN = 64


def hash_password(password: str) -> str:
    """Produce a bcrypt hash for the given plaintext password."""
    if not password:
        raise ValueError("password must not be empty")
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    digest = bcrypt.hashpw(password.encode("utf-8"), salt)
    return digest.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against either a bcrypt hash or a legacy sha256 hash.

    Returns False on any structural mismatch — never raises for
    malformed stored hashes.
    """
    if not password or not password_hash:
        return False
    if is_legacy_hash(password_hash):
        return _verify_legacy_sha256(password, password_hash)
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def is_legacy_hash(password_hash: str) -> bool:
    """A legacy sha256 hex digest is exactly 64 lowercase hex characters."""
    if len(password_hash) != _LEGACY_SHA256_LEN:
        return False
    try:
        int(password_hash, 16)
    except ValueError:
        return False
    return True


def _verify_legacy_sha256(password: str, password_hash: str) -> bool:
    candidate = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return candidate == password_hash
