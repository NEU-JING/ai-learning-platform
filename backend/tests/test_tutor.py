"""Tests for Tutor Recommendations API (T14).

AC18: 内容个性化推荐 — 用户算法理解维度薄弱，推荐补强课程和练习
AC19: 路径动态优化 — 用户连续3周超额完成任务，建议 Fast Track 模式
"""

from datetime import datetime, timedelta, timezone

from app.models import UserSkillScore
from app.models.path import UserPath


class TestTutorRecommendations:
    """Test Tutor Recommendations API endpoints."""

    def test_recommendations_success(self, client, auth_headers, test_db):
        """AC18: 个性化推荐应该成功返回."""
        user_id = 1

        # Create skill scores for the test user
        scores = [
            UserSkillScore(user_id=user_id, dimension="algorithm_understanding", score=35.0),
            UserSkillScore(user_id=user_id, dimension="coding_thinking", score=72.0),
            UserSkillScore(user_id=user_id, dimension="system_design", score=55.0),
            UserSkillScore(user_id=user_id, dimension="ai_collaboration", score=80.0),
        ]
        test_db.add_all(scores)
        test_db.commit()

        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "based_on" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_recommendations_targets_weak_dimension(self, client, auth_headers, test_db):
        """AC18: 推荐应该基于用户最薄弱的维度."""
        user_id = 1

        # Create scores with a clear weak dimension
        scores = [
            UserSkillScore(user_id=user_id, dimension="algorithm_understanding", score=25.0),
            UserSkillScore(user_id=user_id, dimension="coding_thinking", score=88.0),
            UserSkillScore(user_id=user_id, dimension="system_design", score=90.0),
        ]
        test_db.add_all(scores)
        test_db.commit()

        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # The "based_on" should mention the weak dimension
        assert "algorithm" in data["based_on"].lower() or "算法" in data["based_on"]

    def test_recommendations_has_course_and_practice(self, client, auth_headers, test_db):
        """AC18: 推荐应该包含课程和练习两种类型."""
        user_id = 1

        scores = [
            UserSkillScore(user_id=user_id, dimension="algorithm_understanding", score=30.0),
            UserSkillScore(user_id=user_id, dimension="data_analysis", score=40.0),
        ]
        test_db.add_all(scores)
        test_db.commit()

        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        recs = data["recommendations"]
        types = {r["type"] for r in recs}

        # Should contain both "course" and "practice" types
        assert "course" in types, f"Expected 'course' type in recommendations, got {types}"
        assert "practice" in types, f"Expected 'practice' type in recommendations, got {types}"

    def test_recommendations_structure(self, client, auth_headers, test_db):
        """AC18: 每条推荐应有完整的字段结构."""
        user_id = 1

        scores = [
            UserSkillScore(user_id=user_id, dimension="coding_thinking", score=20.0),
        ]
        test_db.add_all(scores)
        test_db.commit()

        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for rec in data["recommendations"]:
            assert "type" in rec, f"Missing 'type' in {rec}"
            assert rec["type"] in ("course", "practice"), f"Invalid type: {rec['type']}"
            assert "title" in rec, f"Missing 'title' in {rec}"
            assert "reason" in rec, f"Missing 'reason' in {rec}"
            assert "priority" in rec, f"Missing 'priority' in {rec}"
            assert rec["priority"] in (
                "high",
                "medium",
                "low",
            ), f"Invalid priority: {rec['priority']}"

    def test_recommendations_priority_order(self, client, auth_headers, test_db):
        """AC18: 推荐应该按优先级排序（high优先）."""
        user_id = 1

        scores = [
            UserSkillScore(user_id=user_id, dimension="algorithm_understanding", score=15.0),
        ]
        test_db.add_all(scores)
        test_db.commit()

        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        priorities = [r["priority"] for r in data["recommendations"]]

        # First items should be higher priority
        # Map to numeric for ordering check
        priority_order = {"high": 0, "medium": 1, "low": 2}
        priority_nums = [priority_order[p] for p in priorities]
        assert priority_nums == sorted(
            priority_nums
        ), f"Recommendations not sorted by priority: {priorities}"

    def test_recommendations_fast_track_suggestion(self, client, auth_headers, test_db):
        """AC19: 连续3周超额完成任务的用户应收到 Fast Track 建议."""
        user_id = 1

        # Create skill scores
        scores = [
            UserSkillScore(user_id=user_id, dimension="coding_thinking", score=75.0),
        ]
        test_db.add_all(scores)

        # Create a user path with fast_track eligibility
        # Simulate 3+ weeks of exceeding expectations by creating lab submissions
        # that show high completion rate
        now = datetime.now(timezone.utc)
        user_path = UserPath(
            user_id=user_id,
            status="active",
            start_date=(now - timedelta(weeks=4)).date(),
            progress_percent=85.0,
            mode="standard",
        )
        test_db.add(user_path)
        test_db.commit()

        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Check if fast_track suggestion is present
        recs = data["recommendations"]
        fast_track_recs = [
            r
            for r in recs
            if "fast" in r.get("title", "").lower() or "fast" in r.get("reason", "").lower()
        ]
        assert (
            len(fast_track_recs) > 0
        ), f"Expected fast track suggestion for high-performing user, got: {recs}"

    def test_recommendations_fast_track_includes_estimated_time(
        self, client, auth_headers, test_db
    ):
        """AC19: Fast Track 建议应有预估时间."""
        user_id = 1

        scores = [
            UserSkillScore(user_id=user_id, dimension="coding_thinking", score=80.0),
        ]
        test_db.add_all(scores)

        now = datetime.now(timezone.utc)
        user_path = UserPath(
            user_id=user_id,
            status="active",
            start_date=(now - timedelta(weeks=4)).date(),
            progress_percent=90.0,
            mode="standard",
        )
        test_db.add(user_path)
        test_db.commit()

        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        fast_track = next(
            (r for r in data["recommendations"] if "fast" in r.get("title", "").lower()),
            None,
        )
        assert fast_track is not None
        assert (
            "estimated_time" in fast_track or fast_track.get("type") == "practice"
        ), f"Course recommendations should include estimated_time: {fast_track}"

    def test_recommendations_requires_auth(self, client):
        """个性化推荐端点需要认证."""
        response = client.get("/api/v1/tutor/recommendations")
        assert response.status_code == 401

    def test_recommendations_no_scores_returns_default(self, client, auth_headers):
        """AC18: 无评分数据的用户应返回默认推荐."""
        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0, "Should have default recommendations"

    def test_recommendations_multiple_weak_dimensions(self, client, auth_headers, test_db):
        """AC18: 多个薄弱维度应有多个推荐."""
        user_id = 1

        scores = [
            UserSkillScore(user_id=user_id, dimension="algorithm_understanding", score=20.0),
            UserSkillScore(user_id=user_id, dimension="data_analysis", score=25.0),
            UserSkillScore(user_id=user_id, dimension="engineering_practice", score=30.0),
            UserSkillScore(user_id=user_id, dimension="prompt_engineering", score=85.0),
        ]
        test_db.add_all(scores)
        test_db.commit()

        response = client.get("/api/v1/tutor/recommendations", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert (
            len(data["recommendations"]) >= 2
        ), "Multiple weak dimensions should produce multiple recommendations"


# ── T15: Obstacle Detection (AC20) ─────────────────────────────────────────────


class TestTutorObstacleDetection:
    """Test Tutor Obstacle Detection API endpoint (AC20)."""

    def test_obstacle_detection_no_obstacles(self, client, auth_headers, test_course, test_db):
        """AC20: 无学习障碍时应返回空列表."""
        user_id = 1
        lab = test_course["lab"]

        # Create normal progress — user spent roughly same time as others
        now = datetime.now(timezone.utc)
        from app.models import LearningProgress

        # User 1 progress (normal time)
        progress = LearningProgress(
            user_id=user_id,
            chapter_id=lab.chapter_id,
            status="completed",
            completed_at=now,
            last_accessed_at=now,
            created_at=now - timedelta(hours=1),
        )
        test_db.add(progress)
        test_db.commit()

        response = client.get("/api/v1/tutor/obstacles", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["has_obstacles"] is False
        assert data["obstacles"] == []

    def test_obstacle_detection_time_exceeded(self, client, auth_headers, test_course, test_db):
        """AC20: 用户在某Lab停留超过平均时长3倍，应标记为学习障碍."""
        user_id = 1
        lab = test_course["lab"]
        now = datetime.now(timezone.utc)

        from app.models import LearningProgress

        # Other users: average ~1 hour
        for other_uid in range(2, 5):
            progress = LearningProgress(
                user_id=other_uid,
                chapter_id=lab.chapter_id,
                status="completed",
                completed_at=now,
                last_accessed_at=now,
                created_at=now - timedelta(hours=1),
            )
            test_db.add(progress)

        # Our user: spent 4 hours (4x average)
        progress = LearningProgress(
            user_id=user_id,
            chapter_id=lab.chapter_id,
            status="completed",
            completed_at=now,
            last_accessed_at=now,
            created_at=now - timedelta(hours=4),
        )
        test_db.add(progress)
        test_db.commit()

        response = client.get("/api/v1/tutor/obstacles", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["has_obstacles"] is True
        assert len(data["obstacles"]) == 1

        obstacle = data["obstacles"][0]
        assert obstacle["lab_id"] == lab.id
        assert obstacle["type"] == "time_exceeded"
        assert obstacle["data"]["ratio"] >= 3.0
        assert "tutor_message" in obstacle

    def test_obstacle_detection_structure(self, client, auth_headers, test_course, test_db):
        """AC20: 障碍检测响应结构应完整."""
        user_id = 1
        lab = test_course["lab"]
        now = datetime.now(timezone.utc)

        from app.models import LearningProgress

        # Other users: average ~1 hour
        for other_uid in range(2, 5):
            progress = LearningProgress(
                user_id=other_uid,
                chapter_id=lab.chapter_id,
                status="completed",
                completed_at=now,
                last_accessed_at=now,
                created_at=now - timedelta(hours=1),
            )
            test_db.add(progress)

        # Our user: 4 hours
        progress = LearningProgress(
            user_id=user_id,
            chapter_id=lab.chapter_id,
            status="completed",
            completed_at=now,
            last_accessed_at=now,
            created_at=now - timedelta(hours=4),
        )
        test_db.add(progress)
        test_db.commit()

        response = client.get("/api/v1/tutor/obstacles", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        obstacle = data["obstacles"][0]
        # Verify all expected fields
        assert "lab_id" in obstacle
        assert "lab_name" in obstacle
        assert "type" in obstacle
        assert obstacle["type"] in ("time_exceeded", "multiple_failures", "stuck")
        assert "data" in obstacle
        assert "user_time" in obstacle["data"]
        assert "average_time" in obstacle["data"]
        assert "ratio" in obstacle["data"]
        assert "tutor_message" in obstacle

    def test_obstacle_detection_requires_auth(self, client):
        """AC20: 障碍检测端点需要认证."""
        response = client.get("/api/v1/tutor/obstacles")
        assert response.status_code == 401

    def test_obstacle_detection_ratio_threshold(self, client, auth_headers, test_course, test_db):
        """AC20: 低于3倍阈值的Lab不应标记为障碍."""
        user_id = 1
        lab = test_course["lab"]
        now = datetime.now(timezone.utc)

        from app.models import LearningProgress

        # Other users: average ~1 hour
        for other_uid in range(2, 5):
            progress = LearningProgress(
                user_id=other_uid,
                chapter_id=lab.chapter_id,
                status="completed",
                completed_at=now,
                last_accessed_at=now,
                created_at=now - timedelta(hours=1),
            )
            test_db.add(progress)

        # Our user: 2.5 hours (below 3x threshold)
        progress = LearningProgress(
            user_id=user_id,
            chapter_id=lab.chapter_id,
            status="completed",
            completed_at=now,
            last_accessed_at=now,
            created_at=now - timedelta(hours=2, minutes=30),
        )
        test_db.add(progress)
        test_db.commit()

        response = client.get("/api/v1/tutor/obstacles", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["has_obstacles"] is False
        assert data["obstacles"] == []
