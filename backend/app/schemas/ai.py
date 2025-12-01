"""
AI and knowledge base-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class QuestionRequest(BaseModel):
    """Schema for asking a question."""
    question: str = Field(..., min_length=1, max_length=500)


class QuestionResponse(BaseModel):
    """Schema for question response."""
    question: str
    answer: str
    source: str  # "local_kb" or "llm"
    chat_log_id: int
    can_rate: bool  # True if from KB, False if from LLM


class AnswerRating(BaseModel):
    """Schema for rating an answer."""
    chat_log_id: int
    rating: int = Field(ge=0, le=5)
    feedback: Optional[str] = None


class KnowledgeBaseCreate(BaseModel):
    """Schema for creating KB entry (manager only)."""
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    category: Optional[str] = None
    tags: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """Schema for KB entry response."""
    id: int
    question: str
    answer: str
    category: Optional[str] = None
    tags: Optional[str] = None
    times_used: int
    average_rating: float
    is_flagged: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MenuRecommendationRequest(BaseModel):
    """Schema for menu recommendation request."""
    time_of_day: Optional[str] = None  # morning, lunch, dinner, night
    preferences: Optional[str] = None  # comma-separated tags

