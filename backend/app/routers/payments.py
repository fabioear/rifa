from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import httpx
import uuid
from datetime import datetime

from app.db.session import get_db
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.rifa import Rifa
from app.models.user import User
from app.services.pixup_service import pixup_service
from app.api.deps import get_current_active_user

router = APIRouter()
logger = logging.getLogger(__name__)

class PaymentRequest(BaseModel):
    payment_id: str

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
        
    if rifa.status != "ATIVA": # Assuming 'ATIVA' string or Enum. Using string for safety if Enum not imported
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
    
    # 4. Generate Unified Payment ID
    master_payment_id = str(uuid.uuid4())
    
    # 5. Update all numbers to use this Payment ID
    for num in numeros_db:
        num.payment_id = master_payment_id
        # Refresh expiry time? Maybe reset the 15min timer? 
        # Let's keep original or refresh. Refreshing is nicer.
        # num.reserved_until = datetime.utcnow() + timedelta(minutes=15) 
    
    db.commit() # Save the payment_id update before calling API (to ensure webhook finds it)
    
    # 6. Call Pixup
    try:
        payer_cpf = "00000000000" # TODO: Get from User profile
        
        result = await pixup_service.create_payment(
            reference_id=master_payment_id,
            amount=total_amount,
            payer_name=current_user.name or "Cliente",
            payer_cpf=payer_cpf,
            payer_email=current_user.email
        )
        
        pix_code = result.get("pixCopiaECola") or result.get("qrcode") or "BR.GOV.BCB.PIX..."
        qr_code_base64 = result.get("imagemQrCode") or result.get("qr_code_base64")
        
        return {
            "payment_id": master_payment_id,
            "pix_code": pix_code,
            "qr_code": qr_code_base64,
            "amount": total_amount,
            "expires_at": numeros_db[0].reserved_until # Assuming all have similar expiry
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Error Pixup HTTP: {e.response.text}")
        try:
            error_data = e.response.json()
            msg = error_data.get("message") or error_data.get("error_description") or str(e)
            if "Valor mínimo" in msg:
                 raise HTTPException(status_code=400, detail=f"Erro Pixup: {msg}")
        except:
            pass
        raise HTTPException(status_code=400, detail=f"Erro na comunicação com Pixup: {e.response.text}")
    except Exception as e:
        logger.error(f"Error generating checkout payment: {e}")
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

    # Get Rifa price
    rifa = rifa_numero.rifa
    if not rifa:
        raise HTTPException(status_code=404, detail="Rifa não encontrada")
        
    user = rifa_numero.comprador
    if not user:
        # Fallback if no user linked yet (shouldn't happen for valid reservation)
        raise HTTPException(status_code=404, detail="Comprador não identificado")

    amount = float(rifa.preco_numero)
    
    try:
        # Call Pixup Service
        # We need a CPF. Since User model doesn't have it, we'll use a dummy for now
        # OR checking if we can get it from somewhere else.
        # Assuming we need to update User model later.
        payer_cpf = "00000000000" 
        
        result = await pixup_service.create_payment(
            reference_id=request.payment_id,
            amount=amount,
            payer_name=user.name or "Cliente",
            payer_cpf=payer_cpf,
            payer_email=user.email
        )
        
        # Adjust based on real Pixup response
        # Assuming standard Pix keys
        pix_code = result.get("pixCopiaECola") or result.get("qrcode") or "BR.GOV.BCB.PIX..."
        qr_code_base64 = result.get("imagemQrCode") or result.get("qr_code_base64")
        
        return {
            "payment_id": request.payment_id,
            "pix_code": pix_code,
            "qr_code": qr_code_base64,
            "expires_at": rifa_numero.reserved_until
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Error Pixup HTTP: {e.response.text}")
        # Tenta extrair mensagem amigável do JSON de erro
        try:
            error_data = e.response.json()
            msg = error_data.get("message") or error_data.get("error_description") or str(e)
            if "Valor mínimo" in msg:
                raise HTTPException(status_code=400, detail=f"Erro Pixup: {msg}")
        except:
            pass
        raise HTTPException(status_code=400, detail=f"Erro na comunicação com Pixup: {e.response.text}")
    except Exception as e:
        logger.error(f"Error generating payment: {e}")
        # Return detail for debugging
        raise HTTPException(status_code=500, detail=f"Erro ao gerar pagamento Pix: {str(e)}")

@router.post("/webhook/pixup")
async def pixup_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        payload = await request.json()
        logger.info(f"Webhook Pixup received: {payload}")
        
        # Parse payload to get reference_id/payment_id
        # This part requires knowledge of Pixup webhook format.
        # Assuming it sends 'pix' list with 'txid' or 'infoAdicionais'
        
        # Example payload structure assumption (standard Pix):
        # { "pix": [ { "txid": "...", "infoAdicionais": [ { "nome": "Referência", "valor": "PAYMENT_ID" } ] } ] }
        
        payment_id = None
        pix_data = payload.get("pix", [])
        if pix_data and isinstance(pix_data, list):
            item = pix_data[0]
            info_adicionais = item.get("infoAdicionais", [])
            for info in info_adicionais:
                if info.get("nome") == "Referência":
                    payment_id = info.get("valor")
                    break
        
        if payment_id:
            # Update status
            rifa_numeros = db.query(RifaNumero).filter(RifaNumero.payment_id == payment_id).all()
            for rn in rifa_numeros:
                if rn.status != NumeroStatus.PAGO:
                    rn.status = NumeroStatus.PAGO
                    rn.updated_at = datetime.now()
                    # Log payment success
                    logger.info(f"Payment confirmed for reservation {rn.id} (Payment ID: {payment_id})")
            
            db.commit()
            return {"status": "ok"}
        else:
            logger.warning("Payment ID not found in webhook payload")
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
    return {"status": "ignored"}
