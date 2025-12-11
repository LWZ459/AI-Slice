"""
User-related database models.
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..core.database import Base


class UserType(enum.Enum):
    """User type enumeration."""
    VISITOR = "visitor"
    CUSTOMER = "customer"
    VIP = "vip"
    CHEF = "chef"
    DELIVERY = "delivery"
    MANAGER = "manager"


class UserStatus(enum.Enum):
    """User status enumeration."""
    PENDING = "pending"  # Registration pending approval
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"
    DEACTIVATED = "deactivated"


class User(Base):
    """Base user model for all user types."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    
    user_type = Column(Enum(UserType), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Failed login tracking
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    reputation = relationship("Reputation", back_populates="user", uselist=False)
    chat_logs = relationship("ChatLog", back_populates="user")
    
    # Type specific relationships
    customer = relationship("Customer", back_populates="user", uselist=False)
    chef = relationship("Chef", back_populates="user", uselist=False)
    delivery_person = relationship("DeliveryPerson", back_populates="user", uselist=False)
    manager = relationship("Manager", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User {self.username} ({self.user_type.value})>"


class Visitor(Base):
    """Extended information for visitors."""
    __tablename__ = "visitors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Application for registration
    application_status = Column(String, default="none")  # none, pending, approved, rejected
    application_date = Column(DateTime(timezone=True))
    
    user = relationship("User", foreign_keys=[user_id])


class Customer(Base):
    """Extended information for customers."""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    address = Column(String)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    warnings_count = Column(Integer, default=0)
    
    # VIP tracking
    is_vip = Column(Boolean, default=False)
    vip_since = Column(DateTime(timezone=True), nullable=True)
    vip_orders_count = Column(Integer, default=0)  # For tracking free delivery
    
    user = relationship("User", back_populates="customer")
    orders = relationship("Order", back_populates="customer")


class VIPCustomer(Base):
    """Extended information for VIP customers."""
    __tablename__ = "vip_customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True)
    
    vip_level = Column(Integer, default=1)
    free_deliveries_earned = Column(Integer, default=0)
    free_deliveries_used = Column(Integer, default=0)
    
    customer = relationship("Customer", foreign_keys=[customer_id])


class Chef(Base):
    """Extended information for chefs."""
    __tablename__ = "chefs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    specialization = Column(String)
    bio = Column(String)
    profile_image = Column(String)
    
    total_dishes_created = Column(Integer, default=0)
    total_orders_completed = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    complaints_count = Column(Integer, default=0)
    compliments_count = Column(Integer, default=0)
    demotion_count = Column(Integer, default=0)
    
    salary = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="chef")
    dishes = relationship("Dish", back_populates="chef")


class DeliveryPerson(Base):
    """Extended information for delivery personnel."""
    __tablename__ = "delivery_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    vehicle_type = Column(String)  # bike, car, scooter
    license_number = Column(String)
    
    total_deliveries = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    complaints_count = Column(Integer, default=0)
    compliments_count = Column(Integer, default=0)
    demotion_count = Column(Integer, default=0)
    
    is_available = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="delivery_person")
    bids = relationship("DeliveryBid", back_populates="delivery_person")
    deliveries = relationship("Delivery", back_populates="delivery_person")


class Manager(Base):
    """Extended information for managers."""
    __tablename__ = "managers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    department = Column(String)
    access_level = Column(Integer, default=1)
    
    user = relationship("User", back_populates="manager")

