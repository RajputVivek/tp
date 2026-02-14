from datetime import date

from backend.app.main import init_db
from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.route import Route

from backend.app.services.flight_api.client import AmadeusClient
from backend.app.services.alert_dispatcher import send_telegram_alert
from backend.app.services.date_agnostic_scanner import scan_best_date


def run_daily_scan():
    print("⏰ Running daily flight scan (date-agnostic)...")

    # Ensure DB & tables exist
    init_db()
    db = SessionLocal()

    users = db.query(User).filter(User.alerts_enabled == True).all()
    if not users:
        print("ℹ️ No active users found")
        return

    # Initialize Amadeus once (safe)
    try:
        AmadeusClient()
    except RuntimeError as e:
        print(f"❌ {e}")
        return

    for user in users:
        if not user.home_airport:
            continue

        # MVP destination (will expand later / anywhere mode)
        destination = "BKK"

        # Ensure route exists
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

        # 🔥 DATE-AGNOSTIC SCAN (next 90 days)
        result = scan_best_date(
            db=db,
            origin=user.home_airport,
            destination=destination,
            threshold=user.discount_threshold,
        )

        if not result:
            continue

        # Build alert message
        message = (
            "🔥 INSANE FLIGHT DEAL (FLEXIBLE DATES)\n\n"
            f"✈️ {user.home_airport} → {destination}\n"
            f"📅 Best date: {result['departure_date']}\n"
            f"💰 ₹{result['price']} (↓ {result['discount']}%)\n"
            f"🧠 Confidence: {result['confidence_label']}\n\n"
            f"💡 Why this is a deal:\n{result['explanation']}\n\n"
            "⏳ Likely to disappear soon"
        )

        send_telegram_alert(
            db=db,
            user_id=user.id,
            route_id=route.id,
            departure_date=result["departure_date"],
            price=result["price"],
            discount_percent=result["discount"],
            telegram_id=user.telegram_id,
            message=message,
        )

    print("✅ Date-agnostic daily scan completed")
