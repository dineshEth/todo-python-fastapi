"""
MongoDB database connection and session management
"""
from pymongo import MongoClient
from pymongo.database import Database
from config.settings import settings
from typing import Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Global database instance
_db: Optional[Database] = None


def get_database() -> Database:
    """
    Get MongoDB database instance (singleton pattern)
    
    Returns:
        Database: MongoDB database instance
    """
    global _db
    
    if _db is None:
        try:
            # Create MongoDB client
            client = MongoClient(settings.MONGO_URI)
            
            # Test the connection
            client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Get database
            _db = client[settings.MONGO_DB_NAME]
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"Could not connect to MongoDB: {e}")
    
    return _db


def close_database_connection() -> None:
    """Close MongoDB database connection"""
    global _db
    if _db is not None:
        # Get the client from database
        client = _db.client
        client.close()
        _db = None
        logger.info("MongoDB connection closed")


def get_collection(collection_name: str):
    """
    Get MongoDB collection by name
    
    Args:
        collection_name (str): Name of the collection
        
    Returns:
        Collection: MongoDB collection instance
    """
    db = get_database()
    return db[collection_name]
