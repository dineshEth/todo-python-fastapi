"""
User model definitions using Pydantic for data validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user model with common fields"""
    username: str = Field(..., min_length=3, max_length=50, description="User's username")
    email: EmailStr = Field(..., description="User's email address")
    is_active: bool = Field(default=True, description="Whether the user is active")


class UserCreate(UserBase):
    """User model for creating new users"""
    password: str = Field(..., min_length=8, description="User's password")


class UserUpdate(BaseModel):
    """User model for updating existing users"""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None, min_length=8)
    is_active: Optional[bool] = Field(default=None)


class UserResponse(UserBase):
    """User model for API responses"""
    id: str = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: datetime = Field(..., description="When the user was last updated")
    
    class Config:
        from_attributes = True  # For Pydantic v2 compatibility with ORM mode


class UserInDB(UserResponse):
    """User model for database storage (includes hashed password)"""
    hashed_password: str = Field(..., description="Hashed password")


# MongoDB schema for User
class UserDict(BaseModel):
    """User data as stored in MongoDB (dictionary format)"""
    _id: str
    username: str
    email: str
    hashed_password: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


def create_user_dict(username: str, email: str, hashed_password: str, is_active: bool = True) -> dict:
    """
    Create a user dictionary for MongoDB insertion
    
    Args:
        username: User's username
        email: User's email
        hashed_password: Hashed password
        is_active: Whether user is active
        
    Returns:
        dict: User data ready for MongoDB
    """
    now = datetime.utcnow()
    return {
        "_id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "is_active": is_active,
        "created_at": now,
        "updated_at": now
    }


def user_dict_to_response(user_data: dict) -> UserResponse:
    """
    Convert MongoDB user dictionary to UserResponse model
    
    Args:
        user_data: User data from MongoDB
        
    Returns:
        UserResponse: User response model
    """
    return UserResponse(
        id=str(user_data["_id"]),
        username=user_data["username"],
        email=user_data["email"],
        is_active=user_data["is_active"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )


def user_dict_to_in_db(user_data: dict) -> UserInDB:
    """
    Convert MongoDB user dictionary to UserInDB model
    
    Args:
        user_data: User data from MongoDB
        
    Returns:
        UserInDB: User in database model
    """
    return UserInDB(
        id=str(user_data["_id"]),
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data["hashed_password"],
        is_active=user_data["is_active"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"]
    )
