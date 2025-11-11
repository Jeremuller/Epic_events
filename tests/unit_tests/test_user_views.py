import pytest
from click.testing import CliRunner
from epic_events.views import create_user, list_users, update_user, delete_user
from epic_events.models import User


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


def test_create_user_duplicate_username(runner, db_session):
    """Test create_user with a duplicate username."""
    User.create_user(
        db=db_session,
        username="mickey",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )
    inputs = "mickey\nJane\nDoe\njane@example.com\ncommercial\n"
    result = runner.invoke(
        create_user,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: This username is already taken." in result.output
    users = db_session.query(User).all()
    assert len(users) == 1


def test_list_users_with_data(capsys, db_session):
    """Test the list_users function with existing users."""
    User.create_user(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )

    users = User.get_all(db_session)

    list_users(users)

    captured = capsys.readouterr()

    assert "=== List of Users ===" in captured.out
    assert "jdoe" in captured.out
    assert "John Doe" in captured.out


def test_list_users_empty(capsys, db_session):
    """Test the list_users function with an empty database."""
    list_users([])
    captured = capsys.readouterr()
    assert "No users found in the database." in captured.out


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


def test_update_user_duplicate_email(runner, db_session):
    """Test update_user with a duplicate email."""
    user1 = User.create_user(
        db=db_session,
        username="user1",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )
    user2 = User.create_user(
        db=db_session,
        username="user2",
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        role="commercial"
    )
    inputs = "user2\nJane\nDoe\njohn@example.com\ncommercial\n"
    result = runner.invoke(
        update_user,
        args=[str(user2.user_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: This email is already registered." in result.output
    updated_user = db_session.query(User).filter_by(user_id=user2.user_id).first()
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


def test_delete_user_not_found(runner, db_session):
    """Test delete_user with a non-existent user ID."""
    result = runner.invoke(
        delete_user,
        args=["999"],
        input="y\n",
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ User with ID 999 not found." in result.output
