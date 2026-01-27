from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.tenant import Tenant
import logging

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tenant_by_host(request: Request, db: Session = Depends(get_db)) -> Tenant:
    host = request.headers.get("host", "").split(":")[0] # Remove port if present
    
    # In development, fallback to localhost if no specific domain found
    # Or strict white-label:
    
    tenant = db.query(Tenant).filter(Tenant.domain == host).first()
    
    if not tenant:
        # Fallback for localhost development (if not explicitly "localhost" in DB)
        # But we added "localhost" in populate_data.
        # If accessing via IP 127.0.0.1, it might fail if DB has "localhost"
        if host == "127.0.0.1":
             tenant = db.query(Tenant).filter(Tenant.domain == "localhost").first()
    
    if not tenant:
        # Final fallback: default tenant? Or 404?
        # "White-label" usually implies strict domain matching.
        # But for ease of testing, let's grab the first one if strict fails?
        # No, safer to return 404 to verify isolation.
        raise HTTPException(status_code=404, detail=f"Tenant not found for domain {host}")
        
    return tenant
