from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey
from datetime import datetime
from backend.app.db.base import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    route_id = Column(Integer, ForeignKey("routes.id"))
    departure_date = Column(Date)
    price = Column(Float)
    discount_percent = Column(Float)
    sent_at = Column(DateTime, default=datetime.utcnow)
