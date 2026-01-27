from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.routers import rifas, auth, webhooks, admin, payments, dashboard, sorteios, admin_settings
from app.db.init_db import init_db
from app.core.scheduler import scheduler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables on startup (if not exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup Event ---
@app.on_event("startup")
def on_startup():
    logger.info("Checking for initial data...")
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        logger.error(f"Error during startup initialization: {e}")
    finally:
        db.close()
    
    # Start Scheduler
    logger.info("Starting background scheduler...")
    scheduler.start()

@app.on_event("shutdown")
def on_shutdown():
    logger.info("Shutting down background scheduler...")
    scheduler.shutdown()

# --- Routers ---
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(rifas.router, prefix="/api/v1/rifas", tags=["rifas"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(dashboard.router, prefix="/api/v1/admin/dashboard", tags=["dashboard"])
app.include_router(payments.router, prefix="/api/v1/pagamentos", tags=["pagamentos"])
app.include_router(sorteios.router, prefix="/api/v1")
app.include_router(admin_settings.router, prefix="/api/v1/admin", tags=["admin-settings"])

@app.get("/")
def root():
    return {"message": "Welcome to Império das Rifas API"}
