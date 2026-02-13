from datetime import date

from backend.app.main import init_db
from backend.app.db.session import SessionLocal
from backend.app.models.route import Route
from backend.app.models.user import User
from backend.app.services.deal_detector import (
    is_valid_deal,
    calculate_discount,
)
from backend.app.services.alert_dispatcher import send_telegram_alert


def run_test():
    # 1️⃣ Ensure DB & tables exist
    init_db()

    db = SessionLocal()

    # 2️⃣ Fetch first user (created via /start)
    user = db.query(User).first()
    if not user:
        print("❌ No user found. Run /start in Telegram first.")
        return

    if not user.home_airport:
        print("❌ User has no home airport. Use /set_home DEL")
        return

    # 3️⃣ Create or reuse route
    route = (
        db.query(Route)
        .filter(
            Route.origin_airport == user.home_airport,
            Route.destination_airport == "BKK",
        )
        .first()
    )

    if not route:
        route = Route(
            origin_airport=user.home_airport,
            destination_airport="BKK",
            active=True,
        )
        db.add(route)
        db.commit()

    # 4️⃣ Fake pricing data
    current_price = 18000
    historical_avg = 45000
    recent_median = 42000

    # 5️⃣ Deal detection
    if not is_valid_deal(
        current_price=current_price,
        historical_avg=historical_avg,
        recent_median=recent_median,
        threshold=user.discount_threshold,
    ):
        print("❌ Not a valid deal based on thresholds")
        return

    discount = calculate_discount(current_price, historical_avg)

    # 6️⃣ Alert message
    message = (
        "🔥 INSANE FLIGHT DEAL\n\n"
        f"✈️ {route.origin_airport} → {route.destination_airport}\n"
        f"💰 ₹{current_price} (↓ {discount}%)\n"
        f"📉 Avg price: ₹{historical_avg}\n\n"
        "⏳ Likely to disappear soon"
    )

    # 7️⃣ Send alert with duplicate prevention
    sent = send_telegram_alert(
        db=db,
        user_id=user.id,
        route_id=route.id,
        departure_date=date.today(),
        price=current_price,
        discount_percent=discount,
        telegram_id=user.telegram_id,
        message=message,
    )

    if sent:
        print("🎉 Alert delivered")
    else:
        print("🚫 Alert already sent earlier")


if __name__ == "__main__":
    run_test()
