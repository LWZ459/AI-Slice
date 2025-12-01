"""
Menu and dish-related database models.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class DishCategory(Base):
    """Dish category model."""
    __tablename__ = "dish_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    
    dishes = relationship("Dish", back_populates="category")


class Dish(Base):
    """Dish/Menu item model."""
    __tablename__ = "dishes"
    
    id = Column(Integer, primary_key=True, index=True)
    chef_id = Column(Integer, ForeignKey("chefs.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("dish_categories.id"))
    
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String)
    
    is_available = Column(Boolean, default=True)
    is_special = Column(Boolean, default=False)  # Chef special for VIP
    
    # Tags for recommendations (stored as comma-separated string)
    tags = Column(String)  # e.g., "spicy,vegan,italian"
    
    # Popularity metrics
    times_ordered = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chef = relationship("Chef", back_populates="dishes")
    category = relationship("DishCategory", back_populates="dishes")
    order_items = relationship("OrderItem", back_populates="dish")
    
    def __repr__(self):
        return f"<Dish {self.name} by Chef {self.chef_id}>"

