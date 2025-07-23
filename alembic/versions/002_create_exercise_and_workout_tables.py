"""create exercise and workout tables

Revision ID: 002
Revises: 001
Create Date: 2024-03-13 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from psycopg2.errors import DuplicateObject
from sqlalchemy.exc import ProgrammingError

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Crear enum de grupos musculares
    muscle_group_values = ('Pecho', 'Espalda', 'Hombros', 'Bíceps', 'Tríceps', 'Piernas', 'Abdominales', 'Cardio')
    
    # Intentar crear el enum, si ya existe continuar
    try:
        muscle_group_enum = ENUM(*muscle_group_values, name='muscle_group', create_type=False)
        muscle_group_enum.create(op.get_bind(), checkfirst=True)
    except (ProgrammingError, DuplicateObject):
        pass

    # Crear tabla de ejercicios
    op.create_table(
        'exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('muscle_group', ENUM(*muscle_group_values, name='muscle_group', create_type=False), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exercises_id'), 'exercises', ['id'], unique=False)

    # Crear tabla de entrenamientos
    op.create_table(
        'workouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workouts_id'), 'workouts', ['id'], unique=False)

    # Crear tabla de ejercicios en entrenamientos
    op.create_table(
        'workout_exercises',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workout_id', sa.Integer(), nullable=False),
        sa.Column('exercise_id', sa.Integer(), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
        sa.ForeignKeyConstraint(['workout_id'], ['workouts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_exercises_id'), 'workout_exercises', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_workout_exercises_id'), table_name='workout_exercises')
    op.drop_table('workout_exercises')
    op.drop_index(op.f('ix_workouts_id'), table_name='workouts')
    op.drop_table('workouts')
    op.drop_index(op.f('ix_exercises_id'), table_name='exercises')
    op.drop_table('exercises')
    
    # Intentar eliminar el enum
    try:
        ENUM(name='muscle_group').drop(op.get_bind(), checkfirst=True)
    except (ProgrammingError, DuplicateObject):
        pass 