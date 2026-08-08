"""
Application settings and configuration
"""
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Todo API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "A Todo API with User and Todo management"
    
    # MongoDB
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017",
        env="MONGO_URI"
    )
    MONGO_DB_NAME: str = Field(
        default="todo_app",
        env="MONGO_DB_NAME"
    )
    
    # JWT Authentication
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        env="JWT_ALGORITHM"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Security
    HASHING_ALGORITHM: str = "bcrypt"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


# Create settings instance
settings = Settings()
