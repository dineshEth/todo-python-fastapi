"""
Todo model definitions using Pydantic for data validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum


class TodoStatus(str, Enum):
    """Status enum for todos"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TodoPriority(str, Enum):
    """Priority enum for todos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TodoBase(BaseModel):
    """Base todo model with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Todo title")
    description: Optional[str] = Field(default=None, max_length=1000, description="Todo description")
    status: TodoStatus = Field(default=TodoStatus.PENDING, description="Todo status")
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM, description="Todo priority")


class TodoCreate(TodoBase):
    """Todo model for creating new todos"""
    pass


class TodoUpdate(BaseModel):
    """Todo model for updating existing todos"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[TodoStatus] = Field(default=None)
    priority: Optional[TodoPriority] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


class TodoResponse(TodoBase):
    """Todo model for API responses"""
    id: str = Field(..., description="Todo's unique identifier")
    user_id: str = Field(..., description="User who owns this todo")
    created_at: datetime = Field(..., description="When the todo was created")
    updated_at: datetime = Field(..., description="When the todo was last updated")
    completed_at: Optional[datetime] = Field(default=None, description="When the todo was completed")
    
    class Config:
        from_attributes = True  # For Pydantic v2 compatibility with ORM mode


# MongoDB schema for Todo
class TodoDict(BaseModel):
    """Todo data as stored in MongoDB (dictionary format)"""
    _id: str
    user_id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


def create_todo_dict(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    status: TodoStatus = TodoStatus.PENDING,
    priority: TodoPriority = TodoPriority.MEDIUM
) -> dict:
    """
    Create a todo dictionary for MongoDB insertion
    
    Args:
        user_id: ID of the user who owns this todo
        title: Todo title
        description: Todo description
        status: Todo status
        priority: Todo priority
        
    Returns:
        dict: Todo data ready for MongoDB
    """
    now = datetime.utcnow()
    return {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "description": description,
        "status": status.value,
        "priority": priority.value,
        "created_at": now,
        "updated_at": now,
        "completed_at": None
    }


def todo_dict_to_response(todo_data: dict) -> TodoResponse:
    """
    Convert MongoDB todo dictionary to TodoResponse model
    
    Args:
        todo_data: Todo data from MongoDB
        
    Returns:
        TodoResponse: Todo response model
    """
    return TodoResponse(
        id=str(todo_data["_id"]),
        user_id=str(todo_data["user_id"]),
        title=todo_data["title"],
        description=todo_data.get("description"),
        status=TodoStatus(todo_data["status"]),
        priority=TodoPriority(todo_data["priority"]),
        created_at=todo_data["created_at"],
        updated_at=todo_data["updated_at"],
        completed_at=todo_data.get("completed_at")
    )
