from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dcs import Server
from app.models.module import ModuleRole, ModuleSystem

ROLES_DATA = [
    {"code": "cas", "name": "CAS", "position": 1},
    {"code": "strike", "name": "Strike", "position": 2},
    {"code": "sead", "name": "Sead", "position": 3},
    {"code": "cap", "name": "CAP", "position": 4},
]

SYSTEMS_DATA = [
    {"code": "ils", "name": "ILS", "position": 1},
    {"code": "tacan", "name": "TACAN", "position": 2},
    {"code": "vor", "name": "VOR", "position": 3},
    {"code": "adf", "name": "ADF", "position": 4},
    {"code": "vtol", "name": "VTOL", "position": 5},
    {"code": "aa-refuel", "name": "AA-Refuel", "position": 6},
    {"code": "carrier-ops", "name": "Carrier-Ops", "position": 7},
]

SERVERS_DATA = [
    {"code": "public", "name": "Public"},
    {"code": "private", "name": "Privé"},
]


async def load_reference_data(
    session: AsyncSession,
) -> tuple[dict[str, ModuleRole], dict[str, ModuleSystem], dict[str, Server]]:
    roles: dict[str, ModuleRole] = {}
    for data in ROLES_DATA:
        role = ModuleRole(**data)
        session.add(role)
        roles[data["code"]] = role

    systems: dict[str, ModuleSystem] = {}
    for data in SYSTEMS_DATA:
        system = ModuleSystem(**data)
        session.add(system)
        systems[data["code"]] = system

    servers: dict[str, Server] = {}
    for data in SERVERS_DATA:
        server = Server(**data)
        session.add(server)
        servers[data["code"]] = server

    await session.flush()
    return roles, systems, servers
