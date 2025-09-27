import pytest
from ...models import User
from datetime import datetime


def test_create_user(db):
    """Test the creation of a new user."""
    user = User.create_user(
        db=db,
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


def test_get_all_users(db):
    """Test retrieving all users."""
    # Créez quelques utilisateurs de test
    user1 = User.create_user(db, "user1", "User", "One", "user1@example.com", "commercial")
    user2 = User.create_user(db, "user2", "User", "Two", "user2@example.com", "management")

    users = User.get_all(db)
    assert len(users) == 2
    assert users[0].first_name == "User"
    assert users[1].first_name == "User"


def test_get_user_by_id(db):
    """Test retrieving a user by ID."""
    user = User.create_user(db, "jdoe", "John", "Doe", "john@example.com", "commercial")
    fetched_user = User.get_by_id(db, user.user_id)
    assert fetched_user.first_name == "John"
    assert fetched_user.email == "john@example.com"


def test_update_user(db):
    """Test updating a user's information."""
    user = User.create_user(db, "jdoe", "John", "Doe", "john@example.com", "commercial")
    user.update(db, first_name="Jane", email="jane@example.com")
    assert user.first_name == "Jane"
    assert user.email == "jane@example.com"


def test_delete_user(db):
    """Test deleting a user."""
    user = User.create_user(db, "jdoe", "John", "Doe", "john@example.com", "commercial")
    user_id = user.user_id
    user.delete(db)
    assert User.get_by_id(db, user_id) is None
