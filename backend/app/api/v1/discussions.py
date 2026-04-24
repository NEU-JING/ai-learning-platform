from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models import User, Discussion, Comment, Course
from app.schemas.discussion import (
    DiscussionCreate, DiscussionUpdate, DiscussionListResponse,
    DiscussionResponse, DiscussionDetailResponse,
    CommentCreate, CommentResponse, LikeResponse
)

router = APIRouter()


def truncate_content(content: str, max_length: int = 200) -> str:
    """截取内容作为预览"""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


def user_to_brief(user: User) -> dict:
    """转换用户为简要信息"""
    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url
    }


# ========== 讨论区API ==========

@router.get("/courses/{course_id}/discussions", response_model=List[DiscussionListResponse])
def list_discussions(
    course_id: int,
    sort: str = "newest",  # newest, popular, pinned
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """获取课程讨论列表"""
    # 检查课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    query = db.query(Discussion).filter(Discussion.course_id == course_id)
    
    # 排序
    if sort == "pinned":
        query = query.order_by(Discussion.is_pinned.desc(), Discussion.created_at.desc())
    elif sort == "popular":
        query = query.order_by(Discussion.likes_count.desc(), Discussion.created_at.desc())
    else:  # newest
        query = query.order_by(Discussion.created_at.desc())
    
    discussions = query.all()
    
    # 转换为响应格式
    result = []
    for d in discussions:
        result.append({
            "id": d.id,
            "course_id": d.course_id,
            "user": user_to_brief(d.user),
            "title": d.title,
            "content_preview": truncate_content(d.content),
            "likes_count": d.likes_count,
            "comments_count": d.comments_count,
            "is_pinned": d.is_pinned,
            "is_locked": d.is_locked,
            "created_at": d.created_at,
            "updated_at": d.updated_at
        })
    
    return result


@router.post("/courses/{course_id}/discussions", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
def create_discussion(
    course_id: int,
    discussion: DiscussionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建讨论"""
    # 检查课程是否存在
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在"
        )
    
    db_discussion = Discussion(
        course_id=course_id,
        user_id=current_user.id,
        title=discussion.title,
        content=discussion.content,
        likes_count=0,
        comments_count=0,
        is_pinned=False,
        is_locked=False
    )
    
    db.add(db_discussion)
    db.commit()
    db.refresh(db_discussion)
    
    return {
        "id": db_discussion.id,
        "course_id": db_discussion.course_id,
        "user": user_to_brief(db_discussion.user),
        "title": db_discussion.title,
        "content": db_discussion.content,
        "likes_count": db_discussion.likes_count,
        "comments_count": db_discussion.comments_count,
        "is_pinned": db_discussion.is_pinned,
        "is_locked": db_discussion.is_locked,
        "created_at": db_discussion.created_at,
        "updated_at": db_discussion.updated_at
    }


@router.get("/discussions/{discussion_id}", response_model=DiscussionDetailResponse)
def get_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """获取讨论详情"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="讨论不存在"
        )
    
    # 获取评论（只获取顶层评论，不嵌套回复）
    comments = db.query(Comment).filter(
        Comment.discussion_id == discussion_id,
        Comment.parent_id.is_(None)
    ).order_by(Comment.is_solution.desc(), Comment.created_at.desc()).all()
    
    comments_data = []
    for c in comments:
        # 获取回复
        replies = db.query(Comment).filter(
            Comment.parent_id == c.id
        ).order_by(Comment.created_at.asc()).all()
        
        replies_data = []
        for r in replies:
            replies_data.append({
                "id": r.id,
                "discussion_id": r.discussion_id,
                "user": user_to_brief(r.user),
                "content": r.content,
                "likes_count": r.likes_count,
                "is_solution": r.is_solution,
                "parent_id": r.parent_id,
                "created_at": r.created_at,
                "updated_at": r.updated_at
            })
        
        comments_data.append({
            "id": c.id,
            "discussion_id": c.discussion_id,
            "user": user_to_brief(c.user),
            "content": c.content,
            "likes_count": c.likes_count,
            "is_solution": c.is_solution,
            "parent_id": c.parent_id,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
            "replies": replies_data
        })
    
    return {
        "id": discussion.id,
        "course_id": discussion.course_id,
        "user": user_to_brief(discussion.user),
        "title": discussion.title,
        "content": discussion.content,
        "likes_count": discussion.likes_count,
        "comments_count": discussion.comments_count,
        "is_pinned": discussion.is_pinned,
        "is_locked": discussion.is_locked,
        "created_at": discussion.created_at,
        "updated_at": discussion.updated_at,
        "comments": comments_data
    }


@router.put("/discussions/{discussion_id}", response_model=DiscussionResponse)
def update_discussion(
    discussion_id: int,
    discussion_update: DiscussionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新讨论"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="讨论不存在"
        )
    
    # 检查权限（只有作者或管理员可以修改）
    if discussion.user_id != current_user.id and current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此讨论"
        )
    
    # 更新字段
    if discussion_update.title is not None:
        discussion.title = discussion_update.title
    if discussion_update.content is not None:
        discussion.content = discussion_update.content
    
    db.commit()
    db.refresh(discussion)
    
    return {
        "id": discussion.id,
        "course_id": discussion.course_id,
        "user": user_to_brief(discussion.user),
        "title": discussion.title,
        "content": discussion.content,
        "likes_count": discussion.likes_count,
        "comments_count": discussion.comments_count,
        "is_pinned": discussion.is_pinned,
        "is_locked": discussion.is_locked,
        "created_at": discussion.created_at,
        "updated_at": discussion.updated_at
    }


@router.delete("/discussions/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除讨论"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="讨论不存在"
        )
    
    # 检查权限（只有作者或管理员可以删除）
    if discussion.user_id != current_user.id and current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此讨论"
        )
    
    db.delete(discussion)
    db.commit()
    
    return None


@router.post("/discussions/{discussion_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    discussion_id: int,
    comment: CommentCreate,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """发表评论"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="讨论不存在"
        )
    
    # 检查讨论是否被锁定
    if discussion.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该讨论已被锁定，无法回复"
        )
    
    # 如果有parent_id，检查父评论是否存在
    if parent_id:
        parent = db.query(Comment).filter(Comment.id == parent_id).first()
        if not parent or parent.discussion_id != discussion_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="父评论不存在"
            )
    
    db_comment = Comment(
        discussion_id=discussion_id,
        user_id=current_user.id,
        content=comment.content,
        parent_id=parent_id,
        likes_count=0,
        is_solution=False
    )
    
    db.add(db_comment)
    
    # 更新讨论评论数
    discussion.comments_count += 1
    
    db.commit()
    db.refresh(db_comment)
    
    return {
        "id": db_comment.id,
        "discussion_id": db_comment.discussion_id,
        "user": user_to_brief(db_comment.user),
        "content": db_comment.content,
        "likes_count": db_comment.likes_count,
        "is_solution": db_comment.is_solution,
        "parent_id": db_comment.parent_id,
        "created_at": db_comment.created_at,
        "updated_at": db_comment.updated_at
    }


@router.post("/discussions/{discussion_id}/like", response_model=LikeResponse)
def like_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """点赞/取消点赞讨论"""
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    
    if not discussion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="讨论不存在"
        )
    
    # 简单实现：每次请求增加一个赞
    # 生产环境应该使用关联表记录谁点赞了
    discussion.likes_count += 1
    db.commit()
    db.refresh(discussion)
    
    return {
        "liked": True,
        "likes_count": discussion.likes_count
    }
