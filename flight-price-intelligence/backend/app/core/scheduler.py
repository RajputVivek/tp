from apscheduler.schedulers.blocking import BlockingScheduler
from backend.app.services.daily_runner import run_daily_scan


def start_scheduler():
    scheduler = BlockingScheduler()

    # Run once per day at 9 AM
    scheduler.add_job(
        run_daily_scan,
        trigger="cron",
        hour=9,
        minute=0,
    )

    print("⏳ Scheduler started (daily scan at 09:00)")
    scheduler.start()


if __name__ == "__main__":
    start_scheduler()
