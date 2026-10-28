"""gamification_hardening

Leaderboard index on xp_events(created_at) and the sticky UTC offset (tz_offset, tz_changed_at) on
gamification_profiles that stops the X-TZ-Offset header from being used to forge local dates.

Revision ID: e8a2b3c4d5f6
Revises: d7f1a2b3c4e5
Create Date: 2026-10-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e8a2b3c4d5f6'
down_revision = 'd7f1a2b3c4e5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_xp_events_created', 'xp_events', ['created_at'])
    op.add_column('gamification_profiles', sa.Column('tz_offset', sa.Integer(), nullable=True))
    op.add_column('gamification_profiles', sa.Column('tz_changed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('gamification_profiles', 'tz_changed_at')
    op.drop_column('gamification_profiles', 'tz_offset')
    op.drop_index('ix_xp_events_created', table_name='xp_events')
