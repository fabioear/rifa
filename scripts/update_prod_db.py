
import sys
import os
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.models.whatsapp_session import WhatsappSession
from app.db.base import Base

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection String (Tunnel)
# Port 5433 maps to remote 5432
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5433/app_db"

def update_db():
    try:
        engine = create_engine(DATABASE_URL)
        logger.info("Connecting to Production DB via Tunnel...")
        
        # 1. Create WhatsappSession table if not exists
        logger.info("Checking/Creating whatsapp_sessions table...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables checked/created.")

        # 2. Add valor_premio to rifas if not exists
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = [c['name'] for c in inspector.get_columns('rifas')]
            
            if 'valor_premio' not in columns:
                logger.info("Adding 'valor_premio' column to 'rifas' table...")
                conn.execute(text("ALTER TABLE rifas ADD COLUMN valor_premio NUMERIC(10, 2)"))
                conn.commit()
                logger.info("Column added successfully.")
            else:
                logger.info("'valor_premio' column already exists.")
                
    except Exception as e:
        logger.error(f"Error updating DB: {e}")
        raise

if __name__ == "__main__":
    update_db()
