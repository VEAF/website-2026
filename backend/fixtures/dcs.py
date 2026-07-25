from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dcs import Player
from app.models.user import User

# "user" is the fixture key of the account linked to the player (None = unlinked player)
PLAYERS_DATA = [
    {
        "user": "mitch",
        "ucid": "3f9a1c7e4b8d05612a7f3e9c1d4b8a06",
        "nickname": "mitch",
        "join_at": datetime(2024, 3, 12, 20, 15, tzinfo=UTC),
        "last_join_at": datetime(2026, 7, 18, 21, 40, tzinfo=UTC),
    },
    {
        "user": "zip",
        "ucid": "8c2d5f1b9e304a7c6d1f8b2e5a903c74",
        "nickname": "zip",
        "join_at": datetime(2023, 11, 2, 19, 5, tzinfo=UTC),
        "last_join_at": datetime(2026, 7, 22, 20, 10, tzinfo=UTC),
    },
    {
        "user": "sky",
        "ucid": "d41b7a9c052e6f381cb4d7e2a95f0863",
        "nickname": "Sky_VEAF",
        "join_at": datetime(2025, 1, 24, 18, 30, tzinfo=UTC),
        "last_join_at": datetime(2026, 6, 30, 22, 55, tzinfo=UTC),
    },
    {
        "user": None,
        "ucid": "6e0f3b8d17c45a92e8d306b1f7a4c25b",
        "nickname": "Maverick",
        "join_at": datetime(2026, 2, 8, 21, 0, tzinfo=UTC),
        "last_join_at": datetime(2026, 7, 20, 19, 25, tzinfo=UTC),
    },
    {
        "user": None,
        "ucid": "b17d94e2f6035c8a4d2b7f19e806c3a5",
        "nickname": "Goose",
        "join_at": datetime(2026, 5, 17, 20, 45, tzinfo=UTC),
        "last_join_at": datetime(2026, 5, 17, 23, 10, tzinfo=UTC),
    },
]


async def load_players(session: AsyncSession, users: dict[str, User]) -> dict[str, Player]:
    players: dict[str, Player] = {}
    for data in PLAYERS_DATA:
        player = Player(
            ucid=data["ucid"],
            nickname=data["nickname"],
            join_at=data["join_at"],
            last_join_at=data["last_join_at"],
        )
        session.add(player)
        players[data["ucid"]] = player

    await session.flush()

    # User owns the FK to Player
    for data in PLAYERS_DATA:
        if data["user"] is not None:
            users[data["user"]].player_id = players[data["ucid"]].id

    await session.flush()

    return players
