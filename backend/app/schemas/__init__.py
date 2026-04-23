from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    level: str
    category: str
    duration_hours: int


class CourseResponse(CourseBase):
    id: int
    cover_image: Optional[str] = None
    is_published: bool
    order_index: int
    created_at: datetime
    chapters: List['ChapterResponse'] = []
    
    class Config:
        from_attributes = True


class ChapterBase(BaseModel):
    title: str
    content: Optional[str] = None
    chapter_type: str
    duration_minutes: int
    order_index: int


class ChapterResponse(ChapterBase):
    id: int
    course_id: int
    created_at: datetime
    lab: Optional['LabResponse'] = None
    
    class Config:
        from_attributes = True


class LabBase(BaseModel):
    title: str
    description: Optional[str] = None
    starter_code: Optional[str] = None
    hints: List[str] = []
    time_limit_seconds: int = 30
    memory_limit_mb: int = 256


class LabResponse(LabBase):
    id: int
    chapter_id: int
    test_cases: List[Dict[str, Any]] = []
    created_at: datetime
    
    class Config:
        from_attributes = True


class CodeExecutionRequest(BaseModel):
    code: str
    timeout: Optional[int] = 30


class CodeExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: int


class ProgressUpdate(BaseModel):
    status: str  # not_started, in_progress, completed


class ProgressResponse(BaseModel):
    id: int
    user_id: int
    chapter_id: int
    status: str
    completed_at: Optional[datetime] = None
    last_accessed_at: datetime
    
    class Config:
        from_attributes = True


# 解决循环引用
CourseResponse.model_rebuild()
ChapterResponse.model_rebuild()
