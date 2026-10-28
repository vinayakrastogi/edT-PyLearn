"""add_roles_and_classroom_system

Revision ID: c5d8e9f12a34
Revises: b502a5f3ef56
Create Date: 2025-01-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c5d8e9f12a34'
down_revision = 'b502a5f3ef56'
branch_labels = None
depends_on = None


def upgrade():
    # Add role column to users table
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='student'))
    
    # Create classroom_modules table
    op.create_table(
        'classroom_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=6), nullable=False),
        sa.Column('module_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_test', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create enrollments table
    op.create_table(
        'enrollments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('classroom_module_id', sa.Integer(), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['classroom_module_id'], ['classroom_modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_classroom_modules_creator_id', 'classroom_modules', ['creator_id'])
    op.create_index('ix_enrollments_student_id', 'enrollments', ['student_id'])
    op.create_index('ix_enrollments_classroom_module_id', 'enrollments', ['classroom_module_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_enrollments_classroom_module_id', table_name='enrollments')
    op.drop_index('ix_enrollments_student_id', table_name='enrollments')
    op.drop_index('ix_classroom_modules_creator_id', table_name='classroom_modules')
    
    # Drop tables
    op.drop_table('enrollments')
    op.drop_table('classroom_modules')
    
    # Remove role column
    op.drop_column('users', 'role')
