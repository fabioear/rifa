import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.rifa import Rifa

db = SessionLocal()
rifas = db.query(Rifa).all()
for r in rifas:
    print(f"Rifa: {r.titulo} | ID: {r.id} | Status: {r.status}")
db.close()
