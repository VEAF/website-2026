"""Permission checks (equivalent to Symfony Voters)."""

from app.models.calendar import CalendarEvent
from app.models.user import User


def can_add_event(user: User) -> bool:
    """Only members can create events."""
    return user.is_member or user.is_admin


def can_edit_event(user: User, event: CalendarEvent) -> bool:
    """Owner or admin can edit."""
    return event.owner_id == user.id or user.is_admin


def can_delete_event(user: User, event: CalendarEvent) -> bool:
    """Owner or admin can delete."""
    return event.owner_id == user.id or user.is_admin


def can_vote_event(user: User, event: CalendarEvent) -> bool:
    """Check if user can vote on an event."""
    if not event.registration:
        return False
    if event.is_finished:
        return False
    # Check restrictions
    if event.has_restriction(CalendarEvent.RESTRICTION_MEMBER) and not (user.is_member or user.is_admin):
        return False
    if event.has_restriction(CalendarEvent.RESTRICTION_CADET) and not (user.is_cadet or user.is_member or user.is_admin):
        return False
    # Check simulators
    if event.sim_dcs and not user.sim_dcs:
        return False
    if event.sim_bms and not user.sim_bms:
        return False
    return True


def can_choose_event(user: User, event: CalendarEvent) -> bool:
    """Same rules as voting."""
    return can_vote_event(user, event)


def can_control_server(user: User) -> bool:
    """Members can control servers."""
    return user.is_member or user.is_admin


def can_mark_presentation(user: User) -> bool:
    """Members can mark cadet as presented."""
    return user.is_member or user.is_admin


def can_add_activity(user: User) -> bool:
    """Members can log cadet flights."""
    return user.is_member or user.is_admin


def is_granted_to_level(user: User | None, level: int) -> bool:
    """Check if user meets the access restriction level."""
    LEVEL_ALL = 0
    LEVEL_GUEST = 1
    LEVEL_CADET = 2
    LEVEL_MEMBER = 3

    if level == LEVEL_ALL:
        return True
    if user is None:
        return False
    if level == LEVEL_GUEST:
        return True  # Any logged-in user
    if level == LEVEL_CADET:
        return user.is_cadet or user.is_member or user.is_admin
    if level == LEVEL_MEMBER:
        return user.is_member or user.is_admin
    return False
