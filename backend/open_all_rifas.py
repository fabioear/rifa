from app.db.session import SessionLocal
from app.models.rifa import Rifa, RifaStatus
from app.models.tenant import Tenant
from app.models.user import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def open_all_rifas():
    db = SessionLocal()
    try:
        rifas = db.query(Rifa).all()
        count = 0
        for rifa in rifas:
            if rifa.status != RifaStatus.ATIVA:
                rifa.status = RifaStatus.ATIVA
                count += 1
        
        if count > 0:
            db.commit()
            logger.info(f"Updated {count} rifas to ATIVA status.")
        else:
            logger.info("All rifas are already ATIVA.")
            
    except Exception as e:
        logger.error(f"Error updating rifas: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    open_all_rifas()
