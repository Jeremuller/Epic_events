import pytest
from click.testing import CliRunner
from ...views import create_user, list_users, update_user, delete_user
from ...models import User


@pytest.fixture
def runner():
    """Fixture to provide a CliRunner for testing CLI commands."""
    return CliRunner()


def test_create_user_command(runner, db_session):
    """Test the create_user CLI command with valid inputs."""
    inputs = "mickey\nJohn\nDoe\nmickey@example.com\ncommercial\n"

    result = runner.invoke(
        create_user,
        input=inputs,
        obj={"db": db_session}
    )

    assert result.exit_code == 0
    assert "✅ User created" in result.output

    users = db_session.query(User).all()
    assert len(users) == 1
    assert users[0].username == "mickey"
    assert users[0].first_name == "John"


def test_list_users_command(runner, db_session):
    """Test the list_users CLI command."""
    User.create_user(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )

    result = runner.invoke(list_users, obj={"db": db_session})

    assert result.exit_code == 0
    assert "=== List of Users ===" in result.output
    assert "jdoe" in result.output
    assert "John Doe" in result.output


def test_update_user_command(runner, db_session):
    """Test the update_user CLI command."""
    user = User.create_user(
        db=db_session,
        username="test",
        first_name="John",
        last_name="Doe",
        email="test@example.com",
        role="commercial"
    )

    inputs = "test\nJane\nDoe\njane@example.com\ncommercial\n"

    result = runner.invoke(
        update_user,
        args=[str(user.user_id)],
        input=inputs,
        obj={"db": db_session}
    )

    assert result.exit_code == 0
    assert "✅ User updated" in result.output

    updated_user = db_session.query(User).filter_by(user_id=user.user_id).first()
    assert updated_user.first_name == "Jane"
    assert updated_user.email == "jane@example.com"


def test_delete_user_command(runner, db_session):
    """Test the delete_user CLI command."""

    user = User.create_user(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )

    inputs = "y\n"

    result = runner.invoke(
        delete_user,
        args=[str(user.user_id)],
        input=inputs,
        obj={"db": db_session}
    )

    assert result.exit_code == 0
    assert "✅ User deleted" in result.output

    deleted_user = db_session.query(User).filter_by(user_id=user.user_id).first()
    assert deleted_user is None


def test_delete_user_cancelled(runner, db_session):
    """Test that delete_user cancels when user responds 'no'."""
    user = User.create_user(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )

    inputs = "n\n"

    result = runner.invoke(
        delete_user,
        args=[str(user.user_id)],
        input=inputs,
        obj={"db": db_session}
    )

    assert result.exit_code == 0
    assert "🔄 Operation cancelled" in result.output

    assert db_session.query(User).filter_by(user_id=user.user_id).first() is not None
