"""
Authentication-related Pydantic schemas.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data stored in JWT token."""
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Registration request schema."""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    user_type: str = "customer"  # customer, chef, delivery


class PasswordChange(BaseModel):
    """Password change request."""
    old_password: str
    new_password: str

