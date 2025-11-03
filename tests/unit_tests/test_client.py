import pytest
from epic_events.models import Client


def test_create_client_valid(db_session, test_user):
    """Test that a valid client can be created."""
    client = Client.create(
        db=db_session,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        commercial_contact_id=test_user.user_id
    )
    assert client.first_name == "John"
    assert client.last_name == "Doe"
    assert client.email == "john@example.com"
    assert client.commercial_contact_id == test_user.user_id
    assert client.first_contact is not None
    assert client.last_update is not None


def test_create_client_duplicate_email(db_session, test_user):
    """Test that creating a client with a duplicate email raises a ValueError."""
    Client.create(
        db=db_session,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        commercial_contact_id=test_user.user_id
    )
    with pytest.raises(ValueError, match="EMAIL_TAKEN"):
        Client.create(
            db=db_session,
            first_name="Jane",
            last_name="Doe",
            email="john@example.com",
            commercial_contact_id=test_user.user_id
        )


def test_create_client_empty_fields(db_session, test_user):
    """Test that creating a client with empty required fields raises a ValueError."""
    with pytest.raises(ValueError, match="REQUIRED_FIELDS_EMPTY"):
        Client.create(
            db=db_session,
            first_name="",
            last_name="Doe",
            email="john@example.com",
            commercial_contact_id=test_user.user_id
        )
    with pytest.raises(ValueError, match="REQUIRED_FIELDS_EMPTY"):
        Client.create(
            db=db_session,
            first_name="John",
            last_name="",
            email="john@example.com",
            commercial_contact_id=test_user.user_id
        )
    with pytest.raises(ValueError, match="REQUIRED_FIELDS_EMPTY"):
        Client.create(
            db=db_session,
            first_name="John",
            last_name="Doe",
            email="",  # Champ vide
            commercial_contact_id=test_user.user_id
        )


def test_create_client_invalid_commercial_contact(db_session):
    """Test that creating a client with an invalid commercial_contact_id raises a ValueError."""
    with pytest.raises(ValueError, match="CONTACT_NOT_FOUND"):
        Client.create(
            db=db_session,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            commercial_contact_id=9999
        )


def test_update_client(db_session, test_user):
    """Test that a client can be updated."""
    client = Client.create(
        db=db_session,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        commercial_contact_id=test_user.user_id
    )
    client.update(
        db=db_session,
        first_name="Jane",
        email="jane@example.com"
    )
    assert client.first_name == "Jane"
    assert client.email == "jane@example.com"
    assert client.last_update > client.first_contact


def test_get_all_clients(db_session, test_user):
    """Test that all clients can be retrieved."""
    client1 = Client.create(
        db=db_session,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        commercial_contact_id=test_user.user_id
    )
    client2 = Client.create(
        db=db_session,
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        commercial_contact_id=test_user.user_id
    )
    clients = Client.get_all(db_session)
    assert len(clients) == 2
    assert clients[0].first_name in ["John", "Jane"]
    assert clients[1].first_name in ["John", "Jane"]


def test_get_client_by_id(db_session, test_user):
    """Test that a client can be retrieved by ID."""
    client = Client.create(
        db=db_session,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        commercial_contact_id=test_user.user_id
    )
    fetched_client = Client.get_by_id(db_session, client.client_id)
    assert fetched_client.first_name == "John"
    assert fetched_client.email == "john@example.com"


def test_get_client_by_invalid_id(db_session):
    """Test that getting a client with an invalid ID returns None."""
    assert Client.get_by_id(db_session, 9999) is None
