from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChapterBase(BaseModel):
    title: str
    content: str
    order_index: int
    chapter_type: str = "text"
    duration_minutes: int = 0


class ChapterCreate(ChapterBase):
    course_id: int


class ChapterResponse(ChapterBase):
    id: int
    course_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LabBase(BaseModel):
    title: str
    description: Optional[str] = None
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    test_cases: List[dict] = []
    requirements: Optional[str] = None
    hints: List[str] = []
    time_limit_seconds: int = 30
    memory_limit_mb: int = 256


class LabCreate(LabBase):
    chapter_id: int


class LabResponse(LabBase):
    id: int
    chapter_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    level: str  # beginner, intermediate, advanced, expert
    category: str
    duration_hours: int = 0
    is_published: bool = False


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    level: Optional[str] = None
    category: Optional[str] = None
    duration_hours: Optional[int] = None
    is_published: Optional[bool] = None


class CourseResponse(CourseBase):
    id: int
    order_index: int
    created_at: datetime
    updated_at: datetime
    chapters: List[ChapterResponse] = []
    
    class Config:
        from_attributes = True


class CourseListResponse(CourseBase):
    id: int
    order_index: int
    chapter_count: int = 0
    
    class Config:
        from_attributes = True


class LearningProgressBase(BaseModel):
    chapter_id: int
    status: str = "not_started"


class LearningProgressCreate(LearningProgressBase):
    pass


class LearningProgressResponse(LearningProgressBase):
    id: int
    user_id: int
    completed_at: Optional[datetime]
    last_accessed_at: datetime
    
    class Config:
        from_attributes = True


class LabSubmissionBase(BaseModel):
    lab_id: int
    code: str


class LabSubmissionCreate(LabSubmissionBase):
    pass


class LabSubmissionResponse(BaseModel):
    id: int
    user_id: int
    lab_id: int
    code: str
    output: Optional[str]
    status: str
    execution_time_ms: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
