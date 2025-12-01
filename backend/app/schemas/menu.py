"""
Menu and dish-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DishCreate(BaseModel):
    """Schema for creating a dish."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(gt=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    tags: Optional[str] = None  # comma-separated
    is_special: bool = False  # VIP only


class DishUpdate(BaseModel):
    """Schema for updating a dish."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    is_available: Optional[bool] = None
    is_special: Optional[bool] = None
    tags: Optional[str] = None


class DishResponse(BaseModel):
    """Schema for dish response."""
    id: int
    chef_id: int
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_available: bool
    is_special: bool
    tags: Optional[str] = None
    times_ordered: int
    average_rating: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class DishCategoryCreate(BaseModel):
    """Schema for creating a dish category."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class DishCategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class MenuSearchRequest(BaseModel):
    """Schema for menu search."""
    query: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    tags: Optional[str] = None
    chef_id: Optional[int] = None
    include_special: bool = False  # VIP dishes

