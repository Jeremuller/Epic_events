import pytest
from epic_events.auth import hash_password, verify_password


def test_hash_password_returns_hashed_value():
    password = "my_secret_password"
    hashed = hash_password(password)

    assert hashed != password


def test_hash_password_is_salted():
    password = "my_secret_password"

    hashed1 = hash_password(password)
    hashed2 = hash_password(password)

    assert hashed1 != hashed2


def test_verify_password_success():
    password = "my_secret_password"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    password = "my_secret_password"
    wrong_password = "wrong_password"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_hash_password_returns_string():
    hashed = hash_password("password")
    assert isinstance(hashed, str)
