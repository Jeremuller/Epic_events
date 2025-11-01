import pytest
from click.testing import CliRunner
from epic_events.views import create_event, update_event, list_event
from epic_events.models import Event
from datetime import datetime, timedelta

