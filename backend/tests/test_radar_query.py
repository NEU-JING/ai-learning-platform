"""Test Radar query API with path specialization — T8.

Tests the GET /api/v1/radar endpoint with path_type parameter.

AC覆盖:
- AC7: 10维技能模型落地
- AC8: GET /api/v1/radar 端点
- AC11: 路径特化高亮
- AC14: percentile 和 confidence 返回
"""


class TestRadar10Dimensions:
    """RED phase test: Verify 10-dimension radar data — AC7."""

    def test_radar_returns_10_dimensions(self, client, auth_headers):
        """AC7: 雷达数据应该返回10个维度."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "dimensions" in data
        assert len(data["dimensions"]) == 10

    def test_radar_dimension_structure(self, client, auth_headers):
        """AC7: 每个维度应该有正确的结构."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        # Check required 10 dimensions
        required_slugs = {
            "coding_thinking",
            "algorithm_understanding",
            "system_design",
            "engineering_practice",
            "data_analysis",
            "problem_solving",
            "ai_collaboration",
            "research_depth",
            "ai_application",
            "prompt_engineering",
        }
        actual_slugs = {d["slug"] for d in dimensions}
        assert (
            required_slugs == actual_slugs
        ), f"Missing or extra dimensions: {required_slugs.symmetric_difference(actual_slugs)}"

    def test_radar_dimension_fields(self, client, auth_headers):
        """AC7, AC14: 每个维度应该包含所有必要字段."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        for dim in dimensions:
            assert "slug" in dim
            assert "name" in dim
            assert "score" in dim
            assert "percentile" in dim
            assert "confidence" in dim
            assert "category" in dim

            # Type checks
            assert isinstance(dim["slug"], str)
            assert isinstance(dim["name"], str)
            assert isinstance(dim["score"], (int, float))
            assert isinstance(dim["percentile"], (int, float))
            assert isinstance(dim["confidence"], (int, float))
            assert isinstance(dim["category"], str)

            # Value range checks
            assert 0 <= dim["score"] <= 100
            assert 0 <= dim["percentile"] <= 100
            assert 0 <= dim["confidence"] <= 1

    def test_radar_dimension_categories(self, client, auth_headers):
        """AC7: 维度应该有正确的类别."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        hard_skills = [d for d in dimensions if d["category"] == "hard"]
        soft_skills = [d for d in dimensions if d["category"] == "soft"]
        specialized = [d for d in dimensions if d["category"] == "specialized"]

        # Should have 5 hard skills
        assert len(hard_skills) == 5
        # Should have 3 soft skills
        assert len(soft_skills) == 3
        # Should have 2 specialized skills
        assert len(specialized) == 2

    def test_radar_response_includes_overall(self, client, auth_headers):
        """AC7: 响应应该包含整体评分."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "overall_score" in data
        assert isinstance(data["overall_score"], (int, float))
        assert 0 <= data["overall_score"] <= 100

    def test_radar_response_includes_updated_at(self, client, auth_headers):
        """AC7: 响应应该包含更新时间."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "updated_at" in data


class TestRadarPathSpecialization:
    """RED phase test: Verify path specialization highlighting — AC11."""

    def test_radar_without_path_type_no_highlight(self, client, auth_headers):
        """AC11: 不带path_type时不应该有高亮."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        for dim in dimensions:
            # Without path_type, highlighted should be False or not present
            assert dim.get("highlighted", False) is False

    def test_radar_with_ai_engineer_path_highlight(self, client, auth_headers):
        """AC11: ai-engineer路径应该高亮相关维度."""
        response = client.get("/api/v1/radar?path_type=ai-engineer", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        # AI工程师路径应该高亮这些维度
        expected_highlighted = {
            "coding_thinking",
            "system_design",
            "engineering_practice",
        }

        for dim in dimensions:
            if dim["slug"] in expected_highlighted:
                assert (
                    dim["highlighted"] is True
                ), f"{dim['slug']} should be highlighted for ai-engineer"
            else:
                assert (
                    dim["highlighted"] is False
                ), f"{dim['slug']} should not be highlighted for ai-engineer"

    def test_radar_with_ai_researcher_path_highlight(self, client, auth_headers):
        """AC11: ai-researcher路径应该高亮研究相关维度."""
        response = client.get("/api/v1/radar?path_type=ai-researcher", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        # AI专家路径应该高亮这些维度
        expected_highlighted = {
            "algorithm_understanding",
            "research_depth",
            "data_analysis",
        }

        for dim in dimensions:
            if dim["slug"] in expected_highlighted:
                assert (
                    dim["highlighted"] is True
                ), f"{dim['slug']} should be highlighted for ai-researcher"
            else:
                assert (
                    dim["highlighted"] is False
                ), f"{dim['slug']} should not be highlighted for ai-researcher"

    def test_radar_with_ai_applier_path_highlight(self, client, auth_headers):
        """AC11: ai-applier路径应该高亮应用相关维度."""
        response = client.get("/api/v1/radar?path_type=ai-applier", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        # AI应用者路径应该高亮这些维度
        expected_highlighted = {
            "ai_application",
            "prompt_engineering",
            "ai_collaboration",
        }

        for dim in dimensions:
            if dim["slug"] in expected_highlighted:
                assert (
                    dim["highlighted"] is True
                ), f"{dim['slug']} should be highlighted for ai-applier"
            else:
                assert (
                    dim["highlighted"] is False
                ), f"{dim['slug']} should not be highlighted for ai-applier"

    def test_radar_with_ai_manager_path_highlight(self, client, auth_headers):
        """AC11: ai-manager路径应该高亮管理相关维度."""
        response = client.get("/api/v1/radar?path_type=ai-manager", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        # AI管理者路径应该高亮这些维度
        expected_highlighted = {
            "problem_solving",
            "ai_collaboration",
            "ai_application",
        }

        for dim in dimensions:
            if dim["slug"] in expected_highlighted:
                assert (
                    dim["highlighted"] is True
                ), f"{dim['slug']} should be highlighted for ai-manager"
            else:
                assert (
                    dim["highlighted"] is False
                ), f"{dim['slug']} should not be highlighted for ai-manager"

    def test_radar_invalid_path_type_returns_error(self, client, auth_headers):
        """AC11: 无效的路径类型应该返回错误."""
        response = client.get("/api/v1/radar?path_type=invalid-path", headers=auth_headers)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "path_type" in data["detail"].lower() or "invalid" in data["detail"].lower()

    def test_radar_response_includes_path_info(self, client, auth_headers):
        """AC11: 响应应该包含路径信息."""
        response = client.get("/api/v1/radar?path_type=ai-engineer", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "path_type" in data
        assert data["path_type"] == "ai-engineer"


class TestRadarPercentileAndConfidence:
    """RED phase test: Verify percentile and confidence calculation — AC14."""

    def test_radar_includes_percentile(self, client, auth_headers):
        """AC14: 每个维度应该包含percentile."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        for dim in dimensions:
            assert "percentile" in dim
            # Percentile should be between 0 and 100
            assert 0 <= dim["percentile"] <= 100

    def test_radar_includes_confidence(self, client, auth_headers):
        """AC14: 每个维度应该包含confidence."""
        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        dimensions = data["dimensions"]

        for dim in dimensions:
            assert "confidence" in dim
            # Confidence should be between 0 and 1
            assert 0 <= dim["confidence"] <= 1

    def test_radar_confidence_based_on_data_volume(self, client, auth_headers, test_db):
        """AC14: confidence应该基于数据量计算."""
        # Create some skill events to increase confidence
        from datetime import datetime, timezone

        from app.models.radar import SkillDimension, SkillEvent

        user_id = 1  # test_user
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        # Create multiple events
        for i in range(5):
            event = SkillEvent(
                user_id=user_id,
                dimension_id=dimension.id,
                event_type="lab_completed",
                score_impact=80.0,
                created_at=datetime.now(timezone.utc),
            )
            test_db.add(event)
        test_db.commit()

        response = client.get("/api/v1/radar", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        coding_dim = next(d for d in data["dimensions"] if d["slug"] == "coding_thinking")

        # With 5 events and MAX_CONFIDENCE_EVENTS=10, confidence = 5/10 = 0.5
        # With minimum confidence of 0.1, it should be 0.5
        assert coding_dim["confidence"] >= 0.5


class TestRadarAPIAuth:
    """Test API authentication."""

    def test_radar_requires_auth(self, client):
        """AC8: 雷达端点需要认证."""
        response = client.get("/api/v1/radar")
        assert response.status_code == 401

    def test_radar_with_invalid_token(self, client):
        """AC8: 无效token应该返回401."""
        response = client.get("/api/v1/radar", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401
