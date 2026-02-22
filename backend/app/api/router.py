from fastapi import APIRouter

from app.api import admin_modules, admin_stats, admin_users, auth, calendar, dcsbot, files, header, map, menu, metrics, mission_maker, modules, pages, recruitment, roster, servers, teamspeak, users

api_router = APIRouter(prefix="/api")

api_router.include_router(admin_modules.router)
api_router.include_router(admin_stats.router)
api_router.include_router(admin_users.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(calendar.router)
api_router.include_router(modules.router)
api_router.include_router(roster.router)
api_router.include_router(pages.router)
api_router.include_router(menu.router)
api_router.include_router(files.router)
api_router.include_router(servers.router)
api_router.include_router(recruitment.router)
api_router.include_router(teamspeak.router)
api_router.include_router(dcsbot.router)
api_router.include_router(map.router)
api_router.include_router(mission_maker.router)
api_router.include_router(metrics.router)
api_router.include_router(header.router)
