import sys
import os
import logging

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine
from app.db.base import Base
# Import all models to ensure they are registered with Base
from app.models import user, rifa, rifa_numero

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_db():
    logger.info("Resetting database schema...")
    try:
        # Drop all tables
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database schema reset successfully!")
        
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise e

if __name__ == "__main__":
    reset_db()
