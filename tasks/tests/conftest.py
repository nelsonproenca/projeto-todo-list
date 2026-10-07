from datetime import datetime, timedelta, timezone as dt_timezone
from unittest import mock

import pytest


class Clock:
    """Controllable replacement for django.utils.timezone.now."""

    def __init__(self):
        self.current = datetime(2026, 1, 1, 12, 0, 0, tzinfo=dt_timezone.utc)

    def now(self):
        return self.current

    def advance(self, seconds):
        self.current += timedelta(seconds=seconds)


@pytest.fixture
def clock():
    clock = Clock()
    with mock.patch('tasks.services.timezone.now', clock.now):
        yield clock
