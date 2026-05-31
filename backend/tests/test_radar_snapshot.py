"""Test Radar snapshot and comparison API — T9.

Tests the POST /api/v1/radar/snapshots and GET /api/v1/radar/compare endpoints.

AC覆盖:
- AC12: 历史版本对比功能
"""

from datetime import datetime, timezone

import pytest

from app.models.radar import SkillDimension, SkillEvent, UserSkillSnapshot


class TestCreateSnapshot:
    """RED phase test: Verify snapshot creation — AC12."""

    def test_create_snapshot_success(self, client, auth_headers, test_db):
        """AC12: 应该能成功创建技能快照."""
        # First, create some skill events to have data
        user_id = 1  # test_user
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        # Create a skill event
        event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=80.0,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()

        # Create snapshot
        response = client.post(
            "/api/v1/radar/snapshots", headers=auth_headers, json={"name": "入职前"}
        )
        assert response.status_code == 201

        data = response.json()
        assert "snapshot_id" in data
        assert "name" in data
        assert data["name"] == "入职前"
        assert "snapshot_date" in data
        assert "scores" in data

    def test_create_snapshot_with_path_id(self, client, auth_headers, test_db):
        """AC12: 创建快照时应该能关联路径ID."""
        # Create snapshot with path_id
        response = client.post(
            "/api/v1/radar/snapshots",
            headers=auth_headers,
            json={"name": "阶段1完成", "path_id": 1},
        )
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "阶段1完成"
        # Verify in database
        snapshot = test_db.query(UserSkillSnapshot).filter_by(id=data["snapshot_id"]).first()
        assert snapshot is not None
        assert snapshot.path_id == 1

    def test_create_snapshot_default_name(self, client, auth_headers):
        """AC12: 不提供名称时应该使用默认名称."""
        response = client.post("/api/v1/radar/snapshots", headers=auth_headers, json={})
        assert response.status_code == 201

        data = response.json()
        assert "name" in data
        assert "快照" in data["name"]  # Default name contains timestamp or default text

    def test_create_snapshot_captures_current_scores(self, client, auth_headers, test_db):
        """AC12: 快照应该捕获当前的技能分数."""
        user_id = 1

        # Create multiple skill events with different scores
        dimensions = test_db.query(SkillDimension).limit(3).all()
        for i, dim in enumerate(dimensions):
            event = SkillEvent(
                user_id=user_id,
                dimension_id=dim.id,
                event_type="lab_completed",
                score_impact=70.0 + i * 10,  # 70, 80, 90
                created_at=datetime.now(timezone.utc),
            )
            test_db.add(event)
        test_db.commit()

        response = client.post(
            "/api/v1/radar/snapshots", headers=auth_headers, json={"name": "测试快照"}
        )
        assert response.status_code == 201

        data = response.json()
        assert "scores" in data
        scores = data["scores"]

        # Should have scores for the dimensions we created events for
        for dim in dimensions:
            assert dim.slug in scores
            assert isinstance(scores[dim.slug], (int, float))

    def test_create_snapshot_requires_auth(self, client):
        """AC12: 创建快照需要认证."""
        response = client.post("/api/v1/radar/snapshots", json={"name": "测试"})
        assert response.status_code == 401

    def test_create_snapshot_invalid_name_too_long(self, client, auth_headers):
        """AC12: 名称过长应该返回错误."""
        response = client.post(
            "/api/v1/radar/snapshots", headers=auth_headers, json={"name": "x" * 100}  # Too long
        )
        assert response.status_code == 400


class TestCompareSnapshots:
    """RED phase test: Verify snapshot comparison — AC12."""

    def test_compare_snapshot_success(self, client, auth_headers, test_db):
        """AC12: 应该能成功对比当前与历史快照."""
        user_id = 1
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        # Create historical snapshot with old scores
        old_snapshot = UserSkillSnapshot(
            user_id=user_id,
            snapshot_name="入职前",
            scores={"coding_thinking": 70.0, "algorithm_understanding": 75.0},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(old_snapshot)

        # Create current skill events with higher scores
        event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=85.0,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()
        test_db.refresh(old_snapshot)

        # Compare
        response = client.get(
            f"/api/v1/radar/compare?snapshot_id={old_snapshot.id}", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "current" in data
        assert "snapshot" in data
        assert "comparison" in data
        assert "snapshot_info" in data

    def test_compare_returns_correct_change_values(self, client, auth_headers, test_db):
        """AC12: 对比应该返回正确的变化值."""
        user_id = 1
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        # Create snapshot with known score
        old_score = 70.0
        snapshot = UserSkillSnapshot(
            user_id=user_id,
            snapshot_name="旧快照",
            scores={"coding_thinking": old_score},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(snapshot)

        # Create current event with different score
        new_score = 85.0
        event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=new_score,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()
        test_db.refresh(snapshot)

        response = client.get(
            f"/api/v1/radar/compare?snapshot_id={snapshot.id}", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        comparison = data["comparison"]

        # Find coding_thinking in comparison
        coding_comparison = next(
            (c for c in comparison if c["dimension"] == "coding_thinking"), None
        )
        assert coding_comparison is not None
        assert coding_comparison["current"] == pytest.approx(new_score, rel=1e-1)
        assert coding_comparison["snapshot"] == old_score
        assert coding_comparison["change"] == pytest.approx(new_score - old_score, rel=1e-1)

    def test_compare_returns_correct_trend(self, client, auth_headers, test_db):
        """AC12: 对比应该返回正确的趋势 (up/down/flat)."""
        user_id = 1
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        # Test upward trend
        snapshot_up = UserSkillSnapshot(
            user_id=user_id,
            snapshot_name="上升趋势",
            scores={"coding_thinking": 60.0},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(snapshot_up)

        event_up = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=80.0,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event_up)
        test_db.commit()
        test_db.refresh(snapshot_up)

        response = client.get(
            f"/api/v1/radar/compare?snapshot_id={snapshot_up.id}", headers=auth_headers
        )
        data = response.json()
        coding_comparison = next(
            (c for c in data["comparison"] if c["dimension"] == "coding_thinking"), None
        )
        assert coding_comparison["trend"] == "up"

    def test_compare_downward_trend(self, client, auth_headers, test_db):
        """AC12: 下降趋势应该正确识别."""
        user_id = 1
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        snapshot_down = UserSkillSnapshot(
            user_id=user_id,
            snapshot_name="下降趋势",
            scores={"coding_thinking": 90.0},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(snapshot_down)

        event_down = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=70.0,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event_down)
        test_db.commit()
        test_db.refresh(snapshot_down)

        response = client.get(
            f"/api/v1/radar/compare?snapshot_id={snapshot_down.id}", headers=auth_headers
        )
        data = response.json()
        coding_comparison = next(
            (c for c in data["comparison"] if c["dimension"] == "coding_thinking"), None
        )
        assert coding_comparison["trend"] == "down"

    def test_compare_flat_trend(self, client, auth_headers, test_db):
        """AC12: 持平趋势应该正确识别."""
        user_id = 1
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        same_score = 75.0
        snapshot_flat = UserSkillSnapshot(
            user_id=user_id,
            snapshot_name="持平趋势",
            scores={"coding_thinking": same_score},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(snapshot_flat)

        event_flat = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=same_score,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event_flat)
        test_db.commit()
        test_db.refresh(snapshot_flat)

        response = client.get(
            f"/api/v1/radar/compare?snapshot_id={snapshot_flat.id}", headers=auth_headers
        )
        data = response.json()
        coding_comparison = next(
            (c for c in data["comparison"] if c["dimension"] == "coding_thinking"), None
        )
        assert coding_comparison["trend"] == "flat"

    def test_compare_returns_snapshot_info(self, client, auth_headers, test_db):
        """AC12: 对比响应应该包含快照信息."""
        user_id = 1
        snapshot = UserSkillSnapshot(
            user_id=user_id,
            snapshot_name="入职前",
            scores={"coding_thinking": 70.0},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(snapshot)
        test_db.commit()
        test_db.refresh(snapshot)

        response = client.get(
            f"/api/v1/radar/compare?snapshot_id={snapshot.id}", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "snapshot_info" in data
        assert data["snapshot_info"]["name"] == "入职前"
        assert "date" in data["snapshot_info"]

    def test_compare_requires_auth(self, client):
        """AC12: 对比端点需要认证."""
        response = client.get("/api/v1/radar/compare?snapshot_id=1")
        assert response.status_code == 401

    def test_compare_invalid_snapshot_id(self, client, auth_headers):
        """AC12: 无效的快照ID应该返回404."""
        response = client.get("/api/v1/radar/compare?snapshot_id=99999", headers=auth_headers)
        assert response.status_code == 404

    def test_compare_missing_snapshot_id(self, client, auth_headers):
        """AC12: 缺少快照ID应该返回422 (FastAPI 验证错误)."""
        response = client.get("/api/v1/radar/compare", headers=auth_headers)
        assert response.status_code == 422

    def test_compare_other_user_snapshot_forbidden(self, client, auth_headers, test_db):
        """AC12: 不能访问其他用户的快照."""
        # Create a snapshot for a different user (user_id 999)
        other_snapshot = UserSkillSnapshot(
            user_id=999,  # Different user
            snapshot_name="其他用户快照",
            scores={"coding_thinking": 70.0},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(other_snapshot)
        test_db.commit()
        test_db.refresh(other_snapshot)

        response = client.get(
            f"/api/v1/radar/compare?snapshot_id={other_snapshot.id}", headers=auth_headers
        )
        assert response.status_code == 403  # Forbidden

    def test_compare_returns_assessment(self, client, auth_headers, test_db):
        """AC12: 对比应该返回评估文本."""
        user_id = 1
        dimension = test_db.query(SkillDimension).filter_by(slug="coding_thinking").first()

        snapshot = UserSkillSnapshot(
            user_id=user_id,
            snapshot_name="测试",
            scores={"coding_thinking": 60.0},
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(snapshot)

        event = SkillEvent(
            user_id=user_id,
            dimension_id=dimension.id,
            event_type="lab_completed",
            score_impact=85.0,
            created_at=datetime.now(timezone.utc),
        )
        test_db.add(event)
        test_db.commit()
        test_db.refresh(snapshot)

        response = client.get(
            f"/api/v1/radar/compare?snapshot_id={snapshot.id}", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "assessment" in data
        assert isinstance(data["assessment"], str)
