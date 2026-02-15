from telegram.ext import ApplicationBuilder, CommandHandler

from backend.app.core.config import TELEGRAM_BOT_TOKEN
from backend.app.bots.telegram.commands import (
    start,
    today,
    status,
)


def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("status", status))

    print("🤖 Telegram bot started")
    application.run_polling()


if __name__ == "__main__":
    main()
