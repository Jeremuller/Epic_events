import pytest
from epic_events.models import User, Client, Contract, Event


def test_create_user(db_session):
    """Test the creation of a new user."""
    user = User.create(
        db=db_session,
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial",
        password_hash="testpassword"
    )
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@example.com"
    assert user.role == "commercial"
    assert user.username == "jdoe"


def test_create_user_duplicate_username(db_session, test_user):
    """Test that creating a user with a duplicate username raises a ValueError."""
    with pytest.raises(ValueError, match="USERNAME_TAKEN"):
        User.create(
            db=db_session,
            username="test_user",
            first_name="Jane",
            last_name="Doe",
            email="another@example.com",
            role="management",
            password_hash="testpassword"
        )


def test_create_user_duplicate_email(db_session, test_user):
    """Test that creating a user with a duplicate email raises a ValueError."""
    with pytest.raises(ValueError, match="EMAIL_TAKEN"):
        User.create(
            db=db_session,
            username="JaneDoe",
            first_name="Jane",
            last_name="Doe",
            email="test@example.com",
            role="management",
            password_hash="testpassword"
        )


def test_create_user_with_empty_fields(db_session):
    """
    Test that creating a user with empty required fields raises a ValueError.
    Required fields: username, first_name, last_name, email, role.
    """
    with pytest.raises(ValueError, match="REQUIRED_FIELDS_EMPTY"):
        User.create(db_session, "", "John", "Doe", "john@example.com", "commercial",
                    password_hash="testpassword")
    with pytest.raises(ValueError, match="REQUIRED_FIELDS_EMPTY"):
        User.create(db_session, "jdoe", "", "Doe", "john@example.com", "commercial",
                    password_hash="testpassword")
    with pytest.raises(ValueError, match="REQUIRED_FIELDS_EMPTY"):
        User.create(db_session, "jdoe", "John", "", "john@example.com", "commercial",
                    password_hash="testpassword")
    with pytest.raises(ValueError, match="REQUIRED_FIELDS_EMPTY"):
        User.create(db_session, "jdoe", "John", "Doe", "", "commercial",
                    password_hash="testpassword")
    with pytest.raises(ValueError, match="REQUIRED_FIELDS_EMPTY"):
        User.create(db_session, "jdoe", "John", "Doe", "john@example.com", "",
                    password_hash="testpassword")


def test_create_user_invalid_role(db_session):
    """Test that creating a user with an invalid role raises a ValueError."""
    with pytest.raises(ValueError, match="INVALID_ROLE"):
        User.create(db_session, "jdoe", "John", "Doe", "john@example.com", "invalid_role",
                    password_hash="testpassword")


def test_get_all_users(db_session):
    """Test retrieving all users."""
    # Create a few test users
    user1 = User.create(db_session, "user1", "User", "One", "user1@example.com", "commercial",
                        password_hash="testpassword")
    db_session.add(user1)
    user2 = User.create(db_session, "user2", "User", "Two", "user2@example.com", "management",
                        password_hash="testpassword")
    db_session.add(user2)
    db_session.commit()

    users = User.get_all(db_session)
    assert len(users) == 2
    assert users[0].first_name == "User"
    assert users[1].first_name == "User"


def test_get_user_by_id(db_session):
    """Test retrieving a user by ID."""
    user = User.create(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial",
                       password_hash="testpassword")
    db_session.add(user)
    db_session.commit()
    fetched_user = User.get_by_id(db_session, user.user_id)
    assert fetched_user.first_name == "John"
    assert fetched_user.email == "john@example.com"


def test_get_user_by_username_found(db_session):
    """Should return the user when username exists in database."""
    user = User.create(
        db=db_session,
        username="john_doe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial",
        password_hash="securepassword"
    )
    db_session.add(user)
    db_session.commit()

    result = User.get_by_username(db_session, "john_doe")

    assert result is not None
    assert result.username == "john_doe"


def test_get_user_by_username_not_found(db_session):
    """Should return None when username does not exist."""
    result = User.get_by_username(db_session, "unknown_user")

    assert result is None


def test_get_user_by_invalid_id(db_session):
    """Test that retrieving a user with an invalid ID returns None."""
    assert User.get_by_id(db_session, 9999) is None


def test_update_user(db_session):
    """Test updating a user's information."""
    user = User.create(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial",
                       password_hash="testpassword")
    user.update(db_session, first_name="Jane", email="jane@example.com")
    assert user.first_name == "Jane"
    assert user.email == "jane@example.com"


def test_update_user_duplicate_email(db_session, test_user):
    """Test that updating a user with a duplicate email raises a ValueError."""
    user1 = User.create(db_session, "jdoe1", "John", "Doe", "john@example.com", "commercial",
                        password_hash="testpassword")
    db_session.add(user1)

    db_session.commit()
    with pytest.raises(ValueError, match="EMAIL_TAKEN"):
        user1.update(db_session, email="test@example.com")


def test_update_user_with_none_values(db_session):
    """Test that updating a user with None values does not change existing values."""
    user = User.create(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial",
                       password_hash="testpassword")
    original_first_name = user.first_name
    user.update(db_session, first_name=None, email=None)
    assert user.first_name == original_first_name
    assert user.email == "john@example.com"


def test_delete_user(db_session):
    """Test deleting a user."""
    user = User.create(db_session, "jdoe", "John", "Doe", "john@example.com", "commercial",
                       password_hash="testpassword")
    user_id = user.user_id
    user.delete(db_session)
    assert User.get_by_id(db_session, user_id) is None


def test_user_delete_dissociates_dependencies(db_session):
    """
        Unit test: Verify that User.delete() dissociates dependencies (clients, contracts, events).
        This test focuses solely on the dissociation logic, without database persistence.
        """
    user = User(
        username="jdoe",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial",
        password_hash="testpassword"
    )

    client = Client(commercial_contact_id=user.user_id)
    contract = Contract(commercial_contact_id=user.user_id)
    event = Event(support_contact_id=user.user_id)

    user.clients = [client]
    user.contracts = [contract]
    user.events = [event]

    assert client.commercial_contact_id == user.user_id
    assert contract.commercial_contact_id == user.user_id
    assert event.support_contact_id == user.user_id

    user.delete(db_session)

    assert client.commercial_contact_id is None
    assert contract.commercial_contact_id is None
    assert event.support_contact_id is None
