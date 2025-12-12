import pytest
from unittest.mock import patch, MagicMock
from epic_events.controllers import (
    MenuController,
    DisplayMessages, UserController
)
from epic_events.views import UserView, MenuView
from epic_events.models import User
import builtins

menus = [
    # menu_func, menu_text, choices, controller_patch_path
    (MenuController.run_main_menu, "CRM Main Menu", ["1", "5", "5"], None),
    (MenuController.run_users_menu, "Users Menu", ["1", "5"], "epic_events.controllers.UserController.list_users"),
    (MenuController.run_clients_menu, "Clients Menu", ["1", "4"],
     "epic_events.controllers.ClientController.list_clients"),
    (MenuController.run_contracts_menu, "Contracts Menu", ["1", "4"],
     "epic_events.controllers.ContractController.list_contracts"),
    (MenuController.run_events_menu, "Events Menu", ["1", "4"], "epic_events.controllers.EventController.list_events"),
]


@pytest.mark.parametrize("menu_func, menu_text, choices, controller_path", menus)
def test_menus_parametric(db_session, capsys, monkeypatch, menu_func, menu_text, choices, controller_path):
    iter_choices = iter(choices)
    monkeypatch.setattr(builtins, "input", lambda _: next(iter_choices))

    if controller_path is not None:
        with patch(controller_path) as mock_controller:
            menu_func(db_session)
            mock_controller.assert_called_once()
    else:
        with patch.object(DisplayMessages, "display_goodbye") as mock_goodbye:
            menu_func(db_session)
            mock_goodbye.assert_called_once()

    captured = capsys.readouterr().out
    assert menu_text in captured


def test_list_users_success(db_session):
    """Test that list_users retrieves users and calls UserView.list_users"""
    fake_users = [MagicMock(), MagicMock()]

    with patch.object(User, "get_all", return_value=fake_users) as mock_get_all:
        with patch.object(UserView, "list_users") as mock_view:
            UserController.list_users(db_session)

            mock_get_all.assert_called_once_with(db_session)
            mock_view.assert_called_once_with(fake_users)


def test_list_users_exception(db_session):
    """Test that list_users handles exceptions and calls display_error"""
    with patch.object(User, "get_all", side_effect=Exception("DB failure")):
        with patch.object(DisplayMessages, "display_error") as mock_error:
            with pytest.raises(Exception) as exc:
                UserController.list_users(db_session)

            mock_error.assert_called_once_with("DATABASE_ERROR")
            assert "DB failure" in str(exc.value)


def test_create_user_success(db_session):
    """Test the happy path: user is created and success message displayed."""

    fake_user = User(
        username="jeanmicheltesteur",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        role="commercial",
        password="default_hashed_password"
    )
    fake_user.user_id = 42  # simulate ID after commit

    with patch.object(UserView, "prompt_user_creation", return_value={
        "username": "jeanmicheltesteur",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "role": "commercial"
    }):
        with patch.object(User, "create", return_value=fake_user):
            with patch.object(DisplayMessages, "display_success") as mock_success:
                UserController.create_user(db_session)

                mock_success.assert_called_once_with(
                    "User created: Test User (ID: 42)"
                )


def test_create_user_value_error(db_session):
    """Test that ValueError triggers rollback and error display."""
    with patch.object(UserView, "prompt_user_creation", return_value={
        "username": "duplicate",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "role": "commercial"
    }):
        with patch.object(User, "create", side_effect=ValueError("USERNAME_TAKEN")):
            with patch.object(DisplayMessages, "display_error") as mock_error:
                UserController.create_user(db_session)
                mock_error.assert_called_once_with("USERNAME_TAKEN")


def test_create_user_exception(db_session):
    """Test that generic Exception triggers rollback, error display, and re-raises."""
    with patch.object(UserView, "prompt_user_creation", return_value={
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "role": "commercial"
    }):
        with patch.object(User, "create", side_effect=Exception("DB fail")):
            with patch.object(DisplayMessages, "display_error") as mock_error:
                with pytest.raises(Exception) as exc:
                    UserController.create_user(db_session)

                mock_error.assert_called_once_with("DATABASE_ERROR")
                assert "DB fail" in str(exc.value)


def test_update_user_success(db_session, test_user):
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
                UserController.update_user(db_session)

                mock_success.assert_called_once_with(
                    f"User updated: {test_user.username} (ID: {test_user.user_id})"
                )

                for key, value in updated_data.items():
                    assert getattr(test_user, key) == value


def test_update_user_value_error(db_session, test_user):
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
                    UserController.update_user(db_session)

                    mock_error.assert_called_once_with("USERNAME_TAKEN")


def test_delete_user_success(db_session, test_user):
    """Test successful deletion of a user."""

    with patch.object(MenuView, "prompt_for_id", return_value=test_user.user_id):
        with patch.object(UserView, "prompt_delete_confirmation", return_value=True):
            with patch.object(DisplayMessages, "display_success") as mock_success:
                UserController.delete_user(db_session)

                mock_success.assert_called_once_with(
                    f"User deleted: {test_user.username} (ID: {test_user.user_id})"
                )

                assert db_session.query(User).filter_by(user_id=test_user.user_id).first() is None


def test_delete_user_value_error(db_session, test_user):
    """Test that deletion failure triggers rollback and error display."""

    with patch.object(MenuView, "prompt_for_id", return_value=test_user.user_id):
        with patch.object(UserView, "prompt_delete_confirmation", return_value=True):
            with patch.object(test_user, "delete", side_effect=ValueError("DELETE_FAILED")):
                with patch.object(DisplayMessages, "display_error") as mock_error:
                    UserController.delete_user(db_session)

                    mock_error.assert_called_once_with("DELETE_FAILED")
