"""Transparent password-hash migration helpers.

Existing users have sha256 hashes in the database. Rather than
forcing a password reset, the login path detects legacy hashes
and rehashes to bcrypt on successful auth. The same shape is
reusable if we ever swap algorithms again.
"""

from __future__ import annotations

from typing import Protocol

from sqlalchemy.orm import Session

from .passwords import hash_password, is_legacy_hash, verify_password


class _UserLike(Protocol):
    password_hash: str


def detect_legacy_hash(password_hash: str) -> bool:
    """Return True if the stored hash is a legacy sha256 digest."""
    return is_legacy_hash(password_hash)


def rehash_on_login(
    user: _UserLike,
    plaintext_password: str,
    session: Session,
) -> bool:
    """Rehash the user's stored password with bcrypt if it's still legacy.

    Returns True iff a rehash actually happened. Callers should only
    invoke this after `verify_password` has already returned True for
    the same plaintext — the function re-verifies defensively but
    will not write a new hash if the plaintext doesn't match the
    stored legacy hash.
    """
    if not detect_legacy_hash(user.password_hash):
        return False
    if not verify_password(plaintext_password, user.password_hash):
        return False
    user.password_hash = hash_password(plaintext_password)
    session.add(user)
    session.commit()
    return True
