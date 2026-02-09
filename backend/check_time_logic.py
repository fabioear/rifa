
import sys
import os
from datetime import datetime, timezone, timedelta

# Add backend directory to path
sys.path.append("/app")

from app.db.session import SessionLocal
from app.models.rifa import Rifa, RifaStatus

def check_times():
    db = SessionLocal()
    try:
        now_utc = datetime.now(timezone.utc)
        now_minus_3 = now_utc - timedelta(hours=3)
        
        print(f"Current UTC Time: {now_utc}")
        print(f"Current 'Shifted' Time (UTC-3): {now_minus_3}")
        
        rifas = db.query(Rifa).filter(Rifa.status == RifaStatus.ATIVA).limit(5).all()
        
        print("\nChecking Active Rifas:")
        for r in rifas:
            print(f"ID: {r.id}")
            print(f"  Title: {r.titulo}")
            print(f"  Data Sorteio (DB value): {r.data_sorteio} (Type: {type(r.data_sorteio)})")
            print(f"  Hora Encerramento (DB value): {r.hora_encerramento}")
            
            should_close_utc = False
            if r.hora_encerramento:
                should_close_utc = r.hora_encerramento <= now_utc
            elif r.data_sorteio:
                should_close_utc = r.data_sorteio <= now_utc
                
            should_close_shifted = False
            if r.hora_encerramento:
                should_close_shifted = r.hora_encerramento <= now_minus_3
            elif r.data_sorteio:
                should_close_shifted = r.data_sorteio <= now_minus_3
            
            print(f"  Should close (Standard UTC logic)? {should_close_utc}")
            print(f"  Should close (Current Shifted logic)? {should_close_shifted}")
            print("-" * 30)
            
    finally:
        db.close()

if __name__ == "__main__":
    check_times()
