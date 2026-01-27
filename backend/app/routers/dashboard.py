from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.rifa import Rifa, RifaStatus
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.audit_finance import PaymentLog, PaymentLogStatus, AuditLog
from app.models.tenant import Tenant
from app.api.deps import get_current_active_superuser
from app.core.tenant import get_tenant_by_host

router = APIRouter()

@router.get("/resumo")
def get_dashboard_resumo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    # Total Arrecadado
    total_arrecadado = db.query(func.sum(PaymentLog.valor)).filter(
        PaymentLog.status == PaymentLogStatus.PAGO,
        PaymentLog.tenant_id == current_tenant.id
    ).scalar() or 0
    
    # Total Cancelado
    total_cancelado = db.query(func.sum(PaymentLog.valor)).filter(
        PaymentLog.status == PaymentLogStatus.CANCELADO,
        PaymentLog.tenant_id == current_tenant.id
    ).scalar() or 0
    
    # Total Pago (Count)
    total_pago_count = db.query(func.count(PaymentLog.id)).filter(
        PaymentLog.status == PaymentLogStatus.PAGO,
        PaymentLog.tenant_id == current_tenant.id
    ).scalar() or 0
    
    # Rifas Ativas
    rifas_ativas = db.query(func.count(Rifa.id)).filter(
        Rifa.status == RifaStatus.ATIVA,
        Rifa.tenant_id == current_tenant.id
    ).scalar() or 0
    
    # Rifas Encerradas
    rifas_encerradas = db.query(func.count(Rifa.id)).filter(
        Rifa.status == RifaStatus.ENCERRADA,
        Rifa.tenant_id == current_tenant.id
    ).scalar() or 0
    
    # Usuarios Ativos
    usuarios_ativos = db.query(func.count(User.id)).filter(
        User.is_active == True,
        User.tenant_id == current_tenant.id
    ).scalar() or 0
    
    # Taxa de Conversao (Paid / Total Reservations)
    # Total Reservations = Count of "RESERVE_NUMBER" in AuditLog
    total_reservations = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "RESERVE_NUMBER",
        AuditLog.tenant_id == current_tenant.id
    ).scalar() or 0
    
    taxa_conversao = 0
    if total_reservations > 0:
        taxa_conversao = (total_pago_count / total_reservations) * 100
        
    return {
        "total_arrecadado": total_arrecadado,
        "total_cancelado": total_cancelado,
        "total_pago_count": total_pago_count,
        "rifas_ativas": rifas_ativas,
        "rifas_encerradas": rifas_encerradas,
        "usuarios_ativos": usuarios_ativos,
        "taxa_conversao": round(taxa_conversao, 2)
    }

@router.get("/financeiro")
def get_dashboard_financeiro(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    # Agrupado por Dia
    por_dia = db.query(
        cast(PaymentLog.created_at, Date).label('data'),
        func.sum(PaymentLog.valor).label('total')
    ).filter(
        PaymentLog.status == PaymentLogStatus.PAGO,
        PaymentLog.tenant_id == current_tenant.id
    ).group_by(cast(PaymentLog.created_at, Date)).all()
    
    # Agrupado por Rifa
    por_rifa = db.query(
        Rifa.titulo,
        func.sum(PaymentLog.valor).label('total')
    ).join(Rifa, PaymentLog.rifa_id == Rifa.id).filter(
        PaymentLog.status == PaymentLogStatus.PAGO,
        PaymentLog.tenant_id == current_tenant.id
    ).group_by(Rifa.titulo).all()
    
    # Agrupado por Metodo
    por_metodo = db.query(
        PaymentLog.metodo,
        func.sum(PaymentLog.valor).label('total')
    ).filter(
        PaymentLog.status == PaymentLogStatus.PAGO,
        PaymentLog.tenant_id == current_tenant.id
    ).group_by(PaymentLog.metodo).all()
    
    return {
        "por_dia": [{"data": str(d[0]), "total": d[1]} for d in por_dia],
        "por_rifa": [{"rifa": d[0], "total": d[1]} for d in por_rifa],
        "por_metodo": [{"metodo": d[0], "total": d[1]} for d in por_metodo]
    }

@router.get("/rifas")
def get_dashboard_rifas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    rifas = db.query(Rifa).filter(Rifa.tenant_id == current_tenant.id).all()
    results = []
    
    for rifa in rifas:
        # Numeros Vendidos (PAGO)
        numeros_vendidos = db.query(func.count(RifaNumero.id)).filter(
            RifaNumero.rifa_id == rifa.id,
            RifaNumero.status == NumeroStatus.PAGO,
            RifaNumero.tenant_id == current_tenant.id
        ).scalar() or 0
        
        # Arrecadacao
        arrecadacao = db.query(func.sum(PaymentLog.valor)).filter(
            PaymentLog.rifa_id == rifa.id,
            PaymentLog.status == PaymentLogStatus.PAGO,
            PaymentLog.tenant_id == current_tenant.id
        ).scalar() or 0
        
        # Taxa de Cancelamento
        # (Cancelled Payments / Total Payments) or (Cancelled Numbers / Total Reserved)?
        # Let's use PaymentLog cancellations
        cancelled_payments = db.query(func.count(PaymentLog.id)).filter(
            PaymentLog.rifa_id == rifa.id,
            PaymentLog.status == PaymentLogStatus.CANCELADO,
            PaymentLog.tenant_id == current_tenant.id
        ).scalar() or 0
        
        total_payments = db.query(func.count(PaymentLog.id)).filter(
            PaymentLog.rifa_id == rifa.id,
            PaymentLog.tenant_id == current_tenant.id
        ).scalar() or 0
        
        taxa_cancelamento = 0
        if total_payments > 0:
            taxa_cancelamento = (cancelled_payments / total_payments) * 100
            
        results.append({
            "id": rifa.id,
            "titulo": rifa.titulo,
            "status": rifa.status,
            "numeros_vendidos": numeros_vendidos,
            "arrecadacao": arrecadacao,
            "taxa_cancelamento": round(taxa_cancelamento, 2)
        })
        
    return results

@router.get("/usuarios")
def get_dashboard_usuarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    current_tenant: Tenant = Depends(get_tenant_by_host)
):
    users = db.query(User).filter(User.tenant_id == current_tenant.id).limit(100).all()
    results = []
    
    for user in users:
        # Total Spent
        total_gasto = db.query(func.sum(PaymentLog.valor)).filter(
            PaymentLog.user_id == user.id,
            PaymentLog.status == PaymentLogStatus.PAGO,
            PaymentLog.tenant_id == current_tenant.id
        ).scalar() or 0
        
        # Numeros Comprados
        numeros_comprados = db.query(func.count(RifaNumero.id)).filter(
            RifaNumero.user_id == user.id,
            RifaNumero.status == NumeroStatus.PAGO,
            RifaNumero.tenant_id == current_tenant.id
        ).scalar() or 0
        
        results.append({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "total_gasto": total_gasto,
            "numeros_comprados": numeros_comprados
        })
        
    return results
