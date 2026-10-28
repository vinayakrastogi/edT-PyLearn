"""add_gamification

XP ledger, per-learner gamification profile (cached XP, streak freezes, daily goal, leaderboard
opt-in) and earned badges. See GAMIFICATION.md.

Revision ID: d7f1a2b3c4e5
Revises: c5d8e9f12a34
Create Date: 2026-10-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd7f1a2b3c4e5'
down_revision = 'c5d8e9f12a34'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'gamification_profiles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('xp_total', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('streak_freezes', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('last_active_date', sa.Date(), nullable=True),
        sa.Column('daily_goal', sa.Integer(), nullable=False, server_default=sa.text('30')),
        sa.Column('daily_xp', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('daily_xp_date', sa.Date(), nullable=True),
        sa.Column('show_on_leaderboard', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id'),
    )

    op.create_table(
        'xp_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(length=32), nullable=False),
        sa.Column('ref_key', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('local_date', sa.Date(), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'kind', 'ref_key', name='uq_xp_events_user_kind_ref'),
    )
    op.create_index('ix_xp_events_user_created', 'xp_events', ['user_id', 'created_at'])

    op.create_table(
        'user_badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('badge_id', sa.String(length=64), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'badge_id', name='uq_user_badges_user_badge'),
    )


def downgrade():
    op.drop_table('user_badges')
    op.drop_index('ix_xp_events_user_created', table_name='xp_events')
    op.drop_table('xp_events')
    op.drop_table('gamification_profiles')
