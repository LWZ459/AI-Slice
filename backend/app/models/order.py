"""
Order-related database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class OrderStatus(enum.Enum):
    """Order status enumeration."""
    CART = "cart"
    PENDING_PAYMENT = "pending_payment"
    PLACED = "placed"
    PREPARING = "preparing"
    READY_FOR_DELIVERY = "ready_for_delivery"
    ASSIGNED_FOR_DELIVERY = "assigned_for_delivery"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PaymentStatus(enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    """Order model."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    order_number = Column(String, unique=True, index=True)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.CART)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Pricing
    subtotal = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    is_vip_order = Column(Integer, default=False)
    is_free_delivery = Column(Integer, default=False)
    
    # Delivery information
    delivery_address = Column(Text)
    delivery_instructions = Column(Text)
    
    # Ratings
    food_rating = Column(Float, nullable=True)
    delivery_rating = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery = relationship("Delivery", back_populates="order", uselist=False)
    transaction = relationship("Transaction", back_populates="order", uselist=False)
    
    def __repr__(self):
        return f"<Order {self.order_number} - {self.status.value}>"


class OrderItem(Base):
    """Individual items in an order."""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    special_instructions = Column(Text)
    
    # Individual dish rating
    rating = Column(Float, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    dish = relationship("Dish", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem: {self.quantity}x Dish {self.dish_id}>"

