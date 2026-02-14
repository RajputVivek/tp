from apscheduler.schedulers.blocking import BlockingScheduler
from backend.app.services.daily_runner import run_daily_scan


def start_scheduler():
    scheduler = BlockingScheduler()

    # Run every 4 hours
    scheduler.add_job(
        run_daily_scan,
        trigger="interval",
        hours=4,
        max_instances=1,   # prevent overlapping runs
        coalesce=True,     # if server was down, run once
    )

    print("⏳ Scheduler started (runs every 4 hours)")
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()
