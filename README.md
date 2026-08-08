# Todo FastAPI - MongoDB REST API

A clean, type-first REST API built with FastAPI, MongoDB, and JWT authentication following MVC architecture.

## Project Structure

```
todo-fastapi/
├── config/                    # Configuration files
│   ├── __init__.py
│   └── settings.py           # Application settings from environment variables
│
├── controllers/              # API controllers (route handlers)
│   ├── __init__.py
│   ├── auth_controller.py    # Authentication endpoints
│   ├── user_controller.py    # User management endpoints
│   └── todo_controller.py    # Todo management endpoints
│
├── database/                 # Database connection and utilities
│   ├── __init__.py
│   └── connection.py         # MongoDB connection management
│
├── models/                   # Data models and Pydantic schemas
│   ├── __init__.py
│   ├── user.py               # User model definitions
│   └── todo.py               # Todo model definitions
│
├── repositories/             # Data access layer (MongoDB operations)
│   ├── __init__.py
│   ├── user_repository.py    # User database operations
│   └── todo_repository.py    # Todo database operations
│
├── services/                 # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py       # Authentication services (JWT, password hashing)
│   ├── user_service.py       # User business logic
│   └── todo_service.py       # Todo business logic
│
├── utils/                    # Utility functions
│   └── __init__.py
│
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## Features

### User Management (5 CRUD Operations)
- **Create**: POST `/api/v1/users/` - Create a new user
- **Read**: GET `/api/v1/users/` - Get all users
- **Read**: GET `/api/v1/users/{user_id}` - Get user by ID
- **Read**: GET `/api/v1/users/me` - Get current authenticated user
- **Update**: PUT `/api/v1/users/{user_id}` - Update user
- **Delete**: DELETE `/api/v1/users/{user_id}` - Delete user

### Todo Management (5 CRUD Operations)
- **Create**: POST `/api/v1/todos/` - Create a new todo
- **Read**: GET `/api/v1/todos/` - Get all todos
- **Read**: GET `/api/v1/todos/{todo_id}` - Get todo by ID
- **Read**: GET `/api/v1/todos/my-todos` - Get current user's todos
- **Update**: PUT `/api/v1/todos/{todo_id}` - Update todo
- **Delete**: DELETE `/api/v1/todos/{todo_id}` - Delete todo
- **Special**: POST `/api/v1/todos/{todo_id}/complete` - Mark todo as completed

### Authentication
- **Login**: POST `/api/v1/auth/login` - Authenticate and get JWT token
- **Logout**: POST `/api/v1/auth/logout` - Invalidate token (client-side)

## Protected Routes

All routes except the following are protected and require JWT authentication:
- POST `/api/v1/auth/login`
- POST `/api/v1/users/` (user registration)
- GET `/api/v1/health` (health check)
- GET `/` (root endpoint)

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit the `.env` file with your MongoDB connection string and JWT secret:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=todo_app
JWT_SECRET_KEY=your-very-secure-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Run MongoDB

Ensure MongoDB is running locally or update the `MONGO_URI` in `.env` to point to your MongoDB instance.

### 4. Start the Server

```bash
# For development (with auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/api/docs`

## Usage Examples

### Create a User

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "is_active": true
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword123"
```

### Create a Todo

```bash
curl -X POST "http://localhost:8000/api/v1/todos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, Eggs, Bread",
    "status": "pending",
    "priority": "medium"
  }'
```

### Get My Todos

```bash
curl -X GET "http://localhost:8000/api/v1/todos/my-todos" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Type-First Design

This API follows a type-first approach with comprehensive Pydantic models:

- **Request Models**: Define the shape of incoming data
- **Response Models**: Define the shape of outgoing data
- **Database Models**: Define the structure of data in MongoDB
- **Service Models**: Define the data structures used in business logic

All models include proper type hints, field validation, and documentation.

## Clean Code Principles Applied

1. **Single Responsibility**: Each class and function has a single responsibility
2. **Separation of Concerns**: Clear separation between routes, services, and repositories
3. **Dependency Injection**: Services are injected into controllers
4. **Type Safety**: Comprehensive type hints throughout the codebase
5. **Documentation**: All functions and classes include docstrings
6. **Error Handling**: Proper error handling and logging
7. **DRY Principle**: Reusable code and utilities
8. **MVC Pattern**: Clear Model-View-Controller architecture

## API Versioning

All endpoints are prefixed with `/api/v1/` for versioning. This allows for future API versions without breaking existing clients.

## Technologies

- **FastAPI**: Web framework for building APIs
- **MongoDB**: NoSQL database for data storage
- **PyMongo**: MongoDB driver for Python
- **Pydantic**: Data validation and settings management
- **JWT**: JSON Web Tokens for authentication
- **Passlib**: Password hashing
- **Uvicorn**: ASGI server for FastAPI

## License

MIT License