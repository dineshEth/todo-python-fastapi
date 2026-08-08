"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.logger import Middleware as LoggerMiddleware
import logging
from config.settings import settings
from controllers import user_router, todo_router, auth_router
from database.connection import get_database, close_database_connection
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(todo_router)
    
    # Health check endpoint
    @app.get("/api/v1/health", tags=["Health"])
    async def health_check() -> dict:
        """
        Health check endpoint
        
        Returns basic health information and MongoDB connection status.
        """
        try:
            db = get_database()
            db.command('ping')
            return {
                "status": "healthy",
                "app_name": settings.APP_NAME,
                "app_version": settings.APP_VERSION,
                "database": "connected"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> dict:
        """
        Root endpoint
        
        Returns basic API information.
        """
        return {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "description": settings.APP_DESCRIPTION,
            "docs": "/api/docs",
            "health": "/api/v1/health"
        }
    
    # Startup event
    @app.on_event("startup")
    async def startup_event() -> None:
        """Startup event handler"""
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        try:
            get_database()
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Shutdown event handler"""
        logger.info("Shutting down application")
        close_database_connection()
    
    return app


# Create application instance
app = create_app()


# For development: run with uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    


