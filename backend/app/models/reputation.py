"""
Reputation and complaint/compliment-related database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class ReputationEventType(enum.Enum):
    """Reputation event type enumeration."""
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    WARNING = "warning"
    BONUS = "bonus"
    DEMOTION = "demotion"
    PROMOTION = "promotion"
    ORDER_COMPLETED = "order_completed"
    ORDER_REJECTED = "order_rejected"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    RATING_RECEIVED = "rating_received"


class ComplaintStatus(enum.Enum):
    """Complaint status enumeration."""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISPUTED = "disputed"
    REJECTED = "rejected"


class Reputation(Base):
    """User reputation tracking model."""
    __tablename__ = "reputations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    score = Column(Integer, default=0)
    
    total_complaints = Column(Integer, default=0)
    total_compliments = Column(Integer, default=0)
    total_warnings = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reputation")
    events = relationship("ReputationEvent", back_populates="reputation")
    
    def __repr__(self):
        return f"<Reputation User {self.user_id}: Score {self.score}>"


class ReputationEvent(Base):
    """Individual reputation events."""
    __tablename__ = "reputation_events"
    
    id = Column(Integer, primary_key=True, index=True)
    reputation_id = Column(Integer, ForeignKey("reputations.id"), nullable=False)
    
    event_type = Column(Enum(ReputationEventType), nullable=False)
    score_change = Column(Integer, default=0)
    
    description = Column(Text)
    details = Column(Text)  # JSON string for additional details
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    reputation = relationship("Reputation", back_populates="events")
    
    def __repr__(self):
        return f"<ReputationEvent {self.event_type.value}: {self.score_change:+d}>"


class Complaint(Base):
    """Complaint model."""
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who filed the complaint
    complainant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Who is being complained about
    subject_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Related order (if applicable)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.PENDING)
    
    # Dispute information
    is_disputed = Column(Boolean, default=False)
    dispute_reason = Column(Text)
    
    # Manager decision
    manager_decision = Column(Text)
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Weight (VIP complaints count double)
    weight = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    complainant = relationship("User", foreign_keys=[complainant_id])
    subject = relationship("User", foreign_keys=[subject_id])
    order = relationship("Order", foreign_keys=[order_id])
    
    def __repr__(self):
        return f"<Complaint #{self.id}: {self.title}>"


class Compliment(Base):
    """Compliment model."""
    __tablename__ = "compliments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who gave the compliment
    giver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Who received the compliment
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Related order (if applicable)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Weight (VIP compliments count double)
    weight = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    giver = relationship("User", foreign_keys=[giver_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    order = relationship("Order", foreign_keys=[order_id])
    
    def __repr__(self):
        return f"<Compliment #{self.id}: {self.title}>"

