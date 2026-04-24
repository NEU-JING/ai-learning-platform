from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserBrief(BaseModel):
    """用户信息简要"""
    id: int
    username: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    """评论基础"""
    content: str


class CommentCreate(CommentBase):
    """创建评论"""
    pass


class CommentResponse(CommentBase):
    """评论响应"""
    id: int
    discussion_id: int
    user: UserBrief
    likes_count: int
    is_solution: bool
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommentWithReplies(CommentResponse):
    """带回复的评论"""
    replies: List[CommentResponse] = []


class DiscussionBase(BaseModel):
    """讨论基础"""
    title: str
    content: str


class DiscussionCreate(DiscussionBase):
    """创建讨论"""
    pass


class DiscussionUpdate(BaseModel):
    """更新讨论"""
    title: Optional[str] = None
    content: Optional[str] = None


class DiscussionListResponse(BaseModel):
    """讨论列表项"""
    id: int
    course_id: int
    user: UserBrief
    title: str
    content_preview: str
    likes_count: int
    comments_count: int
    is_pinned: bool
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DiscussionResponse(DiscussionBase):
    """讨论详情"""
    id: int
    course_id: int
    user: UserBrief
    likes_count: int
    comments_count: int
    is_pinned: bool
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DiscussionDetailResponse(DiscussionResponse):
    """讨论详情（含评论）"""
    comments: List[CommentWithReplies] = []


class LikeResponse(BaseModel):
    """点赞响应"""
    liked: bool
    likes_count: int
