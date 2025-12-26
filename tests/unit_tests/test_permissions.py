import pytest
from epic_events.permissions import commercial_only
from epic_events.views import DisplayMessages
from epic_events.auth import SessionContext


def test_commercial_only_without_session(monkeypatch):
    """Should deny access when no session is provided."""

    @commercial_only
    def protected_function(*args, **kwargs):
        return "OK"

    monkeypatch.setattr(
        DisplayMessages,
        "display_error",
        lambda msg: msg
    )

    result = protected_function()

    assert result is None


def test_commercial_only_with_wrong_role(monkeypatch):
    """Should deny access when user role is not commercial."""

    session = SessionContext(
        username="john",
        role="support",
        is_authenticated=True
    )

    @commercial_only
    def protected_function(*args, **kwargs):
        return "OK"

    monkeypatch.setattr(
        DisplayMessages,
        "display_error",
        lambda msg: msg
    )

    result = protected_function(session=session)

    assert result is None


def test_commercial_only_with_valid_session():
    """Should allow access when user is authenticated and commercial."""

    session = SessionContext(
        username="john",
        role="commercial",
        is_authenticated=True
    )

    @commercial_only
    def protected_function(*args, **kwargs):
        return "OK"

    result = protected_function(session=session)

    assert result == "OK"
