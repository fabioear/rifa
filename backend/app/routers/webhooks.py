from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.audit_finance import PaymentLog, PaymentLogMethod, PaymentLogStatus
from app.core.audit import AuditLogger
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/picpay")
async def picpay_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle PicPay webhook callbacks (Mock).
    Payload: { "payment_id": "uuid", "status": "paid | canceled" }
    """
    try:
        payload = await request.json()
        logger.info(f"Received PicPay webhook: {payload}")
        
        payment_id = payload.get("payment_id")
        status = payload.get("status")
        
        if not payment_id:
            logger.warning("Webhook received without payment_id")
            return {"message": "Ignored"}
            
        # Find the reservation
        rifa_numero = db.query(RifaNumero).filter(RifaNumero.payment_id == payment_id).first()
        
        if not rifa_numero:
            logger.warning(f"Reservation not found for payment_id: {payment_id}")
            return {"message": "Not found"}
        
        old_status = rifa_numero.status
        
        if status == "paid":
            if rifa_numero.status != NumeroStatus.PAGO:
                rifa_numero.status = NumeroStatus.PAGO
                rifa_numero.reserved_until = None
                
                # 1. Create Payment Log
                # Assuming price from Rifa (need to join or fetch rifa)
                # But RifaNumero has rifa_id, we can fetch rifa price or assume fixed for now
                # Let's fetch Rifa to get price
                from app.models.rifa import Rifa
                rifa = db.query(Rifa).get(rifa_numero.rifa_id)
                valor = rifa.preco_numero if rifa else 0
                
                pay_log = PaymentLog(
                    rifa_id=rifa_numero.rifa_id,
                    numero_id=rifa_numero.id,
                    user_id=rifa_numero.user_id,
                    payment_id=payment_id,
                    valor=valor,
                    metodo=PaymentLogMethod.PIX, # Mock PicPay usually Pix
                    status=PaymentLogStatus.PAGO,
                    tenant_id=rifa_numero.tenant_id
                )
                db.add(pay_log)
                
                # 2. Audit Log
                AuditLogger.log(
                    db=db,
                    action="PAYMENT_CONFIRMED_WEBHOOK",
                    entity_type="RifaNumero",
                    entity_id=str(rifa_numero.id),
                    actor_id=None, # System/Webhook
                    actor_role="system",
                    old_value={"status": str(old_status)},
                    new_value={"status": "pago", "payment_id": payment_id},
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent"),
                    tenant_id=rifa_numero.tenant_id
                )
                
                logger.info(f"Payment confirmed for number {rifa_numero.numero}")
        
        elif status == "canceled":
             if rifa_numero.status != NumeroStatus.CANCELADO:
                rifa_numero.status = NumeroStatus.CANCELADO
                rifa_numero.reserved_until = None
                
                # Log Payment Cancelled if needed? 
                # Prompt says: "número virar CANCELADO -> criar log" in payment_logs
                # So yes, we create a log with status CANCELADO
                
                from app.models.rifa import Rifa
                rifa = db.query(Rifa).get(rifa_numero.rifa_id)
                valor = rifa.preco_numero if rifa else 0

                pay_log = PaymentLog(
                    rifa_id=rifa_numero.rifa_id,
                    numero_id=rifa_numero.id,
                    user_id=rifa_numero.user_id,
                    payment_id=payment_id,
                    valor=valor,
                    metodo=PaymentLogMethod.PIX,
                    status=PaymentLogStatus.CANCELADO,
                    tenant_id=rifa_numero.tenant_id
                )
                db.add(pay_log)

                AuditLogger.log(
                    db=db,
                    action="PAYMENT_CANCELED_WEBHOOK",
                    entity_type="RifaNumero",
                    entity_id=str(rifa_numero.id),
                    actor_id=None,
                    actor_role="system",
                    old_value={"status": str(old_status)},
                    new_value={"status": "cancelado"},
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent"),
                    tenant_id=rifa_numero.tenant_id
                )

                logger.info(f"Payment cancelled for number {rifa_numero.numero}")
             
        db.commit()
        return {"message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
