import sys
import os
import logging
from datetime import datetime, timezone

# Add backend to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.db.init_db import init_db
from app.models.rifa import Rifa, RifaStatus, RifaTipo, RifaLocal
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.tenant import Tenant
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate():
    db = SessionLocal()
    try:
        # 1. Create Default Tenant
        tenant = db.query(Tenant).filter(Tenant.domain == "localhost").first()
        if not tenant:
            logger.info("Creating Default Tenant...")
            tenant = Tenant(
                name="Imperio das Rifas",
                domain="localhost",
                primary_color="#000000",
                secondary_color="#FFFFFF"
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        
        # 2. Create Admin (linked to Tenant)
        # init_db(db) # This creates admin without tenant_id usually. Let's do it manually or update.
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            from app.core.security import get_password_hash
            admin = User(
                email="admin@example.com",
                password_hash=get_password_hash("admin"),
                role="admin",
                is_active=True,
                tenant_id=tenant.id
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        else:
            if not admin.tenant_id:
                admin.tenant_id = tenant.id
                db.commit()
        
        # 3. Create Rifa
        rifa = db.query(Rifa).filter(Rifa.titulo == "Rifa Teste", Rifa.tenant_id == tenant.id).first()
        if rifa:
             # Clean up if it exists but incomplete (or just reset)
             db.query(RifaNumero).filter(RifaNumero.rifa_id == rifa.id).delete()
             db.delete(rifa)
             db.commit()
             rifa = None

        if not rifa:
            logger.info("Creating Rifa Teste...")
            # For testing automatic closing job, set data_sorteio to future or past depending on what we want.
            # Let's set it to 1 hour from now for "active" test
            from datetime import timedelta
            rifa = Rifa(
                titulo="Rifa Teste",
                descricao="Rifa para teste de pagamento",
                preco_numero=10.0,
                status=RifaStatus.ATIVA,
                tipo_rifa=RifaTipo.DEZENA, # 00-99
                data_sorteio=datetime.now(timezone.utc) + timedelta(hours=1),
                local_sorteio=RifaLocal.PT_RJ,
                owner_id=admin.id,
                tenant_id=tenant.id
            )
            db.add(rifa)
            db.commit()
            db.refresh(rifa)
            
            # Create numbers for rifa
            logger.info("Creating numbers...")
            # For Dezena, it's 00-99
            for i in range(100):
                num_str = f"{i:02d}"
                n = RifaNumero(
                    rifa_id=rifa.id, 
                    numero=num_str, 
                    status=NumeroStatus.LIVRE, 
                    tipo=RifaTipo.DEZENA,
                    tenant_id=tenant.id
                )
                db.add(n)
            db.commit()
        
        # 3. Reserve Number 00
        num_00 = db.query(RifaNumero).filter(RifaNumero.rifa_id == rifa.id, RifaNumero.numero == "00").first()
        if num_00.status == NumeroStatus.LIVRE:
            logger.info("Reserving number 00...")
            payment_id = "PAY-TEST-001"
            num_00.status = NumeroStatus.RESERVADO
            num_00.user_id = admin.id
            num_00.payment_id = payment_id
            num_00.reserved_until = datetime.now(timezone.utc) + timedelta(minutes=15) # Valid for 15 minutes
            # Actually user wants to test webhook, so let's give it a valid payment_id
            db.commit()
            print(f"\n\nSUCESSO! Dados para teste:")
            print(f"Rifa ID: {rifa.id}")
            print(f"Numero: 00")
            print(f"Payment ID: {payment_id}")
            print(f"Comando para testar webhook:")
            print(f'Invoke-RestMethod -Uri "http://localhost:8000/api/v1/webhooks/picpay" -Method Post -ContentType "application/json" -Body \'{{"payment_id": "{payment_id}", "status": "paid"}}\'')
        else:
            print(f"\nNumero 00 ja reservado/pago. Payment ID: {num_00.payment_id}")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate()
