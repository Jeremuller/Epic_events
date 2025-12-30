import pytest
from datetime import datetime, timedelta
from epic_events.models import Event


def test_create_event_valid(db_session, test_user, test_client, test_contract):
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
        client_id=test_client.client_id
    )
    assert event.name == "Team Meeting"
    assert event.notes == "Quarterly team meeting"
    assert event.start_datetime == start_datetime
    assert event.end_datetime == end_datetime
    assert event.location == "Paris"
    assert event.attendees == 50
    assert event.client_id == test_client.client_id


def test_create_failed_contract_not_signed(db_session, test_user, test_client, test_contract):
    """Test an event can't be created if the client contract is not signed."""
    start_datetime = datetime.now() + timedelta(days=30)
    end_datetime = datetime.now() + timedelta(days=31)
    test_contract.signed = False
    with pytest.raises(ValueError, match="CONTRACT_NOT_SIGNED"):
        Event.create(
            db=db_session,
            name="Team Meeting",
            notes="Quarterly team meeting",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location="Paris",
            attendees=50,
            client_id=test_client.client_id
        )


def test_create_event_past_date(db_session, test_user, test_client, test_contract):
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
            client_id=test_client.client_id
        )


def test_create_event_end_before_start(db_session, test_user, test_client, test_contract):
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
            client_id=test_client.client_id
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
            client_id=9999
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


def test_update_event_invalid_client_id(db_session, test_user, test_client, test_event):
    """Test that updating an event with an invalid client_id raises a ValueError."""
    with pytest.raises(ValueError, match="CLIENT_NOT_FOUND"):
        test_event.update(
            db=db_session,
            client_id=9999
        )


def test_update_event_past_date(db_session, test_user, test_client, test_event):
    """Test that updating an event with a past start_datetime raises a ValueError."""
    with pytest.raises(ValueError, match="EVENT_DATE_IN_PAST"):
        test_event.update(
            db=db_session,
            start_datetime=datetime.now() - timedelta(days=1)
        )


def test_update_event_end_before_start(db_session, test_user, test_client, test_event):
    """Test that updating an event with end_datetime before start_datetime raises a ValueError."""
    with pytest.raises(ValueError, match="END_BEFORE_START"):
        test_event.update(
            db=db_session,
            start_datetime=datetime.now() + timedelta(days=35),
            end_datetime=datetime.now() + timedelta(days=34)
        )


def test_get_all_events(db_session, test_user, test_client, test_contract):
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
    )
    db_session.add(event1)
    db_session.commit()
    event2 = Event.create(
        db=db_session,
        name="Event 2",
        notes="Notes for event 2",
        start_datetime=datetime.now() + timedelta(days=40),
        end_datetime=datetime.now() + timedelta(days=41),
        location="Lyon",
        attendees=60,
        client_id=test_client.client_id
    )
    db_session.add(event2)
    db_session.commit()
    events = Event.get_all(db_session)
    assert len(events) == 2
    assert events[0].name in ["Event 1", "Event 2"]
    assert events[1].name in ["Event 1", "Event 2"]


def test_get_unassigned_events(db_session, test_user, test_client, test_contract, test_event):
    start_datetime = datetime.now() + timedelta(days=30)
    end_datetime = datetime.now() + timedelta(days=31)

    event_unassigned = Event.create(
        db=db_session,
        name="Unassigned Event",
        notes="No support",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        location="Lyon",
        attendees=20,
        client_id=test_client.client_id
    )
    db_session.add(event_unassigned)
    db_session.commit()

    unassigned_events = Event.get_unassigned_events(db_session)

    assert len(unassigned_events) == 1
    assert unassigned_events[0].name == "Unassigned Event"
    assert unassigned_events[0].support_contact_id is None


def test_get_assigned_events(db_session, support_session, test_client, test_contract, test_event):
    """
    Test that a support user retrieves only events assigned to them.
    """

    support_session.user_id = 7
    event_unassigned = Event.create(
        db=db_session,
        name="Unassigned Event",
        notes="Event not assigned",
        start_datetime=datetime.now() + timedelta(days=10),
        end_datetime=datetime.now() + timedelta(days=11),
        location="Lyon",
        attendees=20,
        client_id=test_client.client_id
    )
    event_unassigned.support_contact_id = support_session.user_id
    db_session.add(event_unassigned)
    db_session.commit()

    assigned_events = Event.get_assigned_to_user(db_session, support_session.user_id)
    assert len(assigned_events) == 1
    assert assigned_events[0].name == event_unassigned.name
    assert assigned_events[0].support_contact_id == support_session.user_id
