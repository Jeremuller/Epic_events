import pytest
from epic_events.controllers import UserController
from epic_events.views import UserView
from epic_events.models import User


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
