import pytest
from epic_events.utils import ErrorMessages, validate_length


def test_get_message_existing_key():
    msg = ErrorMessages.get_message("USERNAME_TAKEN")
    assert msg == "This username is already taken."


def test_get_message_unknown_key():
    msg = ErrorMessages.get_message("NON_EXISTENT_KEY")
    assert msg == ErrorMessages.DATABASE_ERROR.value


def test_validate_length_valid(monkeypatch):
    """Test that validate_length returns input when within max_length"""
    monkeypatch.setattr("click.prompt", lambda prompt: "short")
    result = validate_length("Enter something", max_length=10)
    assert result == "short"


def test_validate_length_too_long(monkeypatch, capsys):
    """Test that validate_length reprompts when input too long"""
    inputs = iter(["this_is_too_long", "ok"])
    monkeypatch.setattr("click.prompt", lambda prompt: next(inputs))

    result = validate_length("Enter something", max_length=5)

    captured = capsys.readouterr().out
    assert "Error: Input must be 5 characters or less" in captured
    assert result == "ok"
