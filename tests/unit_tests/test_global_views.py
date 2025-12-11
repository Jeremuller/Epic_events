import click
from click.testing import CliRunner
import pytest
from epic_events.views import MenuView


def test_prompt_for_id(monkeypatch):
    """Test that prompt_for_id returns the integer provided by the mocked user input."""
    monkeypatch.setattr("click.prompt", lambda msg, type: 42)
    assert MenuView.prompt_for_id("user") == 42


def test_prompt_for_contact_id(monkeypatch):
    """Test that prompt_for_contact_id returns the integer provided by the mocked user input."""
    monkeypatch.setattr("click.prompt", lambda msg, type: 7)
    assert MenuView.prompt_for_contact_id("client") == 7
