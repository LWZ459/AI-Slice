"""
User-related Pydantic schemas.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    user_type: str
    status: str
    created_at: datetime
    is_vip: Optional[bool] = False
    
    class Config:
        from_attributes = True


class CustomerResponse(UserResponse):
    """Schema for customer with additional info."""
    total_orders: int = 0
    total_spent: float = 0.0
    is_vip: bool = False
    warnings_count: int = 0


class ChefResponse(UserResponse):
    """Schema for chef with additional info."""
    specialization: Optional[str] = None
    total_dishes_created: int = 0
    average_rating: float = 0.0


class DeliveryPersonResponse(UserResponse):
    """Schema for delivery person with additional info."""
    vehicle_type: Optional[str] = None
    total_deliveries: int = 0
    average_rating: float = 0.0
    is_available: bool = True

