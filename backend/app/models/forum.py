"""
Forum-related database models.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class ForumTopic(Base):
    """Forum topic model."""
    __tablename__ = "forum_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Category (e.g., "Dishes", "Chefs", "Delivery")
    category = Column(String, default="General")
    
    view_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="forum_topics")
    posts = relationship("ForumPost", back_populates="topic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ForumTopic {self.title}>"


class ForumPost(Base):
    """Forum post (reply) model."""
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("forum_topics.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    topic = relationship("ForumTopic", back_populates="posts")
    author = relationship("User", back_populates="forum_posts")
    
    def __repr__(self):
        return f"<ForumPost {self.id} in Topic {self.topic_id}>"

