"""Initial migration

Revision ID: 59bef620f990
Revises:
Create Date: 2026-03-07 10:02:10.168705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59bef620f990'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_categories_name', 'categories', ['name'])
    op.create_index('ix_categories_parent_id', 'categories', ['parent_id'])

    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image', sa.String(length=500), nullable=True),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_title', 'products', ['title'])
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
    op.create_index('ix_products_price', 'products', ['price'])
    op.create_index('ix_products_category_id', 'products', ['category_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_products_category_id', table_name='products')
    op.drop_index('ix_products_price', table_name='products')
    op.drop_index('ix_products_sku', table_name='products')
    op.drop_index('ix_products_title', table_name='products')
    op.drop_index('ix_products_id', table_name='products')
    op.drop_table('products')
    op.drop_index('ix_categories_parent_id', table_name='categories')
    op.drop_index('ix_categories_name', table_name='categories')
    op.drop_table('categories')