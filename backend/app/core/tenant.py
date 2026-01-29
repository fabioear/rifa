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
    
    # Force production tenant on localhost for development to access production data
    if host == "127.0.0.1" or host == "localhost":
        tenant = db.query(Tenant).filter(Tenant.domain == "imperiodasrifas.app.br").first()
        if tenant:
            return tenant

    tenant = db.query(Tenant).filter(Tenant.domain == host).first()
    
    if not tenant:
        # Fallback for localhost development:
        # Redirect localhost to the main production tenant ("Imperio das Rifas")
        # so we can see/manage production data locally.
        if host == "127.0.0.1" or host == "localhost":
             tenant = db.query(Tenant).filter(Tenant.domain == "imperiodasrifas.app.br").first()
             
        # If still not found (e.g. production tenant domain changed or not seeded), 
        # try finding the specific "localhost" tenant as a last resort
        if not tenant and (host == "127.0.0.1" or host == "localhost"):
             tenant = db.query(Tenant).filter(Tenant.domain == "localhost").first()
    
    if not tenant:
        # Final fallback: default tenant? Or 404?
        # "White-label" usually implies strict domain matching.
        # But for ease of testing, let's grab the first one if strict fails?
        # No, safer to return 404 to verify isolation.
        raise HTTPException(status_code=404, detail=f"Tenant not found for domain {host}")
        
    return tenant
