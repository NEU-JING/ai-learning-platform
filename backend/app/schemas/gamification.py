"""Gamification & Capstone-chain Pydantic schemas — Phase 4 (F1/F2).

前后端契约唯一真相源。
"""

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Gamification ────────────────────────────────────────────────────────────

class GamificationSummary(BaseModel):
    total_xp: int = 0
    level: int = 1
    badges: list[str] = []
    daily_streak: int = 0


class DailyChallengeResponse(BaseModel):
    id: int
    date: date
    task: str
    xp_reward: int


class DailyChallengeSubmitRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=100000)


class DailyChallengeSubmitResponse(BaseModel):
    xp_awarded: int = 0
    status: str              # passed / failed / already_submitted / not_found
    passed: bool = False
    score: Optional[float] = None
    feedback: Optional[str] = None


# ── Capstone chain ──────────────────────────────────────────────────────────

class CapstoneChainItem(BaseModel):
    id: int
    code: str
    title: str
    description: Optional[str] = None
    skill_tags: list[str] = []


class CapstoneTaskItem(BaseModel):
    id: int
    seq: int
    title: str
    scenario: str
    test_cases: list[Any] = []


class CapstoneSubmitRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=100000)


class CapstoneSubmitResponse(BaseModel):
    status: str              # passed / failed / chain_inactive / not_found / already_passed
    task_id: int
    passed: bool = False
    xp_awarded: int = 0
    chain_completed: bool = False
    chain_xp: int = 0
    feedback: Optional[str] = None


class EvidenceTaskItem(BaseModel):
    seq: int
    title: str
    score: Optional[float] = None
    passed: bool = False
    output: Optional[str] = None
    completed_at: Optional[str] = None


class EvidenceCard(BaseModel):
    chain_id: int
    title: str
    complete: bool
    tasks: list[EvidenceTaskItem]
    generated_at: str


class CapstoneNextTaskResponse(BaseModel):
    chain_id: int
    has_next: bool
    task: Optional[CapstoneTaskItem] = None