"""
User controller for user management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, List
from services.user_service import user_service
from services.auth_service import auth_service
from models.user import UserCreate, UserUpdate, UserResponse
import logging

logger = logging.getLogger(__name__)

# Create router for user endpoints
router = APIRouter(prefix="/api/v1/users", tags=["Users"])


async def get_current_user(token: Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl="api/v1/auth/login"))]) -> UserResponse:
    """
    Dependency to get current user from JWT token
    
    Args:
        token: JWT access token
        
    Returns:
        UserResponse: Current user data
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    user_id = auth_service.verify_token(token)
    if not user_id:
        logger.error("Invalid authentication credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        logger.error(f"Inactive user access attempt: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user"
)
async def create_user(user_data: UserCreate) -> UserResponse:
    """
    Create a new user
    
    This endpoint creates a new user with the provided information.
    The password is hashed before storage.
    """
    try:
        user = user_service.create_user(user_data)
        logger.info(f"User {user.username} created successfully")
        return user
    except ValueError as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all users"
)
async def get_all_users(
    skip: int = 0,
    limit: int = 100
) -> List[UserResponse]:
    """
    Get all users with pagination
    
    Returns a list of all users in the system.
    """
    users = user_service.get_all_users(skip, limit)
    logger.info(f"Retrieved {len(users)} users")
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID"
)
async def get_user_by_id(user_id: str) -> UserResponse:
    """
    Get a specific user by ID
    
    Returns user data if the user exists.
    """
    user = user_service.get_user_by_id(user_id)
    if not user:
        logger.error(f"User with ID {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    logger.info(f"Retrieved user with ID {user_id}")
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user"
)
async def get_current_user_profile(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> UserResponse:
    """
    Get the current authenticated user's profile
    
    Returns the profile of the currently authenticated user.
    """
    logger.info(f"User {current_user.email} accessed their profile")
    return current_user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user"
)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> UserResponse:
    """
    Update a user by ID
    
    Only the authenticated user can update their own profile.
    Admin users could update others (future enhancement).
    """
    # For now, only allow users to update their own profile
    if current_user.id != user_id:
        logger.error(f"User {current_user.id} attempted to update user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    updated_user = user_service.update_user(user_id, user_data)
    if not updated_user:
        logger.error(f"Failed to update user with ID {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    logger.info(f"User {user_id} updated successfully")
    return updated_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user"
)
async def delete_user(
    user_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> None:
    """
    Delete a user by ID
    
    Only the authenticated user can delete their own account.
    """
    # Only allow users to delete their own account
    if current_user.id != user_id:
        logger.error(f"User {current_user.id} attempted to delete user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )
    
    success = user_service.delete_user(user_id)
    if not success:
        logger.error(f"Failed to delete user with ID {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    logger.info(f"User {user_id} deleted successfully")
    return None