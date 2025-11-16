"""Add indexes for performance

Revision ID: 002_add_indexes
Revises: 001_initial
Create Date: 2025-11-16 12:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_indexes'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Index on UsageLog.customer_id for faster filtering
    op.create_index('ix_usagelog_customer_id', 'usagelog', ['customer_id'])
    
    # Index on UsageLog.created_at for time-range queries and cleanup
    op.create_index('ix_usagelog_created_at', 'usagelog', ['created_at'])
    
    # Index on UsageLog.api_key_id for looking up logs by API key
    op.create_index('ix_usagelog_api_key_id', 'usagelog', ['api_key_id'])
    
    # Index on APIKey.customer_id for finding all keys for a customer
    op.create_index('ix_apikey_customer_id', 'apikey', ['customer_id'])
    
    # Unique index on Policy.key to ensure unique policy keys
    op.create_index('ix_policy_key', 'policy', ['key'], unique=True)
    
    # Index on CustomerPolicy for efficient lookups
    op.create_index('ix_customerpolicy_customer_id', 'customerpolicy', ['customer_id'])
    op.create_index('ix_customerpolicy_policy_id', 'customerpolicy', ['policy_id'])


def downgrade() -> None:
    op.drop_index('ix_customerpolicy_policy_id', table_name='customerpolicy')
    op.drop_index('ix_customerpolicy_customer_id', table_name='customerpolicy')
    op.drop_index('ix_policy_key', table_name='policy')
    op.drop_index('ix_apikey_customer_id', table_name='apikey')
    op.drop_index('ix_usagelog_api_key_id', table_name='usagelog')
    op.drop_index('ix_usagelog_created_at', table_name='usagelog')
    op.drop_index('ix_usagelog_customer_id', table_name='usagelog')
