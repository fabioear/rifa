from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
# Import models to ensure they are registered in the correct order
from app.models.tenant import Tenant
from app.models.user import User
from app.models.rifa import Rifa
from app.models.sorteio import Sorteio
from datetime import time, datetime, timedelta

def seed_sorteios():
    # Ensure tables exist
    # Note: create_all checks for table existence, it does not add columns to existing tables.
    # If adding columns, we might need to drop/recreate or assume migration handled elsewhere.
    # For dev speed, we'll try to update existing records if column exists or just recreate.
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Helper to calculate closing time (e.g. 20 mins before)
    def calc_fechamento(h: time) -> time:
        dt = datetime.combine(datetime.today(), h)
        dt_fechamento = dt - timedelta(minutes=20)
        return dt_fechamento.time()

    data = [
        {"nome": "Bandeirantes São Paulo 15h30 (BAN15)", "horario": time(15, 30), "ativo": True},
        {"nome": "Corujão (RJ CORUJÃO)", "horario": time(21, 20), "ativo": True},
        {"nome": "Federal 20:00 (FD 20:00)", "horario": time(20, 0), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 08h30 (LBR08)", "horario": time(8, 30), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 10h00 (LBR10)", "horario": time(10, 0), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 13h40 (LBR13)", "horario": time(13, 40), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 15h00 (LBR15)", "horario": time(15, 0), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 17h00 (LBR17)", "horario": time(17, 0), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 19h00 (LBR19)", "horario": time(19, 0), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 20h40 (LBR20)", "horario": time(20, 40), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 22h00 (LBR22)", "horario": time(22, 0), "ativo": True},
        {"nome": "LBR Loterias Brasília DF 23h00 (LBR23)", "horario": time(23, 0), "ativo": True},
        {"nome": "Look das 07h20 (LOOK07)", "horario": time(7, 20), "ativo": True},
        {"nome": "Look das 09h20 (LOOK09)", "horario": time(9, 20), "ativo": True},
        {"nome": "Look das 11h20 (LOOK11)", "horario": time(11, 20), "ativo": True},
        {"nome": "Look das 14h20 (LOOK14)", "horario": time(14, 20), "ativo": True},
        {"nome": "Look das 16h20 (LOOK16)", "horario": time(16, 20), "ativo": True},
        {"nome": "Look das 18h20 (LOOK18)", "horario": time(18, 20), "ativo": True},
        {"nome": "Look das 21h20 (LOOK21)", "horario": time(21, 20), "ativo": True},
        {"nome": "Look das 23h00 (LOOK23)", "horario": time(23, 0), "ativo": True},
        {"nome": "LOTEP Paraíba 09h45 (LOTEP09)", "horario": time(9, 45), "ativo": True},
        {"nome": "LOTEP Paraíba 10h45 (LOTEP10)", "horario": time(10, 45), "ativo": True},
        {"nome": "LOTEP Paraíba 12h45 (LOTEP12)", "horario": time(12, 45), "ativo": True},
        {"nome": "LOTEP Paraíba 15h45 (LOTEP15)", "horario": time(15, 45), "ativo": True},
        {"nome": "LOTEP Paraíba 18h00 (LOTEP18)", "horario": time(18, 0), "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 17:00)", "horario": time(17, 0), "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 18:30)", "horario": time(18, 30), "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 15:40)", "horario": time(15, 40), "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 14:00)", "horario": time(14, 0), "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 12:40)", "horario": time(12, 40), "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 11:00)", "horario": time(11, 0), "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 09:30)", "horario": time(9, 30), "ativo": True},
        {"nome": "Loteria Teste (TESTE)", "horario": time(23, 59), "ativo": True},
        {"nome": "Nacional (NC 02:00)", "horario": time(2, 0), "ativo": True},
        {"nome": "Nacional (NC 08:00)", "horario": time(8, 0), "ativo": True},
        {"nome": "Nacional (NC 10:00)", "horario": time(10, 0), "ativo": True},
        {"nome": "Nacional (NC 15:00)", "horario": time(15, 0), "ativo": True},
        {"nome": "Nacional (NC 17:00)", "horario": time(17, 0), "ativo": True},
        {"nome": "Nacional (NC 20:00)", "horario": time(20, 0), "ativo": True},
        {"nome": "Nacional (NC 23:00)", "horario": time(23, 0), "ativo": True},
        {"nome": "Paratodos Bahia 10h00 (PTBAH10)", "horario": time(10, 0), "ativo": True},
        {"nome": "Paratodos Bahia 12h00 (PTBAH12)", "horario": time(12, 0), "ativo": True},
        {"nome": "Paratodos Bahia 15h00 (PTBAH15)", "horario": time(15, 0), "ativo": True},
        {"nome": "Paratodos Bahia 19h00 (PTBAH19)", "horario": time(19, 0), "ativo": True},
        {"nome": "Paratodos Bahia 21h00 (PTBAH21)", "horario": time(21, 0), "ativo": True},
        {"nome": "PTN SP São Paulo 20h00 (PTN20)", "horario": time(20, 0), "ativo": True},
        {"nome": "PTSP São Paulo 08h30 (PTSP08)", "horario": time(8, 30), "ativo": True},
        {"nome": "PTSP São Paulo 10h30 (PTSP10)", "horario": time(10, 30), "ativo": True},
        {"nome": "PTSP São Paulo 12h20 (PTSP12)", "horario": time(12, 20), "ativo": True},
        {"nome": "PTSP São Paulo 13h30 (PTSP13)", "horario": time(13, 30), "ativo": True},
        {"nome": "PTSP São Paulo 17h20 (PTSP17)", "horario": time(17, 20), "ativo": True},
        {"nome": "PTSP São Paulo 18h20 (PTSP18)", "horario": time(18, 20), "ativo": True},
        {"nome": "PTSP São Paulo 19h00 (PTSP19)", "horario": time(19, 0), "ativo": True},
        {"nome": "RJ PPT (RJ PPT)", "horario": time(9, 20), "ativo": True},
        {"nome": "RJ PT (RJ PT)", "horario": time(14, 20), "ativo": True},
        {"nome": "RJ PTM (RJ PTM)", "horario": time(11, 20), "ativo": True},
        {"nome": "RJ PTN (RJ PTN)", "horario": time(18, 20), "ativo": True},
        {"nome": "RJ PTV (RJ PTV)", "horario": time(16, 20), "ativo": True},
    ]

    try:
        print("Seeding sorteios...")
        for item in data:
            exists = db.query(Sorteio).filter(Sorteio.nome == item["nome"]).first()
            if not exists:
                sorteio = Sorteio(**item)
                db.add(sorteio)
            else:
                pass
        
        db.commit()
        print("Sorteios seeded successfully!")
    except Exception as e:
        print(f"Error seeding sorteios: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sorteios()
