"""Certification hooks tests — 事件驱动 L1 自动发证 (Phase 4 F3)."""

from unittest.mock import patch

from app.models import Certificate, CertificationLevel, User
from app.services import certificate_hooks as hooks


def _make_user(db, username="cert1"):
    u = User(username=username, email=f"{username}@test.com", password_hash="x")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _make_level(db, required_courses, code="L1"):
    level = CertificationLevel(
        name=code, required_courses=required_courses, min_average_score=70.0, is_active=True
    )
    db.add(level)
    db.commit()
    db.refresh(level)
    return level


class TestLabPassTrigger:
    def test_triggers_evaluation_for_level_requiring_course(self, test_db):
        user = _make_user(test_db)
        level = _make_level(test_db, [10])  # course 10
        with patch(
            "app.services.certificate.CertificateService.auto_evaluate_l1",
            return_value={"status": "approved"},
        ) as mock_eval:
            triggered = hooks.maybe_auto_certify_on_lab_pass(test_db, user.id, course_id=10)
        assert triggered == [level.id]
        mock_eval.assert_called_once()

    def test_skips_level_not_requiring_course(self, test_db):
        user = _make_user(test_db)
        _make_level(test_db, [99])  # 需要别的 course
        with patch("app.services.certificate.CertificateService.auto_evaluate_l1") as mock_eval:
            triggered = hooks.maybe_auto_certify_on_lab_pass(test_db, user.id, course_id=10)
        assert triggered == []
        mock_eval.assert_not_called()

    def test_skips_if_already_certified(self, test_db):
        """幂等：已持该等级证书则不重复评估。"""
        user = _make_user(test_db)
        level = _make_level(test_db, [10])
        test_db.add(Certificate(user_id=user.id, level_id=level.id, cert_number="L1-001"))
        test_db.commit()
        with patch("app.services.certificate.CertificateService.auto_evaluate_l1") as mock_eval:
            triggered = hooks.maybe_auto_certify_on_lab_pass(test_db, user.id, course_id=10)
        assert triggered == []
        mock_eval.assert_not_called()


class TestChainCompleteTrigger:
    def test_triggers_for_linked_level(self, test_db):
        user = _make_user(test_db)
        level = _make_level(test_db, [])
        chain = type("Chain", (), {"cert_level_id": level.id})()
        with patch(
            "app.services.certificate.CertificateService.auto_evaluate_l1",
            return_value={"status": "approved"},
        ) as mock_eval:
            triggered = hooks.maybe_auto_certify_on_chain_complete(test_db, user.id, chain)
        assert triggered == [level.id]
        mock_eval.assert_called_once()

    def test_noop_without_linked_level(self, test_db):
        user = _make_user(test_db)
        chain = type("Chain", (), {"cert_level_id": None})()
        with patch("app.services.certificate.CertificateService.auto_evaluate_l1") as mock_eval:
            triggered = hooks.maybe_auto_certify_on_chain_complete(test_db, user.id, chain)
        assert triggered == []
        mock_eval.assert_not_called()


class TestApplicationIdempotency:
    def test_skips_when_approved_application_exists(self, test_db):
        """同等级已有 approved application → 不重复评估（防累积）。"""
        from app.models.certification import CertificationApplication

        user = _make_user(test_db)
        level = _make_level(test_db, [10])
        test_db.add(CertificationApplication(user_id=user.id, level_id=level.id, status="approved"))
        test_db.commit()
        with patch("app.services.certificate.CertificateService.auto_evaluate_l1") as mock_eval:
            triggered = hooks.maybe_auto_certify_on_lab_pass(test_db, user.id, course_id=10)
        assert triggered == []
        mock_eval.assert_not_called()
