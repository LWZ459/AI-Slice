"""
Delivery and bidding-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeliveryBidCreate(BaseModel):
    """Schema for placing a delivery bid."""
    bid_amount: float = Field(gt=0)
    estimated_time: int = Field(gt=0)  # in minutes
    notes: Optional[str] = None


class DeliveryBidResponse(BaseModel):
    """Schema for delivery bid response."""
    id: int
    delivery_id: int
    delivery_person_id: int
    bid_amount: float
    status: str
    estimated_time: int
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryResponse(BaseModel):
    """Schema for delivery response."""
    id: int
    order_id: int
    delivery_person_id: Optional[int] = None
    status: str
    assignment_type: Optional[str] = None
    pickup_address: str
    delivery_address: str
    distance: Optional[float] = None
    delivery_fee: float
    winning_bid_amount: Optional[float] = None
    bidding_ends_at: Optional[datetime] = None
    actual_pickup_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    manager_justification: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryAssignment(BaseModel):
    """Schema for manager delivery assignment."""
    delivery_person_id: int
    justification: str = Field(..., min_length=10)


class DeliveryStatusUpdate(BaseModel):
    """Schema for updating delivery status."""
    status: str  # picked_up, in_transit, delivered, etc.

