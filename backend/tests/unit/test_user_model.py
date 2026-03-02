"""Unit tests for User model properties."""

from app.models.user import User


def test_is_ready_to_promote_all_conditions_met():
    # GIVEN
    user = User(
        email="test@veaf.org", nickname="test", password="x",
        status=User.STATUS_CADET, sim_dcs=True, need_presentation=False, cadet_flights=5,
    )

    # THEN
    assert user.is_ready_to_promote is True


def test_is_ready_to_promote_not_cadet():
    # GIVEN
    user = User(
        email="test@veaf.org", nickname="test", password="x",
        status=User.STATUS_MEMBER, sim_dcs=True, need_presentation=False, cadet_flights=5,
    )

    # THEN
    assert user.is_ready_to_promote is False


def test_is_ready_to_promote_no_dcs():
    # GIVEN
    user = User(
        email="test@veaf.org", nickname="test", password="x",
        status=User.STATUS_CADET, sim_dcs=False, need_presentation=False, cadet_flights=5,
    )

    # THEN
    assert user.is_ready_to_promote is False


def test_is_ready_to_promote_needs_presentation():
    # GIVEN
    user = User(
        email="test@veaf.org", nickname="test", password="x",
        status=User.STATUS_CADET, sim_dcs=True, need_presentation=True, cadet_flights=5,
    )

    # THEN
    assert user.is_ready_to_promote is False


def test_is_ready_to_promote_not_enough_flights():
    # GIVEN
    user = User(
        email="test@veaf.org", nickname="test", password="x",
        status=User.STATUS_CADET, sim_dcs=True, need_presentation=False, cadet_flights=4,
    )

    # THEN
    assert user.is_ready_to_promote is False
