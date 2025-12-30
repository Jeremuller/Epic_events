import pytest
import click
from epic_events.views import EventView
from epic_events.models import Event
from datetime import datetime, timedelta


def test_list_events_empty(capsys, db_session):
    """Test that list_events prints a message when no events exist."""
    from epic_events.views import EventView

    EventView.list_events([])

    output = capsys.readouterr().out
    assert "No events found in the database." in output


def test_list_events_with_event(capsys, db_session, test_event, test_client, test_user):
    """Test that list_events prints all event information correctly."""
    from epic_events.views import EventView

    EventView.list_events([test_event])

    output = capsys.readouterr().out

    assert "=== List of Events ===" in output
    assert str(test_event.event_id) in output
    assert test_event.name in output
    assert test_client.business_name in output
    assert f"{test_user.first_name} {test_user.last_name}" in output
    assert str(test_event.start_datetime) in output
    assert str(test_event.end_datetime) in output
    assert test_event.location in output
    assert str(test_event.attendees) in output


def test_list_events_no_client_raises(db_session, test_user):
    """Test that creating an event without client raises an exception."""
    with pytest.raises(ValueError):
        event = Event.create(
            db=db_session,
            name="Orphan Event",
            notes="No client assigned",
            start_datetime=datetime.now(),
            end_datetime=datetime.now() + timedelta(hours=2),
            location="Virtual",
            attendees=20,
            client_id=None
        )
        db_session.add(event)
        db_session.commit()


def test_list_events_no_support_raises(db_session, test_client):
    """Test that creating an event without support contact raises an exception."""

    with pytest.raises(ValueError):
        event = Event.create(
            db=db_session,
            name="Supportless Event",
            notes="No support assigned",
            start_datetime=datetime.now(),
            end_datetime=datetime.now() + timedelta(hours=2),
            location="Online",
            attendees=15,
            client_id=test_client.client_id
        )
        db_session.add(event)
        db_session.commit()


def test_prompt_event_creation_full(db_session, monkeypatch):
    """Test full event creation workflow with valid inputs."""

    answers = iter([
        "My Event",  # name
        "Notes here",  # notes
        "2025-01-01 10:00",  # start_datetime
        "2025-01-02 18:00",  # end_datetime
        "Paris",  # location
        50,  # attendees
        1,  # client_id
    ])

    # Monkeypatch click.prompt
    monkeypatch.setattr("click.prompt", lambda prompt_text, **kwargs: next(answers))

    result = EventView.prompt_event_creation()

    assert result["name"] == "My Event"
    assert result["notes"] == "Notes here"
    assert result["start_datetime"] == datetime.strptime("2025-01-01 10:00", "%Y-%m-%d %H:%M")
    assert result["end_datetime"] == datetime.strptime("2025-01-02 18:00", "%Y-%m-%d %H:%M")
    assert result["location"] == "Paris"
    assert result["attendees"] == 50
    assert result["client_id"] == 1


def test_prompt_event_creation_optional_none(db_session, monkeypatch):
    """Test that empty optional fields return None."""

    answers = iter([
        "Event X",  # name
        "",  # notes -> None
        "2025-02-01 09:00",  # start_datetime
        "2025-02-01 17:00",  # end_datetime
        "",  # location -> None
        30,  # attendees
        1,  # client_id
        2  # support_contact_id
    ])

    monkeypatch.setattr("click.prompt", lambda prompt_text, **kwargs: next(answers))

    result = EventView.prompt_event_creation()

    assert result["notes"] is None
    assert result["location"] is None


def test_prompt_event_creation_invalid_date(db_session, monkeypatch, capsys):
    """Test that invalid datetime input is handled and prints an error."""

    inputs = iter([
        "Event Y",  # name
        "",  # notes
        "bad-date",  # start_datetime -> invalid
        "2025-03-01 09:00",  # start_datetime -> corrected
        "2025-03-01 17:00",  # end_datetime
        "",  # location
        20,  # attendees
        1,  # client_id
    ])

    monkeypatch.setattr("click.prompt", lambda prompt_text, **kwargs: next(inputs))

    result = EventView.prompt_event_creation()

    captured = capsys.readouterr().out
    assert "Invalid format" in captured
    assert result["start_datetime"] == datetime.strptime("2025-03-01 09:00", "%Y-%m-%d %H:%M")


def test_prompt_event_creation_abort(db_session, monkeypatch):
    """Test that Ctrl+C propagates click.Abort."""

    monkeypatch.setattr(
        "click.prompt",
        lambda *args, **kwargs: (_ for _ in ()).throw(click.Abort())
    )

    with pytest.raises(click.Abort):
        EventView.prompt_event_creation()


def test_prompt_update_no_changes(db_session, monkeypatch, test_event):
    event = test_event

    answers = iter([
        event.name,
        event.notes or "",
        False,
        False,
        event.location or "",
        event.attendees,
        event.client_id,
        event.support_contact_id
    ])

    monkeypatch.setattr("click.prompt", lambda *a, **kw: next(answers))
    monkeypatch.setattr("click.confirm", lambda *a, **kw: next(answers))

    result = EventView.prompt_update(event)
    assert result == {}


def test_prompt_update_some_changes(db_session, monkeypatch, test_event):
    event = test_event

    new_start = datetime(2030, 1, 1, 10, 0)
    new_end = datetime(2030, 1, 1, 18, 0)

    answers_prompt = iter([
        "New Event Name",
        "",
        "2030-01-01 10:00",
        "2030-01-01 18:00",
        event.location or "",
        event.attendees,
        event.client_id,
        event.support_contact_id
    ])

    answers_confirm = iter([True, True])

    monkeypatch.setattr("click.prompt", lambda *a, **kw: next(answers_prompt))
    monkeypatch.setattr("click.confirm", lambda *a, **kw: next(answers_confirm))

    result = EventView.prompt_update(event)

    assert result["name"] == "New Event Name"
    assert result["start_datetime"] == new_start
    assert result["end_datetime"] == new_end


def test_prompt_update_abort(db_session, monkeypatch, test_event):
    monkeypatch.setattr(
        "click.prompt",
        lambda *a, **kw: (_ for _ in ()).throw(click.Abort())
    )

    with pytest.raises(click.Abort):
        EventView.prompt_update(test_event)
