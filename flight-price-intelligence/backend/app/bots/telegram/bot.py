from backend.app.main import init_db
from telegram.ext import ApplicationBuilder, CommandHandler
from backend.app.core.config import TELEGRAM_BOT_TOKEN
from backend.app.bots.telegram.commands import start, set_home
from backend.app.bots.telegram.commands import anywhere

application.add_handler(CommandHandler("anywhere", anywhere))



def start_bot():
    print("🗄️ Initializing database...")
    init_db()

    print("🤖 Starting Telegram bot...")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_home", set_home))

    print("🤖 Telegram bot started")
    app.run_polling()


if __name__ == "__main__":
    start_bot()
