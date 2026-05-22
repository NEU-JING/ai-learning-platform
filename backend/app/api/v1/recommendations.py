"""Recommendations API — personalized learning recommendations.

Endpoints:
  GET  /recommendations/continue         — last position to resume
  GET  /recommendations/daily            — daily top-N picks
  GET  /recommendations/post-lab/{id}    — after-lab guidance
  GET  /recommendations/coach            — learning coach dashboard widget
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models import User
from app.schemas.recommendation import (
    ContinueLearningResponse,
    DailyRecommendationsResponse,
    LearningCoachResponse,
    PostLabRecommendationsResponse,
    RecommendationItem,
)
from app.services.recommendation import RecommendationService

router = APIRouter()


@router.get(
    "/recommendations/continue",
    response_model=ContinueLearningResponse,
    summary="继续学习",
)
def get_continue_learning(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取用户上次停下的位置，用于「继续学习」卡片。

    返回最近访问的章节、课程标题、完成百分比等信息。
    新用户无数据时返回 404。
    """
    from fastapi import HTTPException, status

    result = RecommendationService.get_continue_learning(current_user.id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="尚未开始学习任何课程",
        )
    return ContinueLearningResponse(**result)


@router.get(
    "/recommendations/daily",
    response_model=DailyRecommendationsResponse,
    summary="每日推荐",
)
def get_daily_recommendations(
    limit: int = Query(default=3, ge=1, le=20, description="返回推荐数量"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取今日个性化推荐章节列表。

    综合薄弱项、新内容、路径优先级、协同过滤和时间衰减五大维度计算推荐分数，
    返回 top N 推荐章节。
    """
    recommendations = RecommendationService.get_daily_recommendations(
        current_user.id, db, limit=limit,
    )

    # Count total incomplete chapters for context
    from app.models import Chapter, Course, LearningProgress

    completed_ids = {
        row[0]
        for row in db.query(LearningProgress.chapter_id).filter(
            LearningProgress.user_id == current_user.id,
            LearningProgress.status == "completed",
        ).all()
    }
    total_published = (
        db.query(Chapter.id)
        .join(Course, Chapter.course_id == Course.id)
        .filter(Course.is_published == True)  # noqa: E712
        .count()
    )
    total_incomplete = max(total_published - len(completed_ids), 0)

    return DailyRecommendationsResponse(
        recommendations=[RecommendationItem(**r) for r in recommendations],
        total_incomplete=total_incomplete,
    )


@router.get(
    "/recommendations/post-lab/{lab_id}",
    response_model=PostLabRecommendationsResponse,
    summary="实验后推荐",
)
def get_post_lab_recommendations(
    lab_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """实验完成后的个性化推荐。

    - 实验通过 → 推荐下一章 + 薄弱项强化练习
    - 实验失败 → 推荐复习相关章节 + 重试建议
    """
    from app.models import LabSubmission

    recommendations = RecommendationService.get_post_lab_recommendations(
        current_user.id, lab_id, db,
    )

    # Determine pass/fail from latest submission
    latest_sub = (
        db.query(LabSubmission)
        .filter(
            LabSubmission.user_id == current_user.id,
            LabSubmission.lab_id == lab_id,
        )
        .order_by(LabSubmission.created_at.desc())
        .first()
    )

    return PostLabRecommendationsResponse(
        lab_id=lab_id,
        passed=latest_sub.passed if latest_sub else None,
        recommendations=[
            RecommendationItem(**r) for r in recommendations
        ],
    )


@router.get(
    "/recommendations/coach",
    response_model=LearningCoachResponse,
    summary="AI 学习教练",
)
def get_learning_coach_advice(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """获取 AI 学习教练建议，供 Dashboard 面板展示。

    包含：本周学习时长及趋势、连续学习天数、最弱技能维度、
    个性化学习建议和推荐章节列表。
    """
    result = RecommendationService.get_learning_coach_advice(current_user.id, db)
    return LearningCoachResponse(
        weekly_hours=result["weekly_hours"],
        hours_trend=result["hours_trend"],
        weakest_dimension=result["weakest_dimension"],
        weakest_score=result["weakest_score"],
        streak_days=result["streak_days"],
        advice=result["advice"],
        recommended_chapters=[
            RecommendationItem(**r) for r in result["recommended_chapters"]
        ],
    )
