import pytest
from epic_events.auth import hash_password, verify_password, SessionContext
from epic_events.views import LoginView, DisplayMessages
from epic_events.models import User
from epic_events.controllers import LoginController

from datetime import datetime, timedelta


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


def test_login_success(monkeypatch, db_session):
    """Login should return a SessionContext when credentials are valid."""
    password = "secure_pass"
    user = User.create(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="jdoe@example.com",
        role="commercial",
        password_hash=hash_password(password)
    )
    db_session.add(user)
    db_session.commit()

    monkeypatch.setattr(
        LoginView,
        "prompt_login",
        lambda: {"username": "jdoe", "password": password}
    )

    session = LoginController.login(db_session)

    assert isinstance(session, SessionContext)
    assert session.is_authenticated is True
    assert session.username == "jdoe"
    assert session.role == "commercial"


def test_login_fails_with_unknown_user(monkeypatch, db_session):
    """Login should fail when the username does not exist."""
    monkeypatch.setattr(
        LoginView,
        "prompt_login",
        lambda: {"username": "unknown_user", "password": "any"}
    )

    session = LoginController.login(db_session)
    assert session is None


def test_login_displays_success_message(monkeypatch, db_session):
    """Login should display a success message on successful authentication."""
    password = "secure_pass"
    user = User.create(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="jdoe@example.com",
        role="commercial",
        password_hash=hash_password(password)
    )
    db_session.add(user)
    db_session.commit()

    monkeypatch.setattr(
        LoginView,
        "prompt_login",
        lambda: {"username": "jdoe", "password": password}
    )

    success_called = {}

    def fake_display_success(msg):
        success_called["msg"] = msg

    monkeypatch.setattr(DisplayMessages, "display_success", fake_display_success)

    session = LoginController.login(db_session)
    assert session.is_authenticated is True
    assert "jdoe" in success_called["msg"]


def test_login_with_empty_username(monkeypatch, db_session):
    """Login should fail gracefully when username is empty."""
    monkeypatch.setattr(
        LoginView,
        "prompt_login",
        lambda: {"username": "", "password": "whatever"}
    )
    session = LoginController.login(db_session)
    assert session is None


def test_login_with_empty_password(monkeypatch, db_session):
    """Login should fail gracefully when password is empty."""
    monkeypatch.setattr(
        LoginView,
        "prompt_login",
        lambda: {"username": "jdoe", "password": ""}
    )
    session = LoginController.login(db_session)
    assert session is None


def test_session_context_authenticated():
    session = SessionContext(
        username="john_doe",
        user_id=98,
        role="commercial",
        is_authenticated=True
    )

    assert session.is_authenticated is True
    assert session.username == "john_doe"
    assert session.role == "commercial"


def test_session_context_default_authentication():
    """A newly created session should be unauthenticated by default."""
    session = SessionContext(username="alice", user_id=98, role="support")
    assert session.is_authenticated is False
    assert session.username == "alice"
    assert session.role == "support"


def test_session_context_repr():
    """The __repr__ method should return a readable string representation."""
    session = SessionContext(username="bob", user_id=98, role="management", is_authenticated=True)
    expected = "<SessionContext username='bob' role='management' authenticated=True>"
    assert repr(session) == expected


def test_session_expired_is_invalid():
    """
        Ensure that a session becomes invalid once its expiration timeout is exceeded.

        This test simulates an expired session by manually setting the creation
        timestamp in the past and verifies that:
        - the session is considered invalid
        - the authentication flag is automatically cleared
    """
    session = SessionContext(
        username="test",
        user_id=1,
        role="management",
        is_authenticated=True
    )

    session.created_at = datetime.now() - timedelta(minutes=20)

    assert session.is_valid() is False
    assert session.is_authenticated is False


def test_session_end_session_invalidates():
    """
        Ensure that calling end_session() explicitly invalidates the session.

        This test verifies that ending a session:
        - immediately marks the session as invalid
        - prevents any further authenticated access
    """
    session = SessionContext(
        username="test",
        user_id=1,
        role="management",
        is_authenticated=True
    )

    session.end_session()

    assert session.is_valid() is False


def test_logout_ends_session(monkeypatch):
    """
        Ensure that the logout controller properly terminates the user session.

        This test mocks the logout confirmation prompt to simulate a user
        confirming the logout action and verifies that:
        - logout returns True
        - the session is no longer authenticated after logout
    """
    session = SessionContext(
        username="test",
        user_id=1,
        role="management",
        is_authenticated=True
    )

    monkeypatch.setattr(
        "epic_events.views.MenuView.logout_confirmation",
        lambda: True
    )

    result = LoginController.logout(session)

    assert result is True
    assert session.is_authenticated is False
