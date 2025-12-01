"""
Manager-specific API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user, require_user_type, get_password_hash
from ..models.user import User, UserType, UserStatus, Manager, Customer
from ..models.wallet import Wallet
from ..models.reputation import Reputation
from ..schemas.user import UserResponse

router = APIRouter()


@router.post("/approve-customer/{user_id}", response_model=dict)
async def approve_customer(
    user_id: int,
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Approve a pending customer registration (Manager only).
    
    Changes user status from PENDING to ACTIVE.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User status is {user.status.value}, not pending"
        )
    
    # Approve user
    user.status = UserStatus.ACTIVE
    db.commit()
    
    return {
        "success": True,
        "message": f"User {user.username} approved and activated"
    }


@router.post("/reject-customer/{user_id}", response_model=dict)
async def reject_customer(
    user_id: int,
    reason: str = Query(..., min_length=10),
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Reject a pending customer registration (Manager only).
    
    - **reason**: Reason for rejection (min 10 chars)
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User status is {user.status.value}, not pending"
        )
    
    # Reject - mark as deactivated
    user.status = UserStatus.DEACTIVATED
    db.commit()
    
    # TODO: Send rejection email with reason
    
    return {
        "success": True,
        "message": f"User {user.username} rejected",
        "reason": reason
    }


@router.get("/pending-registrations", response_model=List[UserResponse])
async def list_pending_registrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    List all pending customer registrations (Manager only).
    
    Returns users waiting for approval.
    """
    users = db.query(User).filter(
        User.status == UserStatus.PENDING
    ).offset(skip).limit(limit).all()
    
    return users


from pydantic import BaseModel

class ManagerCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = None
    secret_code: str


@router.post("/create-manager", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_manager(
    data: ManagerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a manager account.
    
    **IMPORTANT**: Requires secret code for security.
    Set MANAGER_CREATION_SECRET in .env file.
    
    - **secret_code**: Secret code to authorize manager creation
    
    This is the bootstrap endpoint to create the first manager.
    After that, managers can create other managers.
    """
    from ..core.config import settings
    
    # Check secret code (for security)
    # For now, use a simple check. In production, use env variable
    MANAGER_SECRET = "create-manager-2025"  # TODO: Move to settings
    
    if data.secret_code != MANAGER_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret code"
        )
    
    # Check if username/email already exists
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create manager user
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        user_type=UserType.MANAGER,
        status=UserStatus.ACTIVE  # Managers are active immediately
    )
    
    db.add(user)
    db.flush()
    
    # Create manager record
    manager = Manager(user_id=user.id, department="Operations", access_level=1)
    db.add(manager)
    
    # Create reputation
    reputation = Reputation(user_id=user.id, score=0)
    db.add(reputation)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/activate-all-users", response_model=dict)
async def activate_all_pending_users(
    current_user: User = Depends(require_user_type(UserType.MANAGER)),
    db: Session = Depends(get_db)
):
    """
    Activate all pending users (Manager only).
    
    Bulk approval for testing purposes.
    """
    pending_users = db.query(User).filter(User.status == UserStatus.PENDING).all()
    
    count = 0
    for user in pending_users:
        user.status = UserStatus.ACTIVE
        count += 1
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Activated {count} pending users"
    }

