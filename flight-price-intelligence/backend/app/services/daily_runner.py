from datetime import date

from backend.app.main import init_db
from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.route import Route
from backend.app.services.flight_api.client import AmadeusClient
from backend.app.services.deal_detector import (
    is_valid_deal,
    calculate_discount,
)
from backend.app.services.alert_dispatcher import send_telegram_alert


def run_daily_scan():
    print("⏰ Running daily flight scan...")

    init_db()
    db = SessionLocal()

    users = db.query(User).filter(User.alerts_enabled == True).all()
    if not users:
        print("ℹ️ No active users found")
        return

    try:
        amadeus = AmadeusClient()
    except RuntimeError as e:
        print(f"❌ {e}")
        return

    for user in users:
        if not user.home_airport:
            continue

        destination = "BKK"

        route = (
            db.query(Route)
            .filter(
                Route.origin_airport == user.home_airport,
                Route.destination_airport == destination,
            )
            .first()
        )

        if not route:
            route = Route(
                origin_airport=user.home_airport,
                destination_airport=destination,
                active=True,
            )
            db.add(route)
            db.commit()

        offer = amadeus.get_cheapest_offer(
            origin=user.home_airport,
            destination=destination,
            departure_date=date.today().isoformat(),
        )

        if not offer:
            continue

        current_price = offer["price"]

        # Temporary heuristics
        historical_avg = current_price * 1.6
        recent_median = current_price * 1.4

        if not is_valid_deal(
            current_price=current_price,
            historical_avg=historical_avg,
            recent_median=recent_median,
            threshold=user.discount_threshold,
        ):
            continue

        discount = calculate_discount(current_price, historical_avg)

        message = (
            "🔥 INSANE FLIGHT DEAL\n\n"
            f"✈️ {route.origin_airport} → {route.destination_airport}\n"
            f"💰 ₹{current_price} (↓ {discount}%)\n"
            f"📉 Avg price: ₹{historical_avg}\n\n"
            "⏳ Likely to disappear soon"
        )

        send_telegram_alert(
            db=db,
            user_id=user.id,
            route_id=route.id,
            departure_date=date.today(),
            price=current_price,
            discount_percent=discount,
            telegram_id=user.telegram_id,
            message=message,
        )

    print("✅ Daily scan completed")
