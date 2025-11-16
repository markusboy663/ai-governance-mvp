"""Initial models

Revision ID: 001_initial
Revises: 
Create Date: 2025-11-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customer table
    op.create_table('customer',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    # Create api_key table
    op.create_table('apikey',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('customer_id', sa.String(length=36), nullable=False),
    sa.Column('api_key_hash', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create policy table
    op.create_table('policy',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('key', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('default_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )

    # Create customerpolicy table
    op.create_table('customerpolicy',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('customer_id', sa.String(length=36), nullable=False),
    sa.Column('policy_id', sa.String(length=36), nullable=False),
    sa.Column('value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.ForeignKeyConstraint(['policy_id'], ['policy.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # Create usagelog table
    op.create_table('usagelog',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('customer_id', sa.String(length=36), nullable=True),
    sa.Column('api_key_id', sa.String(length=36), nullable=True),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('operation', sa.String(), nullable=False),
    sa.Column('meta', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('risk_score', sa.Integer(), nullable=True),
    sa.Column('allowed', sa.Boolean(), nullable=True),
    sa.Column('reason', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(['api_key_id'], ['apikey.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('usagelog')
    op.drop_table('customerpolicy')
    op.drop_table('policy')
    op.drop_table('apikey')
    op.drop_table('customer')
