"""Tests for Path module — T1-T10: Path + Radar."""

from sqlalchemy import inspect

from app.models import PathTemplate
from app.schemas.path import DiagnosisRequest
from app.services.path_service import DiagnosisService


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


class TestDiagnosisService:
    """T2: Path入学诊断服务 — 诊断算法测试."""

    def test_diagnose_recommends_correct_template(self):
        """AC1: 根据目标角色推荐正确的路径模板."""
        request = DiagnosisRequest(
            target_role="ai-researcher",
            python_level="beginner",
            experience_years=0,
            math_level="beginner",
            current_job="学生",
            time_commitment="full_time",
            goal_timeline="6_months",
        )
        result = DiagnosisService.diagnose(request)
        assert result.recommended_template == "ai-researcher"
        assert result.estimated_duration_weeks > 0

    def test_diagnose_can_skip_phase1_advanced_python(self):
        """AC2: Python高级+2年经验可跳过Phase1."""
        request = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="advanced",
            experience_years=3,
            math_level="intermediate",
            current_job="后端工程师",
            time_commitment="part_time",
            goal_timeline="6_months",
        )
        result = DiagnosisService.diagnose(request)
        assert result.diagnosis.can_skip_phase1 is True
        assert result.diagnosis.start_from == 2

    def test_diagnose_cannot_skip_phase1_beginner(self):
        """AC2: Python初学者不能跳过Phase1."""
        request = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="beginner",
            experience_years=0,
            math_level="beginner",
            current_job="产品经理",
            time_commitment="part_time",
            goal_timeline="6_months",
        )
        result = DiagnosisService.diagnose(request)
        assert result.diagnosis.can_skip_phase1 is False
        assert result.diagnosis.start_from == 1

    def test_diagnose_weak_areas_math_beginner(self):
        """AC2: 数学初学者检测为薄弱领域."""
        request = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="intermediate",
            experience_years=2,
            math_level="beginner",
            current_job="数据分析师",
            time_commitment="full_time",
            goal_timeline="6_months",
        )
        result = DiagnosisService.diagnose(request)
        assert "linear_algebra" in result.diagnosis.weak_areas

    def test_diagnose_no_weak_areas_math_advanced(self):
        """AC2: 数学高级者没有薄弱领域."""
        request = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="advanced",
            experience_years=5,
            math_level="advanced",
            current_job="算法工程师",
            time_commitment="full_time",
            goal_timeline="6_months",
        )
        result = DiagnosisService.diagnose(request)
        assert len(result.diagnosis.weak_areas) == 0

    def test_diagnose_fast_track_mode(self):
        """AC2: 3个月目标启用fast_track模式."""
        request = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="intermediate",
            experience_years=2,
            math_level="intermediate",
            current_job="前端工程师",
            time_commitment="full_time",
            goal_timeline="3_months",
        )
        result = DiagnosisService.diagnose(request)
        assert result.recommended_mode == "fast_track"
        # Fast track should reduce duration
        assert result.estimated_duration_weeks <= 14

    def test_diagnose_standard_mode(self):
        """AC2: 6个月目标启用standard模式."""
        request = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="beginner",
            experience_years=0,
            math_level="beginner",
            current_job="市场专员",
            time_commitment="part_time",
            goal_timeline="6_months",
        )
        result = DiagnosisService.diagnose(request)
        assert result.recommended_mode == "standard"

    def test_diagnose_duration_calculation_skip_phase1(self):
        """AC2: 跳过Phase1减少约3周."""
        # Without skip
        request_standard = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="beginner",
            experience_years=0,
            math_level="beginner",
            current_job="设计师",
            time_commitment="part_time",
            goal_timeline="6_months",
        )
        result_standard = DiagnosisService.diagnose(request_standard)

        # With skip
        request_skip = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="advanced",
            experience_years=3,
            math_level="advanced",
            current_job="高级开发",
            time_commitment="full_time",
            goal_timeline="6_months",
        )
        result_skip = DiagnosisService.diagnose(request_skip)

        # Skip should reduce duration by ~3 weeks
        assert result_skip.estimated_duration_weeks < result_standard.estimated_duration_weeks

    def test_diagnose_includes_reasoning(self):
        """AC2: 诊断结果包含理由说明."""
        request = DiagnosisRequest(
            target_role="ai-engineer",
            python_level="advanced",
            experience_years=3,
            math_level="beginner",
            current_job="全栈工程师",
            time_commitment="full_time",
            goal_timeline="6_months",
        )
        result = DiagnosisService.diagnose(request)
        assert result.diagnosis.reasoning is not None
        assert len(result.diagnosis.reasoning) > 0
        # Should mention Python level
        assert "advanced" in result.diagnosis.reasoning or "Phase" in result.diagnosis.reasoning


class TestPathCreationAPI:
    """T3: Path 创建与进度 API 测试."""

    def test_create_path_success(self, client, test_db, auth_headers):
        """AC1, AC5: 成功创建学习路径."""
        response = client.post(
            "/api/v1/paths",
            json={
                "template_slug": "ai-engineer",
                "mode": "standard",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "path_id" in data
        assert data["template"]["slug"] == "ai-engineer"
        assert data["status"] == "active"
        assert "progress" in data

    def test_create_path_fast_track_mode(self, client, test_db, auth_headers):
        """AC5: 支持 fast_track 模式创建路径."""
        response = client.post(
            "/api/v1/paths",
            json={
                "template_slug": "ai-researcher",
                "mode": "fast_track",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        # Fast track should have reduced duration
        assert data["template"]["duration_weeks"] <= 20

    def test_create_path_duplicate_active(self, client, test_db, auth_headers):
        """AC1: 不能创建重复 active 路径."""
        # First create a path
        response1 = client.post(
            "/api/v1/paths",
            json={"template_slug": "ai-engineer", "mode": "standard"},
            headers=auth_headers,
        )
        assert response1.status_code == 201

        # Try to create another
        response2 = client.post(
            "/api/v1/paths",
            json={"template_slug": "ai-applier", "mode": "standard"},
            headers=auth_headers,
        )
        assert response2.status_code == 400
        assert "active" in response2.json()["detail"].lower()

    def test_create_path_invalid_template(self, client, test_db, auth_headers):
        """AC1: 无效模板返回400错误."""
        response = client.post(
            "/api/v1/paths",
            json={"template_slug": "invalid-template", "mode": "standard"},
            headers=auth_headers,
        )
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_get_path_progress(self, client, test_db, auth_headers):
        """AC3: 获取路径进度."""
        # Create a path first
        create_response = client.post(
            "/api/v1/paths",
            json={"template_slug": "ai-engineer", "mode": "standard"},
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        path_id = create_response.json()["path_id"]

        # Get progress
        response = client.get(f"/api/v1/paths/{path_id}/progress", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["path_id"] == path_id
        assert "progress" in data
        assert "milestones" in data
        assert "estimated_remaining_days" in data

    def test_get_path_progress_not_found(self, client, test_db, auth_headers):
        """AC3: 获取不存在路径的进度返回404."""
        response = client.get("/api/v1/paths/99999/progress", headers=auth_headers)
        assert response.status_code == 404

    def test_get_path_progress_unauthorized(
        self, client, test_db, auth_headers, auth_headers_other
    ):
        """AC3: 不能访问其他用户的路径进度."""
        # Create path with first user
        create_response = client.post(
            "/api/v1/paths",
            json={"template_slug": "ai-engineer", "mode": "standard"},
            headers=auth_headers,
        )
        path_id = create_response.json()["path_id"]

        # Try to access with second user
        response = client.get(f"/api/v1/paths/{path_id}/progress", headers=auth_headers_other)
        assert response.status_code == 403
