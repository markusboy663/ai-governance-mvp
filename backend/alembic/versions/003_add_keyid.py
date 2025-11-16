"""Add key_id column for O(1) authentication lookup

This migration adds:
- key_id column (UUID) to api_keys table
- UNIQUE index on key_id for fast lookup
- Replaces full table-scan auth with indexed lookup

Token format: <key_id>.<secret>
- key_id used for index-based lookup (O(1))
- secret hashed and verified with bcrypt

Revision ID: 003_add_keyid
Revises: 002_add_indexes
Create Date: 2025-11-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '003_add_keyid'
down_revision = '002_add_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add key_id column with default UUID for existing rows
    op.add_column(
        'apikey',
        sa.Column(
            'key_id',
            sa.String(length=36),
            nullable=False,
            server_default=sa.func.gen_random_uuid(),  # generates UUID for existing rows
            unique=True
        )
    )
    
    # Create index on key_id for O(1) lookup
    op.create_index('ix_apikey_key_id', 'apikey', ['key_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_apikey_key_id', table_name='apikey')
    op.drop_column('apikey', 'key_id')
