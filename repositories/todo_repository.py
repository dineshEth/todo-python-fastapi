"""
Todo repository for database operations
"""
from typing import Optional, List
from pymongo.collection import Collection
from database.connection import get_collection
from models.todo import TodoCreate, TodoUpdate, TodoResponse, TodoStatus, TodoPriority, todo_dict_to_response, create_todo_dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TodoRepository:
    """Repository class for Todo CRUD operations"""
    
    def __init__(self):
        """Initialize todo repository with MongoDB collection"""
        self.collection: Collection = get_collection("todos")
        
        # Create indexes for better performance
        self.collection.create_index("user_id")
        self.collection.create_index("status")
        self.collection.create_index("priority")
        self.collection.create_index("created_at")
    
    def create(self, user_id: str, todo_data: TodoCreate) -> TodoResponse:
        """
        Create a new todo in the database
        
        Args:
            user_id: ID of the user who owns this todo
            todo_data: Todo creation data
            
        Returns:
            TodoResponse: Created todo data
        """
        # Create todo dictionary
        todo_dict = create_todo_dict(
            user_id=user_id,
            title=todo_data.title,
            description=todo_data.description,
            status=todo_data.status,
            priority=todo_data.priority
        )
        
        # Insert into MongoDB
        result = self.collection.insert_one(todo_dict)
        
        if not result.inserted_id:
            logger.error("Failed to create todo")
            raise RuntimeError("Failed to create todo")
        
        # Return todo response
        created_todo = self.collection.find_one({"_id": result.inserted_id})
        return todo_dict_to_response(created_todo)
    
    def get_by_id(self, todo_id: str) -> Optional[TodoResponse]:
        """
        Get todo by ID
        
        Args:
            todo_id: Todo ID
            
        Returns:
            TodoResponse or None: Todo data if found, None otherwise
        """
        todo_data = self.collection.find_one({"_id": todo_id})
        if todo_data:
            return todo_dict_to_response(todo_data)
        return None
    
    def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[TodoResponse]:
        """
        Get all todos by user ID with pagination
        
        Args:
            user_id: User ID
            skip: Number of todos to skip
            limit: Maximum number of todos to return
            
        Returns:
            List[TodoResponse]: List of todos for the user
        """
        todos = self.collection.find({"user_id": user_id}).skip(skip).limit(limit)
        return [todo_dict_to_response(todo) for todo in todos]
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[TodoResponse]:
        """
        Get all todos with pagination
        
        Args:
            skip: Number of todos to skip
            limit: Maximum number of todos to return
            
        Returns:
            List[TodoResponse]: List of all todos
        """
        todos = self.collection.find().skip(skip).limit(limit)
        return [todo_dict_to_response(todo) for todo in todos]
    
    def update(self, todo_id: str, todo_data: TodoUpdate) -> Optional[TodoResponse]:
        """
        Update todo by ID
        
        Args:
            todo_id: Todo ID
            todo_data: Todo update data
            
        Returns:
            TodoResponse or None: Updated todo data if successful, None otherwise
        """
        # Build update data
        update_data = {}
        if todo_data.title is not None:
            update_data["title"] = todo_data.title
        if todo_data.description is not None:
            update_data["description"] = todo_data.description
        if todo_data.status is not None:
            update_data["status"] = todo_data.status.value
        if todo_data.priority is not None:
            update_data["priority"] = todo_data.priority.value
        if todo_data.completed_at is not None:
            update_data["completed_at"] = todo_data.completed_at
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        if not update_data:
            return self.get_by_id(todo_id)
        
        # Update in MongoDB
        result = self.collection.update_one(
            {"_id": todo_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return None
        
        # Return updated todo
        updated_todo = self.collection.find_one({"_id": todo_id})
        if updated_todo:
            return todo_dict_to_response(updated_todo)
        return None
    
    def delete(self, todo_id: str) -> bool:
        """
        Delete todo by ID
        
        Args:
            todo_id: Todo ID
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        result = self.collection.delete_one({"_id": todo_id})
        return result.deleted_count > 0
    
    def count(self) -> int:
        """
        Get total number of todos
        
        Returns:
            int: Total number of todos
        """
        return self.collection.count_documents({})
    
    def count_by_user_id(self, user_id: str) -> int:
        """
        Get number of todos for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of todos for the user
        """
        return self.collection.count_documents({"user_id": user_id})


# Singleton instance
todo_repository = TodoRepository()
