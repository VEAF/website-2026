from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module
from app.models.user import User, UserModule

USER_MODULES_DATA = [
    {"user": "mitch", "module": "a10c", "active": True, "level": UserModule.LEVEL_INSTRUCTOR},
    {"user": "mitch", "module": "caucasus", "active": True, "level": UserModule.LEVEL_INSTRUCTOR},
    {"user": "mitch", "module": "nevada", "active": True, "level": UserModule.LEVEL_INSTRUCTOR},
    {"user": "zip", "module": "a10c", "active": True, "level": UserModule.LEVEL_INSTRUCTOR},
    {"user": "zip", "module": "caucasus", "active": True, "level": UserModule.LEVEL_INSTRUCTOR},
]


async def load_user_modules(
    session: AsyncSession,
    users: dict[str, User],
    modules: dict[str, Module],
) -> None:
    for item in USER_MODULES_DATA:
        um = UserModule(
            user_id=users[item["user"]].id,
            module_id=modules[item["module"]].id,
            active=item["active"],
            level=item["level"],
        )
        session.add(um)

    await session.flush()
