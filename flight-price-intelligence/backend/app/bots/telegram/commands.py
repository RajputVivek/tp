from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.route import Route
from backend.app.models.price_snapshot import PriceSnapshot
from backend.app.models.alert import Alert

from backend.app.services.anywhere_scanner import scan_anywhere


async def start(update, context):
    telegram_id = str(update.effective_user.id)
    db = SessionLocal()

    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        user = User(
            telegram_id=telegram_id,
            alerts_enabled=True,
        )
        db.add(user)
        db.commit()

    await update.message.reply_text(
        "👋 Welcome to Flight Price Intelligence!\n\n"
        "I’ll alert you when flights are *insanely cheaper than usual*.\n\n"
        "Commands:\n"
        "/anywhere – find cheap destinations\n"
        "/status – system status\n"
    )


async def anywhere(update, context):
    telegram_id = str(update.effective_user.id)
    db = SessionLocal()

    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user or not user.home_airport:
        await update.message.reply_text(
            "❗ Please set your home airport first using /set_home"
        )
        return

    await update.message.reply_text(
        f"🔍 Searching cheap flights from {user.home_airport} to anywhere..."
    )

    deals = scan_anywhere(
        db=db,
        origin=user.home_airport,
        threshold=user.discount_threshold,
    )

    if not deals:
        await update.message.reply_text(
            "😕 No strong deals right now. Try again later!"
        )
        return

    message = "🔥 TOP DEALS (FLEXIBLE DATES)\n\n"

    for d in deals[:3]:
        message += (
            f"✈️ {user.home_airport} → {d['destination']}\n"
            f"💰 ₹{d['price']} (↓ {d['discount']}%)\n"
            f"🧠 Confidence: {d['confidence_label']}\n\n"
        )

    await update.message.reply_text(message)


async def status(update, context):
    telegram_id = str(update.effective_user.id)
    db = SessionLocal()

    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        await update.message.reply_text(
            "❗ User not found. Please send /start first."
        )
        return

    routes_count = (
        db.query(Route)
        .filter(Route.origin_airport == user.home_airport)
        .count()
    )

    price_points = db.query(PriceSnapshot).count()
    alerts_sent = db.query(Alert).filter(Alert.user_id == user.id).count()

    await update.message.reply_text(
        "📊 *Flight Intelligence Status*\n\n"
        f"👤 Home airport: {user.home_airport or 'Not set'}\n"
        f"🛣 Routes tracked: {routes_count}\n"
        f"📈 Price points collected: {price_points}\n"
        f"🚨 Alerts sent: {alerts_sent}\n\n"
        "🧠 Confidence engine: Active\n"
        "⏱ Scans run automatically every 4 hours",
        parse_mode="Markdown",
    )
