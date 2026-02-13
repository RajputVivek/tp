import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR}/flightintel.db"
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
