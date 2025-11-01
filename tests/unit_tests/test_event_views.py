import pytest
from click.testing import CliRunner
from epic_events.views import create_event, update_event, list_events
from epic_events.models import Event
from datetime import datetime, timedelta


@pytest.fixture
def runner():
    """Fixture to provide a CliRunner for testing CLI commands."""
    return CliRunner()


def test_create_event_command(runner, db_session, test_user, test_client):
    """Test the create_event CLI command with valid inputs."""
    start_datetime = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M")
    end_datetime = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Team Meeting\n{start_datetime}\n{end_datetime}"
              f"\nParis\n50\nNotes for the event\n{test_client.client_id}\n{test_user.user_id}\n")
    result = runner.invoke(
        create_event,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "✅ Event created" in result.output
    events = db_session.query(Event).all()
    assert len(events) == 1
    assert events[0].name == "Team Meeting"
    assert events[0].location == "Paris"
    assert events[0].attendees == 50
    assert events[0].client_id == test_client.client_id
    assert events[0].support_contact_id == test_user.user_id


def test_create_event_invalid_date(runner, db_session, test_user, test_client):
    """Test the create_event CLI command with an invalid date (in the past)."""
    start_datetime = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    end_datetime = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Past Event\n{start_datetime}\n{end_datetime}"
              f"\nParis\n50\nNotes for the event\n{test_client.client_id}\n{test_user.user_id}\n")
    result = runner.invoke(
        create_event,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: Event date must be in the future." in result.output
    events = db_session.query(Event).all()
    assert len(events) == 0


def test_create_event_end_before_start(runner, db_session, test_user, test_client):
    """Test the create_event CLI command with end_datetime before start_datetime."""
    start_datetime = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M")
    end_datetime = (datetime.now() + timedelta(days=29)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Invalid Event\n{start_datetime}\n{end_datetime}"
              f"\nParis\n50\nNotes for the event\n{test_client.client_id}\n{test_user.user_id}\n")
    result = runner.invoke(
        create_event,
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: End date must be after start date." in result.output
    events = db_session.query(Event).all()
    assert len(events) == 0


def test_list_events_command(runner, db_session, test_event):
    """Test the list_events CLI command."""
    result = runner.invoke(list_events, obj={"db": db_session})
    assert result.exit_code == 0
    assert "=== List of Events ===" in result.output
    assert f"ID: {test_event.event_id}" in result.output
    assert f"Name: {test_event.name}" in result.output


def test_list_events_empty_db(runner, db_session):
    """Test list_events with an empty database."""
    result = runner.invoke(list_events, obj={"db": db_session})
    assert result.exit_code == 0
    assert "No events found in the database." in result.output


def test_update_event_command(runner, db_session, test_event):
    """Test the update_event CLI command."""
    new_start_datetime = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d %H:%M")
    new_end_datetime = (datetime.now() + timedelta(days=36)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Updated Event\n{new_start_datetime}\n{new_end_datetime}"
              f"\nLyon\n75\nUpdated notes\n{test_event.client_id}\n{test_event.support_contact_id}\n")
    result = runner.invoke(
        update_event,
        args=[str(test_event.event_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "✅ Event updated" in result.output
    updated_event = db_session.query(Event).filter_by(event_id=test_event.event_id).first()
    assert updated_event.name == "Updated Event"
    assert updated_event.location == "Lyon"
    assert updated_event.attendees == 75
    assert updated_event.notes == "Updated notes"
    assert updated_event.client_id == test_event.client_id
    assert updated_event.support_contact_id == test_event.support_contact_id


def test_update_event_invalid_date(runner, db_session, test_event):
    """Test the update_event CLI command with an invalid date (in the past)."""
    new_start_datetime = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    new_end_datetime = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Updated Event\n{new_start_datetime}\n{new_end_datetime}"
              f"\nLyon\n75\nUpdated notes\n{test_event.client_id}\n{test_event.support_contact_id}\n")
    result = runner.invoke(
        update_event,
        args=[str(test_event.event_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: Event date must be in the future." in result.output
    updated_event = db_session.query(Event).filter_by(event_id=test_event.event_id).first()
    assert updated_event.name != "Updated Event"


def test_update_event_end_before_start(runner, db_session, test_event):
    """Test the update_event CLI command with end_datetime before start_datetime."""
    new_start_datetime = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d %H:%M")
    new_end_datetime = (datetime.now() + timedelta(days=34)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Updated Event\n{new_start_datetime}\n{new_end_datetime}"
              f"\nLyon\n75\nUpdated notes\n{test_event.client_id}\n{test_event.support_contact_id}\n")
    result = runner.invoke(
        update_event,
        args=[str(test_event.event_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: End date must be after start date." in result.output
    updated_event = db_session.query(Event).filter_by(event_id=test_event.event_id).first()
    assert updated_event.name != "Updated Event"


def test_update_event_invalid_client_id(runner, db_session, test_event):
    """Test the update_event CLI command with an invalid client ID."""
    new_start_datetime = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d %H:%M")
    new_end_datetime = (datetime.now() + timedelta(days=36)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Updated Event\n{new_start_datetime}\n{new_end_datetime}"
              f"\nLyon\n75\nUpdated notes\n9999\n{test_event.support_contact_id}\n")
    result = runner.invoke(
        update_event,
        args=[str(test_event.event_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: The specified client does not exist." in result.output
    updated_event = db_session.query(Event).filter_by(event_id=test_event.event_id).first()
    assert updated_event.name != "Updated Event"


def test_update_event_invalid_support_contact_id(runner, db_session, test_event):
    """Test the update_event CLI command with an invalid support contact ID."""
    new_start_datetime = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d %H:%M")
    new_end_datetime = (datetime.now() + timedelta(days=36)).strftime("%Y-%m-%d %H:%M")
    inputs = (f"Updated Event\n{new_start_datetime}\n{new_end_datetime}"
              f"\nLyon\n75\nUpdated notes\n{test_event.client_id}\n9999\n")
    result = runner.invoke(
        update_event,
        args=[str(test_event.event_id)],
        input=inputs,
        obj={"db": db_session}
    )
    assert result.exit_code == 0
    assert "❌ Error: The contact mentioned does not exist." in result.output
    updated_event = db_session.query(Event).filter_by(event_id=test_event.event_id).first()
    assert updated_event.name != "Updated Event"
