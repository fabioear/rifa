from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.core.tenant import get_tenant_by_host
from app.api.deps import get_current_active_superuser
from app.models.rifa import Rifa, RifaStatus, RifaTipo
from app.models.rifa_numero import RifaNumero, NumeroStatus, PremioStatus
from app.models.audit_finance import PaymentLog, AuditLog
from app.models.rifa_resultado import RifaResultado
from app.models.rifa_ganhador import RifaGanhador
from app.core.audit import AuditLogger
from app.schemas.rifa import RifaResultadoCreate
from services.whatsapp_service import whatsapp_service
from app.db.session import SessionLocal
from fastapi import BackgroundTasks

def notify_winners_task(rifa_id: uuid.UUID, tenant_id: uuid.UUID):
    db = SessionLocal()
    try:
        rifa = db.query(Rifa).get(rifa_id)
        if not rifa:
            return
            
        ganhadores = db.query(RifaGanhador).filter(
            RifaGanhador.rifa_id == rifa_id,
            RifaGanhador.tenant_id == tenant_id
        ).all()
        
        for ganhador in ganhadores:
            user = db.query(User).get(ganhador.user_id)
            numero = db.query(RifaNumero).get(ganhador.rifa_numero_id)
            
            if user and user.phone and user.whatsapp_opt_in:
                try:
                    # Idempotency: skip if already notified
                    already = db.query(AuditLog).filter(
                        AuditLog.action == "WHATSAPP_NOTIFIED_GANHADOR",
                        AuditLog.entity_type == "user",
                        AuditLog.entity_id == str(user.id),
                        AuditLog.tenant_id == tenant_id,
                        AuditLog.new_value['rifa_id'].astext == str(rifa.id),
                        AuditLog.new_value['numero'].astext == str(numero.numero)
                    ).first()
                    if already:
                        continue
                    whatsapp_service.send_winner_notification(
                        user_phone=user.phone,
                        rifa_nome=rifa.titulo,
                        numero_sorteado=numero.numero
                    )
                    AuditLogger.log(
                        db=db,
                        action="WHATSAPP_NOTIFIED_GANHADOR",
                        entity_type="user",
                        entity_id=str(user.id),
                        actor_id="system",
                        actor_role="system",
                        old_value=None,
                        new_value={"rifa_id": str(rifa.id), "numero": numero.numero},
                        tenant_id=tenant_id
                    )
                    db.commit()
                except Exception as e:
                    print(f"Error notifying winner {user.id}: {e}")
                    
    finally:
        db.close()

router = APIRouter()

from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_password_hash

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    """
    Update a user.
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == current_tenant.id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.phone is not None:
        user.phone = user_in.phone
    if user_in.whatsapp_opt_in is not None:
        user.whatsapp_opt_in = user_in.whatsapp_opt_in
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)
        
    db.commit()
    db.refresh(user)
    return user

@router.get("/users", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    """
    List all users in the current tenant.
    """
    users = db.query(User).filter(
        User.tenant_id == current_tenant.id
    ).offset(skip).limit(limit).all()
    return users

@router.get("/financeiro")
def get_financeiro_global(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    """
    Relatório financeiro global.
    """
    query = db.query(PaymentLog).filter(PaymentLog.tenant_id == current_tenant.id)
    
    if start_date:
        query = query.filter(PaymentLog.created_at >= start_date)
    if end_date:
        query = query.filter(PaymentLog.created_at <= end_date)
        
    logs = query.order_by(PaymentLog.created_at.desc()).limit(100).all()
    
    # Calculate total based on filters
    total_query = db.query(func.sum(PaymentLog.valor)).filter(
        PaymentLog.status == "pago",
        PaymentLog.tenant_id == current_tenant.id
    )
    if start_date:
        total_query = total_query.filter(PaymentLog.created_at >= start_date)
    if end_date:
        total_query = total_query.filter(PaymentLog.created_at <= end_date)
        
    total_arrecadado = total_query.scalar() or 0
    
    return {
        "total_arrecadado": total_arrecadado,
        "logs": logs
    }

@router.get("/financeiro/rifas/{rifa_id}")
def get_financeiro_rifa(
    rifa_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    """
    Relatório financeiro por rifa.
    """
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")
        
    logs = db.query(PaymentLog).filter(
        PaymentLog.rifa_id == rifa_id,
        PaymentLog.tenant_id == current_tenant.id
    ).order_by(PaymentLog.created_at.desc()).all()
    
    total_arrecadado = db.query(func.sum(PaymentLog.valor)).filter(
        PaymentLog.rifa_id == rifa_id,
        PaymentLog.status == "pago",
        PaymentLog.tenant_id == current_tenant.id
    ).scalar() or 0
    
    return {
        "rifa": rifa.titulo,
        "total_arrecadado": total_arrecadado,
        "logs": logs
    }

@router.get("/auditoria")
def get_audit_logs(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    entity: Optional[str] = None,
    id: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    """
    Lista logs de auditoria.
    """
    query = db.query(AuditLog).filter(AuditLog.tenant_id == current_tenant.id)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if entity:
        query = query.filter(AuditLog.entity_id == entity)
        
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    return logs


@router.post("/rifas/{rifa_id}/fechar")
def close_rifa(
    rifa_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    """
    Fecha uma rifa, impedindo novas reservas.
    """
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa not found")
        
    if rifa.status != RifaStatus.ATIVA:
        raise HTTPException(status_code=400, detail=f"Rifa must be ATIVA to be closed. Current status: {rifa.status}")
        
    old_status = rifa.status
    rifa.status = RifaStatus.ENCERRADA
    
    AuditLogger.log(
        db=db,
        action="RIFA_CLOSED",
        entity_type="rifa",
        entity_id=str(rifa.id),
        actor_id=str(current_user.id),
        actor_role="admin",
        old_value={
            "status": old_status.value if isinstance(old_status, RifaStatus) else str(old_status)
        },
        new_value={
            "status": RifaStatus.ENCERRADA.value
        },
        tenant_id=current_tenant.id
    )
    
    db.commit()
    db.refresh(rifa)
    
    return rifa


def _normalize_match_numero(tipo_rifa: RifaTipo, resultado: str) -> str:
    valor = resultado.strip()
    if tipo_rifa == RifaTipo.MILHAR:
        return valor[-4:].zfill(4)
    if tipo_rifa == RifaTipo.CENTENA:
        return valor[-3:].zfill(3)
    if tipo_rifa == RifaTipo.DEZENA:
        return valor[-2:].zfill(2)
    if tipo_rifa == RifaTipo.GRUPO:
        return str(int(valor)).zfill(2)
    return valor


def apurar_rifa(
    db: Session,
    rifa: Rifa,
    resultado: RifaResultado,
    current_user: User,
    current_tenant: Tenant
):
    if resultado.apurado:
        raise HTTPException(status_code=400, detail="Rifa já apurada para este resultado")

    match_numero = _normalize_match_numero(rifa.tipo_rifa, resultado.resultado)

    numeros_pagos = db.query(RifaNumero).filter(
        RifaNumero.rifa_id == rifa.id,
        RifaNumero.status == NumeroStatus.PAGO,
        RifaNumero.tenant_id == current_tenant.id
    ).all()

    numeros_ganhadores = db.query(RifaNumero).filter(
        RifaNumero.rifa_id == rifa.id,
        RifaNumero.numero == match_numero,
        RifaNumero.status == NumeroStatus.PAGO,
        RifaNumero.tenant_id == current_tenant.id
    ).all()

    ganhadores_ids = {num.id for num in numeros_ganhadores}

    for num in numeros_pagos:
        existing = db.query(RifaGanhador).filter(
            RifaGanhador.rifa_id == rifa.id,
            RifaGanhador.rifa_numero_id == num.id,
            RifaGanhador.user_id == num.user_id,
            RifaGanhador.tenant_id == current_tenant.id
        ).first()
        if existing:
            continue
        if num.id in ganhadores_ids:
            num.premio_status = PremioStatus.WINNER
            ganhador = RifaGanhador(
                rifa_id=rifa.id,
                rifa_numero_id=num.id,
                user_id=num.user_id,
                tenant_id=current_tenant.id
            )
            db.add(ganhador)
            AuditLogger.log(
                db=db,
                action="GANHADOR_DEFINIDO",
                entity_type="rifa",
                entity_id=str(rifa.id),
                actor_id=str(current_user.id),
                actor_role="admin",
                old_value=None,
                new_value={
                    "rifa_id": str(rifa.id),
                    "rifa_numero_id": str(num.id),
                    "user_id": str(num.user_id),
                    "numero": num.numero,
                },
                tenant_id=current_tenant.id,
            )
        else:
            num.premio_status = PremioStatus.LOSER

    resultado.apurado = True
    old_status = rifa.status
    rifa.status = RifaStatus.APURADA

    AuditLogger.log(
        db=db,
        action="RIFA_APURADA",
        entity_type="rifa",
        entity_id=str(rifa.id),
        actor_id=str(current_user.id),
        actor_role="admin",
        old_value={"status": old_status.value if isinstance(old_status, RifaStatus) else str(old_status)},
        new_value={
            "status": RifaStatus.APURADA.value,
            "resultado_id": str(resultado.id),
        },
        tenant_id=current_tenant.id,
    )

    db.commit()
    db.refresh(rifa)
    db.refresh(resultado)
    return rifa


@router.post("/rifas/{rifa_id}/resultado")
def create_rifa_resultado(
    rifa_id: uuid.UUID,
    payload: RifaResultadoCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa não encontrada")

    if rifa.status != RifaStatus.ENCERRADA:
        raise HTTPException(status_code=400, detail="Rifa precisa estar ENCERRADA para lançar resultado")

    existing = db.query(RifaResultado).filter(
        RifaResultado.rifa_id == rifa.id,
        RifaResultado.tenant_id == current_tenant.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Resultado já lançado para esta rifa")

    resultado_entidade = RifaResultado(
        rifa_id=rifa.id,
        tipo_rifa=rifa.tipo_rifa,
        resultado=payload.resultado,
        local_sorteio=payload.local_sorteio,
        data_resultado=payload.data_resultado,
        apurado=False,
        created_by=current_user.id,
        tenant_id=current_tenant.id,
    )
    db.add(resultado_entidade)
    rifa.resultado = payload.resultado

    AuditLogger.log(
        db=db,
        action="RESULTADO_LANCADO",
        entity_type="rifa",
        entity_id=str(rifa.id),
        actor_id=str(current_user.id),
        actor_role="admin",
        old_value=None,
        new_value={
            "resultado": payload.resultado,
            "local_sorteio": payload.local_sorteio,
            "data_resultado": payload.data_resultado.isoformat(),
        },
        tenant_id=current_tenant.id,
    )

    db.commit()
    db.refresh(resultado_entidade)
    return {
        "id": str(resultado_entidade.id),
        "rifa_id": str(resultado_entidade.rifa_id),
        "tipo_rifa": resultado_entidade.tipo_rifa.value,
        "resultado": resultado_entidade.resultado,
        "local_sorteio": resultado_entidade.local_sorteio,
        "data_resultado": resultado_entidade.data_resultado,
        "apurado": resultado_entidade.apurado,
    }

@router.post("/rifas/{rifa_id}/apurar")
def apurar_rifa_endpoint(
    rifa_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa não encontrada")

    if rifa.status != RifaStatus.ENCERRADA:
        raise HTTPException(status_code=400, detail="Rifa precisa estar ENCERRADA para apuração")

    resultado = db.query(RifaResultado).filter(
        RifaResultado.rifa_id == rifa.id,
        RifaResultado.tenant_id == current_tenant.id,
    ).first()
    if not resultado:
        raise HTTPException(status_code=400, detail="Resultado ainda não lançado para esta rifa")

    # Check for at least one paid number
    has_paid_numbers = db.query(RifaNumero).filter(
        RifaNumero.rifa_id == rifa.id,
        RifaNumero.status == NumeroStatus.PAGO,
        RifaNumero.tenant_id == current_tenant.id
    ).first()

    if not has_paid_numbers:
        raise HTTPException(status_code=400, detail="Nenhum número pago encontrado para esta rifa")

    # Check if there is at least one winner (number matches result and is PAID)
    # This prevents closing a rifa where the result wasn't bought (if that's the business rule)
    winner_exists = db.query(RifaNumero).filter(
        RifaNumero.rifa_id == rifa.id,
        RifaNumero.numero == resultado.resultado,
        RifaNumero.status == NumeroStatus.PAGO,
        RifaNumero.tenant_id == current_tenant.id
    ).first()

    if not winner_exists:
        raise HTTPException(status_code=400, detail="O resultado informado não corresponde a nenhum número pago (sem ganhador)")

    rifa_apurada = apurar_rifa(db, rifa, resultado, current_user, current_tenant)
    
    # Trigger winner notifications
    background_tasks.add_task(notify_winners_task, rifa.id, current_tenant.id)
    
    return {
        "rifa_id": str(rifa_apurada.id),
        "status": rifa_apurada.status.value if isinstance(rifa_apurada.status, RifaStatus) else str(rifa_apurada.status),
    }


@router.get("/rifas/{rifa_id}/ganhadores")
def get_ganhadores(
    rifa_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa não encontrada")

    resultado = db.query(RifaResultado).filter(
        RifaResultado.rifa_id == rifa.id,
        RifaResultado.tenant_id == current_tenant.id,
    ).first()

    ganhadores_registrados = db.query(RifaGanhador).filter(
        RifaGanhador.rifa_id == rifa.id,
        RifaGanhador.tenant_id == current_tenant.id,
    ).all()

    response_ganhadores = []
    for registro in ganhadores_registrados:
        numero = db.query(RifaNumero).filter(
            RifaNumero.id == registro.rifa_numero_id,
            RifaNumero.tenant_id == current_tenant.id,
        ).first()
        user = db.query(User).filter(
            User.id == registro.user_id,
            User.tenant_id == current_tenant.id,
        ).first()
        if not numero or not user:
            continue
        response_ganhadores.append(
            {
                "numero": numero.numero,
                "email": user.email,
                "tipo_rifa": rifa.tipo_rifa.value if isinstance(rifa.tipo_rifa, RifaTipo) else str(rifa.tipo_rifa),
                "local_sorteio": resultado.local_sorteio if resultado else str(rifa.local_sorteio),
            }
        )

    return {
        "rifa_id": str(rifa.id),
        "resultado": {
            "valor": resultado.resultado if resultado else None,
            "local_sorteio": resultado.local_sorteio if resultado else None,
            "data_resultado": resultado.data_resultado if resultado else None,
            "apurado": resultado.apurado if resultado else False,
        }
        if resultado
        else None,
        "ganhadores": response_ganhadores,
    }


@router.get("/rifas/{rifa_id}/resumo")
def get_rifa_resumo(
    rifa_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host),
):
    rifa = db.query(Rifa).filter(Rifa.id == rifa_id, Rifa.tenant_id == current_tenant.id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa não encontrada")

    total_arrecadado = (
        db.query(func.sum(PaymentLog.valor))
        .filter(
            PaymentLog.rifa_id == rifa.id,
            PaymentLog.status == "pago",
            PaymentLog.tenant_id == current_tenant.id,
        )
        .scalar()
        or 0
    )

    total_numeros_pagos = (
        db.query(func.count(RifaNumero.id))
        .filter(
            RifaNumero.rifa_id == rifa.id,
            RifaNumero.status == NumeroStatus.PAGO,
            RifaNumero.tenant_id == current_tenant.id,
        )
        .scalar()
        or 0
    )

    resultado = db.query(RifaResultado).filter(
        RifaResultado.rifa_id == rifa.id,
        RifaResultado.tenant_id == current_tenant.id,
    ).first()

    quantidade_ganhadores = (
        db.query(func.count(RifaGanhador.id))
        .filter(
            RifaGanhador.rifa_id == rifa.id,
            RifaGanhador.tenant_id == current_tenant.id,
        )
        .scalar()
        or 0
    )

    return {
        "rifa_id": str(rifa.id),
        "titulo": rifa.titulo,
        "status": rifa.status.value if isinstance(rifa.status, RifaStatus) else str(rifa.status),
        "total_arrecadado": total_arrecadado,
        "total_numeros_pagos": total_numeros_pagos,
        "resultado_lancado": bool(resultado),
        "resultado": {
            "valor": resultado.resultado,
            "local_sorteio": resultado.local_sorteio,
            "data_resultado": resultado.data_resultado,
            "apurado": resultado.apurado,
        }
        if resultado
        else None,
        "quantidade_ganhadores": quantidade_ganhadores,
    }
