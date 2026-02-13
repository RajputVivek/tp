from sqlalchemy import Column, Integer, String, Boolean
from backend.app.db.base import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    origin_airport = Column(String, nullable=False)
    destination_airport = Column(String, nullable=False)
    active = Column(Boolean, default=True)
