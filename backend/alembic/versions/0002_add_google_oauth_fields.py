"""add google oauth fields

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alter hashed_password to be nullable
    op.alter_column("users", "hashed_password", existing_type=sa.String(), nullable=True)
    
    # Add google_id and avatar_url
    op.add_column("users", sa.Column("google_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(), nullable=True))
    
    # Add unique index for google_id
    op.create_index(op.f("ix_users_google_id"), "users", ["google_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_google_id"), table_name="users")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "google_id")
    op.alter_column("users", "hashed_password", existing_type=sa.String(), nullable=False)
