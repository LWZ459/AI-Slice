"""
Forum API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.forum import ForumTopic, ForumPost
from ..schemas.forum import ForumTopicCreate, ForumTopicResponse, ForumTopicDetail, ForumPostCreate, ForumPostResponse

router = APIRouter()


@router.post("/topics", response_model=ForumTopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: ForumTopicCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new discussion topic.
    """
    topic = ForumTopic(
        title=topic_data.title,
        content=topic_data.content,
        category=topic_data.category,
        author_id=current_user.id
    )
    
    db.add(topic)
    db.commit()
    db.refresh(topic)
    
    # Manually map for response to include author_name
    return ForumTopicResponse(
        id=topic.id,
        title=topic.title,
        content=topic.content,
        author_id=topic.author_id,
        author_name=current_user.username,
        category=topic.category,
        view_count=topic.view_count,
        created_at=topic.created_at,
        reply_count=0
    )


@router.get("/topics", response_model=List[ForumTopicResponse])
async def list_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    List discussion topics.
    """
    query = db.query(ForumTopic)
    
    if category:
        query = query.filter(ForumTopic.category == category)
    
    topics = query.order_by(ForumTopic.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for t in topics:
        # Count replies
        reply_count = db.query(ForumPost).filter(ForumPost.topic_id == t.id).count()
        
        result.append(ForumTopicResponse(
            id=t.id,
            title=t.title,
            content=t.content,
            author_id=t.author_id,
            author_name=t.author.username, # Assuming author relationship is loaded or lazy loaded
            category=t.category,
            view_count=t.view_count,
            created_at=t.created_at,
            reply_count=reply_count
        ))
        
    return result


@router.get("/topics/{topic_id}", response_model=ForumTopicDetail)
async def get_topic(
    topic_id: int,
    db: Session = Depends(get_db)
):
    """
    Get topic details and posts.
    """
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    # Increment view count
    topic.view_count += 1
    db.commit()
    
    # Get posts
    posts = db.query(ForumPost).filter(ForumPost.topic_id == topic_id).order_by(ForumPost.created_at.asc()).all()
    
    post_responses = [
        ForumPostResponse(
            id=p.id,
            topic_id=p.topic_id,
            author_id=p.author_id,
            author_name=p.author.username,
            content=p.content,
            created_at=p.created_at
        ) for p in posts
    ]
    
    return ForumTopicDetail(
        id=topic.id,
        title=topic.title,
        content=topic.content,
        author_id=topic.author_id,
        author_name=topic.author.username,
        category=topic.category,
        view_count=topic.view_count,
        created_at=topic.created_at,
        reply_count=len(posts),
        posts=post_responses
    )


@router.post("/topics/{topic_id}/posts", response_model=ForumPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    topic_id: int,
    post_data: ForumPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reply to a topic.
    """
    topic = db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
        
    post = ForumPost(
        topic_id=topic_id,
        author_id=current_user.id,
        content=post_data.content
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return ForumPostResponse(
        id=post.id,
        topic_id=post.topic_id,
        author_id=post.author_id,
        author_name=current_user.username,
        content=post.content,
        created_at=post.created_at
    )

