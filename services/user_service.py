"""
User service for business logic operations
"""
from typing import Optional, List
from models.user import UserCreate, UserUpdate, UserResponse, UserInDB
from repositories.user_repository import user_repository
from services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class for User business logic"""
    
    def __init__(self):
        """Initialize user service with repository"""
        self.repository = user_repository
        self.auth_service = auth_service
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user
        
        Args:
            user_data: User creation data
            
        Returns:
            UserResponse: Created user data
        """
        # Hash password
        hashed_password = self.auth_service.hash_password(user_data.password)
        
        # Create user in repository
        return self.repository.create(user_data, hashed_password)
    
    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            UserResponse or None: User data if found, None otherwise
        """
        return self.repository.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get user by email (for authentication)
        
        Args:
            email: User email
            
        Returns:
            UserInDB or None: User data with password if found, None otherwise
        """
        return self.repository.get_by_email(email)
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        Get all users with pagination
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List[UserResponse]: List of all users
        """
        return self.repository.get_all(skip, limit)
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        Update user by ID
        
        Args:
            user_id: User ID
            user_data: User update data
            
        Returns:
            UserResponse or None: Updated user data if successful, None otherwise
        """
        # Hash new password if provided
        hashed_password = None
        if user_data.password:
            hashed_password = self.auth_service.hash_password(user_data.password)
        
        return self.repository.update(user_id, user_data, hashed_password)
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self.repository.delete(user_id)
    
    def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """
        Authenticate user by email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            UserInDB or None: User data if authentication successful, None otherwise
        """
        user = self.get_user_by_email(email)
        
        if user and self.auth_service.verify_password(password, user.hashed_password):
            return user
        
        return None
    
    def get_user_count(self) -> int:
        """
        Get total number of users
        
        Returns:
            int: Total number of users
        """
        return self.repository.count()


# Singleton instance
user_service = UserService()
