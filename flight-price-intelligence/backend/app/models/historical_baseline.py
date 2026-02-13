from sqlalchemy import Column, Integer, String, Float
from backend.app.db.base import Base

class HistoricalBaseline(Base):
    __tablename__ = "historical_baselines"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, nullable=False)
    avg_price = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    season_month = Column(Integer)
    data_source = Column(String)
