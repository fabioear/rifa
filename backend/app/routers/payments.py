from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.db.session import get_db
from app.models.rifa_numero import RifaNumero

router = APIRouter()

class MockPaymentRequest(BaseModel):
    payment_id: str

@router.post("/mock")
def mock_payment(
    request: MockPaymentRequest,
    db: Session = Depends(get_db)
):
    # Find reservation by payment_id to get real expiration
    rifa_numero = db.query(RifaNumero).filter(RifaNumero.payment_id == request.payment_id).first()
    
    if not rifa_numero:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        
    return {
        "payment_id": request.payment_id,
        "pix_code": "00020126580014BR.GOV.BCB.PIX0136123e4567-e89b-12d3-a456-426614174000",
        "qr_code": "mock_qr_code_base64_string",
        "expires_at": rifa_numero.reserved_until
    }
