from app.services.teamspeak import scan_and_cache


async def scan_teamspeak():
    """APScheduler job: fetch TeamSpeak data and update cache."""
    await scan_and_cache()
