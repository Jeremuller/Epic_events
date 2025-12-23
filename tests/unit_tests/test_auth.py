import pytest
from epic_events.auth import hash_password, verify_password
from epic_events.views import LoginView, UserView
from epic_events.models import User
from epic_events.controllers import UserController, LoginController


def test_hash_password_returns_hashed_value():
    """
    This test verifies that the hash_password function
    transforms the input password into a non - reversible hashed representation.
    """

    password = "my_secret_password"
    hashed = hash_password(password)

    assert hashed != password


def test_hash_password_is_salted():
    """
    This test validates that a random salt is applied during hashing,
    preventing identical passwords from producing identical hashes.
    """
    password = "my_secret_password"

    hashed1 = hash_password(password)
    hashed2 = hash_password(password)

    assert hashed1 != hashed2


def test_verify_password_success():
    """
    This test checks that a plain text password correctly matches
    its previously generated hash.
    """
    password = "my_secret_password"

    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    """
    This test verifies that authentication fails when the plain text password
    does not match the stored hashed password.
    """
    password = "my_secret_password"

    wrong_password = "wrong_password"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_prompt_login(monkeypatch):
    """Should return username and password from user input."""

    answers = iter(["john_doe", "secretpassword"])

    monkeypatch.setattr(
        "click.prompt",
        lambda msg, **kwargs: next(answers)
    )

    result = LoginView.prompt_login()

    assert result == {
        "username": "john_doe",
        "password": "secretpassword"
    }


def test_login_fails_with_wrong_password(monkeypatch, db_session):
    """Login should fail when password is incorrect."""

    fake_user = User(
        username="john_doe",
        password_hash="fakehashedpassword"
    )

    monkeypatch.setattr(
        User,
        "get_by_username",
        lambda db, username: fake_user
    )

    monkeypatch.setattr("epic_events.controllers.verify_password", lambda password, hashed: False)

    monkeypatch.setattr(
        LoginView,
        "prompt_login",
        lambda: {"username": "john_doe", "password": "wrongpassword"}
    )

    result = LoginController.login(db_session)

    assert result is None


def test_login_controller_success(monkeypatch, db_session, test_user):
    """
    Test that login controller returns the user when credentials are correct.
    """

    # Mock view input
    monkeypatch.setattr(
        "epic_events.views.LoginView.prompt_login",
        lambda: {
            "username": test_user.username,
            "password": "test_password"
        }
    )

    # Mock password verification
    monkeypatch.setattr(
        "epic_events.auth.verify_password",
        lambda plain, hashed: True
    )

    # Call
    user = LoginController.login(db_session)

    # Assert
    assert user is not None
    assert user.username == test_user.username
