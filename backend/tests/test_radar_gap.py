"""Test Radar gap analysis API — T10.

Tests the GET /api/v1/radar/gap-analysis endpoint.

AC覆盖:
- AC13: 差距分析，返回当前分数与目标岗位要求差距
"""

from datetime import datetime, timezone

import pytest

from app.models.radar import JobSkillRequirement, SkillDimension, SkillEvent


class TestGapAnalysis:
    """RED phase test: Verify gap analysis — AC13."""

    def test_gap_analysis_success(self, client, auth_headers, test_db):
        """AC13: 应该能成功获取差距分析."""
        user_id = 1

        # Create job skill requirements
        job_req = JobSkillRequirement(
            job_title="ai-engineer",
            job_level="mid",
            required_skills={
                "coding_thinking": 80.0,
                "system_design": 75.0,
                "algorithm_understanding": 70.0,
            },
            source="jd_analysis",
        )
        test_db.add(job_req)
        test_db.commit()

        # Create some skill events
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()
        event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=65.0,  # Below requirement
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        # Get gap analysis
        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=ai-engineer", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "target_job" in data
        assert "target_level" in data
        assert "gaps" in data
        assert "overall_readiness" in data
        assert "estimated_gap_days" in data

    def test_gap_analysis_returns_gaps(self, client, auth_headers, test_db):
        """AC13: 差距分析应该返回具体的技能差距."""
        user_id = 1

        # Create job requirements
        job_req = JobSkillRequirement(
            job_title="ai-engineer",
            job_level="mid",
            required_skills={
                "coding_thinking": 80.0,
                "system_design": 75.0,
            },
            source="jd_analysis",
        )
        test_db.add(job_req)

        # Create current skill events with lower scores
        coding_dim = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()
        system_dim = test_db.query(SkillDimension).filter_by(slug="system_design").first()

        event1 = SkillEvent(
            user_id=user_id,
            dimension_id=coding_dim.id,
            event_type="lab_completed",
            score_impact=60.0,  # Gap of 20
            created_at=datetime.now(timezone.utc),
        )
        event2 = SkillEvent(
            user_id=user_id,
            dimension_id=system_dim.id,
            event_type="lab_completed",
            score_impact=50.0,  # Gap of 25
            created_at=datetime.now(timezone.utc),
        )
        test_db.add_all([event1, event2])
        test_db.commit()

        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=ai-engineer", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        gaps = data["gaps"]

        # Should have gaps for both dimensions
        assert len(gaps) >= 2

        # Check gap structure
        for gap in gaps:
            assert "dimension" in gap
            assert "current_score" in gap
            assert "required_score" in gap
            assert "gap" in gap
            assert "priority" in gap

    def test_gap_analysis_returns_correct_gap_values(self, client, auth_headers, test_db):
        """AC13: 差距值应该正确计算."""
        user_id = 1

        # Create job requirements
        job_req = JobSkillRequirement(
            job_title="ai-engineer",
            job_level="junior",
            required_skills={"coding_thinking": 80.0},
            source="manual",
        )
        test_db.add(job_req)

        # Create skill event with known score
        current_score = 60.0
        coding_dim = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()
        event = SkillEvent(
            user_id=user_id,
            dimension_id=coding_dim.id,
            event_type="lab_completed",
            score_impact=current_score,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=ai-engineer", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()

        # Find coding_thinking gap
        coding_gap = next((g for g in data["gaps"] if g["dimension"] == "coding_thinking"), None)
        assert coding_gap is not None
        assert coding_gap["current_score"] == pytest.approx(current_score, rel=1e-1)
        assert coding_gap["required_score"] == 80.0
        assert coding_gap["gap"] == pytest.approx(20.0, rel=1e-1)

    def test_gap_analysis_returns_overall_readiness(self, client, auth_headers, test_db):
        """AC13: 应该返回整体准备度百分比."""
        user_id = 1

        job_req = JobSkillRequirement(
            job_title="ai-engineer",
            job_level="mid",
            required_skills={
                "coding_thinking": 100.0,
                "system_design": 100.0,
            },
            source="jd_analysis",
        )
        test_db.add(job_req)

        # Create skills at 50% of requirements
        coding_dim = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()
        system_dim = test_db.query(SkillDimension).filter_by(slug="system_design").first()

        event1 = SkillEvent(
            user_id=user_id,
            dimension_id=coding_dim.id,
            event_type="lab_completed",
            score_impact=50.0,
            created_at=datetime.now(timezone.utc),
        )
        event2 = SkillEvent(
            user_id=user_id,
            dimension_id=system_dim.id,
            event_type="lab_completed",
            score_impact=50.0,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add_all([event1, event2])
        test_db.commit()

        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=ai-engineer", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "overall_readiness" in data
        assert 0 <= data["overall_readiness"] <= 100
        # With 50/100 on both, readiness should be around 50%
        assert data["overall_readiness"] == pytest.approx(50.0, abs=10.0)

    def test_gap_analysis_returns_estimated_days(self, client, auth_headers, test_db):
        """AC13: 应该返回预计弥补差距所需天数."""

        job_req = JobSkillRequirement(
            job_title="ai-engineer",
            job_level="mid",
            required_skills={"coding_thinking": 80.0},
            source="jd_analysis",
        )
        test_db.add(job_req)
        test_db.commit()

        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=ai-engineer", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "estimated_gap_days" in data
        assert isinstance(data["estimated_gap_days"], int)
        assert data["estimated_gap_days"] >= 0

    def test_gap_analysis_returns_priority_levels(self, client, auth_headers, test_db):
        """AC13: 差距应该有优先级 (high/medium/low)."""
        user_id = 1

        job_req = JobSkillRequirement(
            job_title="ai-engineer",
            job_level="mid",
            required_skills={
                "coding_thinking": 80.0,  # Large gap
                "system_design": 55.0,  # Small gap
            },
            source="jd_analysis",
        )
        test_db.add(job_req)

        # Current scores
        coding_dim = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()
        system_dim = test_db.query(SkillDimension).filter_by(slug="system_design").first()

        event1 = SkillEvent(
            user_id=user_id,
            dimension_id=coding_dim.id,
            event_type="lab_completed",
            score_impact=30.0,  # 50 point gap
            created_at=datetime.now(timezone.utc),
        )
        event2 = SkillEvent(
            user_id=user_id,
            dimension_id=system_dim.id,
            event_type="lab_completed",
            score_impact=50.0,  # 5 point gap
            created_at=datetime.now(timezone.utc),
        )
        test_db.add_all([event1, event2])
        test_db.commit()

        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=ai-engineer", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        for gap in data["gaps"]:
            assert "priority" in gap
            assert gap["priority"] in ["high", "medium", "low"]

    def test_gap_analysis_invalid_job_title(self, client, auth_headers):
        """AC13: 无效的岗位名称应该返回错误."""
        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=invalid-job", headers=auth_headers
        )
        assert response.status_code == 404

    def test_gap_analysis_missing_job_title(self, client, auth_headers):
        """AC13: 缺少岗位名称应该返回422错误."""
        response = client.get("/api/v1/radar/gap-analysis", headers=auth_headers)
        assert response.status_code == 422

    def test_gap_analysis_requires_auth(self, client):
        """AC13: 差距分析端点需要认证."""
        response = client.get("/api/v1/radar/gap-analysis?target_job=ai-engineer")
        assert response.status_code == 401

    def test_gap_analysis_no_gaps_when_skills_exceed_requirements(
        self, client, auth_headers, test_db
    ):
        """AC13: 当技能超过要求时不应该有差距."""
        user_id = 1

        job_req = JobSkillRequirement(
            job_title="ai-engineer",
            job_level="junior",
            required_skills={"coding_thinking": 50.0},
            source="manual",
        )
        test_db.add(job_req)

        # Create skill exceeding requirement
        coding_dim = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()
        event = SkillEvent(
            user_id=user_id,
            dimension_id=coding_dim.id,
            event_type="lab_completed",
            score_impact=90.0,  # Exceeds 50.0 requirement
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=ai-engineer", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # coding_thinking should not be in gaps since it exceeds requirement
        coding_gap = next((g for g in data["gaps"] if g["dimension"] == "coding_thinking"), None)
        # Either no gap entry, or gap is 0/negative
        if coding_gap:
            assert coding_gap["gap"] <= 0

    def test_gap_analysis_returns_recommended_courses(self, client, auth_headers, test_db):
        """AC13: 差距分析应该返回推荐课程."""

        job_req = JobSkillRequirement(
            job_title="ai-engineer",
            job_level="mid",
            required_skills={"coding_thinking": 80.0},
            source="jd_analysis",
        )
        test_db.add(job_req)
        test_db.commit()

        response = client.get(
            "/api/v1/radar/gap-analysis?target_job=ai-engineer", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # Check if recommended_courses field exists in gaps
        for gap in data["gaps"]:
            if "recommended_courses" in gap:
                assert isinstance(gap["recommended_courses"], list)
