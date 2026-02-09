from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import httpx
import uuid
import qrcode
import io
import base64
from datetime import datetime

from app.db.session import get_db
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.rifa import Rifa, RifaStatus
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
        
        logger.info(f"Pixup Response: {result}")
        
        pix_code = result.get("pixCopiaECola") or result.get("qrcode") or "BR.GOV.BCB.PIX..."
        qr_code_base64 = result.get("imagemQrCode") or result.get("qr_code_base64")
        
        # If no image provided but we have the code, generate it
        if not qr_code_base64 and pix_code:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(pix_code)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                qr_code_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            except Exception as e:
                logger.error(f"Error generating QR code locally: {e}")

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
        
        # If no image provided but we have the code, generate it
        if not qr_code_base64 and pix_code:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(pix_code)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                qr_code_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            except Exception as e:
                logger.error(f"Error generating QR code locally: {e}")

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

@router.post("/check/{payment_id}")
async def check_payment_status_manual(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Endpoint para verificação manual de pagamento pelo usuário.
    Força uma consulta na Pixup para ver se o pagamento já consta.
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

    # Call Pixup to check
    is_paid = await pixup_service.check_payment_status(payment_id)
    
    if is_paid:
        # Update status
        for rn in rifa_numeros:
            if rn.status != NumeroStatus.PAGO:
                rn.status = NumeroStatus.PAGO
                rn.updated_at = datetime.now()
                
                # Log to PaymentLog
                try:
                    from app.models.audit_finance import PaymentLog, PaymentLogMethod, PaymentLogStatus
                    
                    # Avoid duplicate log check
                    existing_log = db.query(PaymentLog).filter(
                        PaymentLog.payment_id == payment_id,
                        PaymentLog.numero_id == rn.id
                    ).first()
                    
                    if not existing_log:
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
                    logger.error(f"Failed to create PaymentLog in manual check: {log_err}")
                    
        db.commit()
        return {"status": "paid", "message": "Pagamento confirmado com sucesso!"}
    
    return {"status": "pending", "message": "Pagamento ainda não identificado. Aguarde alguns instantes."}

@router.post("/webhook/pixup")
async def pixup_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        payload = await request.json()
        logger.info(f"Webhook Pixup received: {payload}")
        
        # Parse payload to get reference_id/payment_id
        # Webhook payload structure varies. Standard Pix usually has 'pix' list.
        # We check multiple fields to ensure we catch the ID.
        
        payment_id = None
        pix_data = payload.get("pix", [])
        
        # Helper to extract ID
        def extract_id(item):
            # 1. Try 'external_id' (Direct reference if supported)
            if item.get("external_id"):
                return item.get("external_id")
            # 2. Try 'txid' (Transaction ID often used as reference)
            if item.get("txid") and len(item.get("txid")) > 10: # Simple length check to avoid tiny IDs
                return item.get("txid")
            # 3. Try 'infoAdicionais' (Legacy/Standard Pix Manual)
            info_adicionais = item.get("infoAdicionais", [])
            for info in info_adicionais:
                if info.get("nome") == "Referência":
                    return info.get("valor")
            return None

        if pix_data and isinstance(pix_data, list):
            for item in pix_data:
                found_id = extract_id(item)
                if found_id:
                    payment_id = found_id
                    break
        
        # Fallback: Check root level if payload is not a list of pix
        if not payment_id:
             if payload.get("external_id"):
                 payment_id = payload.get("external_id")
             elif payload.get("txid"):
                 payment_id = payload.get("txid")
        
        if payment_id:
            # Update status
            rifa_numeros = db.query(RifaNumero).filter(RifaNumero.payment_id == payment_id).all()
            for rn in rifa_numeros:
                if rn.status != NumeroStatus.PAGO:
                    rn.status = NumeroStatus.PAGO
                    rn.updated_at = datetime.now()
                    # Log payment success
                    logger.info(f"Payment confirmed for reservation {rn.id} (Payment ID: {payment_id})")
                    
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

            db.commit()
            return {"status": "ok"}
        else:
            logger.warning("Payment ID not found in webhook payload")
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
    return {"status": "ignored"}
