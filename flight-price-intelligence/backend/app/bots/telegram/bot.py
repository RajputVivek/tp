from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)
from backend.app.core.config import TELEGRAM_BOT_TOKEN
from backend.app.bots.telegram.commands import start, set_home


def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_home", set_home))

    print("🤖 Telegram bot started")
    app.run_polling()
