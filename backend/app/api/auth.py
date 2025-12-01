"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..core.database import get_db
from ..core.config import settings
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user
)
from ..models.user import User, UserType, UserStatus, Customer, Chef, DeliveryPerson, Visitor
from ..models.wallet import Wallet
from ..models.reputation import Reputation
from ..schemas.auth import Token, LoginRequest, RegisterRequest
from ..schemas.user import UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **username**: Unique username (min 3 chars)
    - **password**: Password (min 8 chars)
    - **user_type**: customer, chef, or delivery
    
    Note: Registration requires manager approval (status will be PENDING)
    """
    # Check if username already exists
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate user type
    user_type_map = {
        "customer": UserType.CUSTOMER,
        "chef": UserType.CHEF,
        "delivery": UserType.DELIVERY
    }
    
    if request.user_type not in user_type_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user type. Must be: customer, chef, or delivery"
        )
    
    # Create user
    user = User(
        email=request.email,
        username=request.username,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        phone=request.phone,
        user_type=user_type_map[request.user_type],
        status=UserStatus.PENDING  # Requires manager approval
    )
    
    db.add(user)
    db.flush()
    
    # Create type-specific record
    if user.user_type == UserType.CUSTOMER:
        customer = Customer(user_id=user.id)
        db.add(customer)
        
        # Create wallet for customer
        wallet = Wallet(user_id=user.id, balance=0.0)
        db.add(wallet)
    
    elif user.user_type == UserType.CHEF:
        chef = Chef(user_id=user.id)
        db.add(chef)
    
    elif user.user_type == UserType.DELIVERY:
        delivery_person = DeliveryPerson(user_id=user.id)
        db.add(delivery_person)
    
    # Create reputation record
    reputation = Reputation(user_id=user.id, score=0)
    db.add(reputation)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with username and password to get JWT token.
    
    - **username**: Your username
    - **password**: Your password
    
    Returns JWT access token that should be included in subsequent requests.
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if user.account_locked_until:
        from datetime import datetime
        if datetime.utcnow() < user.account_locked_until:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is temporarily locked. Please try again later."
            )
        else:
            # Unlock account
            user.account_locked_until = None
            user.failed_login_attempts = 0
    
    # Check user status
    if user.status == UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account pending manager approval"
        )
    elif user.status == UserStatus.BLACKLISTED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been blacklisted"
        )
    elif user.status == UserStatus.DEACTIVATED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated"
        )
    elif user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended"
        )
    
    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "user_type": user.user_type.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    
    Requires valid JWT token.
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout current user.
    
    Note: With JWT, logout is handled client-side by discarding the token.
    This endpoint is provided for completeness.
    """
    return {"message": "Successfully logged out"}

