"""Tests for permission checks."""

from app.auth.permissions import (
    can_add_event,
    can_control_server,
    can_edit_event,
    can_vote_event,
    is_granted_to_level,
)
from tests.factories import EventFactory, UserFactory
from app.models.user import User
from app.models.calendar import CalendarEvent
from datetime import UTC, datetime, timedelta


def test_can_add_event_member():
    user = UserFactory.build(status=User.STATUS_MEMBER)
    assert can_add_event(user) is True


def test_can_add_event_guest():
    user = UserFactory.build(status=User.STATUS_UNKNOWN)
    assert can_add_event(user) is False


def test_can_edit_event_owner():
    user = UserFactory.build(id=1)
    event = EventFactory.build(owner_id=1)
    assert can_edit_event(user, event) is True


def test_can_edit_event_non_owner():
    user = UserFactory.build(id=2, roles="ROLE_USER")
    event = EventFactory.build(owner_id=1)
    assert can_edit_event(user, event) is False


def test_can_edit_event_admin():
    user = UserFactory.build(id=2, roles="ROLE_USER,ROLE_ADMIN")
    event = EventFactory.build(owner_id=1)
    assert can_edit_event(user, event) is True


def test_can_vote_not_registered():
    user = UserFactory.build(status=User.STATUS_MEMBER, sim_dcs=True)
    event = EventFactory.build(registration=False)
    assert can_vote_event(user, event) is False


def test_can_vote_finished():
    user = UserFactory.build(status=User.STATUS_MEMBER, sim_dcs=True)
    event = EventFactory.build(
        registration=True,
        end_date=datetime.now(UTC) - timedelta(hours=1),
    )
    assert can_vote_event(user, event) is False


def test_can_control_server_member():
    user = UserFactory.build(status=User.STATUS_MEMBER)
    assert can_control_server(user) is True


def test_can_control_server_guest():
    user = UserFactory.build(status=User.STATUS_UNKNOWN)
    assert can_control_server(user) is False


def test_is_granted_level_all():
    assert is_granted_to_level(None, 0) is True


def test_is_granted_level_member():
    user = UserFactory.build(status=User.STATUS_MEMBER)
    assert is_granted_to_level(user, 3) is True

    guest = UserFactory.build(status=User.STATUS_UNKNOWN)
    assert is_granted_to_level(guest, 3) is False
