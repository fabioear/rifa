from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from app.db.session import get_db
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.user import User
from app.services.pixup_service import pixup_service

router = APIRouter()
logger = logging.getLogger(__name__)

class PaymentRequest(BaseModel):
    payment_id: str

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
        
    except Exception as e:
        logger.error(f"Error generating payment: {e}")
        # Return mock if service fails (for dev/test stability)
        # remove in production
        raise HTTPException(status_code=500, detail="Erro ao gerar pagamento Pix")

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
