"""
Wallet and transaction-related database models.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base


class TransactionType(enum.Enum):
    """Transaction type enumeration."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    ORDER_PAYMENT = "order_payment"
    REFUND = "refund"
    BONUS = "bonus"


class TransactionStatus(enum.Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Wallet(Base):
    """Customer wallet model."""
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    balance = Column(Float, default=0.0)
    
    total_deposited = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    total_refunded = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet")
    
    def __repr__(self):
        return f"<Wallet User {self.user_id}: ${self.balance:.2f}>"


class Transaction(Base):
    """Transaction history model."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    amount = Column(Float, nullable=False)
    balance_before = Column(Float)
    balance_after = Column(Float)
    
    payment_method = Column(String)  # wallet, credit_card, etc.
    reference_number = Column(String, unique=True)
    
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    order = relationship("Order", back_populates="transaction")
    
    def __repr__(self):
        return f"<Transaction {self.transaction_type.value}: ${self.amount:.2f}>"

