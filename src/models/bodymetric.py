from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.database.database import Base

class BodyMetric(Base):
    __tablename__ = "body_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    weight = Column(Float, nullable=False)  # kg
    height = Column(Float, nullable=False)  # cm
    bmi = Column(Float, nullable=True) 