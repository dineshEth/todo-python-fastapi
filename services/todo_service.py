"""
Todo service for business logic operations
"""
from typing import Optional, List
from models.todo import TodoCreate, TodoUpdate, TodoResponse, TodoStatus
from repositories.todo_repository import todo_repository
from repositories.user_repository import user_repository
import logging

logger = logging.getLogger(__name__)


class TodoService:
    """Service class for Todo business logic"""
    
    def __init__(self):
        """Initialize todo service with repository"""
        self.repository = todo_repository
        self.user_repository = user_repository
    
    def create_todo(self, user_id: str, todo_data: TodoCreate) -> TodoResponse:
        """
        Create a new todo for a user
        
        Args:
            user_id: User ID who owns the todo
            todo_data: Todo creation data
            
        Returns:
            TodoResponse: Created todo data
            
        Raises:
            ValueError: If user does not exist
        """
        # Verify user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.error(f"User with ID {user_id} not found")
            raise ValueError(f"User with ID {user_id} not found")
        
        # Create todo in repository
        return self.repository.create(user_id, todo_data)
    
    def get_todo_by_id(self, todo_id: str) -> Optional[TodoResponse]:
        """
        Get todo by ID
        
        Args:
            todo_id: Todo ID
            
        Returns:
            TodoResponse or None: Todo data if found, None otherwise
        """
        return self.repository.get_by_id(todo_id)
    
    def get_todos_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[TodoResponse]:
        """
        Get all todos by user ID
        
        Args:
            user_id: User ID
            skip: Number of todos to skip
            limit: Maximum number of todos to return
            
        Returns:
            List[TodoResponse]: List of todos for the user
        """
        return self.repository.get_by_user_id(user_id, skip, limit)
    
    def get_all_todos(self, skip: int = 0, limit: int = 100) -> List[TodoResponse]:
        """
        Get all todos with pagination
        
        Args:
            skip: Number of todos to skip
            limit: Maximum number of todos to return
            
        Returns:
            List[TodoResponse]: List of all todos
        """
        return self.repository.get_all(skip, limit)
    
    def update_todo(self, todo_id: str, user_id: str, todo_data: TodoUpdate) -> Optional[TodoResponse]:
        """
        Update todo by ID (only if user owns the todo)
        
        Args:
            todo_id: Todo ID
            user_id: User ID (must be owner of todo)
            todo_data: Todo update data
            
        Returns:
            TodoResponse or None: Updated todo data if successful, None otherwise
            
        Raises:
            PermissionError: If user does not own the todo
            ValueError: If todo not found
        """
        # Get todo to verify ownership
        todo = self.repository.get_by_id(todo_id)
        if not todo:
            logger.error(f"Todo with ID {todo_id} not found")
            raise ValueError(f"Todo with ID {todo_id} not found")
        
        # Verify user owns the todo
        if todo.user_id != user_id:
            logger.error(f"User {user_id} does not own todo {todo_id}")
            raise PermissionError(f"User {user_id} does not own todo {todo_id}")
        
        return self.repository.update(todo_id, todo_data)
    
    def delete_todo(self, todo_id: str, user_id: str) -> bool:
        """
        Delete todo by ID (only if user owns the todo)
        
        Args:
            todo_id: Todo ID
            user_id: User ID (must be owner of todo)
            
        Returns:
            bool: True if deletion successful, False otherwise
            
        Raises:
            PermissionError: If user does not own the todo
            ValueError: If todo not found
        """
        # Get todo to verify ownership
        todo = self.repository.get_by_id(todo_id)
        if not todo:
            logger.error(f"Todo with ID {todo_id} not found")
            raise ValueError(f"Todo with ID {todo_id} not found")
        
        # Verify user owns the todo
        if todo.user_id != user_id:
            logger.error(f"User {user_id} does not own todo {todo_id}")
            raise PermissionError(f"User {user_id} does not own todo {todo_id}")
        
        return self.repository.delete(todo_id)
    
    def mark_todo_completed(self, todo_id: str, user_id: str) -> Optional[TodoResponse]:
        """
        Mark a todo as completed
        
        Args:
            todo_id: Todo ID
            user_id: User ID (must be owner of todo)
            
        Returns:
            TodoResponse or None: Updated todo data if successful, None otherwise
        """
        todo_update = TodoUpdate(status=TodoStatus.COMPLETED)
        return self.update_todo(todo_id, user_id, todo_update)
    
    def get_todo_count(self) -> int:
        """
        Get total number of todos
        
        Returns:
            int: Total number of todos
        """
        return self.repository.count()
    
    def get_todo_count_by_user(self, user_id: str) -> int:
        """
        Get number of todos for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of todos for the user
        """
        return self.repository.count_by_user_id(user_id)


# Singleton instance
todo_service = TodoService()
