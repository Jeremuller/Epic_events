import pytest
from epic_events.controllers import UserController, ClientController, ContractController, EventController
from epic_events.views import UserView, MenuView, ClientView, ContractView, EventView
from epic_events.models import User, Client, Contract, Event
from datetime import datetime, timedelta


def test_list_users_integration(db_session, test_user, capsys):
    """
    Full integration test: call UserController.list_users
    and verify that the user in the database is displayed by the view.
    """

    UserController.list_users(db_session)

    captured = capsys.readouterr()

    assert test_user.username in captured.out
    assert test_user.first_name in captured.out
    assert test_user.last_name in captured.out


def test_create_user_integration(db_session, capsys):
    """
    Full integration test: create a user via the controller.
    Verifies that the user is persisted in the database
    and that the view displays the success message.
    """

    original_prompt = UserView.prompt_user_creation
    UserView.prompt_user_creation = staticmethod(lambda: {
        "username": "integration_user",
        "first_name": "Integration",
        "last_name": "Test",
        "email": "integration@test.com",
        "role": "commercial"
    })

    try:
        UserController.create_user(db_session)

        user_in_db = db_session.query(User).filter_by(username="integration_user").first()
        assert user_in_db is not None
        assert user_in_db.first_name == "Integration"
        assert user_in_db.last_name == "Test"
        assert user_in_db.email == "integration@test.com"
        assert user_in_db.role == "commercial"

        captured = capsys.readouterr()
        assert "User created: Integration Test" in captured.out

    finally:
        UserView.prompt_user_creation = original_prompt


def test_update_user_integration_success(db_session, test_user, capsys):
    """
    Full integration test:
    Successfully updates an existing user through the controller
    and verifies database persistence and console output.
    """

    original_prompt_id = MenuView.prompt_for_id
    original_prompt_update = UserView.prompt_update

    MenuView.prompt_for_id = staticmethod(lambda _: test_user.user_id)
    UserView.prompt_update = staticmethod(lambda user: {
        "first_name": "Updated",
        "last_name": "User",
        "username": "updated_username"
    })

    try:
        UserController.update_user(db_session)

        updated_user = db_session.query(User).get(test_user.user_id)

        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "User"
        assert updated_user.username == "updated_username"

        captured = capsys.readouterr()
        assert "User updated: updated_username" in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        UserView.prompt_update = original_prompt_update


def test_update_user_duplicate_username_integration(db_session, test_user, capsys):
    """
    Full integration test:
    Attempts to update a user with a duplicate username
    and verifies rollback and error message.
    """

    other_user = User.create(
        db=db_session,
        username="existing_username",
        first_name="Other",
        last_name="User",
        email="other@example.com",
        role="commercial"
    )
    db_session.add(other_user)
    db_session.commit()

    original_prompt_id = MenuView.prompt_for_id
    original_prompt_update = UserView.prompt_update

    MenuView.prompt_for_id = staticmethod(lambda _: test_user.user_id)
    UserView.prompt_update = staticmethod(lambda user: {
        "username": "existing_username"
    })

    try:
        UserController.update_user(db_session)

        unchanged_user = db_session.query(User).get(test_user.user_id)
        assert unchanged_user.username == "test_user"

        captured = capsys.readouterr()
        assert "❌ Error: This username is already taken.\n" in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        UserView.prompt_update = original_prompt_update


def test_delete_user_integration_success(
        db_session, test_user, test_client, test_contract, test_event, capsys
):
    """
    Full integration test:
    Successfully deletes a user through the controller,
    verifies dependency cleanup and success output.
    """

    original_prompt_id = MenuView.prompt_for_id
    original_prompt_confirm = UserView.prompt_delete_confirmation

    MenuView.prompt_for_id = staticmethod(lambda _: test_user.user_id)
    UserView.prompt_delete_confirmation = staticmethod(lambda user: True)

    try:
        UserController.delete_user(db_session)

        deleted_user = db_session.query(User).get(test_user.user_id)
        assert deleted_user is None

        refreshed_client = db_session.query(Client).get(test_client.client_id)
        refreshed_contract = db_session.query(Contract).get(test_contract.contract_id)
        refreshed_event = db_session.query(Event).get(test_event.event_id)

        assert refreshed_client.commercial_contact_id is None
        assert refreshed_contract.commercial_contact_id is None
        assert refreshed_event.support_contact_id is None

        captured = capsys.readouterr()
        assert f"User deleted: {test_user.username}" in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        UserView.prompt_delete_confirmation = original_prompt_confirm


def test_list_clients_integration(db_session, test_client, capsys):
    """
    Full integration test:
    Calls ClientController.list_clients and verifies that
    the client stored in the database is displayed by the view.
    """

    ClientController.list_clients(db_session)

    captured = capsys.readouterr()

    assert test_client.first_name in captured.out
    assert test_client.last_name in captured.out
    assert test_client.email in captured.out
    assert test_client.business_name in captured.out


def test_create_client_integration_success(db_session, test_user, capsys):
    """
    Full integration test:
    Successfully creates a client through the controller
    and verifies persistence and success message output.
    """

    original_prompt = ClientView.prompt_client_creation
    ClientView.prompt_client_creation = staticmethod(lambda: {
        "first_name": "Integration",
        "last_name": "Client",
        "email": "integration.client@test.com",
        "commercial_contact_id": test_user.user_id,
        "business_name": "Integration Business",
        "telephone": "0102030405",
    })

    try:
        ClientController.create_client(db_session)

        client = db_session.query(Client).filter_by(
            email="integration.client@test.com"
        ).first()

        assert client is not None
        assert client.first_name == "Integration"
        assert client.last_name == "Client"
        assert client.business_name == "Integration Business"
        assert client.telephone == "0102030405"
        assert client.commercial_contact_id == test_user.user_id

        captured = capsys.readouterr()
        assert "Client created:" in captured.out

    finally:
        ClientView.prompt_client_creation = original_prompt


def test_create_client_integration_duplicate_email(db_session, test_user, test_client, capsys):
    """
    Full integration test:
    Attempts to create a client with a duplicate email and verifies
    that the operation fails gracefully without persistence.
    """

    original_prompt = ClientView.prompt_client_creation
    ClientView.prompt_client_creation = staticmethod(lambda: {
        "first_name": "Duplicate",
        "last_name": "Client",
        "email": test_client.email,  # duplicate email
        "commercial_contact_id": test_user.user_id,
        "business_name": "Duplicate Business",
        "telephone": "9999999999",
    })

    try:
        ClientController.create_client(db_session)

        client = db_session.query(Client).filter_by(
            business_name="Duplicate Business"
        ).first()

        assert client is None

        captured = capsys.readouterr()
        assert "❌ Error: This email is already registered.\n" in captured.out

    finally:
        ClientView.prompt_client_creation = original_prompt


def test_update_client_integration_success(db_session, test_client, test_user, capsys):
    """
    Full integration test:
    Successfully updates a client through the controller and verifies
    database persistence and success message output.
    """

    original_prompt_id = MenuView.prompt_for_id
    original_prompt_update = ClientView.prompt_update

    MenuView.prompt_for_id = staticmethod(lambda _: test_client.client_id)
    ClientView.prompt_update = staticmethod(lambda client: {
        "first_name": "Updated",
        "last_name": "Client",
        "email": "updated.client@test.com",
        "business_name": "Updated Business",
        "telephone": "0607080910",
    })

    try:
        ClientController.update_client(db_session)

        updated_client = db_session.query(Client).get(test_client.client_id)

        assert updated_client.first_name == "Updated"
        assert updated_client.last_name == "Client"
        assert updated_client.email == "updated.client@test.com"
        assert updated_client.business_name == "Updated Business"
        assert updated_client.telephone == "0607080910"

        captured = capsys.readouterr()
        assert "Client updated:" in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        ClientView.prompt_update = original_prompt_update


def test_update_client_integration_duplicate_email(db_session, test_client, test_user, capsys):
    """
    Full integration test:
    Attempts to update a client with an email already used by another client
    and verifies rollback and error message.
    """

    # Create a second client with a different email
    other_client = Client.create(
        db=db_session,
        first_name="Other",
        last_name="Client",
        email="other.client@test.com",
        commercial_contact_id=test_user.user_id,
    )
    db_session.add(other_client)
    db_session.commit()

    original_prompt_id = MenuView.prompt_for_id
    original_prompt_update = ClientView.prompt_update

    MenuView.prompt_for_id = staticmethod(lambda _: test_client.client_id)
    ClientView.prompt_update = staticmethod(lambda client: {
        "email": "other.client@test.com"  # duplicate email
    })

    try:
        ClientController.update_client(db_session)

        unchanged_client = db_session.query(Client).get(test_client.client_id)
        assert unchanged_client.email == test_client.email

        captured = capsys.readouterr()
        assert "❌ Error: This email is already registered.\n" in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        ClientView.prompt_update = original_prompt_update


def test_list_contracts_integration(db_session, test_contract, capsys):
    """
    Full integration test:
    Calls ContractController.list_contracts and verifies that
    the existing contract is displayed by the view.
    """

    ContractController.list_contracts(db_session)

    captured = capsys.readouterr()

    assert str(test_contract.contract_id) in captured.out
    assert str(test_contract.total_price) in captured.out
    assert str(test_contract.rest_to_pay) in captured.out
    assert "Yes" in captured.out or "No" in captured.out


def test_create_contract_integration_success(
        db_session, test_user, test_client, capsys
):
    """
    Full integration test:
    Successfully creates a contract via ContractController.create_contract.
    Verifies persistence and success message output.
    """

    original_prompt = ContractView.prompt_contract_creation
    ContractView.prompt_contract_creation = staticmethod(lambda: {
        "total_price": 2000.0,
        "rest_to_pay": 500.0,
        "client_id": test_client.client_id,
        "commercial_contact_id": test_user.user_id,
        "signed": False
    })

    try:
        ContractController.create_contract(db_session)

        contract = db_session.query(Contract).first()
        assert contract is not None
        assert float(contract.total_price) == 2000.0
        assert float(contract.rest_to_pay) == 500.0
        assert contract.client_id == test_client.client_id
        assert contract.commercial_contact_id == test_user.user_id
        assert contract.signed is False

        captured = capsys.readouterr()
        assert "Contract created" in captured.out
        assert str(contract.contract_id) in captured.out

    finally:
        ContractView.prompt_contract_creation = original_prompt


def test_create_contract_integration_invalid_total_price(
        db_session, test_user, test_client, capsys
):
    """
    Full integration test:
    Creating a contract with an invalid total_price should raise
    a ValueError and display the corresponding error message.
    """

    original_prompt = ContractView.prompt_contract_creation
    ContractView.prompt_contract_creation = staticmethod(lambda: {
        "total_price": 0.0,  # invalid
        "rest_to_pay": 0.0,
        "client_id": test_client.client_id,
        "commercial_contact_id": test_user.user_id,
        "signed": False
    })

    try:
        ContractController.create_contract(db_session)

        # No contract should be persisted
        contracts = db_session.query(Contract).all()
        assert len(contracts) == 0

        captured = capsys.readouterr()
        assert "❌ Error: Total_price can't be <= 0.\n" in captured.out

    finally:
        ContractView.prompt_contract_creation = original_prompt


def test_update_contract_integration_success(
        db_session, test_contract, capsys
):
    """
    Full integration test:
    Successfully updates a contract via ContractController.update_contract.
    Verifies persistence and success message output.
    """

    original_prompt_id = MenuView.prompt_for_id
    original_prompt_update = ContractView.prompt_update

    MenuView.prompt_for_id = staticmethod(lambda _: test_contract.contract_id)
    ContractView.prompt_update = staticmethod(lambda contract: {
        "rest_to_pay": 0.0,
        "signed": True
    })

    try:
        ContractController.update_contract(db_session)

        updated_contract = db_session.query(Contract).get(test_contract.contract_id)
        assert updated_contract.rest_to_pay == 0
        assert updated_contract.signed is True

        captured = capsys.readouterr()
        assert "Contract updated" in captured.out
        assert str(test_contract.contract_id) in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        ContractView.prompt_update = original_prompt_update


def test_update_contract_integration_inferior_total_price_error(
        db_session, test_contract, capsys
):
    """
    Full integration test:
    Updating a contract with rest_to_pay greater than total_price
    should raise a ValueError and rollback changes.
    """

    original_prompt_id = MenuView.prompt_for_id
    original_prompt_update = ContractView.prompt_update

    MenuView.prompt_for_id = staticmethod(lambda _: test_contract.contract_id)
    ContractView.prompt_update = staticmethod(lambda contract: {
        "total_price": 1000.0,
        "rest_to_pay": 2000.0  # invalid
    })

    try:
        ContractController.update_contract(db_session)

        # Contract should remain unchanged
        unchanged_contract = db_session.query(Contract).get(test_contract.contract_id)
        assert float(unchanged_contract.rest_to_pay) == float(test_contract.rest_to_pay)

        captured = capsys.readouterr()
        assert "❌ Error: Total price can't be inferior to rest to pay.\n" in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        ContractView.prompt_update = original_prompt_update


def test_list_events_integration_success(db_session, test_event, capsys):
    """
    Full integration test:
    list_events should retrieve events from DB
    and display them via EventView.
    """

    # Act
    EventController.list_events(db_session)

    # Assert (stdout)
    captured = capsys.readouterr()
    output = captured.out

    assert "=== List of Events ===" in output
    assert str(test_event.event_id) in output
    assert test_event.name in output

    if test_event.client:
        assert test_event.client.business_name in output

    if test_event.support_contact:
        assert test_event.support_contact.first_name in output


def test_create_event_success(db_session, test_client, test_user, capsys):
    """
    Full integration test: successful event creation.
    """

    future_start = datetime.now() + timedelta(days=1)
    future_end = future_start + timedelta(hours=2)

    event_data = {
        "name": "Integration Test Event",
        "notes": "Notes for testing",
        "start_datetime": future_start,
        "end_datetime": future_end,
        "location": "Test location",
        "attendees": 10,
        "client_id": test_client.client_id,
        "support_contact_id": test_user.user_id
    }

    EventView.prompt_event_creation = staticmethod(lambda: event_data)

    # Act
    EventController.create_event(db_session)

    # Assert stdout
    captured = capsys.readouterr()
    output = captured.out
    assert "Event created" in output
    assert "Integration Test Event" in output

    event_in_db = db_session.query(Event).filter_by(name="Integration Test Event").first()
    assert event_in_db is not None
    assert event_in_db.client_id == test_client.client_id
    assert event_in_db.support_contact_id == test_user.user_id


def test_create_event_failure_past_date(db_session, test_client, test_user, capsys):
    """
    Full integration test: event creation fails because start_datetime is in the past.
    """

    past_start = datetime.now() - timedelta(days=1)
    future_end = datetime.now() + timedelta(hours=2)

    event_data = {
        "name": "Past Event",
        "notes": "Should fail",
        "start_datetime": past_start,
        "end_datetime": future_end,
        "location": "Test location",
        "attendees": 5,
        "client_id": test_client.client_id,
        "support_contact_id": test_user.user_id
    }

    EventView.prompt_event_creation = staticmethod(lambda: event_data)

    # Act
    EventController.create_event(db_session)

    # Assert stdout
    captured = capsys.readouterr()
    output = captured.out
    assert "❌ Error: Event date must be in the future.\n" in output

    event_in_db = db_session.query(Event).filter_by(name="Past Event").first()
    assert event_in_db is None


def test_update_event_success_integration(db_session, test_event, capsys):
    """
    Full integration test:
    Successfully updating an event using mocked prompts.
    """
    original_prompt_id = MenuView.prompt_for_id
    original_prompt_update = EventView.prompt_update

    MenuView.prompt_for_id = staticmethod(lambda _: test_event.event_id)
    EventView.prompt_update = staticmethod(lambda event: {
        "name": "Updated Event Name",
        "location": "Updated Location"
    })

    try:
        EventController.update_event(db_session)

        updated_event = db_session.query(Event).get(test_event.event_id)
        assert updated_event.name == "Updated Event Name"
        assert updated_event.location == "Updated Location"

        captured = capsys.readouterr()
        assert "✅ Event updated: Updated Event Name (ID: 1)\n" in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        EventView.prompt_update = original_prompt_update


def test_update_event_failure_end_before_start_integration(db_session, test_event, capsys):
    """
    Full integration test:
    Updating an event with end_datetime before start_datetime
    should raise a ValueError and rollback changes.
    """
    original_prompt_id = MenuView.prompt_for_id
    original_prompt_update = EventView.prompt_update

    MenuView.prompt_for_id = staticmethod(lambda _: test_event.event_id)
    EventView.prompt_update = staticmethod(lambda event: {
        "start_datetime": test_event.start_datetime,
        "end_datetime": test_event.start_datetime - timedelta(hours=1)  # invalid
    })

    try:
        EventController.update_event(db_session)

        # Event should remain unchanged
        unchanged_event = db_session.query(Event).get(test_event.event_id)
        assert unchanged_event.end_datetime == test_event.end_datetime

        captured = capsys.readouterr()
        assert "❌ Error: End date must be after start date.\n" in captured.out

    finally:
        MenuView.prompt_for_id = original_prompt_id
        EventView.prompt_update = original_prompt_update

