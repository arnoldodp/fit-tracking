"""create foods and meal_logs tables

Revision ID: 004
Revises: 003
Create Date: 2024-03-13 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'foods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('calories', sa.Float(), nullable=False),
        sa.Column('protein', sa.Float(), nullable=True),
        sa.Column('carbs', sa.Float(), nullable=True),
        sa.Column('fat', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_foods_id'), 'foods', ['id'], unique=False)

    op.create_table(
        'meal_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('food_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['food_id'], ['foods.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_logs_id'), 'meal_logs', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_meal_logs_id'), table_name='meal_logs')
    op.drop_table('meal_logs')
    op.drop_index(op.f('ix_foods_id'), table_name='foods')
    op.drop_table('foods') 