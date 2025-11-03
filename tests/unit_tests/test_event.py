import pytest
from datetime import datetime, timedelta
from epic_events.models import Event


def test_create_event_valid(db_session, test_user, test_client):
    """Test that a valid event can be created."""
    start_datetime = datetime.now() + timedelta(days=30)
    end_datetime = datetime.now() + timedelta(days=31)
    event = Event.create(
        db=db_session,
        name="Team Meeting",
        notes="Quarterly team meeting",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        location="Paris",
        attendees=50,
        client_id=test_client.client_id,
        support_contact_id=test_user.user_id
    )
    assert event.name == "Team Meeting"
    assert event.notes == "Quarterly team meeting"
    assert event.start_datetime == start_datetime
    assert event.end_datetime == end_datetime
    assert event.location == "Paris"
    assert event.attendees == 50
    assert event.client_id == test_client.client_id
    assert event.support_contact_id == test_user.user_id


def test_create_event_past_date(db_session, test_user, test_client):
    """Test that creating an event with a past date raises a ValueError."""
    start_datetime = datetime.now() - timedelta(days=1)
    end_datetime = datetime.now() + timedelta(days=1)
    with pytest.raises(ValueError, match="EVENT_DATE_IN_PAST"):
        Event.create(
            db=db_session,
            name="Past Event",
            notes="This event is in the past",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location="Paris",
            attendees=50,
            client_id=test_client.client_id,
            support_contact_id=test_user.user_id
        )


def test_create_event_end_before_start(db_session, test_user, test_client):
    """Test that creating an event with end_datetime before start_datetime raises a ValueError."""
    start_datetime = datetime.now() + timedelta(days=30)
    end_datetime = datetime.now() + timedelta(days=29)
    with pytest.raises(ValueError, match="END_BEFORE_START"):
        Event.create(
            db=db_session,
            name="Invalid Event",
            notes="End date before start date",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location="Paris",
            attendees=50,
            client_id=test_client.client_id,
            support_contact_id=test_user.user_id
        )


def test_create_event_invalid_client(db_session, test_user):
    """Test that creating an event with an invalid client_id raises a ValueError."""
    start_datetime = datetime.now() + timedelta(days=30)
    end_datetime = datetime.now() + timedelta(days=31)
    with pytest.raises(ValueError, match="CLIENT_NOT_FOUND"):
        Event.create(
            db=db_session,
            name="Invalid Client Event",
            notes="Client does not exist",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location="Paris",
            attendees=50,
            client_id=9999,
            support_contact_id=test_user.user_id
        )


def test_create_event_invalid_support_contact(db_session, test_client):
    """Test that creating an event with an invalid support_contact_id raises a ValueError."""
    start_datetime = datetime.now() + timedelta(days=30)
    end_datetime = datetime.now() + timedelta(days=31)
    with pytest.raises(ValueError, match="CONTACT_NOT_FOUND"):
        Event.create(
            db=db_session,
            name="Invalid Contact Event",
            notes="Support contact does not exist",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location="Paris",
            attendees=50,
            client_id=test_client.client_id,
            support_contact_id=9999
        )


def test_update_event(db_session, test_user, test_client, test_event):
    """Test that an event can be updated."""
    new_start_datetime = datetime.now() + timedelta(days=35)
    new_end_datetime = datetime.now() + timedelta(days=36)
    test_event.update(
        db=db_session,
        name="Updated Event",
        notes="Updated notes",
        start_datetime=new_start_datetime,
        end_datetime=new_end_datetime,
        location="Lyon",
        attendees=75,
        client_id=test_client.client_id,
        support_contact_id=test_user.user_id
    )
    assert test_event.name == "Updated Event"
    assert test_event.notes == "Updated notes"
    assert test_event.start_datetime == new_start_datetime
    assert test_event.end_datetime == new_end_datetime
    assert test_event.location == "Lyon"
    assert test_event.attendees == 75


def test_get_all_events(db_session, test_user, test_client):
    """Test that all events can be retrieved."""
    event1 = Event.create(
        db=db_session,
        name="Event 1",
        notes="Notes for event 1",
        start_datetime=datetime.now() + timedelta(days=30),
        end_datetime=datetime.now() + timedelta(days=31),
        location="Paris",
        attendees=50,
        client_id=test_client.client_id,
        support_contact_id=test_user.user_id
    )
    event2 = Event.create(
        db=db_session,
        name="Event 2",
        notes="Notes for event 2",
        start_datetime=datetime.now() + timedelta(days=40),
        end_datetime=datetime.now() + timedelta(days=41),
        location="Lyon",
        attendees=60,
        client_id=test_client.client_id,
        support_contact_id=test_user.user_id
    )
    events = Event.get_all(db_session)
    assert len(events) == 2
    assert events[0].name in ["Event 1", "Event 2"]
    assert events[1].name in ["Event 1", "Event 2"]
