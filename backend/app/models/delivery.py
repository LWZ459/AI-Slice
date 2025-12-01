"""
Delivery and bidding-related database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class DeliveryStatus(enum.Enum):
    """Delivery status enumeration."""
    PENDING_BIDDING = "pending_bidding"
    NO_BIDDERS = "no_bidders"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BidStatus(enum.Enum):
    """Bid status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AssignmentType(enum.Enum):
    """Assignment type enumeration."""
    AUTO_ASSIGN = "auto_assign"  # Lowest bidder
    MANAGER_OVERRIDE = "manager_override"  # Manager chose higher bidder
    MANUAL_ASSIGN = "manual_assign"  # No bids, manager assigned


class Delivery(Base):
    """Delivery model."""
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    delivery_person_id = Column(Integer, ForeignKey("delivery_persons.id"), nullable=True)
    
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING_BIDDING)
    assignment_type = Column(Enum(AssignmentType), nullable=True)
    
    # Location information
    pickup_address = Column(Text)
    delivery_address = Column(Text)
    distance = Column(Float)  # in kilometers
    
    # Pricing
    delivery_fee = Column(Float)
    winning_bid_amount = Column(Float, nullable=True)
    
    # Timing
    bidding_ends_at = Column(DateTime(timezone=True))
    estimated_pickup_time = Column(DateTime(timezone=True))
    estimated_delivery_time = Column(DateTime(timezone=True))
    
    actual_pickup_time = Column(DateTime(timezone=True), nullable=True)
    actual_delivery_time = Column(DateTime(timezone=True), nullable=True)
    
    # Manager override justification
    manager_justification = Column(Text, nullable=True)
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="delivery")
    delivery_person = relationship("DeliveryPerson", back_populates="deliveries")
    bids = relationship("DeliveryBid", back_populates="delivery")
    
    def __repr__(self):
        return f"<Delivery Order {self.order_id}: {self.status.value}>"


class DeliveryBid(Base):
    """Delivery bid model."""
    __tablename__ = "delivery_bids"
    
    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=False)
    delivery_person_id = Column(Integer, ForeignKey("delivery_persons.id"), nullable=False)
    
    bid_amount = Column(Float, nullable=False)
    status = Column(Enum(BidStatus), default=BidStatus.PENDING)
    
    estimated_time = Column(Integer)  # in minutes
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    delivery = relationship("Delivery", back_populates="bids")
    delivery_person = relationship("DeliveryPerson", back_populates="bids")
    
    def __repr__(self):
        return f"<DeliveryBid ${self.bid_amount:.2f} by {self.delivery_person_id}>"

