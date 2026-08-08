"""
Authentication controller for login, logout, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta
from pydantic import BaseModel
from services.auth_service import auth_service
from services.user_service import user_service
from models.user import UserResponse
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create router for authentication endpoints
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class TokenResponse(BaseModel):
    """Response model for token endpoint"""
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    """Request model for login endpoint"""
    email: str
    password: str


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_user(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenResponse:
    """
    Authenticate user and return JWT token
    
    This endpoint authenticates a user using email and password
    and returns a JWT access token for protected routes.
    """
    # Authenticate user
    user = user_service.authenticate_user(
        email=login_data.username,  # OAuth2 uses 'username' for email
        password=login_data.password
    )
    
    if not user:
        logger.error(f"Authentication failed for email: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        logger.error(f"Inactive user login attempt: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User {user.email} logged in successfully")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user() -> dict:
    """
    Logout user (client-side token invalidation)
    
    This endpoint is for client-side logout. The JWT token should be
    discarded by the client. Server-side token blacklisting would
    require additional implementation.
    """
    logger.info("User logged out")
    return {"message": "Successfully logged out. Please discard your token."}