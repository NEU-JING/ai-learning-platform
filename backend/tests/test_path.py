"""Tests for Path module — T1: Path tables and seed data."""

from sqlalchemy import inspect

from app.models import PathTemplate


class TestPathTablesExist:
    """T1: Verify path module database tables exist."""

    def test_path_templates_table_exists(self, test_db):
        """AC1: path_templates table should exist."""

        inspector = inspect(test_db.bind)
        assert "path_templates" in inspector.get_table_names()

    def test_user_paths_table_exists(self, test_db):
        """AC1: user_paths table should exist."""

        inspector = inspect(test_db.bind)
        assert "user_paths" in inspector.get_table_names()

    def test_path_courses_table_exists(self, test_db):
        """AC1: path_courses table should exist."""

        inspector = inspect(test_db.bind)
        assert "path_courses" in inspector.get_table_names()

    def test_path_milestones_table_exists(self, test_db):
        """AC1: path_milestones table should exist."""

        inspector = inspect(test_db.bind)
        assert "path_milestones" in inspector.get_table_names()

    def test_skill_gap_diagnoses_table_exists(self, test_db):
        """AC1: skill_gap_diagnoses table should exist."""

        inspector = inspect(test_db.bind)
        assert "skill_gap_diagnoses" in inspector.get_table_names()


class TestPathSeedData:
    """T1: Verify 4 path templates seed data exist."""

    def test_ai_researcher_path_template_exists(self, test_db):
        """AC3: AI专家路径模板应该存在."""
        template = test_db.query(PathTemplate).filter_by(slug="ai-researcher").first()
        assert template is not None
        assert template.name == "AI专家路径"
        assert template.target_role == "AI专家"
        assert template.duration_weeks == 20

    def test_ai_engineer_path_template_exists(self, test_db):
        """AC3: AI工程师路径模板应该存在."""
        template = test_db.query(PathTemplate).filter_by(slug="ai-engineer").first()
        assert template is not None
        assert template.name == "AI工程师路径"
        assert template.target_role == "AI工程师"
        assert template.duration_weeks == 14

    def test_ai_practitioner_path_template_exists(self, test_db):
        """AC3: AI应用者路径模板应该存在."""
        template = test_db.query(PathTemplate).filter_by(slug="ai-applier").first()
        assert template is not None
        assert template.name == "AI应用者路径"
        assert template.target_role == "AI应用者"
        assert template.duration_weeks == 8

    def test_ai_manager_path_template_exists(self, test_db):
        """AC3: AI管理者路径模板应该存在."""
        template = test_db.query(PathTemplate).filter_by(slug="ai-manager").first()
        assert template is not None
        assert template.name == "AI管理者路径"
        assert template.target_role == "AI管理者"
        assert template.duration_weeks == 6

    def test_path_templates_count(self, test_db):
        """AC3: 应该正好有4个路径模板."""
        count = test_db.query(PathTemplate).count()
        assert count == 4

    def test_path_templates_have_required_courses(self, test_db):
        """AC3: 路径模板应该有required_courses字段."""
        templates = test_db.query(PathTemplate).all()
        for template in templates:
            assert isinstance(template.required_courses, list)
            assert len(template.required_courses) > 0

    def test_path_templates_have_description(self, test_db):
        """AC3: 路径模板应该有描述."""
        templates = test_db.query(PathTemplate).all()
        for template in templates:
            assert template.description is not None
            assert len(template.description) > 0
