"""Certification hooks — 事件驱动自动发证判定 (Phase 4 F3).

在 Lab 通过 / 任务链完成时自动触发 L1 评估，替代手动 apply。
幂等：用户已持对应等级证书则跳过。
"""

from sqlalchemy.orm import Session

from app.models import (
    CapstoneChain,
    Certificate,
    CertificationApplication,
    CertificationLevel,
)


def has_level_cert(db: Session, user_id: int, level_id: int) -> bool:
    return (
        db.query(Certificate)
        .filter(Certificate.user_id == user_id, Certificate.level_id == level_id)
        .first()
        is not None
    )


def _has_approved_application(db: Session, user_id: int, level_id: int) -> bool:
    """同等级是否已有 approved 申请（避免同一必修触发时累积多条 application）。"""
    return (
        db.query(CertificationApplication)
        .filter(
            CertificationApplication.user_id == user_id,
            CertificationApplication.level_id == level_id,
            CertificationApplication.status == "approved",
        )
        .first()
        is not None
    )


def _is_already_evaluated(db: Session, user_id: int, level_id: int) -> bool:
    """已持证或已有 approved 申请 → 无需再自动评估。"""
    return has_level_cert(db, user_id, level_id) or _has_approved_application(db, user_id, level_id)


def _active_levels_requiring_course(db: Session, course_id: int) -> list:
    return [
        level
        for level in db.query(CertificationLevel)
        .filter(CertificationLevel.is_active.is_(True))
        .all()
        if course_id in (level.required_courses or [])
    ]


def maybe_auto_certify_on_lab_pass(db: Session, user_id: int, course_id: int) -> list:
    """Lab 通过后触发：若该 course 属某活跃等级的必修，则评估该等级。返回新评估的 level_id 列表。"""
    evaluated = []
    for level in _active_levels_requiring_course(db, course_id):
        if _is_already_evaluated(db, user_id, level.id):  # 幂等：已持证/已有 approved 申请
            continue
        from app.services.certificate import CertificateService

        result = CertificateService.auto_evaluate_l1(db, user_id, level.id)
        if result and result.get("status") in ("approved", "failed", "pending_approval"):
            evaluated.append(level.id)
    return evaluated


def maybe_auto_certify_on_chain_complete(db: Session, user_id: int, chain: CapstoneChain) -> list:
    """任务链完成后触发：若关联某认证等级，则评估。幂等。"""
    if not chain.cert_level_id:
        return []
    if _is_already_evaluated(db, user_id, chain.cert_level_id):  # 幂等
        return []
    from app.services.certificate import CertificateService

    result = CertificateService.auto_evaluate_l1(db, user_id, chain.cert_level_id)
    if result and result.get("status") in ("approved", "failed", "pending_approval"):
        return [chain.cert_level_id]
    return []
