import pytest
from epic_events.controllers import UserController, ClientController, ContractController, EventController
from epic_events.views import UserView, MenuView, ClientView, ContractView, EventView
from epic_events.models import User, Client, Contract, Event


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
