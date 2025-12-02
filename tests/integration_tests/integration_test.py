import pytest
from click.testing import CliRunner
from epic_events.views import (UserView, ClientView, ContractView, EventView)
from epic_events.models import User, Client, Contract, Event
from datetime import datetime, timedelta


def test_user_client_contract_event_integration(db_session, test_user, test_client, test_contract):
    """
    Test the complete integration flow from User to Client to Contract to Event.
    This test verifies that all relationships and validations work correctly together.
    """
    assert test_user is not None
    assert test_user.role == "commercial"

    assert test_client is not None
    assert test_client.commercial_contact_id == test_user.user_id

    assert test_contract is not None
    assert test_contract.client_id == test_client.client_id
    assert test_contract.commercial_contact_id == test_user.user_id

    start_datetime = datetime.now() + timedelta(days=30)
    end_datetime = datetime.now() + timedelta(days=31)
    event = Event.create(
        db=db_session,
        name="Team Meeting",
        notes="Quarterly team meeting",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        location="Paris",
        attendees=50,
        client_id=test_client.client_id,
        support_contact_id=test_user.user_id
    )

    assert event is not None
    assert event.client_id == test_client.client_id
    assert event.support_contact_id == test_user.user_id

    assert test_user in [event.support_contact]
    assert test_client in [event.client]


def test_create_user_cli_integration(db_session, test_user):
    """
    Test the complete integration flow for the create_user CLI command.
    This test verifies that the CLI command correctly creates a user in the database.
    """
    runner = CliRunner()

    inputs = "jane_doe\nJane\nDoe\njane.doe@example.com\ncommercial\n"
    result = runner.invoke(
        create_user,
        input=inputs,
        obj={"db": db_session}
    )

    assert result.exit_code == 0

    assert "✅ User created" in result.output

    users = db_session.query(User).all()
    assert len(users) == 2

    new_user = users[-1]
    assert new_user.username == "jane_doe"
    assert new_user.first_name == "Jane"
    assert new_user.last_name == "Doe"
    assert new_user.email == "jane.doe@example.com"
    assert new_user.role == "commercial"


def test_create_user_cli_integration_error(db_session, test_user):
    """
    Test the error handling in the create_user CLI command.
    This test verifies that the CLI command correctly handles duplicate usernames.
    """
    runner = CliRunner()

    inputs = f"{test_user.username}\nJohn\nDoe\njohn.doe@example.com\ncommercial\n"
    result = runner.invoke(
        create_user,
        input=inputs,
        obj={"db": db_session}
    )

    assert result.exit_code == 0
    assert "❌ Error: This username is already taken." in result.output

    users = db_session.query(User).all()
    assert len(users) == 1


def test_full_flow_integration(db_session):
    """
    Test the complete integration flow from User to Client to Contract to Event using CLI commands.
    This test verifies that all CLI commands work together correctly.
    """
    runner = CliRunner()

    user_inputs = "john_doe\nJohn\nDoe\njohn.doe@example.com\ncommercial\n"
    result = runner.invoke(create_user, input=user_inputs, obj={"db": db_session})
    assert result.exit_code == 0
    assert "✅ User created" in result.output

    users = db_session.query(User).all()
    assert len(users) == 1
    user = users[0]

    client_inputs = f"Alice\nSmith\nalice.smith@example.com\n{user.user_id}\nSmith Corp\n1234567890\n"
    result = runner.invoke(
        create_client,
        input=client_inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "✅ Client created" in result.output

    clients = db_session.query(Client).all()
    assert len(clients) == 1
    client = clients[0]

    from datetime import datetime, timedelta
    contract_inputs = f"1000.0\n500.0\n{client.client_id}\n{user.user_id}\n"
    result = runner.invoke(
        create_contract,
        input=contract_inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "✅ Contract created" in result.output

    contracts = db_session.query(Contract).all()
    assert len(contracts) == 1
    contract = contracts[0]

    start_datetime = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M")
    end_datetime = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d %H:%M")
    event_inputs = f"Team Meeting\n{start_datetime}\n{end_datetime}\nParis\n50\nNotes\n{client.client_id}\n{user.user_id}\n"
    result = runner.invoke(
        create_event,
        input=event_inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "✅ Event created" in result.output

    events = db_session.query(Event).all()
    assert len(events) == 1


def test_list_users_integration(capsys, db_session, test_user):
    """
    Test the list_users function with a pre-populated database.
    This test verifies that the function correctly lists all users.
    """
    users = User.get_all(db_session)

    UserView.list_users(users)

    captured = capsys.readouterr()

    assert "=== List of Users ===" in captured.out
    assert f"ID: {test_user.user_id}" in captured.out
    assert f"{test_user.username}" in captured.out


def test_update_user_cli_integration(db_session, test_user):
    """
    Test the update_user CLI command.
    This test verifies that the CLI command correctly updates a user.
    """
    runner = CliRunner()

    result = runner.invoke(
        update_user,
        args=[str(test_user.user_id)],
        input=f"johnny_doe\nJohnny\nDoe\njohnny.doe@example.com\ncommercial\n",
        obj={"db": db_session}
    )

    assert result.exit_code == 0
    assert "✅ User updated" in result.output

    updated_user = db_session.query(User).filter_by(user_id=test_user.user_id).first()
    assert updated_user.username == "johnny_doe"
    assert updated_user.first_name == "Johnny"
    assert updated_user.email == "johnny.doe@example.com"


def test_delete_user_cli_integration(db_session, test_user):
    """
    Test the delete_user CLI command.
    This test verifies that the CLI command correctly deletes a user.
    """
    runner = CliRunner()

    result = runner.invoke(
        delete_user,
        args=[str(test_user.user_id)],
        input="y\n",
        obj={"db": db_session}
    )

    assert result.exit_code == 0
    assert "✅ User deleted" in result.output

    users = db_session.query(User).all()
    assert len(users) == 0


def test_create_client_cli_integration_duplicate_email(db_session, test_client):
    """
    Test the error handling in the create_client CLI command.
    This test verifies that the CLI command correctly handles duplicate emails.
    """
    runner = CliRunner()
    inputs = f"Test\nClient\n{test_client.email}\n1\nBusiness Corp\n1234567890\n"
    result = runner.invoke(
        create_client,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: This email is already registered." in result.output
    clients = db_session.query(Client).all()
    assert len(clients) == 1


def test_create_contract_cli_integration_invalid_client(db_session, test_user):
    """
    Test the error handling in the create_contract CLI command.
    This test verifies that the CLI command correctly handles invalid client IDs.
    """
    runner = CliRunner()
    inputs = "1000.0\n500.0\n999\n1\n"
    result = runner.invoke(
        create_contract,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: The specified client does not exist." in result.output
    contracts = db_session.query(Contract).all()
    assert len(contracts) == 0


def test_create_event_cli_integration_invalid_dates(db_session, test_user, test_client):
    """
    Test the error handling in the create_event CLI command.
    This test verifies that the CLI command correctly handles invalid dates.
    """
    runner = CliRunner()
    from datetime import datetime, timedelta
    start_datetime = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    end_datetime = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Past Event\n{start_datetime}\n{end_datetime}\nParis\n50\nNotes\n{test_client.client_id}"
              f"\n{test_user.user_id}\n")
    result = runner.invoke(
        create_event,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: Event date must be in the future." in result.output
    events = db_session.query(Event).all()
    assert len(events) == 0


def test_update_user_cli_integration_duplicate_email(db_session, test_user):
    """
    Test the error handling in the update_user CLI command.
    This test verifies that the CLI command correctly handles duplicate emails during update.
    """

    user2 = User.create(
        db=db_session,
        username="test_user2",
        first_name="Test2",
        last_name="User2",
        email="test2@example.com",
        role="commercial"
    )

    runner = CliRunner()
    result = runner.invoke(
        update_user,
        args=[str(test_user.user_id)],
        input=f"{test_user.username}\n{test_user.first_name}\n{test_user.last_name}\n{user2.email}\n{test_user.role}\n",
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: This email is already registered." in result.output
    updated_user = db_session.query(User).filter_by(user_id=test_user.user_id).first()
    assert updated_user.email == test_user.email


def test_update_contract_cli_integration_invalid_amount(db_session, test_contract):
    """
    Test the error handling in the update_contract CLI command.
    This test verifies that the CLI command correctly handles invalid amounts.
    """
    runner = CliRunner()
    inputs = "-10\n500.0\n"
    result = runner.invoke(
        update_contract,
        args=[str(test_contract.contract_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 1
    assert " ❌ Unexpected error: A technical error occurred." in result.output
    updated_contract = db_session.query(Contract).filter_by(contract_id=test_contract.contract_id).first()
    assert updated_contract.total_price == test_contract.total_price


def test_list_contracts_cli_integration_filter(db_session, test_user, test_client, test_contract):
    """
    Test the list_contracts CLI command with a filter.
    This test verifies that the CLI command correctly lists contracts filtered by client.
    """
    client2 = Client.create(
        db=db_session,
        first_name="Test2",
        last_name="Client2",
        email="test2.client@example.com",
        commercial_contact_id=test_user.user_id
    )
    contract2 = Contract.create(
        db=db_session,
        total_price=2000.0,
        rest_to_pay=1000.0,
        client_id=client2.client_id,
        commercial_contact_id=test_user.user_id
    )

    runner = CliRunner()
    result = runner.invoke(
        list_contracts,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "=== List of Contracts ===" in result.output
    assert f"ID: {test_contract.contract_id}" in result.output
    assert f"ID: {contract2.contract_id}" in result.output


def test_full_flow_integration_with_error(db_session):
    """
    Test the complete integration flow with a validation error.
    This test verifies that the CLI commands correctly handle validation errors in a full flow.
    """
    runner = CliRunner()

    user_inputs = "john_doe\nJohn\nDoe\njohn.doe@example.com\ncommercial\n"
    result = runner.invoke(create_user, input=user_inputs, obj={"db": db_session})
    assert result.exit_code == 0
    assert "✅ User created" in result.output

    users = db_session.query(User).all()
    assert len(users) == 1
    user = users[0]

    second_user_inputs = "jane_doe\nJane\nDoe\njohn.doe@example.com\ncommercial\n"
    result = runner.invoke(create_user, input=second_user_inputs, obj={"db": db_session})

    assert result.exit_code == 0
    assert "❌ Error: This email is already registered." in result.output

    users = db_session.query(User).all()
    assert len(users) == 1
