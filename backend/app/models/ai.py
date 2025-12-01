"""
AI and knowledge base-related database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class KnowledgeBase(Base):
    """Local knowledge base for AI responses."""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    
    question = Column(Text, nullable=False, index=True)
    answer = Column(Text, nullable=False)
    
    category = Column(String)  # menu, delivery, restaurant_info, policies, etc.
    tags = Column(String)  # comma-separated tags for search
    
    # Quality tracking
    times_used = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    
    # Flagging for poor quality
    is_flagged = Column(Boolean, default=False)
    flag_count = Column(Integer, default=0)
    
    created_by = Column(Integer, ForeignKey("managers.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ratings = relationship("QuestionRating", back_populates="knowledge_entry")
    
    def __repr__(self):
        return f"<KnowledgeBase #{self.id}: {self.question[:50]}>"


class ChatLog(Base):
    """Chat interaction log."""
    __tablename__ = "chat_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for visitors
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # Source of answer
    source = Column(String, nullable=False)  # "local_kb", "llm", "fallback"
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"), nullable=True)
    
    # LLM information (if applicable)
    llm_model = Column(String, nullable=True)
    llm_response_time = Column(Float, nullable=True)  # in seconds
    
    # Session information
    session_id = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_logs")
    knowledge_entry = relationship("KnowledgeBase", foreign_keys=[knowledge_base_id])
    rating = relationship("QuestionRating", back_populates="chat_log", uselist=False)
    
    def __repr__(self):
        return f"<ChatLog #{self.id} from {self.source}>"


class QuestionRating(Base):
    """Rating for AI answers from knowledge base."""
    __tablename__ = "question_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_log_id = Column(Integer, ForeignKey("chat_logs.id"), unique=True, nullable=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 0-5 stars
    feedback = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat_log = relationship("ChatLog", back_populates="rating")
    knowledge_entry = relationship("KnowledgeBase", back_populates="ratings")
    
    def __repr__(self):
        return f"<QuestionRating {self.rating} stars>"

