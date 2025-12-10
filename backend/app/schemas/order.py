"""
Order-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class CartItemCreate(BaseModel):
    """Schema for adding item to cart."""
    dish_id: int
    quantity: int = Field(gt=0, le=100)
    special_instructions: Optional[str] = None


class OrderCreate(BaseModel):
    """Schema for creating an order."""
    items: List[CartItemCreate]
    delivery_address: Optional[str] = "Customer Address"  # Made optional for UI, default provided
    delivery_instructions: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Schema for order item response."""
    id: int
    dish_id: int
    dish_name: str
    quantity: int
    unit_price: float
    total_price: float
    special_instructions: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Schema for order response."""
    id: int
    order_number: str
    status: str
    payment_status: str
    subtotal: float
    discount_amount: float
    delivery_fee: float
    total_amount: float
    is_vip_order: bool
    is_free_delivery: bool
    delivery_address: str
    food_rating: Optional[float] = None
    delivery_rating: Optional[float] = None
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderRating(BaseModel):
    """Schema for rating an order."""
    food_rating: Optional[float] = Field(None, ge=1, le=5)
    delivery_rating: Optional[float] = Field(None, ge=1, le=5)

