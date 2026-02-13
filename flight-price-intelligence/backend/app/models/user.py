from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from backend.app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    home_airport = Column(String, nullable=True)
    discount_threshold = Column(Integer, default=40)
    alerts_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
