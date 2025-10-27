import pytest
from click.testing import CliRunner
from epic_events.views import create_contract, list_contracts, update_contract
from epic_events.models import User, Client, Contract


@pytest.fixture
def runner():
    """Fixture to provide a CliRunner for testing CLI commands."""
    return CliRunner()


def test_create_contract_command(runner, db_session, test_user, test_client):
    """Test the create_contract CLI command with valid inputs."""
    inputs = f"1000.0\n500.0\n{test_client.client_id}\n{test_user.user_id}\n"
    result = runner.invoke(
        create_contract,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "✅ Contract created" in result.output
    contracts = db_session.query(Contract).all()
    assert len(contracts) == 1
    assert contracts[0].total_price == 1000.0
    assert contracts[0].rest_to_pay == 500.0
    assert contracts[0].client_id == test_client.client_id
    assert contracts[0].commercial_contact_id == test_user.user_id


def test_create_contract_invalid_total_price(runner, db_session, test_user, test_client):
    """Test create_contract with an invalid total price (≤ 0)."""
    inputs = f"0.0\n500.0\n{test_client.client_id}\n{test_user.user_id}\n"
    result = runner.invoke(
        create_contract,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: Total_price can't be <= 0." in result.output
    contracts = db_session.query(Contract).all()
    assert len(contracts) == 0


def test_create_contract_invalid_rest_to_pay(runner, db_session, test_user, test_client):
    """Test create_contract with an invalid rest to pay (> total_price)."""
    inputs = f"1000.0\n1500.0\n{test_client.client_id}\n{test_user.user_id}\n"
    result = runner.invoke(
        create_contract,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: Total price can't be inferior to rest to pay." in result.output
    contracts = db_session.query(Contract).all()
    assert len(contracts) == 0


def test_create_contract_invalid_client_id(runner, db_session, test_user):
    """Test create_contract with an invalid client ID."""
    inputs = f"1000.0\n500.0\n999\n{test_user.user_id}\n"
    result = runner.invoke(
        create_contract,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: The specified client does not exist." in result.output
    contracts = db_session.query(Contract).all()
    assert len(contracts) == 0


def test_create_contract_invalid_commercial_id(runner, db_session, test_client):
    """Test create_contract with an invalid commercial contact ID."""
    inputs = f"1000.0\n500.0\n{test_client.client_id}\n999\n"
    result = runner.invoke(
        create_contract,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: The contact mentioned does not exist." in result.output
    contracts = db_session.query(Contract).all()
    assert len(contracts) == 0


def test_list_contracts_command(runner, db_session, test_contract):
    """Test the list_contracts CLI command."""
    result = runner.invoke(list_contracts, obj={"db": db_session})
    assert result.exit_code == 0
    assert "=== List of Contracts ===" in result.output
    assert f"ID: {test_contract.contract_id}" in result.output
    assert f"Total: {test_contract.total_price}" in result.output


def test_update_contract_command(runner, db_session, test_contract):
    """Test the update_contract CLI command."""
    inputs = f"2000.0\n1000.0\ny\n"
    result = runner.invoke(
        update_contract,
        args=[str(test_contract.contract_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "✅ Contract updated" in result.output
    updated_contract = db_session.query(Contract).filter_by(contract_id=test_contract.contract_id).first()
    assert updated_contract.total_price == 2000.0
    assert updated_contract.rest_to_pay == 1000.0
    assert updated_contract.signed is True


def test_update_contract_invalid_total_price(runner, db_session, test_contract):
    """Test update_contract with an invalid total price (≤ 0)."""
    inputs = f"0.0\n1000.0\ny\n"
    result = runner.invoke(
        update_contract,
        args=[str(test_contract.contract_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: Total_price can't be <= 0." in result.output
    updated_contract = db_session.query(Contract).filter_by(contract_id=test_contract.contract_id).first()
    assert updated_contract.total_price == 1000.0


def test_update_contract_invalid_rest_to_pay(runner, db_session, test_contract):
    """Test update_contract with an invalid rest to pay (> total_price)."""
    inputs = f"1000.0\n1500.0\ny\n"
    result = runner.invoke(
        update_contract,
        args=[str(test_contract.contract_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: Total price can't be inferior to rest to pay." in result.output
    updated_contract = db_session.query(Contract).filter_by(contract_id=test_contract.contract_id).first()
    assert updated_contract.rest_to_pay == 500.0
