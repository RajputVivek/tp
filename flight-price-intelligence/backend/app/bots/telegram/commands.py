import asyncio
from functools import partial

from backend.app.db.session import SessionLocal
from backend.app.models.user import User
from backend.app.models.route import Route
from backend.app.models.price_snapshot import PriceSnapshot
from backend.app.models.alert import Alert

from backend.app.services.anywhere_scanner import scan_anywhere
from backend.app.services.date_agnostic_scanner import scan_best_date


async def start(update, context):
    telegram_id = str(update.effective_user.id)
    db = SessionLocal()

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, alerts_enabled=True)
        db.add(user)
        db.commit()

    await update.message.reply_text(
        "👋 Welcome to Flight Price Intelligence!\n\n"
        "Commands:\n"
        "/anywhere – flexible destinations\n"
        "/today – today’s best deals\n"
        "/status – system status\n"
    )


async def today(update, context):
    telegram_id = str(update.effective_user.id)
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user or not user.home_airport:
        await update.message.reply_text(
            "❗ Please set your home airport using /set_home"
        )
        return

    await update.message.reply_text(
        "📅 Finding today’s best flight deals...\n⏳ Please wait a few seconds."
    )

    # 🔥 DETACH heavy work from handler
    context.application.create_task(
        _run_today_scan(context, telegram_id)
    )


async def _run_today_scan(context, telegram_id: str):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    destinations = ["BKK", "SIN", "DXB"]
    loop = asyncio.get_running_loop()

    results = []

    for dest in destinations:
        result = await loop.run_in_executor(
            None,
            partial(
                scan_best_date,
                db,
                user.home_airport,
                dest,
                user.discount_threshold,
            ),
        )
        if result:
            results.append(result)

    if not results:
        await context.bot.send_message(
            chat_id=telegram_id,
            text="😕 No strong flight deals today.\nTry again tomorrow.",
        )
        return

    message = "📅 *Best Flight Deals Today*\n\n"
    for r in results[:3]:
        message += (
            f"✈️ {user.home_airport} → {r['destination']}\n"
            f"💰 ₹{r['price']} (↓ {r['discount']}%)\n"
            f"🧠 {r['confidence_label']} confidence\n"
            f"📆 Best date: {r['departure_date']}\n\n"
        )

    await context.bot.send_message(
        chat_id=telegram_id,
        text=message,
        parse_mode="Markdown",
    )


async def status(update, context):
    telegram_id = str(update.effective_user.id)
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    routes = db.query(Route).count()
    prices = db.query(PriceSnapshot).count()
    alerts = db.query(Alert).count()

    await update.message.reply_text(
        "📊 *Flight Intelligence Status*\n\n"
        f"👤 Home airport: {user.home_airport or 'Not set'}\n"
        f"🛣 Routes tracked: {routes}\n"
        f"📈 Price points collected: {prices}\n"
        f"🚨 Alerts sent: {alerts}\n\n"
        "🧠 Engine: Active\n"
        "⏱ Scan: Every 4 hours",
        parse_mode="Markdown",
    )
