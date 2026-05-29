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


class TestPathCreate:
    """T3: 路径创建与进度 API 测试 — AC1, AC3, AC5."""

    def test_create_path(self, client, auth_headers, test_db):
        """验证创建路径 API.

        AC1: 根据模板创建用户路径
        """
        # 先获取一个有效的模板
        from app.models.path import PathTemplate

        template = test_db.query(PathTemplate).filter_by(slug="ai-engineer").first()
        assert template is not None, "Template not found"

        create_data = {
            "template_slug": "ai-engineer",
            "mode": "standard",
        }

        response = client.post(
            "/api/v1/paths",
            json=create_data,
            headers=auth_headers,
        )

        assert (
            response.status_code == 201
        ), f"Expected 201, got {response.status_code}: {response.text}"
        result = response.json()

        # 验证响应结构
        assert "path_id" in result
        assert "template" in result
        assert result["status"] == "active"
        assert "start_date" in result
        assert "target_end_date" in result
        assert "progress" in result

        # 验证进度摘要
        progress = result["progress"]
        assert "percent" in progress
        assert "completed_courses" in progress
        assert "total_courses" in progress

        # 验证 template 数据
        assert result["template"]["slug"] == "ai-engineer"

    def test_path_progress(self, client, auth_headers, test_db):
        """验证进度追踪 API.

        AC3: 路径进度追踪
        """
        # 先创建一个路径
        from app.services.path_service import PathService

        # 使用 PathService 创建路径
        service = PathService(test_db)
        user_path = service.create_user_path(
            user_id=1,  # 测试用户的 ID
            template_slug="ai-engineer",
            mode="standard",
        )

        path_id = user_path.id

        # 获取进度
        response = client.get(
            f"/api/v1/paths/{path_id}/progress",
            headers=auth_headers,
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()

        # 验证响应结构
        assert result["path_id"] == path_id
        assert result["status"] == "active"
        assert "progress" in result
        assert "milestones" in result
        assert "estimated_remaining_days" in result
        assert "ahead_behind_schedule" in result

        # 验证进度数据
        progress = result["progress"]
        assert "percent" in progress
        assert "completed_courses" in progress
        assert "in_progress_courses" in progress
        assert "total_courses" in progress

    def test_fast_track_mode(self, client, auth_headers, test_db):
        """验证 fast_track 模式创建路径.

        AC5: Fast Track 模式缩短学习周期
        """
        # 创建 standard 模式路径
        response_standard = client.post(
            "/api/v1/paths",
            json={"template_slug": "ai-engineer", "mode": "standard"},
            headers=auth_headers,
        )
        assert response_standard.status_code == 201
        standard_result = response_standard.json()

        # 创建 fast_track 模式路径
        # 注意：需要先删除之前的路径，因为用户只能有一个 active 路径
        from app.models.path import UserPath

        test_db.query(UserPath).filter_by(user_id=1).delete()
        test_db.commit()

        response_fast = client.post(
            "/api/v1/paths",
            json={"template_slug": "ai-engineer", "mode": "fast_track"},
            headers=auth_headers,
        )
        assert response_fast.status_code == 201
        fast_result = response_fast.json()

        # 验证 fast_track 的目标结束日期更短
        from datetime import datetime

        standard_end = datetime.strptime(standard_result["target_end_date"], "%Y-%m-%d")
        fast_end = datetime.strptime(fast_result["target_end_date"], "%Y-%m-%d")

        # fast_track 应该比 standard 周期更短
        assert fast_end < standard_end, "Fast track should have shorter duration"

    def test_create_path_invalid_template(self, client, auth_headers):
        """验证无效模板返回 400 错误."""
        response = client.post(
            "/api/v1/paths",
            json={"template_slug": "invalid-template", "mode": "standard"},
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "Template not found" in response.json()["detail"]

    def test_get_progress_not_found(self, client, auth_headers):
        """验证获取不存在路径的进度返回 404."""
        response = client.get(
            "/api/v1/paths/99999/progress",
            headers=auth_headers,
        )

        assert response.status_code == 404


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


class TestSkillGapDetection:
    """T4: 能力缺口诊断测试 — AC4."""

    def test_skill_gap_detection_returns_weak_skills(self, client, auth_headers, test_db):
        """验证技能缺口检测能识别薄弱技能.

        AC4: 基于实验通过率 < 60% 判定为薄弱
        """
        # 创建用户路径
        from app.services.path_service import PathService

        service = PathService(test_db)
        user_path = service.create_user_path(
            user_id=1,
            template_slug="ai-engineer",
            mode="standard",
        )
        path_id = user_path.id

        # 获取技能缺口
        response = client.get(
            f"/api/v1/paths/{path_id}/gaps",
            headers=auth_headers,
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()

        # 验证响应结构
        assert "path_id" in result
        assert "weak_skills" in result
        assert "recommendations" in result
        assert "summary" in result

        # weak_skills 应该是一个列表
        assert isinstance(result["weak_skills"], list)

        # 验证每个弱技能项的结构
        for skill in result["weak_skills"]:
            assert "dimension" in skill
            assert "pass_rate" in skill
            assert "status" in skill
            assert skill["status"] == "weak"
            assert skill["pass_rate"] < 60.0

    def test_skill_gap_detection_algorithm(self, client, auth_headers, test_db):
        """验证缺口检测算法的正确性.

        算法规则：实验通过率 < 60% 判定为薄弱
        """
        from app.services.path_service import PathService

        service = PathService(test_db)

        # 测试算法：低于 60% 应该返回 weak
        result = service._determine_gap_status(55.0)
        assert result == "weak"

        result = service._determine_gap_status(59.9)
        assert result == "weak"

        # 测试算法：等于或高于 60% 应该返回 normal 或 strong
        result = service._determine_gap_status(60.0)
        assert result == "normal"

        result = service._determine_gap_status(75.0)
        assert result == "normal"

        # 100% 返回 strong (优秀)
        result = service._determine_gap_status(100.0)
        assert result == "strong"

        # >= 85% 都返回 strong
        result = service._determine_gap_status(85.0)
        assert result == "strong"

    def test_skill_gap_not_found(self, client, auth_headers):
        """验证获取不存在路径的技能缺口返回 404."""
        response = client.get(
            "/api/v1/paths/99999/gaps",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_skill_gap_unauthorized(self, client, auth_headers, test_db):
        """验证不能访问其他用户的技能缺口."""
        # 创建一个路径，但设置给其他用户（user_id=999）
        from app.services.path_service import PathService

        service = PathService(test_db)
        user_path = service.create_user_path(
            user_id=999,  # 不同的用户
            template_slug="ai-engineer",
            mode="standard",
        )
        path_id = user_path.id

        # 当前用户（user_id=1）尝试访问
        response = client.get(
            f"/api/v1/paths/{path_id}/gaps",
            headers=auth_headers,
        )

        assert response.status_code == 403


class TestPathVisualization:
    """T5: 路径可视化数据 API 测试 — AC6."""

    def test_path_visualization_returns_nodes_and_edges(self, client, auth_headers, test_db):
        """验证可视化 API 返回正确的 nodes 和 edges 结构.

        AC6: 返回路径可视化数据，包含 nodes 和 edges
        """
        # 创建用户路径
        from app.services.path_service import PathService

        service = PathService(test_db)
        user_path = service.create_user_path(
            user_id=1,
            template_slug="ai-engineer",
            mode="standard",
        )
        path_id = user_path.id

        # 获取可视化数据
        response = client.get(
            f"/api/v1/paths/{path_id}/visualization",
            headers=auth_headers,
        )

        assert (
            response.status_code == 200
        ), f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()

        # 验证响应结构
        assert "path_id" in result
        assert result["path_id"] == path_id
        assert "nodes" in result
        assert "edges" in result
        assert "milestones" in result

        # nodes 应该是列表
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) > 0

        # edges 应该是列表
        assert isinstance(result["edges"], list)

        # 验证 node 结构
        for node in result["nodes"]:
            assert "id" in node
            assert "type" in node
            assert node["type"] in ["course", "milestone"]
            assert "name" in node
            assert "status" in node

    def test_path_visualization_course_nodes(self, client, auth_headers, test_db):
        """验证 course 类型节点包含正确信息."""
        from app.services.path_service import PathService

        service = PathService(test_db)
        user_path = service.create_user_path(
            user_id=1,
            template_slug="ai-engineer",
            mode="standard",
        )
        path_id = user_path.id

        response = client.get(
            f"/api/v1/paths/{path_id}/visualization",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()

        # 查找 course 节点
        course_nodes = [n for n in result["nodes"] if n["type"] == "course"]
        assert len(course_nodes) > 0, "应该有 course 节点"

        # 验证 course 节点结构
        for node in course_nodes:
            assert node["id"].startswith("course_")
            assert "dependencies" in node
            assert isinstance(node["dependencies"], list)
            assert "position" in node
            assert "x" in node["position"]
            assert "y" in node["position"]

    def test_path_visualization_milestone_nodes(self, client, auth_headers, test_db):
        """验证 milestone 类型节点包含正确信息."""
        from app.services.path_service import PathService

        service = PathService(test_db)
        user_path = service.create_user_path(
            user_id=1,
            template_slug="ai-engineer",
            mode="standard",
        )
        path_id = user_path.id

        response = client.get(
            f"/api/v1/paths/{path_id}/visualization",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()

        # milestones 应该在单独列表中
        assert isinstance(result["milestones"], list)

        # 查找 milestone 节点（在 nodes 中）
        milestone_nodes = [n for n in result["nodes"] if n["type"] == "milestone"]

        # 验证 milestone 节点结构（如果有的话）
        for node in milestone_nodes:
            assert node["id"].startswith("milestone_")
            assert "name" in node
            assert "status" in node

    def test_path_visualization_edges_structure(self, client, auth_headers, test_db):
        """验证 edges 表示正确的依赖关系."""
        from app.services.path_service import PathService

        service = PathService(test_db)
        user_path = service.create_user_path(
            user_id=1,
            template_slug="ai-engineer",
            mode="standard",
        )
        path_id = user_path.id

        response = client.get(
            f"/api/v1/paths/{path_id}/visualization",
            headers=auth_headers,
        )

        assert response.status_code == 200
        result = response.json()

        # 验证 edges 结构
        for edge in result["edges"]:
            assert "from" in edge
            assert "to" in edge
            # from 和 to 必须对应存在的节点
            node_ids = {n["id"] for n in result["nodes"]}
            assert edge["from"] in node_ids, f"Edge from {edge['from']} not in nodes"
            assert edge["to"] in node_ids, f"Edge to {edge['to']} not in nodes"

    def test_path_visualization_not_found(self, client, auth_headers):
        """验证获取不存在路径的可视化数据返回 404."""
        response = client.get(
            "/api/v1/paths/99999/visualization",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_path_visualization_unauthorized(self, client, auth_headers, test_db):
        """验证不能访问其他用户的可视化数据."""
        # 创建一个路径，但设置给其他用户（user_id=999）
        from app.services.path_service import PathService

        service = PathService(test_db)
        user_path = service.create_user_path(
            user_id=999,  # 不同的用户
            template_slug="ai-engineer",
            mode="standard",
        )
        path_id = user_path.id

        # 当前用户（user_id=1）尝试访问
        response = client.get(
            f"/api/v1/paths/{path_id}/visualization",
            headers=auth_headers,
        )

        assert response.status_code == 403
