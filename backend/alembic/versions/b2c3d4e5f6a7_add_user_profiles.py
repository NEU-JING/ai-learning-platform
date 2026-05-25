"""add user_profiles table

Revision ID: 001_add_user_profiles
Revises: a1b2c3d4e5f6
Create Date: 2026-05-24

Adds user_profiles table for public profile visibility settings (Task-1).
Each user has at most one record (1:1 with users).
No backfill needed — record absence = profile never enabled (BR1).
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("show_basic_info", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("show_skill_radar", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("show_labs", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("show_certificates", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("display_name", sa.String(length=50), nullable=True),
        sa.Column("bio", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_profiles_id"), "user_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_user_profiles_user_id"), "user_profiles", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_profiles_user_id"), table_name="user_profiles")
    op.drop_index(op.f("ix_user_profiles_id"), table_name="user_profiles")
    op.drop_table("user_profiles")
