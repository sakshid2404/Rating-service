from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, index=True)
    customer_id = Column(Integer, index=True)
    rating = Column(Integer, nullable=False)
    review = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
