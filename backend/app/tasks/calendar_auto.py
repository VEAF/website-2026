"""APScheduler job for recurring calendar events."""

import logging

from app.database import AsyncSessionLocal
from app.services.calendar import check_recurring_events

logger = logging.getLogger(__name__)


async def process_recurring_events():
    """APScheduler job: check recurring events and create next occurrences."""
    try:
        async with AsyncSessionLocal() as db:
            count = await check_recurring_events(db)
            if count > 0:
                logger.info("Recurring events processed: %d new event(s) created", count)
    except Exception:
        logger.exception("Failed to process recurring events")
