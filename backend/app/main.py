from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize APScheduler
    from app.tasks.scheduler import start_scheduler

    start_scheduler()

    # Run initial TeamSpeak scan so cache is populated immediately
    if settings.API_TEAMSPEAK_URL:
        from app.services.teamspeak import scan_and_cache

        await scan_and_cache()

    yield
    # Shutdown: cleanup


app = FastAPI(
    title="VEAF Website API",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.APP_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
