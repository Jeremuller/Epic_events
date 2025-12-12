import pytest
import click
from epic_events.views import ClientView


def test_list_clients_empty(capsys):
    """Test that list_clients prints a message when no clients exist."""
    ClientView.list_clients([])

    output = capsys.readouterr().out
    assert "No clients found in the database." in output


def test_list_clients_with_commercial(capsys, test_client, test_user):
    """
    Test that list_clients prints the correct commercial contact information.
    """

    # test_client fixture already linked to test_user through commercial_contact_id

    ClientView.list_clients([test_client])
    output = capsys.readouterr().out

    assert "=== List of Clients ===" in output
    assert str(test_client.client_id) in output
    assert test_client.first_name in output
    assert test_client.last_name in output
    assert test_client.email in output

    # Business / phone values possibly None in your model, check presence
    if test_client.business_name:
        assert test_client.business_name in output

    # Commercial contact full name
    expected_commercial = f"{test_user.first_name} {test_user.last_name}"
    assert expected_commercial in output


def test_prompt_client_creation_full(monkeypatch):
    """Test that prompt_client_creation returns correct dict when all fields are filled."""

    answers = iter([
        "John",  # First name
        "Doe",  # Last name
        "john.doe@example.com",  # Email
        42,  # Commercial ID
        "JD Consulting",  # Business
        "0601020304"  # Telephone
    ])

    monkeypatch.setattr(
        "click.prompt",
        lambda msg, **kwargs: next(answers)
    )

    result = ClientView.prompt_client_creation()

    assert result == {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "commercial_contact_id": 42,
        "business_name": "JD Consulting",
        "telephone": "0601020304",
    }


def test_prompt_client_creation_optional_fields_none(monkeypatch):
    """Test that empty optional fields return None."""

    answers = iter([
        "Alice",  # First name
        "Smith",  # Last name
        "alice@example.com",  # Email
        12,  # Commercial ID
        "",  # Business name → becomes None
        ""  # Telephone → becomes None
    ])

    monkeypatch.setattr(
        "click.prompt",
        lambda msg, **kwargs: next(answers)
    )

    result = ClientView.prompt_client_creation()

    assert result["business_name"] is None
    assert result["telephone"] is None


def test_prompt_client_creation_abort(monkeypatch):
    """Test that Click's Abort exception is propagated."""

    monkeypatch.setattr(
        "click.prompt",
        lambda *args, **kwargs: (_ for _ in ()).throw(click.Abort())
    )

    with pytest.raises(click.Abort):
        ClientView.prompt_client_creation()


def test_prompt_update_single_change(monkeypatch, test_client, capsys):
    """Test that only modified fields are returned by prompt_update."""

    answers = iter([
        test_client.first_name,  # unchanged
        test_client.last_name,  # unchanged
        test_client.email,  # unchanged
        42,  # NEW commercial_contact_id
        "New Business",  # changed
        test_client.telephone or ""  # unchanged
    ])

    monkeypatch.setattr(
        "click.prompt",
        lambda *args, **kwargs: next(answers)
    )

    result = ClientView.prompt_update(test_client)

    assert result == {
        "commercial_contact_id": 42,
        "business_name": "New Business"
    }

    output = capsys.readouterr().out
    expected_name = test_client.business_name or f"{test_client.first_name} {test_client.last_name}"
    assert f"Updating client: {expected_name} (ID: {test_client.client_id})" in output


def test_prompt_update_no_changes(monkeypatch, test_client):
    """Test that an empty dict is returned when no field is changed."""

    answers = iter([
        test_client.first_name,
        test_client.last_name,
        test_client.email,
        test_client.commercial_contact_id,
        test_client.business_name or "",
        test_client.telephone or "",
    ])

    monkeypatch.setattr(
        "click.prompt",
        lambda *args, **kwargs: next(answers)
    )

    result = ClientView.prompt_update(test_client)
    assert result == {}


def test_prompt_update_optional_empty_ignored(monkeypatch, test_client):
    """Test that empty optional values are ignored unless original was None."""

    answers = iter([
        test_client.first_name,
        test_client.last_name,
        test_client.email,
        test_client.commercial_contact_id,
        "",    # Business name → ignored
        "",    # Telephone → ignored
    ])

    monkeypatch.setattr(
        "click.prompt",
        lambda *args, **kwargs: next(answers)
    )

    result = ClientView.prompt_update(test_client)
    assert result == {}


def test_prompt_update_abort(monkeypatch, test_client):
    """Test that Click's Abort exception is propagated."""

    monkeypatch.setattr(
        "click.prompt",
        lambda *args, **kwargs: (_ for _ in ()).throw(click.Abort())
    )

    with pytest.raises(click.Abort):
        ClientView.prompt_update(test_client)
