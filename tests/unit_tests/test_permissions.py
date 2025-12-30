import pytest
from epic_events.permissions import commercial_only, role_permission
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


def test_manager_can_update_any_contract(db_session, management_session, test_contract):
    @role_permission(["management", "commercial"])
    def fake_update(*, db, session, contract_id):
        return "OK"

    result = fake_update(db=db_session, session=management_session, contract_id=test_contract.contract_id)
    assert result == "OK"


def test_commercial_can_update_own_contract(db_session, commercial_session, test_contract):
    @role_permission(["management", "commercial"])
    def fake_update(*, db, session, contract_id):
        # assignment check
        contract = db.query(Contract).get(contract_id)
        if session.role == "commercial" and contract.client.commercial_contact_id != session.user_id:
            raise ValueError("ACCESS_DENIED")
        return "OK"

    result = fake_update(db=db_session, session=commercial_session, contract_id=test_contract.contract_id)
    assert result == "OK"


def test_commercial_cannot_update_other_contract(db_session, commercial_session, test_contract):
    commercial_session.user_id += 999

    @role_permission(["management", "commercial"])
    def fake_update(*, db, session, contract_id):
        contract = db.query(Contract).get(contract_id)
        if session.role == "commercial" and contract.client.commercial_contact_id != session.user_id:
            raise ValueError("ACCESS_DENIED")
        return "OK"

    import pytest
    with pytest.raises(ValueError) as exc:
        fake_update(db=db_session, session=commercial_session, contract_id=test_contract.contract_id)
    assert str(exc.value) == "ACCESS_DENIED"


def test_support_cannot_update_contract(db_session, support_session, test_contract):
    """
    Ensure that a support user cannot update a contract.
    Should raise ValueError with message "ACCESS_DENIED".
    """
    @role_permission(["management", "commercial"])
    def fake_update(*, db, session, contract_id):
        contract = db.query(Contract).get(contract_id)
        # Check assignment for commercial
        if session.role == "commercial" and contract.client.commercial_contact_id != session.user_id:
            raise ValueError("ACCESS_DENIED")
        return "OK"

    import pytest
    with pytest.raises(ValueError) as exc:
        fake_update(db=db_session, session=support_session, contract_id=test_contract.contract_id)

    assert str(exc.value) == "ACCESS_DENIED"

