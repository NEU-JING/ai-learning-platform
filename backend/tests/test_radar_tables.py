"""Test Radar module database tables — T6.

Tests the existence and structure of Radar module tables:
- skill_dimensions: 技能维度定义表
- user_skill_scores: 用户技能分数表 (已有，保持向后兼容)
- skill_events: 技能事件日志表

AC覆盖:
- AC7: 10维技能模型落地
- AC9: 自动汇总多源数据
"""

import pytest
from sqlalchemy import inspect



class TestRadarTablesExist:
    """RED phase test: Verify radar tables are created in database."""

    def test_skill_dimensions_table_exists(self, test_db):
        """AC7: skill_dimensions table should exist with required columns."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "skill_dimensions" in tables, "skill_dimensions table should exist"

        columns = {col["name"] for col in inspector.get_columns("skill_dimensions")}
        required_columns = {
            "id",
            "slug",
            "name",
            "name_en",
            "description",
            "category",
            "weight_formula",
            "max_score",
            "created_at",
        }
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_user_skill_scores_table_exists(self, test_db):
        """AC7, AC9: user_skill_scores table should exist."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "user_skill_scores" in tables, "user_skill_scores table should exist"

        # 验证基本字段存在（保持向后兼容）
        columns = {col["name"] for col in inspector.get_columns("user_skill_scores")}
        required_columns = {"id", "user_id", "dimension", "score", "created_at", "updated_at"}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_skill_events_table_exists(self, test_db):
        """AC9: skill_events table should exist with required columns."""
        inspector = inspect(test_db.bind)
        tables = inspector.get_table_names()
        assert "skill_events" in tables, "skill_events table should exist"

        columns = {col["name"] for col in inspector.get_columns("skill_events")}
        required_columns = {
            "id",
            "user_id",
            "event_type",
            "dimension_id",
            "score_impact",
            "event_metadata",
            "created_at",
        }
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_skill_dimensions_seed_data(self, test_db):
        """AC7: 10 skill dimensions should be seeded in database."""
        from app.models.radar import SkillDimension

        dimensions = test_db.query(SkillDimension).all()
        assert len(dimensions) >= 10, f"Expected at least 10 dimensions, got {len(dimensions)}"

        # Check required dimensions exist
        slugs = {d.slug for d in dimensions}
        required_slugs = {
            "coding_thinking",
            "algorithm_understanding",
            "ai_collaboration",
            "problem_solving",
            "engineering_practice",
            "system_design",
            "research_depth",
            "ai_application",
            "prompt_engineering",
            "data_analysis",
        }
        assert required_slugs.issubset(slugs), f"Missing dimension slugs: {required_slugs - slugs}"

    def test_skill_dimensions_unique_slug(self, test_db):
        """Skill dimensions should have unique slugs."""
        from sqlalchemy.exc import IntegrityError

        from app.models.radar import SkillDimension

        dim = SkillDimension(slug="coding_thinking", name="Test Duplicate", category="hard")
        test_db.add(dim)
        with pytest.raises(IntegrityError):
            test_db.commit()
        test_db.rollback()

    def test_skill_dimensions_categories(self, test_db):
        """AC7: Skill dimensions should have correct categories."""
        from app.models.radar import SkillDimension

        dimensions = test_db.query(SkillDimension).all()
        categories = {d.category for d in dimensions}

        # Should have hard, soft, and specialized categories
        assert "hard" in categories, "Should have hard skill dimensions"
        assert "soft" in categories, "Should have soft skill dimensions"
        assert "specialized" in categories, "Should have specialized dimensions"

    def test_skill_events_foreign_keys(self, test_db):
        """skill_events should have FK to users and skill_dimensions."""
        inspector = inspect(test_db.bind)
        fks = inspector.get_foreign_keys("skill_events")
        fk_names = {fk["referred_table"] for fk in fks}
        assert "users" in fk_names, "Should have FK to users"
        assert "skill_dimensions" in fk_names, "Should have FK to skill_dimensions"

    def test_skill_dimension_model_repr(self, test_db):
        """SkillDimension model should have proper repr."""
        from app.models.radar import SkillDimension

        dim = test_db.query(SkillDimension).first()
        assert dim is not None
        assert "SkillDimension" in repr(dim)
        assert dim.slug in repr(dim)

    def test_skill_event_model_repr(self):
        """SkillEvent model should have proper repr."""
        from app.models.radar import SkillEvent

        event = SkillEvent(user_id=1, event_type="lab_completed")
        assert "SkillEvent" in repr(event)
        assert "lab_completed" in repr(event)
