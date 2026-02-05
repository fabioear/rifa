from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from app.models.antifraud import BlockedEntity, BlockedEntityType
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.user import User
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

# Configuração Hardcoded (Simples)
MAX_SIMULTANEOUS_RESERVATIONS = 5
COOLDOWN_SECONDS = 0
RATE_LIMIT_PER_MINUTE = 10

def check_antifraud(
    db: Session,
    user: User,
    ip_address: str,
    rifa_id: str
):
    if user.role == "admin":
        return

    # 1. Blacklist Check
    blocked = db.query(BlockedEntity).filter(
        ((BlockedEntity.type == BlockedEntityType.IP) & (BlockedEntity.value == ip_address)) |
        ((BlockedEntity.type == BlockedEntityType.USER) & (BlockedEntity.value == str(user.id))),
        BlockedEntity.tenant_id == user.tenant_id
    ).first()
    
    if blocked:
        raise HTTPException(status_code=403, detail=f"Blocked: {blocked.reason}")

    # 2. Reservation Limit Check (Active reservations)
    active_reservations = db.query(func.count(RifaNumero.id)).filter(
        RifaNumero.user_id == user.id,
        RifaNumero.status == NumeroStatus.RESERVADO,
        RifaNumero.rifa_id == rifa_id # Usually limit per rifa or global? "por usuário" implies global usually, but let's stick to rifa or global.
        # Let's assume global per tenant (which is filtered by user_id being in tenant)
    ).scalar()
    
    if active_reservations >= MAX_SIMULTANEOUS_RESERVATIONS:
        raise HTTPException(status_code=429, detail=f"Limite de {MAX_SIMULTANEOUS_RESERVATIONS} reservas simultâneas atingido.")

    # 3. Cooldown Check (Last reservation time)
    # Get latest reservation for this user
    last_reservation = db.query(RifaNumero).filter(
        RifaNumero.user_id == user.id,
        RifaNumero.status == NumeroStatus.RESERVADO
    ).order_by(RifaNumero.updated_at.desc()).first()
    
    if last_reservation and last_reservation.updated_at:
        # Ensure updated_at is timezone aware if stored that way. 
        # Postgres stores with timezone usually if configured.
        now = datetime.now(timezone.utc)
        
        # If updated_at is naive, assume UTC or convert. SQLAlchemy usually returns what DB has.
        # Assuming UTC for now.
        last_time = last_reservation.updated_at
        if last_time.tzinfo is None:
            last_time = last_time.replace(tzinfo=timezone.utc)
            
        if (now - last_time).total_seconds() < COOLDOWN_SECONDS:
             raise HTTPException(status_code=429, detail=f"Aguarde {COOLDOWN_SECONDS} segundos entre reservas.")

    # 4. Rate Limit (Reservations per minute per IP)
    # This is tricky without a separate table for IP logs. 
    # We can query RifaNumero but that only tracks successful reservations, not attempts.
    # But prompt says "Intercepta reserva, valida regras".
    # Using RifaNumero created_at/updated_at is a proxy for "successful reservations".
    # If we want to limit *attempts*, we need middleware/Redis.
    # "Anti-fraude simples" -> Limit successful reservations per minute is likely enough to prevent hoarding.
    
    one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
    
    # We need to join User to check IP? No, we don't store IP on RifaNumero.
    # We only have User ID.
    # So we can limit by User ID per minute (which we effectively did with Cooldown, but Cooldown is 10s -> 6/min).
    # If we want IP limit, we need to log IP or check BlockedEntity.
    # The prompt says "Rate limit por IP".
    # Since we don't store IP in RifaNumero, we can't strictly enforce "Rate limit per IP" using historical DB data
    # UNLESS we add ip_address to RifaNumero or have a separate log.
    # AuditLog has IP!
    # Let's check AuditLog for "RESERVE_NUMBER" actions in last minute by this IP.
    
    from app.models.audit_finance import AuditLog
    
    recent_actions_by_ip = db.query(func.count(AuditLog.id)).filter(
        AuditLog.ip_address == ip_address,
        AuditLog.action == "RESERVE_NUMBER",
        AuditLog.created_at >= one_minute_ago
    ).scalar()
    
    if recent_actions_by_ip >= RATE_LIMIT_PER_MINUTE:
         # Auto-block IP?
         # "Estados que disparam antifraude: muitas reservas..."
         # Let's just block the request for now.
         raise HTTPException(status_code=429, detail="Muitas requisições deste IP. Tente novamente mais tarde.")

