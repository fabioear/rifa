from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select, cast, Integer
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from jose import jwt, JWTError

from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_active_user, get_current_active_superuser
from app.schemas.rifa import RifaCreate, RifaResponse, RifaUpdate, RifaStatusUpdate, WinnerResponse
from app.schemas.rifa_numero import RifaNumeroResponse
from app.models.rifa import Rifa, RifaStatus, RifaTipo
from app.models.rifa_ganhador import RifaGanhador
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.admin_settings import AdminSettings
from app.core.config import settings
from app.core.audit import AuditLogger
from services.whatsapp_service import whatsapp_service
from app.models.audit_finance import AuditLog
from app.db.session import SessionLocal
import logging

logger = logging.getLogger(__name__)

def notify_users_new_rifa(rifa_id: uuid.UUID, tenant_id: uuid.UUID):
    logger.info(f"Starting new raffle notification for Rifa {rifa_id} (Tenant {tenant_id})")
    db = SessionLocal()
    try:
        rifa = db.query(Rifa).get(rifa_id)
        if not rifa:
            logger.error(f"Rifa {rifa_id} not found during notification")
            return
        
        # Only notify if ATIVA
        if rifa.status != RifaStatus.ATIVA:
            logger.info(f"Rifa {rifa_id} is not ATIVA (Status: {rifa.status}). Skipping notification.")
            return

        users = db.query(User).filter(
            User.tenant_id == tenant_id,
            User.whatsapp_opt_in == True,
            User.phone.isnot(None)
        ).all()
        
        logger.info(f"Found {len(users)} users with WhatsApp Opt-In")
        
        count_sent = 0
        for user in users:
                try:
                    already = db.query(AuditLog).filter(
                        AuditLog.action == "WHATSAPP_NOTIFIED_RIFA",
                        AuditLog.entity_type == "user",
                        AuditLog.entity_id == str(user.id),
                        AuditLog.tenant_id == tenant_id,
                        AuditLog.new_value['rifa_id'].astext == str(rifa.id)
                    ).first()
                    if already:
                        continue
                    
                    sid = whatsapp_service.send_new_raffle_notification(
                        user_phone=user.phone,
                        rifa_nome=rifa.titulo,
                        data_sorteio=rifa.data_sorteio,
                        tipo=rifa.tipo_rifa.value if hasattr(rifa.tipo_rifa, 'value') else str(rifa.tipo_rifa),
                        rifa_id=str(rifa.id)
                    )
                    
                    if sid:
                        count_sent += 1
                        AuditLogger.log(
                            db=db,
                            action="WHATSAPP_NOTIFIED_RIFA",
                            entity_type="user",
                            entity_id=str(user.id),
                            actor_id="system",
                            actor_role="system",
                            old_value=None,
                            new_value={"rifa_id": str(rifa.id), "titulo": rifa.titulo},
                            tenant_id=tenant_id
                        )
                        db.commit()
                except Exception as e:
                    logger.error(f"Error notifying user {user.id}: {e}")
        
        logger.info(f"Finished notifications. Sent to {count_sent} users.")
                
    finally:
        db.close()

router = APIRouter()

@router.get("/recent-winners", response_model=List[WinnerResponse])
def get_recent_winners(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    winners = db.query(RifaGanhador).order_by(RifaGanhador.created_at.desc()).limit(limit).all()
    
    response = []
    
    if not winners:
        # Mock winners for testing if no real winners exist
        mock_winners = [
            {"user_name": "Carlos Silva", "rifa_title": "iPhone 15 Pro Max", "numero": "159", "hours_ago": 0},
            {"user_name": "Ana Oliveira", "rifa_title": "Honda Titan 160", "numero": "042", "hours_ago": 1},
            {"user_name": "Marcos Santos", "rifa_title": "R$ 5.000 no PIX", "numero": "777", "hours_ago": 2},
            {"user_name": "Fernanda Costa", "rifa_title": "PlayStation 5", "numero": "333", "hours_ago": 3},
            {"user_name": "Roberto Lima", "rifa_title": "Salário Extra", "numero": "010", "hours_ago": 4},
        ]
        
        for mock in mock_winners:
            response.append(WinnerResponse(
                user_name=mock["user_name"],
                avatar_url=None,
                rifa_title=mock["rifa_title"],
                numero=mock["numero"],
                data_ganho=datetime.now() - timedelta(hours=mock["hours_ago"])
            ))
        return response

    for winner in winners:
        # Ensure relationships are loaded or handle None
        user_name = winner.user.name if winner.user else "Usuário Removido"
        avatar_url = winner.user.avatar_url if winner.user else None
        rifa_title = winner.rifa.titulo if winner.rifa else "Rifa Removida"
        numero_val = winner.numero.numero if winner.numero else "???"
        
        response.append(WinnerResponse(
            user_name=user_name,
            avatar_url=avatar_url,
            rifa_title=rifa_title,
            numero=numero_val,
            data_ganho=winner.created_at
        ))
        
    return response

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token", auto_error=False)

def get_current_user_optional(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme_optional)
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user

from app.models.tenant import Tenant
from app.core.tenant import get_tenant_by_host
from app.core.antifraud import check_antifraud
from fastapi import Request

# ...

@router.get("/user/minhas-rifas", response_model=List[dict])
def get_user_rifas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    """
    Retorna as rifas que o usuário comprou números, com status de ganho/perda.
    """
    # Find all numbers bought by user
    numeros = db.query(RifaNumero).filter(
        RifaNumero.user_id == current_user.id,
        RifaNumero.status == NumeroStatus.PAGO,
        RifaNumero.tenant_id == current_tenant.id
    ).all()
    
    # Group by Rifa
    rifas_map = {}
    
    for num in numeros:
        if num.rifa_id not in rifas_map:
            rifa = db.query(Rifa).filter(Rifa.id == num.rifa_id).first()
            if rifa:
                rifas_map[num.rifa_id] = {
                    "rifa": rifa,
                    "numeros": []
                }
        
        if num.rifa_id in rifas_map:
            rifas_map[num.rifa_id]["numeros"].append({
                "numero": num.numero,
                "status": num.status,
                "premio_status": num.premio_status, # winner, loser, pending
                "data_compra": num.updated_at
            })
            
    # Format response
    result = []
    for rifa_id, data in rifas_map.items():
        rifa = data["rifa"]
        result.append({
            "id": rifa.id,
            "titulo": rifa.titulo,
            "status": rifa.status,
            "data_sorteio": rifa.data_sorteio,
            "resultado": rifa.resultado,
            "numeros_comprados": data["numeros"]
        })
        
    return result


@router.post("/", response_model=RifaResponse)
def create_rifa(
    rifa_in: RifaCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifa = Rifa(**rifa_in.dict(), owner_id=current_user.id, tenant_id=current_tenant.id)
    db.add(rifa)
    db.commit()
    db.refresh(rifa)
    
    # Generate numbers automatically
    numeros = []
    if rifa.tipo_rifa == RifaTipo.MILHAR:
        numeros = [f"{i:04d}" for i in range(1, 10000)] + ["0000"]
    elif rifa.tipo_rifa == RifaTipo.CENTENA:
        numeros = [f"{i:03d}" for i in range(1, 1000)] + ["000"]
    elif rifa.tipo_rifa == RifaTipo.DEZENA:
        numeros = [f"{i:02d}" for i in range(1, 100)] + ["00"]
    elif rifa.tipo_rifa == RifaTipo.GRUPO:
        numeros = [f"{i:02d}" for i in range(1, 26)]
        
    db.bulk_save_objects([
        RifaNumero(
            rifa_id=rifa.id,
            tipo=rifa.tipo_rifa,
            numero=num,
            status=NumeroStatus.LIVRE,
            tenant_id=current_tenant.id
        ) for num in numeros
    ])
    db.commit()
    
    # Trigger notification if Active
    if rifa.status == RifaStatus.ATIVA:
        background_tasks.add_task(notify_users_new_rifa, rifa.id, current_tenant.id)

    return rifa

@router.put("/{rifa_id}", response_model=RifaResponse)
def update_rifa(
    rifa_id: uuid.UUID,
    rifa_in: RifaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")
        
    for field, value in rifa_in.dict(exclude_unset=True).items():
        setattr(rifa, field, value)
        
    db.commit()
    db.refresh(rifa)
    return rifa

@router.patch("/{rifa_id}/status", response_model=RifaResponse)
def update_rifa_status(
    rifa_id: uuid.UUID,
    status_in: RifaStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")
        
    old_status = rifa.status
    rifa.status = status_in.status
    db.commit()
    db.refresh(rifa)
    
    # Trigger notification if changed to ATIVA
    if rifa.status == RifaStatus.ATIVA and old_status != RifaStatus.ATIVA:
        background_tasks.add_task(notify_users_new_rifa, rifa.id, current_tenant.id)
        
    return rifa

# --- Public Routes ---

@router.get("/", response_model=List[RifaResponse])
def read_rifas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifas = db.query(Rifa).filter(Rifa.tenant_id == current_tenant.id).offset(skip).limit(limit).all()
    return rifas

@router.get("/{rifa_id}", response_model=RifaResponse)
def read_rifa(
    rifa_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")
    return rifa

@router.get("/{rifa_id}/numeros", response_model=List[RifaNumeroResponse])
def read_rifa_numeros(
    rifa_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    numeros = db.query(RifaNumero).filter(
        RifaNumero.rifa_id == rifa_id, 
        RifaNumero.tenant_id == current_tenant.id
    ).order_by(cast(RifaNumero.numero, Integer)).all()
    
    results = []
    for num in numeros:
        is_owner = False
        if current_user:
             # Debug
             # print(f"Checking ownership: num.user_id={num.user_id} ({type(num.user_id)}) vs current_user.id={current_user.id} ({type(current_user.id)})")
             if num.user_id == current_user.id:
                 is_owner = True
        
        # Determine visibility based on status and ownership
        # Status is always returned, but maybe frontend handles display
        # The prompt says: "RESERVADO: dono vê como 'em pagamento', outros veem como bloqueado"
        # We will return the real status and 'is_owner' so frontend can decide label.
        
        # Privacy: Don't show user_id of others
        if not is_owner:
            num.user_id = None
            num.payment_id = None
            
        # If EXPIRADO, frontend should treat as available/clickable
        # If CANCELADO, frontend should treat as blocked? Prompt says "PAGO e CANCELADO: bloqueados"
        # So we just pass the status as is.
        
        num.is_owner = is_owner
        results.append(num)
        
    return results

# --- Purchase/Reservation Logic ---

@router.post("/{rifa_id}/numeros/{numero_id}/reservar", response_model=dict)
def reserve_numero(
    rifa_id: uuid.UUID,
    numero_id: str, # Can be UUID or string number
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    # Anti-Fraud Check
    ip_address = request.headers.get("x-forwarded-for") or request.client.host
    if ip_address and "," in ip_address:
        ip_address = ip_address.split(",")[0].strip()
        
    check_antifraud(db, current_user, ip_address, str(rifa_id))

    # 1. Get Rifa and check status
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")
    if rifa.status != RifaStatus.ATIVA:
        raise HTTPException(status_code=400, detail="Rifa não está ativa para compras")
    
    # 2. Get Admin Settings for timeout
    admin_settings = db.query(AdminSettings).filter(AdminSettings.user_id == rifa.owner_id).first()
    timeout_minutes = admin_settings.reservation_timeout_minutes if admin_settings else 20
    
    # 3. Atomic Transaction with Row Locking
    try:
        # Determine if numero_id is UUID or string
        try:
            uuid_obj = uuid.UUID(numero_id)
            is_uuid = True
        except ValueError:
            is_uuid = False
            
        query = db.query(RifaNumero).filter(RifaNumero.rifa_id == rifa_id, RifaNumero.tenant_id == current_tenant.id)
        if is_uuid:
            query = query.filter(RifaNumero.id == uuid_obj)
        else:
            query = query.filter(RifaNumero.numero == numero_id)
            
        num_obj = query.with_for_update().first()
        
        if not num_obj:
            raise HTTPException(status_code=404, detail="Número não encontrado")
            
        # Check if available
        # Allowed states for new reservation: LIVRE or EXPIRADO
        if num_obj.status not in [NumeroStatus.LIVRE, NumeroStatus.EXPIRADO]:
            # Check if it's reserved by ME (allow re-checkout)
            if num_obj.status == NumeroStatus.RESERVADO and num_obj.user_id == current_user.id:
                # Return existing payment info
                 return {
                    "message": "Número já reservado por você",
                    "payment_id": num_obj.payment_id,
                    "expires_at": num_obj.reserved_until
                }
            else:
                raise HTTPException(status_code=409, detail="Número indisponível")

        # 4. Reserve
        reservation_time = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        payment_id = str(uuid.uuid4())
        
        num_obj.status = NumeroStatus.RESERVADO
        num_obj.user_id = current_user.id
        num_obj.reserved_until = reservation_time
        num_obj.payment_id = payment_id
        
        # Audit
        AuditLogger.log(
            db=db,
            action="RESERVE_NUMBER",
            entity_type="RifaNumero",
            entity_id=str(num_obj.id),
            actor_id=str(current_user.id),
            actor_role=current_user.role,
            old_value={"status": "livre"},
            new_value={"status": "reservado", "payment_id": payment_id},
            tenant_id=current_tenant.id,
            ip_address=ip_address
        )

        db.commit()
        
        return {
            "message": "Número reservado com sucesso",
            "numero": num_obj.numero,
            "payment_id": payment_id,
            "expires_at": reservation_time
        }
        
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- Admin Manual Actions ---

@router.post("/{rifa_id}/numeros/{numero}/cancelar", response_model=dict)
def cancel_numero_admin(
    rifa_id: uuid.UUID,
    numero: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Admin manually cancels a number reservation/purchase.
    """
    num_obj = db.query(RifaNumero).filter(
        RifaNumero.rifa_id == rifa_id,
        RifaNumero.numero == numero
    ).first()
    
    if not num_obj:
        raise HTTPException(status_code=404, detail="Número não encontrado")
        
    old_status = num_obj.status
    num_obj.status = NumeroStatus.CANCELADO
    # Keep history? Or clear? Prompt says "Manter histórico" generally for webhooks, 
    # but manual cancel usually implies voiding. Let's keep data but change status.
    num_obj.reserved_until = None
    
    # Audit
    AuditLogger.log(
        db=db,
        action="ADMIN_CANCEL_NUMBER",
        entity_type="RifaNumero",
        entity_id=str(num_obj.id),
        actor_id=str(current_user.id),
        actor_role="admin",
        old_value={"status": str(old_status)},
        new_value={"status": "cancelado"}
    )
    
    # Log Payment Cancelled if it was PAID or RESERVED
    from app.models.audit_finance import PaymentLog, PaymentLogMethod, PaymentLogStatus
    
    # If it had a payment_id, log cancellation in finance
    if num_obj.payment_id:
         # Fetch Rifa for price
         rifa = db.query(Rifa).get(num_obj.rifa_id)
         valor = rifa.preco_numero if rifa else 0
         
         pay_log = PaymentLog(
            rifa_id=num_obj.rifa_id,
            numero_id=num_obj.id,
            user_id=num_obj.user_id,
            payment_id=num_obj.payment_id,
            valor=valor,
            metodo=PaymentLogMethod.PIX, # Assume Pix for manual or whatever
            status=PaymentLogStatus.CANCELADO
         )
         db.add(pay_log)

    db.commit()
    return {"message": f"Número {numero} cancelado com sucesso"}

@router.post("/{rifa_id}/numeros/{numero}/pagar", response_model=dict)
def pay_numero_admin(
    rifa_id: uuid.UUID,
    numero: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Admin manually marks a number as PAID.
    """
    num_obj = db.query(RifaNumero).filter(
        RifaNumero.rifa_id == rifa_id,
        RifaNumero.numero == numero
    ).first()
    
    if not num_obj:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    
    if num_obj.status == NumeroStatus.LIVRE:
         raise HTTPException(status_code=400, detail="Não é possível pagar um número livre sem usuário associado.")

    old_status = num_obj.status
    num_obj.status = NumeroStatus.PAGO
    num_obj.reserved_until = None
    
    # Audit
    AuditLogger.log(
        db=db,
        action="ADMIN_MARK_PAID",
        entity_type="RifaNumero",
        entity_id=str(num_obj.id),
        actor_id=str(current_user.id),
        actor_role="admin",
        old_value={"status": str(old_status)},
        new_value={"status": "pago"}
    )
    
    # Log Payment
    from app.models.audit_finance import PaymentLog, PaymentLogMethod, PaymentLogStatus
    
    rifa = db.query(Rifa).get(num_obj.rifa_id)
    valor = rifa.preco_numero if rifa else 0
    
    # Generate fake payment ID if missing (manual payment)
    if not num_obj.payment_id:
        num_obj.payment_id = f"MANUAL-{uuid.uuid4()}"
    
    pay_log = PaymentLog(
        rifa_id=num_obj.rifa_id,
        numero_id=num_obj.id,
        user_id=num_obj.user_id,
        payment_id=num_obj.payment_id,
        valor=valor,
        metodo=PaymentLogMethod.PIX, # Defaulting to Pix for now
        status=PaymentLogStatus.PAGO
    )
    db.add(pay_log)

    db.commit()
    return {"message": f"Número {numero} marcado como PAGO com sucesso"}
