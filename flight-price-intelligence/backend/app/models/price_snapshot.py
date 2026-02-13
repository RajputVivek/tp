from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from datetime import datetime
from backend.app.db.base import Base

class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("routes.id"))
    departure_date = Column(Date, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    airline = Column(String, nullable=True)
    stops = Column(Integer, default=0)
    collected_at = Column(DateTime, default=datetime.utcnow)
