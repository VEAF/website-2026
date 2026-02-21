from sqlalchemy.ext.asyncio import AsyncSession

from app.models.module import Module, ModuleRole, ModuleSystem

MODULES_DATA = [
    # Maps
    {"key": "caucasus", "code": "caucasus", "name": "Caucase", "long_name": "Caucase", "type": Module.TYPE_MAP, "landing_page": True, "landing_page_number": 1, "roles": [], "systems": []},
    {"key": "nevada", "code": "nevada", "name": "Nevada", "long_name": "Nevada", "type": Module.TYPE_MAP, "landing_page": True, "landing_page_number": 2, "roles": [], "systems": []},
    {"key": "syria", "code": "syria", "name": "Syrie", "long_name": "Syrie", "type": Module.TYPE_MAP, "landing_page": True, "landing_page_number": 3, "roles": [], "systems": []},
    {"key": "channel", "code": "channel", "name": "Manche", "long_name": "La manche", "type": Module.TYPE_MAP, "landing_page": False, "landing_page_number": 4, "roles": [], "systems": []},
    # Special
    {"key": "supercarrier", "code": "supercarrier", "name": "S.C.", "long_name": "Supercarrier", "type": Module.TYPE_SPECIAL, "landing_page": False, "landing_page_number": 1, "roles": [], "systems": []},
    {"key": "ca", "code": "ca", "name": "C.A.", "long_name": "Combined Arms", "type": Module.TYPE_SPECIAL, "landing_page": False, "landing_page_number": 1, "roles": [], "systems": []},
    # Aircraft
    {"key": "a10c", "code": "a-10c", "name": "A-10C", "long_name": "A-10C", "type": Module.TYPE_AIRCRAFT, "landing_page": False, "landing_page_number": 2, "period": Module.PERIOD_MODERN, "roles": ["cas", "strike"], "systems": ["ils", "tacan"]},
    {"key": "a10c2", "code": "a-10c-2", "name": "A-10C II", "long_name": "A-10C II Tank Killer", "type": Module.TYPE_AIRCRAFT, "landing_page": True, "landing_page_number": 3, "period": Module.PERIOD_MODERN, "roles": ["cas", "strike"], "systems": ["ils", "tacan"]},
    {"key": "m2000c", "code": "m2000c", "name": "M-2000C", "long_name": "M-2000C", "type": Module.TYPE_AIRCRAFT, "landing_page": True, "landing_page_number": 1, "period": Module.PERIOD_MODERN, "roles": ["strike", "cap"], "systems": ["tacan", "aa-refuel"]},
    {"key": "mig15", "code": "mig-15", "name": "MiG-15", "long_name": "MiG-15", "type": Module.TYPE_AIRCRAFT, "landing_page": True, "landing_page_number": 4, "period": Module.PERIOD_COLD_WAR, "roles": [], "systems": []},
    {"key": "mig21", "code": "mig-21", "name": "MiG-21", "long_name": "MiG-21 Bis", "type": Module.TYPE_AIRCRAFT, "landing_page": True, "landing_page_number": 5, "period": Module.PERIOD_COLD_WAR, "roles": [], "systems": []},
    {"key": "mig29", "code": "mig-29", "name": "MiG-29", "long_name": "MiG-29", "type": Module.TYPE_AIRCRAFT, "landing_page": True, "landing_page_number": 6, "period": Module.PERIOD_MODERN, "roles": [], "systems": []},
    {"key": "su27", "code": "su-27", "name": "Su-27", "long_name": "Su-27", "type": Module.TYPE_AIRCRAFT, "landing_page": True, "landing_page_number": 7, "period": Module.PERIOD_MODERN, "roles": [], "systems": []},
    {"key": "su25t", "code": "su-25t", "name": "Su-25t", "long_name": "Su-25t", "type": Module.TYPE_AIRCRAFT, "landing_page": True, "landing_page_number": 5, "period": Module.PERIOD_MODERN, "roles": ["cas", "strike", "sead"], "systems": []},
    # Helicopters
    {"key": "sa342", "code": "sa342", "name": "SA-342", "long_name": "SA-342", "type": Module.TYPE_HELICOPTER, "landing_page": True, "landing_page_number": 1, "period": Module.PERIOD_MODERN, "roles": [], "systems": []},
    {"key": "ka50", "code": "ka-50", "name": "KA-50", "long_name": "KA-50 Black Shark 2", "type": Module.TYPE_HELICOPTER, "landing_page": True, "landing_page_number": 2, "period": Module.PERIOD_MODERN, "roles": [], "systems": []},
]


async def load_modules(
    session: AsyncSession,
    roles: dict[str, ModuleRole],
    systems: dict[str, ModuleSystem],
) -> dict[str, Module]:
    modules: dict[str, Module] = {}

    for item in MODULES_DATA:
        data = {k: v for k, v in item.items() if k not in ("key", "roles", "systems")}
        module = Module(**data)
        module.roles = [roles[code] for code in item["roles"]]
        module.systems = [systems[code] for code in item["systems"]]
        session.add(module)
        modules[item["key"]] = module

    await session.flush()
    return modules
