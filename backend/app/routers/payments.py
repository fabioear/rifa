from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import httpx
import uuid
import qrcode
import io
import base64
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.rifa import Rifa, RifaStatus
from app.models.user import User
from app.services.asaas_service import asaas_service
from app.api.deps import get_current_active_user
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

class PaymentRequest(BaseModel):
    payment_id: str

import random

def generate_valid_cpf():
    """Gera um CPF válido para testes."""
    def calculate_digit(digits):
        s = sum(d * w for d, w in zip(digits, range(len(digits) + 1, 1, -1)))
        r = (s * 10) % 11
        return 0 if r == 10 else r

    cpf = [random.randint(0, 9) for _ in range(9)]
    cpf.append(calculate_digit(cpf))
    cpf.append(calculate_digit(cpf))
    return "".join(map(str, cpf))

class CheckoutRequest(BaseModel):
    rifa_id: str
    numeros: List[str]

@router.post("/checkout")
async def create_checkout_payment(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 1. Validate Rifa
    rifa = db.query(Rifa).filter(Rifa.id == request.rifa_id).first()
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa não encontrada")
        
    if rifa.status != RifaStatus.ATIVA:
         raise HTTPException(status_code=400, detail="Rifa não está ativa")

    # 2. Validate Numbers Ownership and Status
    # We look for numbers that are RESERVED by this user
    numeros_db = db.query(RifaNumero).filter(
        RifaNumero.rifa_id == request.rifa_id,
        RifaNumero.numero.in_(request.numeros),
        RifaNumero.user_id == current_user.id,
        RifaNumero.status == NumeroStatus.RESERVADO
    ).all()
    
    # Check if we found all requested numbers
    found_numeros_set = {n.numero for n in numeros_db}
    missing = [n for n in request.numeros if n not in found_numeros_set]
    
    if missing:
        # Some numbers might have expired or not been reserved
        raise HTTPException(
            status_code=400, 
            detail=f"Os seguintes números não estão reservados para você (ou expiraram): {', '.join(missing)}"
        )
        
    if not numeros_db:
        raise HTTPException(status_code=400, detail="Nenhum número válido para pagamento.")

    # 3. Calculate Total Amount
    total_amount = float(rifa.preco_numero) * len(numeros_db)
    
    # 4. Generate Unified Payment ID (Internal Reference)
    master_payment_id = str(uuid.uuid4())
    
    # 5. Update all numbers to use this Payment ID
    for num in numeros_db:
        num.payment_id = master_payment_id
        # Refresh expiry time (optional but good practice)
        num.reserved_until = datetime.utcnow() + timedelta(minutes=15) 
    
    db.commit() # Save the payment_id update before calling API
    
    # 6. Call Asaas
    try:
        # Get or Create Customer
        # Note: We need a CPF. Using a dummy if not available, or trying to find by email.
        # Ideally User model should have CPF.
        payer_cpf = getattr(current_user, 'cpf', None) or generate_valid_cpf()
        
        customer = await asaas_service.create_customer(
            name=current_user.name or "Cliente",
            cpf_cnpj=payer_cpf,
            email=current_user.email,
            phone=current_user.phone
        )
        
        customer_id = customer["id"]
        
        # Create Payment
        description = f"Pagamento Rifa: {rifa.titulo} - {len(numeros_db)} numeros"
        due_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        payment_result = await asaas_service.create_pix_payment(
            customer_id=customer_id,
            value=total_amount,
            due_date=due_date,
            external_reference=master_payment_id,
            description=description
        )
        
        asaas_payment_id = payment_result["id"]
        
        # Get QR Code
        qr_data = await asaas_service.get_pix_qrcode(asaas_payment_id)
        
        pix_code = qr_data.get("payload")
        qr_code_base64 = qr_data.get("encodedImage")
        
        return {
            "payment_id": master_payment_id, # We keep using our UUID as the main reference for frontend
            "asaas_id": asaas_payment_id,
            "pix_code": pix_code,
            "qr_code": qr_code_base64,
            "amount": total_amount,
            "expires_at": numeros_db[0].reserved_until
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error generating checkout payment with Asaas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar pagamento: {str(e)}")


@router.post("/pix")
async def generate_pix_payment(
    request: PaymentRequest,
    db: Session = Depends(get_db)
):
    # Find reservation by payment_id
    rifa_numero = db.query(RifaNumero).filter(RifaNumero.payment_id == request.payment_id).first()
    
    if not rifa_numero:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
        
    if rifa_numero.status == NumeroStatus.PAGO:
        raise HTTPException(status_code=400, detail="Este número já foi pago")

    # This endpoint seems redundant if /checkout does everything, 
    # but sometimes frontend calls it separately or for retry.
    # Re-implement logic similar to checkout but retrieving existing data?
    # For simplicity, we assume /checkout is the main entry.
    # If this is a retry, we should check if Asaas payment already exists?
    # For now, let's treat it as a "regenerate" or "get info" if possible, 
    # but we don't store Asaas ID in DB yet (only in memory during checkout).
    # Todo: Store Asaas ID in DB or rely on external_reference search.
    
    raise HTTPException(status_code=501, detail="Use /checkout para gerar novo pagamento.")


@router.post("/check/{payment_id}")
async def check_payment_status_manual(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint para verificação manual de pagamento pelo usuário.
    Força uma consulta no Asaas para ver se o pagamento já consta.
    """
    # Find reservation
    rifa_numeros = db.query(RifaNumero).filter(RifaNumero.payment_id == payment_id).all()
    
    if not rifa_numeros:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        
    # Check if already paid
    if all(rn.status == NumeroStatus.PAGO for rn in rifa_numeros):
        return {"status": "paid", "message": "Pagamento já confirmado!"}
        
    # Check ownership
    if rifa_numeros[0].user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Acesso negado")

    # We need to find the Asaas Payment ID.
    # Since we didn't store it in a dedicated column (we used payment_id for our UUID),
    # we can try to search Asaas by externalReference.
    
    try:
        payment_data = await asaas_service.get_payment_by_external_reference(payment_id)
        
        if payment_data:
            status = payment_data.get("status")
            if status in ["RECEIVED", "CONFIRMED", "PAID"]:
                # Update DB immediately
                confirmed_count = 0
                for rn in rifa_numeros:
                    if rn.status != NumeroStatus.PAGO:
                        rn.status = NumeroStatus.PAGO
                        rn.updated_at = datetime.now()
                        confirmed_count += 1
                        # PaymentLog logic could be added here too, but let's keep it simple for now or extract to function
                
                if confirmed_count > 0:
                    db.commit()
                    return {"status": "paid", "message": "Pagamento confirmado com sucesso!"}
            
            return {"status": "pending", "message": f"Pagamento identificado, status atual: {status}"}
            
    except Exception as e:
        logger.error(f"Erro no check manual Asaas: {e}")
    
    return {"status": "pending", "message": "Aguardando confirmação do banco..."}


@router.post("/webhook/asaas")
async def asaas_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Verify Secret
        auth_token = request.headers.get("asaas-access-token")
        if settings.ASAAS_WEBHOOK_SECRET and auth_token != settings.ASAAS_WEBHOOK_SECRET:
            logger.warning("Invalid Asaas Webhook Token")
            raise HTTPException(status_code=401, detail="Unauthorized")

        payload = await request.json()
        logger.info(f"Webhook Asaas received: {payload}")
        
        event = payload.get("event")
        payment = payload.get("payment", {})
        
        if event in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
            external_reference = payment.get("externalReference")
            
            if not external_reference:
                logger.warning("Payment without externalReference")
                return {"status": "ignored"}
                
            payment_id = external_reference # Our UUID
            
            # Update status
            rifa_numeros = db.query(RifaNumero).filter(RifaNumero.payment_id == payment_id).all()
            
            confirmed_count = 0
            for rn in rifa_numeros:
                if rn.status != NumeroStatus.PAGO:
                    rn.status = NumeroStatus.PAGO
                    rn.updated_at = datetime.now()
                    confirmed_count += 1
                    
                    # Log to PaymentLog
                    try:
                        from app.models.audit_finance import PaymentLog, PaymentLogMethod, PaymentLogStatus
                        
                        pay_log = PaymentLog(
                            rifa_id=rn.rifa_id,
                            numero_id=rn.id,
                            user_id=rn.user_id,
                            payment_id=payment_id,
                            valor=float(rn.rifa.preco_numero),
                            metodo=PaymentLogMethod.PIX,
                            status=PaymentLogStatus.PAGO,
                            tenant_id=rn.tenant_id
                        )
                        db.add(pay_log)
                    except Exception as log_err:
                        logger.error(f"Failed to create PaymentLog in webhook: {log_err}")

            if confirmed_count > 0:
                db.commit()
                logger.info(f"Payment confirmed for {confirmed_count} numbers (Ref: {payment_id})")
                
            return {"status": "processed"}
            
        return {"status": "ignored_event"}
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
