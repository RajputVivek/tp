import time
from datetime import datetime, timedelta
import pytz

from backend.app.db.session import SessionLocal
from backend.app.models.user import User

from backend.app.services.date_agnostic_scanner import scan_best_date
from backend.app.services.alert_dispatcher import send_telegram_message


IST = pytz.timezone("Asia/Kolkata")


def is_8am_ist(now_ist: datetime) -> bool:
    return now_ist.hour == 8 and now_ist.minute == 0


def run_daily_broadcast():
    db = SessionLocal()
    users = db.query(User).filter(User.alerts_enabled == True).all()

    if not users:
        return

    for user in users:
        if not user.telegram_id or not user.home_airport:
            continue

        destinations = ["BKK", "SIN", "DXB"]
        results = []

        for dest in destinations:
            result = scan_best_date(
                db=db,
                origin=user.home_airport,
                destination=dest,
                threshold=user.discount_threshold,
            )
            if result:
                results.append(result)

        if not results:
            continue  # 🔕 silent if no good deals

        message = "📅 *Today’s Best Flight Deals*\n\n"

        for r in results[:3]:
            message += (
                f"✈️ {user.home_airport} → {r['destination']}\n"
                f"💰 ₹{r['price']} (↓ {r['discount']}%)\n"
                f"🧠 {r['confidence_label']} confidence\n"
                f"📆 Best date: {r['departure_date']}\n\n"
            )

        send_telegram_message(
            telegram_id=user.telegram_id,
            message=message,
        )


def scheduler_loop():
    print("⏰ Scheduler started (IST-based)")

    last_run_date = None

    while True:
        now_ist = datetime.now(IST)

        if is_8am_ist(now_ist):
            today = now_ist.date()

            if last_run_date != today:
                print("📢 Running 8 AM IST daily broadcast")
                run_daily_broadcast()
                last_run_date = today

        time.sleep(60)  # check every minute


if __name__ == "__main__":
    scheduler_loop()
