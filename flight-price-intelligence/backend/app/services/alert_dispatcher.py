import asyncio
from telegram import Bot
from sqlalchemy.orm import Session

from backend.app.core.config import TELEGRAM_BOT_TOKEN
from backend.app.models.alert import Alert


async def _send_async(telegram_id: str, message: str):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=telegram_id, text=message)


def send_telegram_alert(
    db: Session,
    user_id: int,
    route_id: int,
    departure_date,
    price: float,
    discount_percent: float,
    telegram_id: str,
    message: str,
):
    existing = (
        db.query(Alert)
        .filter(
            Alert.user_id == user_id,
            Alert.route_id == route_id,
            Alert.departure_date == departure_date,
        )
        .first()
    )

    if existing:
        print("⏭️ Duplicate alert skipped")
        return False

    asyncio.run(_send_async(telegram_id, message))

    alert = Alert(
        user_id=user_id,
        route_id=route_id,
        departure_date=departure_date,
        price=price,
        discount_percent=discount_percent,
    )

    db.add(alert)
    db.commit()

    print("✅ Alert sent & stored")
    return True
