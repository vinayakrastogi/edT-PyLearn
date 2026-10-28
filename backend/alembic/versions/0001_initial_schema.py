"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # Lesson progress table
    op.create_table(
        "lesson_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.String(), nullable=False),
        sa.Column("lesson_id", sa.String(), nullable=False),
        sa.Column(
            "viewed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_complete", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lesson_progress_id"), "lesson_progress", ["id"], unique=False)
    op.create_index(op.f("ix_lesson_progress_lesson_id"), "lesson_progress", ["lesson_id"], unique=False)
    op.create_index(op.f("ix_lesson_progress_module_id"), "lesson_progress", ["module_id"], unique=False)
    op.create_index(op.f("ix_lesson_progress_user_id"), "lesson_progress", ["user_id"], unique=False)

    # Quiz attempts table
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.String(), nullable=False),
        sa.Column("quiz_id", sa.String(), nullable=False),
        sa.Column("answers", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("per_question_results", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "attempted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_quiz_attempts_id"), "quiz_attempts", ["id"], unique=False)
    op.create_index(op.f("ix_quiz_attempts_module_id"), "quiz_attempts", ["module_id"], unique=False)
    op.create_index(op.f("ix_quiz_attempts_quiz_id"), "quiz_attempts", ["quiz_id"], unique=False)
    op.create_index(op.f("ix_quiz_attempts_user_id"), "quiz_attempts", ["user_id"], unique=False)

    # Code submissions table
    op.create_table(
        "code_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.String(), nullable=False),
        sa.Column("problem_id", sa.String(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PASS", "FAIL", "ERROR", "TIMEOUT", name="submissionstatus"),
            nullable=False,
        ),
        sa.Column("test_results", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("stdout", sa.Text(), nullable=True),
        sa.Column("stderr", sa.Text(), nullable=True),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_code_submissions_id"), "code_submissions", ["id"], unique=False)
    op.create_index(op.f("ix_code_submissions_module_id"), "code_submissions", ["module_id"], unique=False)
    op.create_index(op.f("ix_code_submissions_problem_id"), "code_submissions", ["problem_id"], unique=False)
    op.create_index(op.f("ix_code_submissions_user_id"), "code_submissions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_code_submissions_user_id"), table_name="code_submissions")
    op.drop_index(op.f("ix_code_submissions_problem_id"), table_name="code_submissions")
    op.drop_index(op.f("ix_code_submissions_module_id"), table_name="code_submissions")
    op.drop_index(op.f("ix_code_submissions_id"), table_name="code_submissions")
    op.drop_table("code_submissions")
    op.execute("DROP TYPE IF EXISTS submissionstatus")

    op.drop_index(op.f("ix_quiz_attempts_user_id"), table_name="quiz_attempts")
    op.drop_index(op.f("ix_quiz_attempts_quiz_id"), table_name="quiz_attempts")
    op.drop_index(op.f("ix_quiz_attempts_module_id"), table_name="quiz_attempts")
    op.drop_index(op.f("ix_quiz_attempts_id"), table_name="quiz_attempts")
    op.drop_table("quiz_attempts")

    op.drop_index(op.f("ix_lesson_progress_user_id"), table_name="lesson_progress")
    op.drop_index(op.f("ix_lesson_progress_module_id"), table_name="lesson_progress")
    op.drop_index(op.f("ix_lesson_progress_lesson_id"), table_name="lesson_progress")
    op.drop_index(op.f("ix_lesson_progress_id"), table_name="lesson_progress")
    op.drop_table("lesson_progress")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
