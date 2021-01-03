from datetime import datetime

import pytest
from freezegun import freeze_time

from src.models import Reminder


class TestReminder:
    @pytest.mark.parametrize(
        "time",
        [
            datetime(2021, 1, 16, 11, 57),
            datetime(2021, 1, 16, 11, 58),
            datetime(2021, 1, 16, 11, 59),
            datetime(2021, 1, 16, 12, 0),
            datetime(2021, 1, 16, 12, 30),
        ],
    )
    @pytest.mark.usefixtures("reminder")
    def test_returns_reminder_when_is_finished_is_false_and_it_is_due(self, time):
        with freeze_time(time):
            assert Reminder.due_now().count() == 1

    @pytest.mark.parametrize(
        "time",
        [
            datetime(2020, 4, 15, 20, 32),
            datetime(2021, 1, 16, 11, 56),
        ],
    )
    @pytest.mark.usefixtures("reminder")
    def test_does_not_return_reminder_when_is_finished_is_false_and_it_is_not_due(
        self, reminder, time
    ):
        with freeze_time(time):
            assert Reminder.due_now().count() == 0

    def test_does_not_return_finished_reminders(self, reminder):
        reminder.finish()

        assert Reminder.due_now().count() == 0
