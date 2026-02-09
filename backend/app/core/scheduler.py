from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.core.audit import AuditLogger
from datetime import datetime, timezone, timedelta
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.rifa import Rifa, RifaStatus
from app.db.session import SessionLocal
from app.models.audit_finance import AuditLog
from app.models.antifraud import BlockedEntity, BlockedEntityType
from sqlalchemy import func, or_, and_
import logging

logger = logging.getLogger(__name__)

def run_antifraud_analysis():
    """
    Analyze logs for suspicious behavior and block entities.
    Rules:
    1. IP with > 100 reservations in last hour -> Block IP
    """
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        
        # 1. IP Rate Limit (Heavy) por tenant
        suspicious_ips = db.query(
            AuditLog.tenant_id,
            AuditLog.ip_address,
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.action == "RESERVE_NUMBER",
            AuditLog.created_at >= one_hour_ago,
            AuditLog.ip_address.isnot(None),
            AuditLog.tenant_id.isnot(None)
        ).group_by(AuditLog.tenant_id, AuditLog.ip_address).having(func.count(AuditLog.id) > 100).all()
        
        for tenant_id, ip, count in suspicious_ips:
            # Check if already blocked
            exists = db.query(BlockedEntity).filter(
                BlockedEntity.type == BlockedEntityType.IP,
                BlockedEntity.value == ip,
                BlockedEntity.tenant_id == tenant_id
            ).first()
            
            if not exists:
                logger.warning(f"Blocking IP {ip} due to suspicious activity ({count} reservations/hour)")
                blocked = BlockedEntity(
                    type=BlockedEntityType.IP,
                    value=ip,
                    reason=f"Auto-block: {count} reservations in 1 hour",
                    tenant_id=tenant_id
                )
                db.add(blocked)

        # 2. Excessive Expirations (User) por tenant
        suspicious_users = db.query(
            AuditLog.tenant_id,
            AuditLog.actor_id,
            func.count(AuditLog.id).label("count")
        ).filter(
            AuditLog.action == "RESERVATION_EXPIRED_JOB",
            AuditLog.created_at >= one_hour_ago,
            AuditLog.actor_id.isnot(None),
            AuditLog.tenant_id.isnot(None)
        ).group_by(AuditLog.tenant_id, AuditLog.actor_id).having(func.count(AuditLog.id) > 10).all()

        for tenant_id, user_id, count in suspicious_users:
            if not user_id:
                continue

            user_id_str = str(user_id)

            exists = db.query(BlockedEntity).filter(
                BlockedEntity.type == BlockedEntityType.USER,
                BlockedEntity.value == user_id_str,
                BlockedEntity.tenant_id == tenant_id
            ).first()
            
            if not exists:
                logger.warning(f"Blocking User {user_id_str} due to excessive expirations ({count}/hour)")
                blocked = BlockedEntity(
                    type=BlockedEntityType.USER,
                    value=user_id_str,
                    reason=f"Auto-block: {count} expired reservations in 1 hour",
                    tenant_id=tenant_id
                )
                db.add(blocked)
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error in antifraud analysis: {e}")
    finally:
        db.close()

def release_expired_reservations():
    """
    Check for expired reservations and set them to EXPIRADO.
    """
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        expired_numbers = db.query(RifaNumero).filter(
            RifaNumero.status == NumeroStatus.RESERVADO,
            RifaNumero.reserved_until < now
        ).all()
        
        if expired_numbers:
            logger.info(f"Found {len(expired_numbers)} expired reservations. Expiring...")
            for num in expired_numbers:
                old_status = num.status
                old_user_id = num.user_id

                num.status = NumeroStatus.LIVRE
                num.user_id = None # Prompt explicitly asks to clean user_id
                num.payment_id = None
                num.reserved_until = None
                
                AuditLogger.log(
                    db=db,
                    action="RESERVATION_EXPIRED_JOB",
                    entity_type="RifaNumero",
                    entity_id=str(num.id),
                    actor_id=str(old_user_id) if old_user_id else None,
                    actor_role="system",
                    old_value={"status": str(old_status)},
                    new_value={"status": "livre"},
                    tenant_id=num.tenant_id
                )
            db.commit()
    except Exception as e:
        logger.error(f"Error releasing expired reservations: {e}")
        db.rollback()
    finally:
        db.close()

def close_expired_rifas():
    """
    Check for active raffles that reached draw date.
    """
    db = SessionLocal()
    try:
        # Adjust for Brazil time (UTC-3)
        # Using ZoneInfo to handle timezone correctly instead of hardcoded subtraction
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo
            
        br_tz = ZoneInfo("America/Sao_Paulo")
        now = datetime.now(br_tz)
        
        expired_rifas = db.query(Rifa).filter(
            Rifa.status == RifaStatus.ATIVA,
            or_(
                and_(Rifa.hora_encerramento.isnot(None), Rifa.hora_encerramento <= now),
                and_(Rifa.hora_encerramento.is_(None), Rifa.data_sorteio <= now)
            )
        ).all()
        
        if expired_rifas:
            logger.info(f"Found {len(expired_rifas)} expired raffles. Closing...")
            for rifa in expired_rifas:
                old_status = rifa.status
                rifa.status = RifaStatus.ENCERRADA
                
                AuditLogger.log(
                    db=db,
                    action="RIFA_CLOSED_JOB",
                    entity_type="Rifa",
                    entity_id=str(rifa.id),
                    actor_role="system",
                    old_value={"status": str(old_status)},
                    new_value={"status": "encerrada"},
                    tenant_id=rifa.tenant_id
                )
            db.commit()
    except Exception as e:
        logger.error(f"Error closing expired raffles: {e}")
        db.rollback()
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(release_expired_reservations, 'interval', minutes=1)
scheduler.add_job(close_expired_rifas, 'interval', minutes=1)
scheduler.add_job(run_antifraud_analysis, 'interval', minutes=5)
