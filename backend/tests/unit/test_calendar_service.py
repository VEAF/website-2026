"""Unit tests for calendar recurring event date calculations."""

from datetime import UTC, datetime, timedelta

from app.models.calendar import CalendarEvent
from app.services.calendar import AUTO_CREATE_EVENT_DAYS, get_next_event_datetime, is_needed_to_create_next_event


def _make_event(start_date: datetime, repeat_event: int) -> CalendarEvent:
    return CalendarEvent(start_date=start_date, repeat_event=repeat_event)


# --- get_next_event_datetime ---


class TestGetNextEventDatetime:
    def test_repeat_none_returns_none(self):
        # GIVEN an event with no repeat
        event = _make_event(datetime(2026, 3, 10, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_NONE)

        # WHEN / THEN
        assert get_next_event_datetime(event) is None

    def test_repeat_day_of_week(self):
        # GIVEN an event repeating weekly (Monday)
        event = _make_event(datetime(2026, 3, 9, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_DAY_OF_WEEK)

        # WHEN / THEN
        assert get_next_event_datetime(event) == datetime(2026, 3, 16, 20, 0, tzinfo=UTC)

    def test_repeat_day_of_week_preserves_time(self):
        # GIVEN an event at 21:30
        event = _make_event(datetime(2026, 3, 9, 21, 30, tzinfo=UTC), CalendarEvent.REPEAT_DAY_OF_WEEK)

        # WHEN
        result = get_next_event_datetime(event)

        # THEN
        assert result.hour == 21
        assert result.minute == 30

    def test_repeat_day_of_month(self):
        # GIVEN an event repeating monthly on the 15th
        event = _make_event(datetime(2026, 3, 15, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_DAY_OF_MONTH)

        # WHEN / THEN
        assert get_next_event_datetime(event) == datetime(2026, 4, 15, 20, 0, tzinfo=UTC)

    def test_repeat_day_of_month_end_of_month(self):
        # GIVEN an event on Jan 31 repeating monthly
        event = _make_event(datetime(2026, 1, 31, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_DAY_OF_MONTH)

        # WHEN / THEN — Feb has 28 days in 2026
        assert get_next_event_datetime(event) == datetime(2026, 2, 28, 20, 0, tzinfo=UTC)

    def test_repeat_day_of_month_leap_year(self):
        # GIVEN an event on Jan 31 in a leap year
        event = _make_event(datetime(2028, 1, 31, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_DAY_OF_MONTH)

        # WHEN / THEN — Feb 29 in 2028
        assert get_next_event_datetime(event) == datetime(2028, 2, 29, 20, 0, tzinfo=UTC)

    def test_repeat_day_of_month_december_to_january(self):
        # GIVEN an event on Dec 15 repeating monthly
        event = _make_event(datetime(2026, 12, 15, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_DAY_OF_MONTH)

        # WHEN / THEN
        assert get_next_event_datetime(event) == datetime(2027, 1, 15, 20, 0, tzinfo=UTC)

    def test_repeat_nth_weekday_first_monday(self):
        # GIVEN an event on the 1st Monday of March 2026 (March 2)
        event = _make_event(datetime(2026, 3, 2, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_NTH_WEEK_DAY_OF_MONTH)

        # WHEN / THEN — 1st Monday of April 2026 is April 6
        assert get_next_event_datetime(event) == datetime(2026, 4, 6, 20, 0, tzinfo=UTC)

    def test_repeat_nth_weekday_second_tuesday(self):
        # GIVEN an event on the 2nd Tuesday of March 2026 (March 10)
        event = _make_event(datetime(2026, 3, 10, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_NTH_WEEK_DAY_OF_MONTH)

        # WHEN / THEN — 2nd Tuesday of April 2026 is April 14
        assert get_next_event_datetime(event) == datetime(2026, 4, 14, 20, 0, tzinfo=UTC)

    def test_repeat_nth_weekday_last_sunday(self):
        # GIVEN an event on the last Sunday of March 2026 (March 29)
        # nth = (29-1)//7 = 4, which maps to "last"
        event = _make_event(datetime(2026, 3, 29, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_NTH_WEEK_DAY_OF_MONTH)

        # WHEN / THEN — last Sunday of April 2026 is April 26
        assert get_next_event_datetime(event) == datetime(2026, 4, 26, 20, 0, tzinfo=UTC)

    def test_repeat_nth_weekday_preserves_time(self):
        # GIVEN an event at 21:30
        event = _make_event(datetime(2026, 3, 2, 21, 30, tzinfo=UTC), CalendarEvent.REPEAT_NTH_WEEK_DAY_OF_MONTH)

        # WHEN
        result = get_next_event_datetime(event)

        # THEN
        assert result.hour == 21
        assert result.minute == 30

    def test_repeat_nth_weekday_december_to_january(self):
        # GIVEN an event on the 2nd Wednesday of Dec 2026 (Dec 9)
        event = _make_event(datetime(2026, 12, 9, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_NTH_WEEK_DAY_OF_MONTH)

        # WHEN / THEN — 2nd Wednesday of Jan 2027 is Jan 13
        assert get_next_event_datetime(event) == datetime(2027, 1, 13, 20, 0, tzinfo=UTC)

    def test_repeat_nth_weekday_fifth_occurrence_uses_last(self):
        # GIVEN an event on the 5th Thursday of a month (e.g. Oct 29, 2026 — nth=4)
        event = _make_event(datetime(2026, 10, 29, 20, 0, tzinfo=UTC), CalendarEvent.REPEAT_NTH_WEEK_DAY_OF_MONTH)

        # WHEN — November 2026 only has 4 Thursdays (5, 12, 19, 26)
        result = get_next_event_datetime(event)

        # THEN — falls back to last Thursday (Nov 26)
        assert result == datetime(2026, 11, 26, 20, 0, tzinfo=UTC)


# --- is_needed_to_create_next_event ---


class TestIsNeededToCreateNextEvent:
    def test_within_threshold(self):
        # GIVEN a weekly event starting in 3 days (next = 3+7 = 10 days < 32)
        now = datetime.now(UTC)
        event = _make_event(now + timedelta(days=3), CalendarEvent.REPEAT_DAY_OF_WEEK)

        # WHEN / THEN
        assert is_needed_to_create_next_event(event) is True

    def test_beyond_threshold(self):
        # GIVEN a weekly event starting in 40 days (next = 40+7 = 47 days > 32)
        now = datetime.now(UTC)
        event = _make_event(now + timedelta(days=40), CalendarEvent.REPEAT_DAY_OF_WEEK)

        # WHEN / THEN
        assert is_needed_to_create_next_event(event) is False

    def test_at_exact_threshold(self):
        # GIVEN next occurrence exactly at threshold boundary
        now = datetime.now(UTC)
        event = _make_event(now + timedelta(days=AUTO_CREATE_EVENT_DAYS - 7), CalendarEvent.REPEAT_DAY_OF_WEEK)

        # WHEN — next = (32-7)+7 = 32 days, delta.days = 32 <= 32
        assert is_needed_to_create_next_event(event) is True

    def test_past_date_still_triggers(self):
        # GIVEN a weekly event that started 10 days ago (next = -10+7 = -3 days, i.e. past)
        now = datetime.now(UTC)
        event = _make_event(now - timedelta(days=10), CalendarEvent.REPEAT_DAY_OF_WEEK)

        # WHEN / THEN — past dates are < 32, still triggers creation
        assert is_needed_to_create_next_event(event) is True

    def test_repeat_none_returns_false(self):
        # GIVEN an event with no repeat
        event = _make_event(datetime.now(UTC), CalendarEvent.REPEAT_NONE)

        # WHEN / THEN
        assert is_needed_to_create_next_event(event) is False
