"""
Forum-related Pydantic schemas.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ForumPostCreate(BaseModel):
    """Schema for creating a forum post."""
    content: str


class ForumPostResponse(BaseModel):
    """Schema for forum post response."""
    id: int
    topic_id: int
    author_id: int
    author_name: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ForumTopicCreate(BaseModel):
    """Schema for creating a forum topic."""
    title: str
    content: str
    category: Optional[str] = "General"


class ForumTopicResponse(BaseModel):
    """Schema for forum topic response."""
    id: int
    title: str
    content: str
    author_id: int
    author_name: str
    category: str
    view_count: int
    created_at: datetime
    reply_count: int = 0
    
    class Config:
        from_attributes = True


class ForumTopicDetail(ForumTopicResponse):
    """Schema for detailed forum topic response (including posts)."""
    posts: List[ForumPostResponse] = []

