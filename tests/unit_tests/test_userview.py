import pytest
import click
from epic_events.views import UserView


def test_prompt_user_creation(monkeypatch, db_session):
    """Test that prompt_user_creation returns a dict with values from mocked inputs."""

    # Mock validate_length to return fixed strings
    monkeypatch.setattr(
        "epic_events.views.validate_length",
        lambda msg, _: f"fake_{msg}"
    )

    # Mock click.prompt for email and role
    answers = iter(["john@example.com", "commercial", "testpassword"])
    monkeypatch.setattr("click.prompt", lambda msg, **kwargs: next(answers))

    result = UserView.prompt_user_creation()

    assert result == {
        "username": "fake_Username (max 100 chars)",
        "first_name": "fake_First name (max 100 chars)",
        "last_name": "fake_Last name (max 100 chars)",
        "email": "john@example.com",
        "role": "commercial",
        "password": "testpassword"
    }


def test_prompt_update_single_change(monkeypatch, db_session, test_user, capsys):
    """Test that prompt_update returns only fields that were modified."""

    # Simulate answers: same username, NEW first_name, same last_name, email, role
    answers = iter([
        test_user.username,  # unchanged
        "NewFirstName",  # changed
        test_user.last_name,  # unchanged
        test_user.email,  # unchanged
        test_user.role  # unchanged
    ])

    monkeypatch.setattr("click.prompt", lambda *args, **kwargs: next(answers))

    result = UserView.prompt_update(test_user)

    # Only first_name should be updated
    assert result == {"first_name": "NewFirstName"}

    # Optional: check intro message is printed
    intro = capsys.readouterr().out
    assert f"Updating user: {test_user.first_name} {test_user.last_name} (ID: {test_user.user_id})" in intro


def test_prompt_update_abort(monkeypatch, db_session, test_user):
    """Test that prompt_update propagates Click's Abort exception when user aborts."""

    # Simulate a user abort (Ctrl+C)
    monkeypatch.setattr("click.prompt", lambda *args, **kwargs: (_ for _ in ()).throw(click.Abort()))

    with pytest.raises(click.Abort):
        UserView.prompt_update(test_user)


def test_prompt_delete_confirmation_yes(monkeypatch, db_session):
    """Test that prompt_delete_confirmation returns True when user confirms."""
    monkeypatch.setattr("click.confirm", lambda msg: True)

    class FakeUser:
        user_id = 1
        username = "john"

    assert UserView.prompt_delete_confirmation(FakeUser()) is True


def test_prompt_delete_confirmation_no(monkeypatch, db_session):
    """Test that prompt_delete_confirmation returns False when user declines."""
    monkeypatch.setattr("click.confirm", lambda msg: False)

    class FakeUser:
        user_id = 1
        username = "john"

    assert UserView.prompt_delete_confirmation(FakeUser()) is False
