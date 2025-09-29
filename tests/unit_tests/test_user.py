import pytest
from ...models import User, Client


def test_create_user(db_session):
    """Test the creation of a new user."""
    user = User.create_user(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@example.com"
    assert user.role == "commercial"
    assert user.username == "jdoe"


def test_create_user_duplicate_username(db_session):
    """Test that creating a user with a duplicate username raises a ValueError."""
    User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial")
    with pytest.raises(ValueError, match="username_taken"):
        User.create_user(db_session, "jdoe", "Jane", "Doe", "jane@example.com", "management")


def test_create_user_duplicate_email(db_session):
    """Test that creating a user with a duplicate email raises a ValueError."""
    User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial")
    with pytest.raises(ValueError, match="email_taken"):
        User.create_user(db_session, "jdoe2", "Jane", "Doe", "john@example.com", "management")


def test_create_user_with_empty_fields(db_session):
    """
    Test that creating a user with empty required fields raises a ValueError.
    Required fields: username, first_name, last_name, email, role.
    """
    with pytest.raises(ValueError, match="required_fields_empty"):
        User.create_user(db_session, "", "John", "Doe", "john@example.com", "commercial")
    with pytest.raises(ValueError, match="required_fields_empty"):
        User.create_user(db_session, "jdoe", "", "Doe", "john@example.com", "commercial")
    with pytest.raises(ValueError, match="required_fields_empty"):
        User.create_user(db_session, "jdoe", "John", "", "john@example.com", "commercial")
    with pytest.raises(ValueError, match="required_fields_empty"):
        User.create_user(db_session, "jdoe", "John", "Doe", "", "commercial")
    with pytest.raises(ValueError, match="required_fields_empty"):
        User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "")


def test_create_user_invalid_role(db_session):
    """Test that creating a user with an invalid role raises a ValueError."""
    with pytest.raises(ValueError, match="invalid_role"):
        User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "invalid_role")


def test_get_all_users(db_session):
    """Test retrieving all users."""
    # Créez quelques utilisateurs de test
    user1 = User.create_user(db_session, "user1", "User", "One", "user1@example.com", "commercial")
    user2 = User.create_user(db_session, "user2", "User", "Two", "user2@example.com", "management")

    users = User.get_all(db_session)
    assert len(users) == 2
    assert users[0].first_name == "User"
    assert users[1].first_name == "User"


def test_get_user_by_id(db_session):
    """Test retrieving a user by ID."""
    user = User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial")
    fetched_user = User.get_by_id(db_session, user.user_id)
    assert fetched_user.first_name == "John"
    assert fetched_user.email == "john@example.com"


def test_get_user_by_invalid_id(db_session):
    """Test that retrieving a user with an invalid ID returns None."""
    assert User.get_by_id(db_session, 9999) is None


def test_update_user(db_session):
    """Test updating a user's information."""
    user = User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial")
    user.update(db_session, first_name="Jane", email="jane@example.com")
    assert user.first_name == "Jane"
    assert user.email == "jane@example.com"


def test_update_user_duplicate_email(db_session):
    """Test that updating a user with a duplicate email raises a ValueError."""
    user1 = User.create_user(db_session, "jdoe1", "John", "Doe", "john@example.com", "commercial")
    user2 = User.create_user(db_session, "jdoe2", "Jane", "Doe", "jane@example.com", "management")
    with pytest.raises(ValueError, match="email_taken"):
        user2.update(db_session, email="john@example.com")


def test_update_user_with_none_values(db_session):
    """Test that updating a user with None values does not change existing values."""
    user = User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial")
    original_first_name = user.first_name
    user.update(db_session, first_name=None, email=None)  # None ne doit pas écraser les valeurs existantes
    assert user.first_name == original_first_name
    assert user.email == "john@example.com"


def test_delete_user(db_session):
    """Test deleting a user."""
    user = User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial")
    user_id = user.user_id
    user.delete(db_session)
    assert User.get_by_id(db_session, user_id) is None


def test_delete_user_with_dependencies(db_session):
    """
    Test that deleting a user with active dependencies succeeds,
    and dependencies are properly dissociated (set to None).
    """
    # Create a user and a dependent client
    user = User.create_user(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial")
    client = Client.create(db_session, "Client", "One", "client1@example.com", user.user_id)

    # Verify the client is initially linked to the user
    assert client.commercial_contact_id == user.user_id

    # Delete the user (should succeed and dissociate dependencies)
    user.delete(db_session)

    # Verify the user is deleted
    assert User.get_by_id(db_session, user.user_id) is None

    # Verify the client's commercial_contact_id is set to None
    updated_client = Client.get_by_id(db_session, client.client_id)
    assert updated_client.commercial_contact_id is None
