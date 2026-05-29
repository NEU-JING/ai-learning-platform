"""Tests for Path module — TDD approach (RED → GREEN → REFACTOR).

AC Coverage:
- AC1: 路径创建与入学诊断
- AC3: 路径进度追踪
"""

from sqlalchemy import inspect


class TestTablesExist:
    """T1: Verify path-related database tables exist."""

    def test_path_templates_table_exists(self, test_db):
        """path_templates 表必须存在，包含4条种子数据."""
        inspector = inspect(test_db.bind)
        assert "path_templates" in inspector.get_table_names(), "path_templates table missing"

        # Verify seed data exists (4 paths)
        from app.models.path import PathTemplate

        templates = test_db.query(PathTemplate).all()
        assert len(templates) == 4, f"Expected 4 path templates, got {len(templates)}"

        # Verify expected slugs
        slugs = {t.slug for t in templates}
        expected_slugs = {"ai-researcher", "ai-engineer", "ai-applier", "ai-manager"}
        assert slugs == expected_slugs, f"Missing templates: {expected_slugs - slugs}"

    def test_user_paths_table_exists(self, test_db):
        """user_paths 表必须存在."""
        inspector = inspect(test_db.bind)
        assert "user_paths" in inspector.get_table_names(), "user_paths table missing"

    def test_path_courses_table_exists(self, test_db):
        """path_courses 表必须存在."""
        inspector = inspect(test_db.bind)
        assert "path_courses" in inspector.get_table_names(), "path_courses table missing"

    def test_path_milestones_table_exists(self, test_db):
        """path_milestones 表必须存在."""
        inspector = inspect(test_db.bind)
        assert "path_milestones" in inspector.get_table_names(), "path_milestones table missing"

    def test_all_path_tables_have_required_columns(self, test_db):
        """所有 Path 表必须包含设计文档中定义的必要列."""
        inspector = inspect(test_db.bind)

        # Path templates required columns
        pt_cols = {c["name"] for c in inspector.get_columns("path_templates")}
        required_pt = {
            "id",
            "slug",
            "name",
            "description",
            "duration_weeks",
            "target_role",
            "required_courses",
            "created_at",
        }
        assert required_pt <= pt_cols, f"path_templates missing columns: {required_pt - pt_cols}"

        # User paths required columns
        up_cols = {c["name"] for c in inspector.get_columns("user_paths")}
        required_up = {
            "id",
            "user_id",
            "template_id",
            "status",
            "start_date",
            "target_end_date",
            "progress_percent",
            "created_at",
        }
        assert required_up <= up_cols, f"user_paths missing columns: {required_up - up_cols}"

        # Path courses required columns
        pc_cols = {c["name"] for c in inspector.get_columns("path_courses")}
        required_pc = {"id", "path_id", "course_id", "sequence_order", "status"}
        assert required_pc <= pc_cols, f"path_courses missing columns: {required_pc - pc_cols}"

        # Path milestones required columns
        pm_cols = {c["name"] for c in inspector.get_columns("path_milestones")}
        required_pm = {"id", "template_id", "name", "description", "sequence_order"}
        assert required_pm <= pm_cols, f"path_milestones missing columns: {required_pm - pm_cols}"


class TestPathDiagnosis:
    """T2: 入学诊断 API 测试."""

    def test_diagnosis_recommend_path(self, client, auth_headers):
        """验证诊断能推荐正确路径.

        AC1: 根据目标角色推荐对应的路径模板
        """
        diagnosis_data = {
            "target_role": "ai-engineer",
            "experience_years": 3,
            "python_level": "intermediate",
            "math_level": "intermediate",
            "current_job": "Java开发",
            "time_commitment": "part_time",
            "goal_timeline": "6_months",
        }

        response = client.post(
            "/api/v1/paths/diagnosis",
            json=diagnosis_data,
            headers=auth_headers,
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()

        # 验证响应结构
        assert "recommended_template" in result
        assert "recommended_mode" in result
        assert "diagnosis" in result
        assert "estimated_duration_weeks" in result

        # 验证推荐的路径与目标角色匹配
        assert result["recommended_template"] == "ai-engineer"
        assert result["recommended_mode"] == "standard"  # 6_months -> standard

    def test_diagnosis_skip_phase1(self, client, auth_headers):
        """验证有 Python 经验可跳过 Phase 1.

        AC2: 有经验的用户可以直接从 Phase 2 开始
        """
        diagnosis_data = {
            "target_role": "ai-researcher",
            "experience_years": 3,
            "python_level": "intermediate",  # intermediate/advanced 可以跳过 Phase 1
            "math_level": "beginner",
            "current_job": "后端开发",
            "time_commitment": "full_time",
            "goal_timeline": "3_months",
        }

        response = client.post(
            "/api/v1/paths/diagnosis",
            json=diagnosis_data,
            headers=auth_headers,
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()

        # 验证诊断结果
        assert result["diagnosis"]["can_skip_phase1"] is True
        assert result["diagnosis"]["start_from"] == 2
        assert result["recommended_mode"] == "fast_track"  # 3_months -> fast_track

        # 验证弱项检测
        assert "weak_areas" in result["diagnosis"]
        assert "linear_algebra" in result["diagnosis"]["weak_areas"]  # beginner math

    def test_diagnosis_invalid_role(self, client, auth_headers):
        """验证无效的 target_role 返回 400 错误."""
        diagnosis_data = {
            "target_role": "invalid-role",  # 无效的角色
            "experience_years": 3,
            "python_level": "intermediate",
            "math_level": "intermediate",
            "current_job": "开发者",
            "time_commitment": "full_time",
            "goal_timeline": "6_months",
        }

        response = client.post(
            "/api/v1/paths/diagnosis",
            json=diagnosis_data,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "Invalid target_role" in response.json()["detail"]

    def test_diagnosis_beginner_cannot_skip_phase1(self, client, auth_headers):
        """验证 beginner Python 用户不能跳过 Phase 1."""
        diagnosis_data = {
            "target_role": "ai-engineer",
            "experience_years": 3,
            "python_level": "beginner",  # beginner 不能跳过
            "math_level": "intermediate",
            "current_job": "产品经理",
            "time_commitment": "part_time",
            "goal_timeline": "6_months",
        }

        response = client.post(
            "/api/v1/paths/diagnosis",
            json=diagnosis_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()

        # beginner 不能跳过 Phase 1
        assert result["diagnosis"]["can_skip_phase1"] is False
        assert result["diagnosis"]["start_from"] == 1
