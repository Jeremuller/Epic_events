import pytest
from unittest.mock import patch, MagicMock
from epic_events.controllers import (
    MenuController,
    DisplayMessages, UserController, ClientController, ContractController, EventController
)
from epic_events.views import UserView, MenuView, ClientView, ContractView, EventView
from epic_events.models import User, Client, Contract, Event
import builtins
from datetime import datetime, timedelta

menus = [
    (MenuController.run_main_menu, "CRM Main Menu", ["1", "4", "5"], None),
    (MenuController.run_users_menu, "Users Menu", ["1", "4"],
     "epic_events.controllers.UserController.create_user"),
    (MenuController.run_clients_menu, "Clients Menu", ["1", "4"],
     "epic_events.controllers.ClientController.list_clients"),
    (MenuController.run_contracts_menu, "Contracts Menu", ["1", "4"],
     "epic_events.controllers.ContractController.list_contracts"),
    (MenuController.run_events_menu, "Events Menu", ["1", "4"],
     "epic_events.controllers.EventController.list_events"),
]


@pytest.mark.parametrize("menu_func, menu_text, choices, controller_path", menus)
def test_menus_parametric(db_session, management_session, capsys, monkeypatch, menu_func, menu_text, choices, controller_path):
    iter_choices = iter(choices)
    monkeypatch.setattr(builtins, "input", lambda _: next(iter_choices))

    if controller_path is not None:
        with patch(controller_path) as mock_controller:
            menu_func(db_session, management_session)
            mock_controller.assert_called_once()
    else:
        with patch.object(DisplayMessages, "display_goodbye") as mock_goodbye:
            menu_func(db_session, management_session)
            mock_goodbye.assert_called_once()

    captured = capsys.readouterr().out
    assert menu_text in captured


def test_create_user_success(db_session, management_session):
    """Test the happy path: user is created and success message displayed."""

    fake_user = User(
        username="jeanmicheltesteur",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        role="commercial",
        password_hash="testpassword"
    )
    fake_user.user_id = 42  # simulate ID after commit

    with patch.object(UserView, "prompt_user_creation", return_value={
        "username": "jeanmicheltesteur",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "role": "commercial",
        "password": "testpassword"
    }):
        with patch.object(User, "create", return_value=fake_user):
            with patch.object(DisplayMessages, "display_success") as mock_success:
                UserController.create_user(db_session, management_session)

                mock_success.assert_called_once_with(
                    "User created: Test User (ID: 42)"
                )


def test_create_user_value_error(db_session, management_session):
    """Test that ValueError triggers rollback and error display."""
    with patch.object(UserView, "prompt_user_creation", return_value={
        "username": "duplicate",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "role": "commercial",
        "password": "testpassword"
    }):
        with patch.object(User, "create", side_effect=ValueError("USERNAME_TAKEN")):
            with patch.object(DisplayMessages, "display_error") as mock_error:
                UserController.create_user(db_session, management_session)
                mock_error.assert_called_once_with("USERNAME_TAKEN")


def test_create_user_exception(db_session, management_session):
    """Test that generic Exception triggers rollback, error display, and re-raises."""
    with patch.object(UserView, "prompt_user_creation", return_value={
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "role": "commercial",
        "password": "testpassword"
    }):
        with patch.object(User, "create", side_effect=Exception("DB fail")):
            with patch.object(DisplayMessages, "display_error") as mock_error:
                with pytest.raises(Exception) as exc:
                    UserController.create_user(db_session, management_session)

                mock_error.assert_called_once_with("DATABASE_ERROR")
                assert "DB fail" in str(exc.value)


def test_update_user_success(db_session, management_session, test_user):
    """Test updating an existing user with valid data."""

    updated_data = {
        "username": "updated_user",
        "first_name": "Updated",
        "last_name": "Name",
        "email": "updated@example.com",
        "role": "support",
    }

    with patch.object(MenuView, "prompt_for_id", return_value=test_user.user_id):
        with patch.object(UserView, "prompt_update", return_value=updated_data):
            with patch.object(DisplayMessages, "display_success") as mock_success:
                UserController.update_user(db_session, management_session)

                mock_success.assert_called_once_with(
                    f"User updated: {test_user.username} (ID: {test_user.user_id})"
                )

                for key, value in updated_data.items():
                    assert getattr(test_user, key) == value


def test_update_user_value_error(db_session, management_session, test_user):
    """Test that a ValueError during user update triggers rollback and error display."""

    updated_data = {
        "username": "duplicate_user",
        "first_name": "Updated",
        "last_name": "Name",
        "email": "duplicate@example.com",
        "role": "support",
    }

    with patch.object(MenuView, "prompt_for_id", return_value=test_user.user_id):
        with patch.object(UserView, "prompt_update", return_value=updated_data):
            with patch.object(test_user, "update", side_effect=ValueError("USERNAME_TAKEN")):
                with patch.object(DisplayMessages, "display_error") as mock_error:
                    UserController.update_user(db_session, management_session)

                    mock_error.assert_called_once_with("USERNAME_TAKEN")


def test_delete_user_success(db_session, management_session, test_user):
    """Test successful deletion of a user."""

    with patch.object(MenuView, "prompt_for_id", return_value=test_user.user_id):
        with patch.object(UserView, "prompt_delete_confirmation", return_value=True):
            with patch.object(DisplayMessages, "display_success") as mock_success:
                UserController.delete_user(db_session, management_session)

                mock_success.assert_called_once_with(
                    f"User deleted: {test_user.username} (ID: {test_user.user_id})"
                )

                assert db_session.query(User).filter_by(user_id=test_user.user_id).first() is None


def test_delete_user_value_error(db_session, management_session, test_user):
    """Test that deletion failure triggers rollback and error display."""

    with patch.object(MenuView, "prompt_for_id", return_value=test_user.user_id):
        with patch.object(UserView, "prompt_delete_confirmation", return_value=True):
            with patch.object(test_user, "delete", side_effect=ValueError("DELETE_FAILED")):
                with patch.object(DisplayMessages, "display_error") as mock_error:
                    UserController.delete_user(db_session, management_session)

                    mock_error.assert_called_once_with("DELETE_FAILED")


def test_list_clients_success(db_session, commercial_session, test_client):
    """Test that list_clients retrieves clients and sends them to the view."""

    with patch.object(ClientView, "list_clients") as mock_view:
        ClientController.list_clients(db_session, commercial_session)

        mock_view.assert_called_once()
        # verify the list passed contains our test_client
        passed_list = mock_view.call_args[0][0]
        assert len(passed_list) == 1
        assert passed_list[0].client_id == test_client.client_id


def test_list_clients_database_error(db_session, commercial_session):
    with patch.object(Client, "get_all", side_effect=Exception("DB failure")):
        with patch.object(DisplayMessages, "display_error") as mock_error:
            with pytest.raises(Exception):
                ClientController.list_clients(db_session, commercial_session)

            mock_error.assert_called_once_with("DATABASE_ERROR")


def test_create_client_success(db_session, commercial_session, test_user):
    """Test successful client creation with real ORM object."""

    client_input = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@doe.com",
        "commercial_contact_id": test_user.user_id,
        "business_name": "Doe Corp",
        "telephone": "0601020304",
    }

    with patch.object(ClientView, "prompt_client_creation", return_value=client_input):
        with patch.object(DisplayMessages, "display_success") as mock_success:
            ClientController.create_client(db_session, commercial_session)

            created_client = (
                db_session.query(Client)
                .filter_by(email="john@doe.com")
                .first()
            )

            assert created_client is not None
            assert created_client.first_name == "John"
            assert created_client.last_name == "Doe"
            assert created_client.business_name == "Doe Corp"
            assert created_client.telephone == "0601020304"
            assert created_client.commercial_contact_id == test_user.user_id

            mock_success.assert_called_once_with(
                f"Client created: Doe Corp (ID: {created_client.client_id})"
            )


def test_update_client_success(db_session, commercial_session, test_client):
    """Test updating a client successfully."""

    updated_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@smith.com",
        "business_name": "Smith Industries",
        "telephone": "0606060606",
    }

    with patch.object(MenuView, "prompt_for_id", return_value=test_client.client_id):
        with patch.object(ClientView, "prompt_update", return_value=updated_data):
            with patch.object(DisplayMessages, "display_success") as mock_success:
                ClientController.update_client(db_session, commercial_session)

                db_session.refresh(test_client)

                for key, value in updated_data.items():
                    assert getattr(test_client, key) == value

                mock_success.assert_called_once_with(
                    f"Client updated: Smith Industries (ID: {test_client.client_id})"
                )


def test_list_contracts_success(db_session, commercial_session, test_contract):
    """Test successful listing of all contracts."""

    with patch.object(ContractView, "list_contracts") as mock_list:
        ContractController.list_contracts(db_session, commercial_session)

        mock_list.assert_called_once()
        passed_contracts = mock_list.call_args[0][0]

        assert len(passed_contracts) == 1
        assert passed_contracts[0].contract_id == test_contract.contract_id
        assert passed_contracts[0].total_price == test_contract.total_price


def test_list_contracts_database_error(db_session, commercial_session):
    """Test database error handling during contract listing."""

    with patch("epic_events.models.Contract.get_all", side_effect=Exception("DB ERROR")), \
            patch.object(DisplayMessages, "display_error") as mock_error:
        with pytest.raises(Exception):
            ContractController.list_contracts(db_session, commercial_session)

        mock_error.assert_called_once_with("DATABASE_ERROR")


def test_create_contract_success(db_session, management_session, test_user, test_client):
    """Test creating a contract successfully."""

    contract_data = {
        "total_price": 1200.0,
        "rest_to_pay": 600.0,
        "client_id": test_client.client_id,
        "commercial_contact_id": test_user.user_id,
        "signed": False
    }

    with patch.object(ContractView, "prompt_contract_creation", return_value=contract_data), \
            patch.object(DisplayMessages, "display_success") as mock_success:
        ContractController.create_contract(db_session, management_session)

        created_contract = db_session.query(Contract).first()

        assert created_contract is not None
        assert created_contract.total_price == contract_data["total_price"]
        assert created_contract.rest_to_pay == contract_data["rest_to_pay"]
        assert created_contract.client_id == test_client.client_id
        assert created_contract.commercial_contact_id == test_user.user_id

        mock_success.assert_called_once()
        msg = mock_success.call_args[0][0]
        assert f"Contract created: ID {created_contract.contract_id}" in msg


def test_create_contract_validation_error(db_session, management_session, test_user, test_client):
    """Test contract creation failing due to validation error."""

    invalid_data = {
        "total_price": -10,
        "rest_to_pay": 0,
        "client_id": test_client.client_id,
        "commercial_contact_id": test_user.user_id,
    }

    with patch.object(ContractView, "prompt_contract_creation", return_value=invalid_data), \
            patch.object(DisplayMessages, "display_error") as mock_error:
        ContractController.create_contract(db_session, management_session)

        from epic_events.models import Contract
        assert db_session.query(Contract).count() == 0

        mock_error.assert_called_once_with("INVALID_TOTAL_PRICE")


def test_create_contract_database_error(db_session, management_session, test_user, test_client):
    """Test unexpected database error during contract creation."""

    valid_data = {
        "total_price": 1000.0,
        "rest_to_pay": 200.0,
        "client_id": test_client.client_id,
        "commercial_contact_id": test_user.user_id,
    }

    with patch.object(ContractView, "prompt_contract_creation", return_value=valid_data), \
            patch("epic_events.models.Contract.create", side_effect=Exception("DB FAIL")), \
            patch.object(DisplayMessages, "display_error") as mock_error:
        with pytest.raises(Exception):
            ContractController.create_contract(db_session, management_session)

        mock_error.assert_called_once_with("DATABASE_ERROR")

        assert db_session.query(Contract).count() == 0


def test_update_contract_success(db_session, management_session, test_contract, test_client):
    """Test successfully updating a contract."""

    updated_data = {
        "total_price": 1500.0,
        "rest_to_pay": 700.0,
        "client_id": test_client.client_id,
        "commercial_contact_id": test_contract.commercial_contact_id,
        "signed": True
    }

    with patch.object(MenuView, "prompt_for_id", return_value=test_contract.contract_id), \
            patch.object(ContractView, "prompt_update", return_value=updated_data), \
            patch.object(DisplayMessages, "display_success") as mock_success:
        ContractController.update_contract(db_session, management_session)

        db_session.refresh(test_contract)

        assert test_contract.total_price == updated_data["total_price"]
        assert test_contract.rest_to_pay == updated_data["rest_to_pay"]
        assert test_contract.client_id == updated_data["client_id"]
        assert test_contract.signed is True

        mock_success.assert_called_once()
        msg = mock_success.call_args[0][0]
        assert f"Contract updated: ID {test_contract.contract_id}" in msg


def test_update_contract_not_found(db_session, management_session):
    """Test update attempt on nonexistent contract."""

    with patch.object(MenuView, "prompt_for_id", return_value=99999), \
            patch.object(DisplayMessages, "display_error") as mock_error:
        ContractController.update_contract(db_session, management_session)

        mock_error.assert_called_once_with("CONTRACT_NOT_FOUND")


def test_update_contract_validation_error(db_session, management_session, test_contract):
    """Test update failing due to validation (ValueError)."""

    invalid_data = {
        "total_price": -500,
    }

    with patch.object(MenuView, "prompt_for_id", return_value=test_contract.contract_id), \
            patch.object(ContractView, "prompt_update", return_value=invalid_data), \
            patch.object(DisplayMessages, "display_error") as mock_error:
        ContractController.update_contract(db_session, management_session)

        mock_error.assert_called_once_with("INVALID_TOTAL_PRICE")


def test_list_events_success(db_session, support_session, test_event):
    """Test successful listing of events."""

    fake_events = [test_event]

    with patch.object(Event, "get_all", return_value=fake_events) as mock_get_all, \
            patch("epic_events.views.EventView.list_events") as mock_list_events:
        EventController.list_events(db_session, support_session)

        mock_get_all.assert_called_once_with(db_session)
        mock_list_events.assert_called_once_with(fake_events)


def test_list_events_db_error(db_session, support_session):
    """Test DB error during event listing."""

    with patch.object(Event, "get_all", side_effect=Exception("DB error")) as mock_get_all, \
            patch("epic_events.views.DisplayMessages.display_error") as mock_display:
        with pytest.raises(Exception):
            EventController.list_events(db_session, support_session)

        mock_get_all.assert_called_once()
        mock_display.assert_called_once_with("DATABASE_ERROR")


def test_create_event_success(db_session, commercial_session, test_user, test_client):
    """Test successful creation of a new event."""

    fake_input = {
        "name": "New Event",
        "notes": "Some notes",
        "start_datetime": datetime.now() + timedelta(days=10),
        "end_datetime": datetime.now() + timedelta(days=11),
        "location": "Paris",
        "attendees": 20,
        "client_id": test_client.client_id,
        "support_contact_id": test_user.user_id,
    }

    fake_event = Event(
        name=fake_input["name"],
        notes=fake_input["notes"],
        start_datetime=fake_input["start_datetime"],
        end_datetime=fake_input["end_datetime"],
        location=fake_input["location"],
        attendees=fake_input["attendees"],
        client_id=fake_input["client_id"],
        support_contact_id=fake_input["support_contact_id"],
    )

    with patch("epic_events.views.EventView.prompt_event_creation", return_value=fake_input) as mock_prompt, \
            patch.object(Event, "create", return_value=fake_event) as mock_create, \
            patch("epic_events.views.DisplayMessages.display_success") as mock_success:
        EventController.create_event(db_session, commercial_session)

        mock_prompt.assert_called_once()
        mock_create.assert_called_once()

        mock_success.assert_called_once()


def test_create_event_validation_error(db_session, commercial_session, test_user, test_client):
    """Test validation error (ValueError) during event creation."""

    fake_input = {
        "name": "Test Event",
        "notes": "Some notes",
        "start_datetime": datetime.now() + timedelta(days=1),
        "end_datetime": datetime.now() + timedelta(days=2),
        "location": "Paris",
        "attendees": 10,
        "client_id": test_client.client_id,
        "support_contact_id": test_user.user_id,
    }

    with patch("epic_events.views.EventView.prompt_event_creation", return_value=fake_input) as mock_prompt, \
            patch.object(Event, "create", side_effect=ValueError("CLIENT_NOT_FOUND")) as mock_create, \
            patch("epic_events.views.DisplayMessages.display_error") as mock_display:
        EventController.create_event(db_session, commercial_session)

        mock_prompt.assert_called_once()
        mock_create.assert_called_once()
        mock_display.assert_called_once_with("CLIENT_NOT_FOUND")


def test_update_event_success(db_session, support_session, test_event):
    """Test successful update of an event."""

    updated_data = {
        "name": "Updated Event Name",
        "notes": "Updated notes",
        "start_datetime": test_event.start_datetime + timedelta(days=1),
        "end_datetime": test_event.end_datetime + timedelta(days=1),
        "location": "Lyon",
        "attendees": 100,
        "client_id": test_event.client_id,
        "support_contact_id": test_event.support_contact_id
    }

    with patch("epic_events.views.MenuView.prompt_for_id", return_value=test_event.event_id), \
            patch("epic_events.views.EventView.prompt_update", return_value=updated_data), \
            patch("epic_events.views.DisplayMessages.display_success") as mock_success:
        EventController.update_event(db_session, support_session)

        mock_success.assert_called_once_with(
            f"Event updated: {test_event.name} (ID: {test_event.event_id})"
        )

        for key, value in updated_data.items():
            assert getattr(test_event, key) == value


def test_update_event_validation_error(db_session, support_session, test_event):
    """Test ValueError during event update."""

    updated_data = {
        "name": "Updated Event Name",
        "notes": "Updated notes",
        "start_datetime": test_event.start_datetime,
        "end_datetime": test_event.end_datetime,
        "location": "Lyon",
        "attendees": 100,
        "client_id": test_event.client_id,
        "support_contact_id": test_event.support_contact_id
    }

    with patch("epic_events.views.MenuView.prompt_for_id", return_value=test_event.event_id), \
            patch("epic_events.views.EventView.prompt_update", return_value=updated_data), \
            patch.object(Event, "update", side_effect=ValueError("END_BEFORE_START")), \
            patch("epic_events.views.DisplayMessages.display_error") as mock_error:
        EventController.update_event(db_session, support_session)

        mock_error.assert_called_once_with("END_BEFORE_START")


def test_update_event_not_found(db_session, support_session):
    """Test update when event ID does not exist."""

    with patch("epic_events.views.MenuView.prompt_for_id", return_value=999), \
            patch("epic_events.views.DisplayMessages.display_error") as mock_error:
        EventController.update_event(db_session, support_session)

        mock_error.assert_called_once_with("EVENT_NOT_FOUND")
