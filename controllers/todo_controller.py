"""
Todo controller for todo management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from services.todo_service import todo_service
from services.auth_service import auth_service
from models.todo import TodoCreate, TodoUpdate, TodoResponse, TodoStatus, TodoPriority
from fastapi.security import OAuth2PasswordBearer
from models.user import UserResponse
import logging

logger = logging.getLogger(__name__)

# Create router for todo endpoints
router = APIRouter(prefix="/api/v1/todos", tags=["Todos"])

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserResponse:
    """
    Dependency to get current user from JWT token
    """
    user_id = auth_service.verify_token(token)
    if not user_id:
        logger.error("Invalid authentication credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    from services.user_service import user_service
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
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new todo"
)
async def create_todo(
    todo_data: TodoCreate,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> TodoResponse:
    """
    Create a new todo for the authenticated user
    
    Creates a new todo with the provided information for the current user.
    """
    try:
        todo = todo_service.create_todo(current_user.id, todo_data)
        logger.info(f"Todo created by user {current_user.id}")
        return todo
    except ValueError as e:
        logger.error(f"Todo creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model=List[TodoResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all todos"
)
async def get_all_todos(
    skip: int = 0,
    limit: int = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> List[TodoResponse]:
    """
    Get all todos in the system (admin view)
    
    Returns a list of all todos. This endpoint is accessible to all
    authenticated users but could be restricted to admins.
    """
    todos = todo_service.get_all_todos(skip, limit)
    logger.info(f"Retrieved {len(todos)} todos")
    return todos


@router.get(
    "/my-todos",
    response_model=List[TodoResponse],
    status_code=status.HTTP_200_OK,
    summary="Get my todos"
)
async def get_my_todos(
    skip: int = 0,
    limit: int = 100,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> List[TodoResponse]:
    """
    Get all todos for the current authenticated user
    
    Returns a list of todos owned by the current user.
    """
    todos = todo_service.get_todos_by_user_id(current_user.id, skip, limit)
    logger.info(f"Retrieved {len(todos)} todos for user {current_user.id}")
    return todos


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    summary="Get todo by ID"
)
async def get_todo_by_id(
    todo_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> TodoResponse:
    """
    Get a specific todo by ID
    
    Returns todo data if the todo exists and belongs to the current user.
    """
    try:
        todo = todo_service.get_todo_by_id(todo_id)
        if not todo:
            logger.error(f"Todo with ID {todo_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with ID {todo_id} not found"
            )
        
        # Verify user owns the todo
        if todo.user_id != current_user.id:
            logger.error(f"User {current_user.id} attempted to access todo {todo_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this todo"
            )
        
        logger.info(f"Retrieved todo with ID {todo_id}")
        return todo
        
    except ValueError as e:
        logger.error(f"Error getting todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    summary="Update todo"
)
async def update_todo(
    todo_id: str,
    todo_data: TodoUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> TodoResponse:
    """
    Update a todo by ID
    
    Updates a todo with the provided information. Only the owner can update their todos.
    """
    try:
        todo = todo_service.update_todo(todo_id, current_user.id, todo_data)
        if not todo:
            logger.error(f"Todo with ID {todo_id} not found or update failed")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with ID {todo_id} not found"
            )
        
        logger.info(f"Todo {todo_id} updated by user {current_user.id}")
        return todo
        
    except PermissionError as e:
        logger.error(f"Permission error updating todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        logger.error(f"Error updating todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete todo"
)
async def delete_todo(
    todo_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> None:
    """
    Delete a todo by ID
    
    Deletes a todo. Only the owner can delete their todos.
    """
    try:
        success = todo_service.delete_todo(todo_id, current_user.id)
        if not success:
            logger.error(f"Todo with ID {todo_id} not found or deletion failed")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with ID {todo_id} not found"
            )
        
        logger.info(f"Todo {todo_id} deleted by user {current_user.id}")
        return None
        
    except PermissionError as e:
        logger.error(f"Permission error deleting todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        logger.error(f"Error deleting todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{todo_id}/complete",
    response_model=TodoResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark todo as completed"
)
async def mark_todo_completed(
    todo_id: str,
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> TodoResponse:
    """
    Mark a todo as completed
    
    Marks a todo as completed. Only the owner can complete their todos.
    """
    try:
        todo = todo_service.mark_todo_completed(todo_id, current_user.id)
        if not todo:
            logger.error(f"Todo with ID {todo_id} not found or completion failed")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with ID {todo_id} not found"
            )
        
        logger.info(f"Todo {todo_id} marked as completed by user {current_user.id}")
        return todo
        
    except PermissionError as e:
        logger.error(f"Permission error completing todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        logger.error(f"Error completing todo: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/count",
    status_code=status.HTTP_200_OK,
    summary="Get todo count"
)
async def get_todo_count(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> dict:
    """
    Get total number of todos in the system
    """
    count = todo_service.get_todo_count()
    return {"count": count}


@router.get(
    "/my-todos/count",
    status_code=status.HTTP_200_OK,
    summary="Get my todo count"
)
async def get_my_todo_count(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> dict:
    """
    Get number of todos for the current user
    """
    count = todo_service.get_todo_count_by_user(current_user.id)
    return {"count": count}