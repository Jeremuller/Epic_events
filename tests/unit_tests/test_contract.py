import pytest
from epic_events.models import Contract


def test_create_contract_valid(db_session, test_user, test_client):
    """Test that a valid contract can be created."""
    contract = Contract.create(
        db=db_session,
        total_price=1000.00,
        rest_to_pay=500.00,
        client_id=test_client.client_id,
        commercial_contact_id=test_user.user_id
    )
    assert contract.total_price == 1000.00
    assert contract.client_id == test_client.client_id


def test_create_contract_invalid_rest_to_pay(db_session, test_user, test_client):
    """Test that creating a contract with rest_to_pay > total_price raises a ValueError."""
    with pytest.raises(ValueError, match="inferior_total_price"):
        Contract.create(
            db=db_session,
            total_price=1000.00,
            rest_to_pay=1500.00,  # rest_to_pay > total_price
            client_id=test_client.client_id,
            commercial_contact_id=test_user.user_id
        )


def test_update_contract_signed_status(db_session, test_user, test_client):
    """Test that a contract's signed status can be updated."""
    contract = Contract.create(
        db=db_session,
        total_price=1000.00,
        rest_to_pay=500.00,
        client_id=test_client.client_id,
        commercial_contact_id=test_user.user_id
    )
    assert contract.signed is False
    contract.update(db=db_session, signed=True)
    assert contract.signed is True


def test_update_contract_rest_to_pay(db_session, test_user, test_client):
    """Test that updating rest_to_pay respects total_price constraint."""
    contract = Contract.create(
        db=db_session,
        total_price=1000.00,
        rest_to_pay=500.00,
        client_id=test_client.client_id,
        commercial_contact_id=test_user.user_id
    )
    # Valid update
    contract.update(db=db_session, rest_to_pay=300.00)
    assert contract.rest_to_pay == 300.00
    # Wrong update (rest_to_pay > total_price)
    with pytest.raises(ValueError, match="inferior_total_price"):
        contract.update(db=db_session, rest_to_pay=1500.00)


def test_contract_creation_date(db_session, test_user, test_client):
    """Test that a contract's creation date is set on creation."""
    contract = Contract.create(
        db=db_session,
        total_price=1000.00,
        rest_to_pay=500.00,
        client_id=test_client.client_id,
        commercial_contact_id=test_user.user_id
    )
    assert contract.creation is not None


def test_create_contract_with_none_client_id(db_session, test_user):
    """Test that creating a contract with None client_id raises a ValueError."""
    with pytest.raises(ValueError, match="client_not_found"):
        Contract.create(
            db=db_session,
            total_price=1000.00,
            rest_to_pay=500.00,
            client_id=None,
            commercial_contact_id=test_user.user_id
        )


def test_create_contract_with_none_commercial_id(db_session, test_client):
    """Test that creating a contract with None commercial_contact_id raises a ValueError."""
    with pytest.raises(ValueError, match="contact_not_found"):
        Contract.create(
            db=db_session,
            total_price=1000.00,
            rest_to_pay=500.00,
            client_id=test_client.client_id,
            commercial_contact_id=9999
        )


def test_update_contract_with_invalid_client_id(db_session, test_user, test_client):
    """Test that updating a contract with an invalid client_id raises a ValueError."""
    contract = Contract.create(
        db=db_session,
        total_price=1000.00,
        rest_to_pay=500.00,
        client_id=test_client.client_id,
        commercial_contact_id=test_user.user_id
    )
    with pytest.raises(ValueError, match="client_not_found"):
        contract.update(
            db=db_session,
            client_id=9999
        )


def test_update_contract_with_invalid_commercial_id(db_session, test_user, test_client):
    """Test that updating a contract with an invalid commercial_contact_id raises a ValueError."""
    contract = Contract.create(
        db=db_session,
        total_price=1000.00,
        rest_to_pay=500.00,
        client_id=test_client.client_id,
        commercial_contact_id=test_user.user_id
    )
    with pytest.raises(ValueError, match="contact_not_found"):
        contract.update(
            db=db_session,
            commercial_contact_id=9999
        )


def test_get_contracts_by_client(db_session, test_user, test_client):
    """Test that all contracts for a specific client can be retrieved."""
    contract1 = Contract.create(
        db=db_session,
        total_price=1000.00,
        rest_to_pay=500.00,
        client_id=test_client.client_id,
        commercial_contact_id=test_user.user_id
    )
    contract2 = Contract.create(
        db=db_session,
        total_price=2000.00,
        rest_to_pay=1000.00,
        client_id=test_client.client_id,
        commercial_contact_id=test_user.user_id
    )
    contracts = [c for c in Contract.get_all(db_session) if c.client_id == test_client.client_id]
    assert len(contracts) == 2
    assert contract1 in contracts
    assert contract2 in contracts
