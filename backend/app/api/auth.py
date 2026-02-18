"""
Authentication Routes
Handles user registration, login, logout, and password management
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
)
from app.models.database import User, Organization

router = APIRouter(prefix="/auth", tags=["authentication"])


# Pydantic Models
class UserRegister(BaseModel):
    """User registration request"""

    username: str
    email: EmailStr
    password: str
    full_name: str
    organization_name: str


class UserLogin(BaseModel):
    """User login request"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """User response"""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Change password request"""

    old_password: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str


# Routes
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    User registration endpoint
    Creates new user and organization
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create organization
    org = Organization(
        name=user_data.organization_name,
        email=user_data.email,
        industry="Technology",
        subscription_tier="starter",
    )
    db.add(org)
    db.flush()

    # Create user
    user = User(
        organization_id=org.id,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "org_id": str(org.id)}
    )
    refresh_token_str = create_refresh_token(
        data={"sub": str(user.id), "org_id": str(org.id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User login endpoint
    Returns access and refresh tokens
    """
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Generate tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "org_id": str(user.organization_id)}
    )
    refresh_token_str = create_refresh_token(
        data={"sub": str(user.id), "org_id": str(user.organization_id)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get current user profile
    """
    user_id = int(current_user["user_id"])
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    User logout endpoint
    """
    return {"message": "Logged out successfully"}


@router.put("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change user password
    """
    user_id = int(current_user["user_id"])
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not verify_password(request.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect",
        )

    user.hashed_password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    refresh_token_str = request.refresh_token
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token required",
        )

    try:
        payload = verify_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        org_id = payload.get("org_id")

        # Generate new access token
        access_token = create_access_token(
            data={"sub": user_id, "org_id": org_id}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
