from sqlalchemy import Column, Integer, String, Text, Enum
from database.database import Base
import enum

class MuscleGroup(enum.Enum):
    Pecho = "Pecho"
    Espalda = "Espalda"
    Hombros = "Hombros"
    Bíceps = "Bíceps"
    Tríceps = "Tríceps"
    Piernas = "Piernas"
    Abdominales = "Abdominales"
    Cardio = "Cardio"

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    muscle_group = Column(Enum(MuscleGroup), nullable=False)
    instructions = Column(Text)
    video_url = Column(String)
    image_url = Column(String) 