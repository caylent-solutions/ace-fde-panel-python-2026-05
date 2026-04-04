"""Auth package public surface.

Re-exports the password helpers so existing call sites keep
working while the implementation moves to bcrypt under the hood.
"""

from .passwords import hash_password, is_legacy_hash, verify_password

__all__ = ["hash_password", "is_legacy_hash", "verify_password"]
