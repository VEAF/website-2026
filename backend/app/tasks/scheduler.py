from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def start_scheduler():
    """Start APScheduler with periodic tasks."""
    from app.tasks.calendar_auto import process_recurring_events

    # from app.tasks.dcsbot_import import import_dcsbot_stats

    scheduler.add_job(process_recurring_events, "interval", hours=1, id="calendar_auto")
    # scheduler.add_job(import_dcsbot_stats, "interval", minutes=2, id="dcsbot_import")

    scheduler.start()
