from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar import CalendarEvent
from app.models.dcs import Server
from app.models.module import Module
from app.models.user import User


async def load_calendar_events(
    session: AsyncSession,
    users: dict[str, User],
    modules: dict[str, Module],
    servers: dict[str, Server],
) -> None:
    now = datetime.now(UTC)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    plus2 = today + timedelta(days=2)
    plus3 = today + timedelta(days=3)

    events_data = [
        {
            "title": "Training test",
            "type": CalendarEvent.EVENT_TYPE_TRAINING,
            "start_date": today.replace(hour=21, minute=0),
            "end_date": today.replace(hour=23, minute=0),
            "sim_dcs": True,
            "owner_key": "mitch",
            "registration": False,
            "modules_keys": [],
        },
        {
            "title": "Training test suppression",
            "type": CalendarEvent.EVENT_TYPE_TRAINING,
            "start_date": today.replace(hour=21, minute=0),
            "end_date": today.replace(hour=23, minute=0),
            "sim_dcs": True,
            "owner_key": "mitch",
            "deleted": True,
            "registration": True,
            "modules_keys": [],
        },
        {
            "title": "Las Vegas",
            "type": CalendarEvent.EVENT_TYPE_MISSION,
            "start_date": tomorrow.replace(hour=21, minute=0),
            "end_date": tomorrow.replace(hour=23, minute=30),
            "sim_dcs": True,
            "owner_key": "mitch",
            "map_key": "nevada",
            "restrictions": "1,2",
            "registration": True,
            "modules_keys": [],
        },
        {
            "title": "Rampstart",
            "type": CalendarEvent.EVENT_TYPE_TRAINING,
            "start_date": plus2.replace(hour=21, minute=0),
            "end_date": plus2.replace(hour=23, minute=30),
            "sim_dcs": True,
            "owner_key": "mitch",
            "map_key": "caucasus",
            "restrictions": "1,2",
            "registration": True,
            "modules_keys": ["a10c2"],
        },
        {
            "title": "Las Vegas CAS",
            "type": CalendarEvent.EVENT_TYPE_MISSION,
            "start_date": plus3.replace(hour=20, minute=0),
            "end_date": plus3.replace(hour=22, minute=0),
            "sim_dcs": True,
            "owner_key": "mitch",
            "map_key": "nevada",
            "restrictions": "1,2",
            "registration": True,
            "modules_keys": ["a10c", "a10c2"],
        },
        {
            "title": "ATC Nevada",
            "type": CalendarEvent.EVENT_TYPE_ATC,
            "start_date": today.replace(hour=0, minute=0),
            "end_date": today.replace(hour=23, minute=59),
            "sim_dcs": True,
            "owner_key": "mitch",
            "map_key": "nevada",
            "restrictions": "1,2",
            "server_key": "public",
            "registration": True,
            "modules_keys": ["a10c", "a10c2"],
        },
    ]

    for item in events_data:
        owner_key = item.pop("owner_key")
        map_key = item.pop("map_key", None)
        server_key = item.pop("server_key", None)
        modules_keys = item.pop("modules_keys")

        event = CalendarEvent(
            owner_id=users[owner_key].id,
            map_id=modules[map_key].id if map_key else None,
            server_id=servers[server_key].id if server_key else None,
            created_at=now,
            updated_at=now,
            **item,
        )
        event.modules = [modules[k] for k in modules_keys]
        session.add(event)

    await session.flush()
