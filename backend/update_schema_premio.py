import sys
import os
import logging
from sqlalchemy import text

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_schema():
    logger.info("Updating schema for premio_status...")
    try:
        with engine.connect() as connection:
            # Check if type exists
            result = connection.execute(text("SELECT 1 FROM pg_type WHERE typname = 'premiostatus'"))
            if not result.fetchone():
                logger.info("Creating Type PremioStatus...")
                connection.execute(text("CREATE TYPE premiostatus AS ENUM ('PENDING', 'WINNER', 'LOSER')"))
                connection.commit()
            
            # Check if column exists
            result = connection.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='rifa_numeros' AND column_name='premio_status'"
            ))
            if not result.fetchone():
                logger.info("Adding column premio_status to rifa_numeros...")
                connection.execute(text(
                    "ALTER TABLE rifa_numeros ADD COLUMN premio_status premiostatus NOT NULL DEFAULT 'PENDING'"
                ))
                connection.commit()
            
            logger.info("Schema updated successfully!")
            
    except Exception as e:
        logger.error(f"Error updating schema: {e}")
        raise e

if __name__ == "__main__":
    update_schema()
