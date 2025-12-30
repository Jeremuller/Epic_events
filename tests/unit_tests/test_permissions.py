import pytest
from epic_events.permissions import commercial_only, requires_assignment
from epic_events.views import DisplayMessages
from epic_events.auth import SessionContext
from epic_events.controllers import ContractController
from epic_events.models import Event, Client, Contract, User


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
        username="john", user_id=98,
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
        username="john", user_id=98,
        role="commercial",
        is_authenticated=True
    )

    @commercial_only
    def protected_function(*args, **kwargs):
        return "OK"

    result = protected_function(session=session)

    assert result == "OK"


def test_list_contracts_requires_authentication(db_session, monkeypatch):
    """
    Should deny access if session is missing or not authenticated.
    """
    mock_list = monkeypatch.setattr(
        "epic_events.views.ContractView.list_contracts",
        lambda *_: pytest.fail("list_contracts should not be called")
    )

    called = {}

    def fake_error(msg):
        called["msg"] = msg

    monkeypatch.setattr(
        "epic_events.views.DisplayMessages.display_error",
        fake_error
    )

    ContractController.list_contracts(db_session, session=None)

    assert called["msg"] == "ACCESS_DENIED"


def test_list_contracts_authenticated(db_session, management_session, monkeypatch):
    """
    Should allow access when session is authenticated.
    """

    called = {"called": False}

    def fake_list_contracts(contracts):
        called["called"] = True

    monkeypatch.setattr(
        "epic_events.views.ContractView.list_contracts",
        fake_list_contracts
    )

    ContractController.list_contracts(db_session, management_session)

    assert called["called"] is True
