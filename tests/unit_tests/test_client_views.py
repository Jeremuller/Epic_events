import pytest
from click.testing import CliRunner
from epic_events.views import create_client, list_clients, update_client
from epic_events.models import User, Client


@pytest.fixture
def runner():
    """Fixture to provide a CliRunner for testing CLI commands."""
    return CliRunner()


def test_create_client_command(runner, db_session):
    """Test the create_client CLI command with valid inputs."""
    user = User.create_user(
        db=db_session,
        username="commercial1",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )
    db_session.refresh(user)
    inputs = f"Acme\nCorp\ncontact@acme.com\n{user.user_id}\nAcme Inc\n0123456789\n"
    result = runner.invoke(
        create_client,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "✅ Client created" in result.output
    clients = db_session.query(Client).all()
    assert len(clients) == 1
    assert clients[0].first_name == "Acme"
    assert clients[0].commercial_contact_id == user.user_id


def test_create_client_duplicate_email(runner, db_session):
    """Test create_client with a duplicate email."""
    user = User.create_user(
        db=db_session,
        username="commercial1",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )
    Client.create(
        db=db_session,
        first_name="Acme",
        last_name="Corp",
        email="contact@acme.com",
        commercial_contact_id=user.user_id,
        business_name="Acme Inc",
        telephone="0123456789"
    )
    inputs = "Globex\nCorp\ncontact@acme.com\n1\nGlobex Inc\n9876543210\n"
    result = runner.invoke(
        create_client,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: This email is already registered." in result.output
    clients = db_session.query(Client).all()
    assert len(clients) == 1


def test_create_client_invalid_commercial_id(runner, db_session):
    """Test create_client with an invalid commercial contact ID."""
    inputs = "Acme\nCorp\ncontact@acme.com\n999\nAcme Inc\n0123456789\n"
    result = runner.invoke(
        create_client,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "The contact mentioned does not exists." in result.output
    clients = db_session.query(Client).all()
    assert len(clients) == 0


def test_list_clients_command(runner, db_session):
    """Test the list_clients CLI command."""
    user = User.create_user(
        db=db_session,
        username="commercial1",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )
    client = Client.create(
        db=db_session,
        first_name="Acme",
        last_name="Corp",
        email="contact@acme.com",
        commercial_contact_id=user.user_id,
        business_name="Acme Inc",
        telephone="0123456789"
    )
    result = runner.invoke(list_clients, obj={"db": db_session})
    assert result.exit_code == 0
    assert "=== List of Clients ===" in result.output
    assert "Acme Corp" in result.output
    assert "John Doe" in result.output


def test_update_client_command(runner, db_session, test_user, test_client):
    """Test the update_client CLI command."""
    inputs = f"Globex\nCorp\ncontact@globex.com\nGlobex Inc\n9876543210\n{test_user.user_id}\n"
    result = runner.invoke(
        update_client,
        args=[str(test_client.client_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "Updating client:" in result.output
    updated_client = db_session.query(Client).filter_by(client_id=test_client.client_id).first()
    assert updated_client.first_name == "Globex"
    assert updated_client.email == "contact@globex.com"
    assert updated_client.commercial_contact_id == test_user.user_id


def test_update_client_duplicate_email(runner, db_session):
    """Test update_client with a duplicate email."""
    user = User.create_user(
        db=db_session,
        username="commercial1",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        role="commercial"
    )
    client1 = Client.create(
        db=db_session,
        first_name="Acme",
        last_name="Corp",
        email="contact@acme.com",
        commercial_contact_id=user.user_id,
        business_name="Acme Inc",
        telephone="0123456789"
    )
    client2 = Client.create(
        db=db_session,
        first_name="Globex",
        last_name="Corp",
        email="contact@globex.com",
        commercial_contact_id=user.user_id,
        business_name="Globex Inc",
        telephone="9876543210"
    )
    inputs = "Globex\nCorp\ncontact@acme.com\n1\nGlobex Inc\n9876543210\n"
    result = runner.invoke(
        update_client,
        args=[str(client2.client_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: This email is already registered." in result.output
    updated_client = db_session.query(Client).filter_by(client_id=client2.client_id).first()
    assert updated_client.email == "contact@globex.com"


def test_update_client_invalid_commercial_id(runner, db_session, test_user, test_client):
    """Test update_client with an invalid commercial contact ID."""
    inputs = f"Acme\nCorp\ncontact@acme.com\nAcme Inc\n0123456789\n999\n"
    result = runner.invoke(
        update_client,
        args=[str(test_client.client_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: The contact mentioned does not exists." in result.output
    updated_client = db_session.query(Client).filter_by(client_id=test_client.client_id).first()
    assert updated_client.commercial_contact_id == test_user.user_id
