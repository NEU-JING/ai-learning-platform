from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProgressBase(BaseModel):
    chapter_id: int
    status: str = "not_started"  # not_started, in_progress, completed


class ProgressCreate(ProgressBase):
    pass


class ProgressUpdate(BaseModel):
    status: str  # not_started, in_progress, completed


class ProgressResponse(BaseModel):
    id: int
    chapter_id: int
    status: str
    completed_at: Optional[datetime]
    last_accessed_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class CourseProgressResponse(BaseModel):
    """课程进度统计响应"""
    course_id: int
    course_title: str
    total_chapters: int
    completed_chapters: int
    in_progress_chapters: int
    progress_percentage: float
    is_completed: bool


class LearningStatsResponse(BaseModel):
    """学习统计概览"""
    total_chapters_accessed: int
    completed_chapters: int
    in_progress_chapters: int
    not_started_chapters: int
    total_learning_minutes: int
    completed_courses: int
