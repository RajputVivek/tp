from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.user import User


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)

    db: Session = SessionLocal()

    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()

    await update.message.reply_text(
        "✈️ Welcome!\n\n"
        "I’ll alert you when flights get unusually cheap.\n\n"
        "Set your home airport using:\n"
        "/set_home DEL"
    )


async def set_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /set_home DEL")
        return

    home_airport = context.args[0].upper()
    telegram_id = str(update.effective_user.id)

    db: Session = SessionLocal()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user:
        user.home_airport = home_airport
        db.commit()

        await update.message.reply_text(
            f"✅ Home airport set to {home_airport}"
        )
