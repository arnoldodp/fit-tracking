from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text
from database.database import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # 'weight', 'exercise', 'nutrition', etc.
    target_value = Column(Float)  # valor numérico objetivo
    target_unit = Column(String)  # kg, reps, kcal, etc.
    start_date = Column(Date, nullable=False)
    target_date = Column(Date)
    completed = Column(Boolean, default=False)
    completed_date = Column(Date) 