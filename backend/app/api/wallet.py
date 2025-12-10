"""
Wallet and payment API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type
from ..models.user import User, UserType, Customer
from ..models.wallet import Wallet
from ..services.payment_service import PaymentService

router = APIRouter()


class DepositRequest(BaseModel):
    """Schema for deposit request."""
    amount: float = Field(..., gt=0, description="Amount to deposit (must be positive)")
    payment_method: str = Field(default="credit_card", description="Payment method")


class WalletResponse(BaseModel):
    """Schema for wallet response."""
    balance: float
    total_deposited: float
    total_spent: float
    total_refunded: float
    
    class Config:
        from_attributes = True


@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    current_user: User = Depends(require_user_type(UserType.CUSTOMER, UserType.VIP)),
    db: Session = Depends(get_db)
):
    """
    Get current user's wallet balance and transaction summary.
    
    Returns wallet information including current balance.
    """
    # Get customer record
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer record not found"
        )
    
    # Get wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        # Create wallet if it doesn't exist
        wallet = Wallet(user_id=current_user.id, balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    
    return wallet


@router.post("/wallet/deposit", response_model=dict)
async def deposit_money(
    deposit_data: DepositRequest,
    current_user: User = Depends(require_user_type(UserType.CUSTOMER, UserType.VIP)),
    db: Session = Depends(get_db)
):
    """
    Deposit money into user's wallet.
    
    - **amount**: Amount to deposit (must be positive)
    - **payment_method**: Payment method (default: credit_card)
    
    Returns success message and updated balance.
    """
    payment_service = PaymentService(db)
    
    success, message = payment_service.deposit_money(
        user_id=current_user.id,
        amount=deposit_data.amount,
        payment_method=deposit_data.payment_method
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Get updated wallet balance
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    
    return {
        "success": True,
        "message": message,
        "balance": wallet.balance
    }

