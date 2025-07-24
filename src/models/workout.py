from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    name = Column(String, nullable=False)
    notes = Column(String)
    duration = Column(Integer)  # en minutos

    # Relaciones
    exercises = relationship("WorkoutExercise", back_populates="workout")
    user = relationship("User", backref="workouts")

class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float)  # en kilogramos
    notes = Column(String)

    # Relaciones
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise") 