"""Tests for the bcrypt-based password helpers + legacy-hash compat."""

from __future__ import annotations

import hashlib

import pytest

from app.auth.passwords import hash_password, is_legacy_hash, verify_password


def _legacy_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def test_hash_password_produces_a_bcrypt_digest() -> None:
    digest = hash_password("correct horse battery staple")
    assert digest.startswith("$2b$") or digest.startswith("$2a$")
    assert digest != _legacy_hash("correct horse battery staple")


def test_hash_password_is_salted() -> None:
    a = hash_password("hunter2")
    b = hash_password("hunter2")
    assert a != b


def test_verify_password_accepts_correct_bcrypt_password() -> None:
    digest = hash_password("hunter2")
    assert verify_password("hunter2", digest) is True


def test_verify_password_rejects_wrong_bcrypt_password() -> None:
    digest = hash_password("hunter2")
    assert verify_password("hunter3", digest) is False


def test_verify_password_accepts_correct_legacy_sha256_password() -> None:
    legacy = _legacy_hash("oldpass")
    assert verify_password("oldpass", legacy) is True


def test_verify_password_rejects_wrong_legacy_password() -> None:
    legacy = _legacy_hash("oldpass")
    assert verify_password("nope", legacy) is False


def test_verify_password_returns_false_for_empty_inputs() -> None:
    assert verify_password("", "anything") is False
    assert verify_password("anything", "") is False


def test_verify_password_returns_false_for_malformed_hash() -> None:
    assert verify_password("hunter2", "not-a-real-hash") is False


def test_is_legacy_hash_recognizes_64_char_hex() -> None:
    assert is_legacy_hash(_legacy_hash("anything")) is True


def test_is_legacy_hash_rejects_bcrypt_digest() -> None:
    assert is_legacy_hash(hash_password("hunter2")) is False


def test_is_legacy_hash_rejects_short_strings() -> None:
    assert is_legacy_hash("deadbeef") is False


def test_is_legacy_hash_rejects_non_hex_64_char_string() -> None:
    not_hex = "z" * 64
    assert is_legacy_hash(not_hex) is False


def test_hash_password_rejects_empty_password() -> None:
    with pytest.raises(ValueError):
        hash_password("")
