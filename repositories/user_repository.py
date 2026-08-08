"""
User repository for database operations
"""
from typing import Optional, List
from pymongo.collection import Collection
from database.connection import get_collection
from models.user import UserCreate, UserUpdate, UserResponse, UserInDB, user_dict_to_response, user_dict_to_in_db, create_user_dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository class for User CRUD operations"""
    
    def __init__(self):
        """Initialize user repository with MongoDB collection"""
        self.collection: Collection = get_collection("users")
        
        # Create index on email for faster lookups and to ensure uniqueness
        self.collection.create_index("email", unique=True)
        self.collection.create_index("username", unique=True)
    
    def create(self, user_data: UserCreate, hashed_password: str) -> UserResponse:
        """
        Create a new user in the database
        
        Args:
            user_data: User creation data
            hashed_password: Hashed password
            
        Returns:
            UserResponse: Created user data
            
        Raises:
            ValueError: If user with email or username already exists
        """
        # Check if user with email already exists
        existing_user = self.collection.find_one({"email": user_data.email})
        if existing_user:
            logger.error(f"User with email {user_data.email} already exists")
            raise ValueError(f"User with email {user_data.email} already exists")
        
        # Check if user with username already exists
        existing_user = self.collection.find_one({"username": user_data.username})
        if existing_user:
            logger.error(f"User with username {user_data.username} already exists")
            raise ValueError(f"User with username {user_data.username} already exists")
        
        # Create user dictionary
        user_dict = create_user_dict(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=user_data.is_active
        )
        
        # Insert into MongoDB
        result = self.collection.insert_one(user_dict)
        
        if not result.inserted_id:
            logger.error("Failed to create user")
            raise RuntimeError("Failed to create user")
        
        # Return user response
        created_user = self.collection.find_one({"_id": result.inserted_id})
        return user_dict_to_response(created_user)
    
    def get_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            UserResponse or None: User data if found, None otherwise
        """
        user_data = self.collection.find_one({"_id": user_id})
        if user_data:
            return user_dict_to_response(user_data)
        return None
    
    def get_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get user by email (returns UserInDB which includes hashed password)
        
        Args:
            email: User email
            
        Returns:
            UserInDB or None: User data with password if found, None otherwise
        """
        user_data = self.collection.find_one({"email": email})
        if user_data:
            return user_dict_to_in_db(user_data)
        return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        Get all users with pagination
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List[UserResponse]: List of all users
        """
        users = self.collection.find().skip(skip).limit(limit)
        return [user_dict_to_response(user) for user in users]
    
    def update(self, user_id: str, user_data: UserUpdate, hashed_password: Optional[str] = None) -> Optional[UserResponse]:
        """
        Update user by ID
        
        Args:
            user_id: User ID
            user_data: User update data
            hashed_password: New hashed password (if password is being updated)
            
        Returns:
            UserResponse or None: Updated user data if successful, None otherwise
        """
        # Build update data
        update_data = {}
        if user_data.username is not None:
            update_data["username"] = user_data.username
        if user_data.email is not None:
            update_data["email"] = user_data.email
        if hashed_password is not None:
            update_data["hashed_password"] = hashed_password
        if user_data.is_active is not None:
            update_data["is_active"] = user_data.is_active
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        if not update_data:
            return self.get_by_id(user_id)
        
        # Update in MongoDB
        result = self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return None
        
        # Return updated user
        updated_user = self.collection.find_one({"_id": user_id})
        if updated_user:
            return user_dict_to_response(updated_user)
        return None
    
    def delete(self, user_id: str) -> bool:
        """
        Delete user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        result = self.collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
    
    def count(self) -> int:
        """
        Get total number of users
        
        Returns:
            int: Total number of users
        """
        return self.collection.count_documents({})


# Singleton instance
user_repository = UserRepository()
