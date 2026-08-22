"""Gamification & Capstone chain API — Phase 4 (F1/F2).

Endpoints:
  GET  /gamification/me                     — XP/等级/徽章/streak 汇总
  GET  /gamification/badges                 — 徽章墙
  GET  /gamification/daily-challenge/today  — 当日挑战
  POST /gamification/daily-challenge/today/submit
  GET  /capstone/chains                     — 任务链列表
  GET  /capstone/chains/{id}/next           — 当前任务
  POST /capstone/chains/{id}/tasks/{tid}/submit
  GET  /capstone/chains/{id}/evidence       — 证据卡
"""

import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import DailyChallenge, User
from app.schemas.gamification import (
    CapstoneChainItem,
    CapstoneNextTaskResponse,
    CapstoneSubmitRequest,
    CapstoneSubmitResponse,
    CapstoneTaskItem,
    DailyChallengeResponse,
    DailyChallengeSubmitRequest,
    DailyChallengeSubmitResponse,
    EvidenceCard,
    GamificationSummary,
)
from app.services import capstone as capstone_service
from app.services import gamification as gm
from app.services.grader import CodeGrader

router = APIRouter()


# ── Gamification ────────────────────────────────────────────────────────────


@router.get("/gamification/me", response_model=GamificationSummary)
def get_gamification_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return gm.get_user_gamification(db, current_user.id)


@router.get("/gamification/badges", response_model=list[str])
def get_user_badges(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return gm.get_user_gamification(db, current_user.id)["badges"]


@router.get("/gamification/daily-challenge/today", response_model=DailyChallengeResponse)
def get_today_challenge(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    challenge = (
        db.query(DailyChallenge)
        .filter(DailyChallenge.date == datetime.date.today(), DailyChallenge.is_active.is_(True))
        .first()
    )
    if challenge is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="今日暂无挑战")
    return challenge


@router.post(
    "/gamification/daily-challenge/today/submit", response_model=DailyChallengeSubmitResponse
)
def submit_today_challenge(
    body: DailyChallengeSubmitRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    challenge = (
        db.query(DailyChallenge)
        .filter(DailyChallenge.date == datetime.date.today(), DailyChallenge.is_active.is_(True))
        .first()
    )
    if challenge is None:
        return DailyChallengeSubmitResponse(status="not_found", passed=False)

    # 自动评分
    grading = CodeGrader.grade_in_sandbox(body.code, challenge.test_cases or [])
    passed = bool(grading["passed"])
    result = gm.submit_daily_challenge(db, current_user.id, challenge.id, passed=passed)
    return DailyChallengeSubmitResponse(
        xp_awarded=result["xp_awarded"],
        status=result["status"],
        passed=passed,
        score=float(grading["score"]),
        feedback=str(grading.get("feedback", "")),
    )


# ── Capstone chain ──────────────────────────────────────────────────────────


@router.get("/capstone/chains", response_model=list[CapstoneChainItem])
def list_chains(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return capstone_service.list_chains(db, only_active=True)


@router.get("/capstone/chains/{chain_id}/next", response_model=CapstoneNextTaskResponse)
def get_next_task(
    chain_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    chain = capstone_service.get_chain(db, chain_id)
    if chain is None or not chain.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务链不存在")

    task = capstone_service.get_next_task(db, current_user.id, chain_id)
    if task is None:
        return CapstoneNextTaskResponse(chain_id=chain_id, has_next=False, task=None)
    task_item = CapstoneTaskItem(**task)
    return CapstoneNextTaskResponse(chain_id=chain_id, has_next=True, task=task_item)


@router.post(
    "/capstone/chains/{chain_id}/tasks/{task_id}/submit", response_model=CapstoneSubmitResponse
)
def submit_chain_task(
    chain_id: int,
    task_id: int,
    body: CapstoneSubmitRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    result = capstone_service.submit_task(db, current_user.id, task_id, body.code)
    if result["status"] == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    if result["status"] == "chain_inactive":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="任务链未开放")

    return CapstoneSubmitResponse(
        status=result["status"],
        task_id=task_id,
        passed=result["status"] == "passed",
        xp_awarded=result.get("xp_awarded", 0),
        chain_completed=result.get("chain_completed", False),
        chain_xp=result.get("chain_xp", 0),
        feedback=result.get("feedback"),
    )


@router.get("/capstone/chains/{chain_id}/evidence", response_model=EvidenceCard)
def get_evidence_card(
    chain_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    card = capstone_service.get_evidence_card(db, current_user.id, chain_id)
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务链不存在")
    return card
