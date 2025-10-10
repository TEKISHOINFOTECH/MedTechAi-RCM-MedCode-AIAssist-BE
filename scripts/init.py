"""
Initialization script for MedTechAi RCM Assistant.
"""
import asyncio
import logging
from pathlib import Path

from app.core import init_db
from config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize the application."""
    logger.info("Starting MedTechAi RCM Assistant initialization...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Create required directories
    directories = [
        "data/raw",
        "data/processed", 
        "data/external",
        "logs",
        "static/docs",
        "deployment/docker",
        "deployment/kubernetes",
        "deployment/terraform",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Create .gitkeep files for empty directories
    for directory in directories:
        gitkeep_file = Path(directory) / ".gitkeep"
        gitkeep_file.touch()
    
    logger.info("MedTechAi RCM Assistant initialization completed!")
    logger.info(f"Configuration: {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")


if __name__ == "__main__":
    main()
