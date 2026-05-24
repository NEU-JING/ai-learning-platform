"""v3 user profile and learning paths

Revision ID: a1b2c3d4e5f6
Revises: 777e4f62342d
Create Date: 2026-05-22 07:50:00.000000

Adds V3 PRD multi-path learning and user profile system:
  - user_settings: per-user profile / learning path preferences
  - user_skill_scores: multi-dimensional skill radar (0-100)
  - user_achievements: badges & achievements
  - learning_paths: learning path definitions (ai_expert/engineer/practitioner/manager)
  - learning_path_modules: path-course many-to-many bridge
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "777e4f62342d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── user_settings ──────────────────────────────────────────────────────────
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("learning_path", sa.String(length=50), nullable=True),
        sa.Column("background_language", sa.String(length=50), nullable=True),
        sa.Column("background_industry", sa.String(length=50), nullable=True),
        sa.Column("ai_experience_level", sa.String(length=20), nullable=True),
        sa.Column("assessment_completed", sa.Boolean(), nullable=True),
        sa.Column("assessment_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_settings_id"), "user_settings", ["id"], unique=False)
    op.create_index(op.f("ix_user_settings_user_id"), "user_settings", ["user_id"], unique=True)

    # ── user_skill_scores ──────────────────────────────────────────────────────
    op.create_table(
        "user_skill_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("dimension", sa.String(length=30), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "dimension", name="uq_user_skill_dimension"),
    )
    op.create_index(op.f("ix_user_skill_scores_id"), "user_skill_scores", ["id"], unique=False)
    op.create_index(
        op.f("ix_user_skill_scores_user_id"), "user_skill_scores", ["user_id"], unique=False
    )

    # ── user_achievements ──────────────────────────────────────────────────────
    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("achievement_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("earned_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "achievement_type", name="uq_user_achievement_type"),
    )
    op.create_index(op.f("ix_user_achievements_id"), "user_achievements", ["id"], unique=False)
    op.create_index(
        op.f("ix_user_achievements_user_id"), "user_achievements", ["user_id"], unique=False
    )

    # ── learning_paths ─────────────────────────────────────────────────────────
    op.create_table(
        "learning_paths",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path_id", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("subtitle", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("target_role", sa.String(length=100), nullable=False),
        sa.Column("estimated_weeks", sa.Integer(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("path_id"),
    )
    op.create_index(op.f("ix_learning_paths_id"), "learning_paths", ["id"], unique=False)
    op.create_index(op.f("ix_learning_paths_path_id"), "learning_paths", ["path_id"], unique=True)

    # ── learning_path_modules ──────────────────────────────────────────────────
    op.create_table(
        "learning_path_modules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("path_id", sa.String(length=30), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("requirement", sa.String(length=20), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["path_id"], ["learning_paths.path_id"]),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("path_id", "course_id", name="uq_path_course"),
    )
    op.create_index(
        op.f("ix_learning_path_modules_id"), "learning_path_modules", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_learning_path_modules_path_id"),
        "learning_path_modules",
        ["path_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_path_modules_course_id"),
        "learning_path_modules",
        ["course_id"],
        unique=False,
    )


def downgrade() -> None:
    # ── learning_path_modules ──────────────────────────────────────────────────
    op.drop_index(op.f("ix_learning_path_modules_course_id"), table_name="learning_path_modules")
    op.drop_index(op.f("ix_learning_path_modules_path_id"), table_name="learning_path_modules")
    op.drop_index(op.f("ix_learning_path_modules_id"), table_name="learning_path_modules")
    op.drop_table("learning_path_modules")

    # ── learning_paths ─────────────────────────────────────────────────────────
    op.drop_index(op.f("ix_learning_paths_path_id"), table_name="learning_paths")
    op.drop_index(op.f("ix_learning_paths_id"), table_name="learning_paths")
    op.drop_table("learning_paths")

    # ── user_achievements ──────────────────────────────────────────────────────
    op.drop_index(op.f("ix_user_achievements_user_id"), table_name="user_achievements")
    op.drop_index(op.f("ix_user_achievements_id"), table_name="user_achievements")
    op.drop_table("user_achievements")

    # ── user_skill_scores ──────────────────────────────────────────────────────
    op.drop_index(op.f("ix_user_skill_scores_user_id"), table_name="user_skill_scores")
    op.drop_index(op.f("ix_user_skill_scores_id"), table_name="user_skill_scores")
    op.drop_table("user_skill_scores")

    # ── user_settings ──────────────────────────────────────────────────────────
    op.drop_index(op.f("ix_user_settings_user_id"), table_name="user_settings")
    op.drop_index(op.f("ix_user_settings_id"), table_name="user_settings")
    op.drop_table("user_settings")
