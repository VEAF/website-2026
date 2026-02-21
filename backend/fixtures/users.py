from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.password import hash_password
from app.models.user import User

USERS_DATA = [
    {"key": "mitch", "email": "mitch@localhost", "nickname": "mitch", "roles": "ROLE_USER,ROLE_ADMIN", "status": User.STATUS_MEMBER, "sim_dcs": True, "sim_bms": False},
    {"key": "zip", "email": "zip@localhost", "nickname": "zip", "roles": "ROLE_USER,ROLE_ADMIN", "status": User.STATUS_TREASURER, "sim_dcs": True, "sim_bms": False},
    {"key": "fifi", "email": "fifi@localhost", "nickname": "fifi", "roles": "ROLE_USER", "status": User.STATUS_TREASURER_DEPUTY, "sim_dcs": True, "sim_bms": False},
    {"key": "lost", "email": "lost@localhost", "nickname": "lost", "roles": "ROLE_USER", "status": User.STATUS_GUEST, "sim_dcs": False, "sim_bms": False},
    {"key": "user", "email": "user@localhost", "nickname": "user", "roles": "ROLE_USER", "status": User.STATUS_UNKNOWN, "sim_dcs": True, "sim_bms": False},
    {"key": "guest", "email": "guest@localhost", "nickname": "guest", "roles": "ROLE_USER", "status": User.STATUS_GUEST, "sim_dcs": True, "sim_bms": False},
    {"key": "cadet", "email": "cadet@localhost", "nickname": "cadet", "roles": "ROLE_USER,ROLE_CADET", "status": User.STATUS_CADET, "sim_dcs": True, "sim_bms": False},
    {"key": "cadet_need_presentation", "email": "cadet_need_presentation@localhost", "nickname": "cadet_need_presentation", "roles": "ROLE_USER,ROLE_CADET", "status": User.STATUS_CADET, "sim_dcs": True, "sim_bms": False, "need_presentation": True},
    {"key": "cadet_with_presentation", "email": "cadet_with_presentation@localhost", "nickname": "cadet_with_presentation", "roles": "ROLE_USER,ROLE_CADET", "status": User.STATUS_CADET, "sim_dcs": True, "sim_bms": False},
    {"key": "membre", "email": "membre@localhost", "nickname": "membre", "roles": "ROLE_USER", "status": User.STATUS_MEMBER, "sim_dcs": True, "sim_bms": False},
    {"key": "tresorier_adjoint", "email": "tresorier-adjoint@localhost", "nickname": "trésorier adjoint", "roles": "ROLE_USER", "status": User.STATUS_TREASURER_DEPUTY, "sim_dcs": True, "sim_bms": False},
    {"key": "tresorier", "email": "tresorier@localhost", "nickname": "trésorier", "roles": "ROLE_USER", "status": User.STATUS_TREASURER, "sim_dcs": True, "sim_bms": False},
    {"key": "secretaire_adjoint", "email": "secretaire-adjoint@localhost", "nickname": "secrétaire adjoint", "roles": "ROLE_USER", "status": User.STATUS_SECRETARY_DEPUTY, "sim_dcs": True, "sim_bms": False},
    {"key": "secretaire", "email": "secretaire@localhost", "nickname": "secrétaire", "roles": "ROLE_USER", "status": User.STATUS_SECRETARY, "sim_dcs": True, "sim_bms": False},
    {"key": "president_adjoint", "email": "president-adjoint@localhost", "nickname": "président adjoint", "roles": "ROLE_USER", "status": User.STATUS_PRESIDENT_DEPUTY, "sim_dcs": True, "sim_bms": False},
    {"key": "president", "email": "president@localhost", "nickname": "président", "roles": "ROLE_USER", "status": User.STATUS_PRESIDENT, "sim_dcs": True, "sim_bms": False},
    {"key": "sky", "email": "sky@localhost", "nickname": "sky", "roles": "ROLE_USER", "status": User.STATUS_MEMBER, "sim_dcs": True, "sim_bms": True},
    {"key": "shark", "email": "shark@localhost", "nickname": "shark", "roles": "ROLE_USER", "status": User.STATUS_MEMBER, "sim_dcs": True, "sim_bms": False},
    {"key": "polo", "email": "polo@localhost", "nickname": "polo", "roles": "ROLE_USER", "status": User.STATUS_CADET, "sim_dcs": True, "sim_bms": False},
    {"key": "mge", "email": "mge@localhost", "nickname": "mge", "roles": "ROLE_USER", "status": User.STATUS_MEMBER, "sim_dcs": True, "sim_bms": True},
]


async def load_users(session: AsyncSession) -> dict[str, User]:
    now = datetime.utcnow()
    hashed = hash_password("test1234")

    users: dict[str, User] = {}
    for item in USERS_DATA:
        key = item["key"]
        user = User(
            email=item["email"],
            nickname=item["nickname"],
            password=hashed,
            roles=item["roles"],
            status=item["status"],
            sim_dcs=item["sim_dcs"],
            sim_bms=item["sim_bms"],
            need_presentation=item.get("need_presentation", False),
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        users[key] = user

    await session.flush()
    return users
