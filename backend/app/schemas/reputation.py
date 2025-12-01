"""
Reputation-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ComplaintCreate(BaseModel):
    """Schema for filing a complaint."""
    subject_id: int
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    order_id: Optional[int] = None


class ComplaintResponse(BaseModel):
    """Schema for complaint response."""
    id: int
    complainant_id: int
    subject_id: int
    title: str
    description: str
    status: str
    is_disputed: bool
    dispute_reason: Optional[str] = None
    manager_decision: Optional[str] = None
    weight: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ComplaintDispute(BaseModel):
    """Schema for disputing a complaint."""
    dispute_reason: str = Field(..., min_length=10)


class ComplimentCreate(BaseModel):
    """Schema for giving a compliment."""
    receiver_id: int
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    order_id: Optional[int] = None


class ComplimentResponse(BaseModel):
    """Schema for compliment response."""
    id: int
    giver_id: int
    receiver_id: int
    title: str
    description: Optional[str] = None
    weight: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReputationResponse(BaseModel):
    """Schema for reputation response."""
    user_id: int
    score: int
    total_complaints: int
    total_compliments: int
    total_warnings: int
    
    class Config:
        from_attributes = True


class ManagerComplaintDecision(BaseModel):
    """Schema for manager decision on complaint."""
    decision: str = Field(..., min_length=10)
    action: str  # resolve, reject, warn_complainant, warn_subject


class WarningCreate(BaseModel):
    """Schema for issuing a warning."""
    user_id: int
    reason: str = Field(..., min_length=10)

