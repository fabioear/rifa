import os
import sys
import uuid
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path so we can import app modules if needed
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/rifas_db"

engine = create_engine(DATABASE_URL)

def populate_sorteios():
    data = [
        {"nome": "Bandeirantes São Paulo 15h30 (BAN15)", "horario": "15:30:00", "ativo": True},
        {"nome": "Corujão (RJ CORUJÃO)", "horario": "21:20:00", "ativo": True},
        {"nome": "Federal 20:00 (FD 20:00)", "horario": "20:00:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 08h30 (LBR08)", "horario": "08:30:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 10h00 (LBR10)", "horario": "10:00:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 13h40 (LBR13)", "horario": "13:40:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 15h00 (LBR15)", "horario": "15:00:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 17h00 (LBR17)", "horario": "17:00:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 19h00 (LBR19)", "horario": "19:00:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 20h40 (LBR20)", "horario": "20:40:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 22h00 (LBR22)", "horario": "22:00:00", "ativo": True},
        {"nome": "LBR Loterias Brasília DF 23h00 (LBR23)", "horario": "23:00:00", "ativo": True},
        {"nome": "Look das 07h20 (LOOK07)", "horario": "07:20:00", "ativo": True},
        {"nome": "Look das 09h20 (LOOK09)", "horario": "09:20:00", "ativo": True},
        {"nome": "Look das 11h20 (LOOK11)", "horario": "11:20:00", "ativo": True},
        {"nome": "Look das 14h20 (LOOK14)", "horario": "14:20:00", "ativo": True},
        {"nome": "Look das 16h20 (LOOK16)", "horario": "16:20:00", "ativo": True},
        {"nome": "Look das 18h20 (LOOK18)", "horario": "18:20:00", "ativo": True},
        {"nome": "Look das 21h20 (LOOK21)", "horario": "21:20:00", "ativo": True},
        {"nome": "Look das 23h00 (LOOK23)", "horario": "23:00:00", "ativo": True},
        {"nome": "LOTEP Paraíba 09h45 (LOTEP09)", "horario": "09:45:00", "ativo": True},
        {"nome": "LOTEP Paraíba 10h45 (LOTEP10)", "horario": "10:45:00", "ativo": True},
        {"nome": "LOTEP Paraíba 12h45 (LOTEP12)", "horario": "12:45:00", "ativo": True},
        {"nome": "LOTEP Paraíba 15h45 (LOTEP15)", "horario": "15:45:00", "ativo": True},
        {"nome": "LOTEP Paraíba 18h00 (LOTEP18)", "horario": "18:00:00", "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 17:00)", "horario": "17:00:00", "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 18:30)", "horario": "18:30:00", "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 15:40)", "horario": "15:40:00", "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 14:00)", "horario": "14:00:00", "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 12:40)", "horario": "12:40:00", "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 11:00)", "horario": "11:00:00", "ativo": True},
        {"nome": "Loteria Popular - Recife (LPR 09:30)", "horario": "09:30:00", "ativo": True},
        {"nome": "Loteria Teste (TESTE)", "horario": "23:59:00", "ativo": True},
        {"nome": "Nacional (NC 02:00)", "horario": "02:00:00", "ativo": True},
        {"nome": "Nacional (NC 08:00)", "horario": "08:00:00", "ativo": True},
        {"nome": "Nacional (NC 10:00)", "horario": "10:00:00", "ativo": True},
        {"nome": "Nacional (NC 15:00)", "horario": "15:00:00", "ativo": True},
        {"nome": "Nacional (NC 17:00)", "horario": "17:00:00", "ativo": True},
        {"nome": "Nacional (NC 20:00)", "horario": "20:00:00", "ativo": True},
        {"nome": "Nacional (NC 23:00)", "horario": "23:00:00", "ativo": True},
        {"nome": "Paratodos Bahia 10h00 (PTBAH10)", "horario": "10:00:00", "ativo": True},
        {"nome": "Paratodos Bahia 12h00 (PTBAH12)", "horario": "12:00:00", "ativo": True},
        {"nome": "Paratodos Bahia 15h00 (PTBAH15)", "horario": "15:00:00", "ativo": True},
        {"nome": "Paratodos Bahia 19h00 (PTBAH19)", "horario": "19:00:00", "ativo": True},
        {"nome": "Paratodos Bahia 21h00 (PTBAH21)", "horario": "21:00:00", "ativo": True},
        {"nome": "PTN SP São Paulo 20h00 (PTN20)", "horario": "20:00:00", "ativo": True},
        {"nome": "PTSP São Paulo 08h30 (PTSP08)", "horario": "08:30:00", "ativo": True},
        {"nome": "PTSP São Paulo 10h30 (PTSP10)", "horario": "10:30:00", "ativo": True},
        {"nome": "PTSP São Paulo 12h20 (PTSP12)", "horario": "12:20:00", "ativo": True},
        {"nome": "PTSP São Paulo 13h30 (PTSP13)", "horario": "13:30:00", "ativo": True},
        {"nome": "PTSP São Paulo 17h20 (PTSP17)", "horario": "17:20:00", "ativo": True},
        {"nome": "PTSP São Paulo 18h20 (PTSP18)", "horario": "18:20:00", "ativo": True},
        {"nome": "PTSP São Paulo 19h00 (PTSP19)", "horario": "19:00:00", "ativo": True},
        {"nome": "RJ PPT (RJ PPT)", "horario": "09:20:00", "ativo": True},
        {"nome": "RJ PT (RJ PT)", "horario": "14:20:00", "ativo": True},
        {"nome": "RJ PTM (RJ PTM)", "horario": "11:20:00", "ativo": True},
        {"nome": "RJ PTN (RJ PTN)", "horario": "18:20:00", "ativo": True},
        {"nome": "RJ PTV (RJ PTV)", "horario": "16:20:00", "ativo": True},
    ]

    with engine.connect() as connection:
        try:
            print(f"Checking {len(data)} items...")
            
            # Since 'nome' is unique, we check if exists, then insert if not.
            # Or use upsert (ON CONFLICT DO UPDATE).
            
            for item in data:
                # Check existence
                result = connection.execute(
                    text("SELECT id FROM sorteios WHERE nome = :nome"),
                    {"nome": item["nome"]}
                )
                existing = result.fetchone()
                
                if existing:
                    # Update
                    connection.execute(
                        text("UPDATE sorteios SET horario = :horario, ativo = :ativo WHERE id = :id"),
                        {
                            "horario": item["horario"],
                            "ativo": item["ativo"],
                            "id": existing[0]
                        }
                    )
                    # print(f"Updated {item['nome']}")
                else:
                    # Insert
                    connection.execute(
                        text("INSERT INTO sorteios (id, nome, horario, ativo) VALUES (:id, :nome, :horario, :ativo)"),
                        {
                            "id": uuid.uuid4(),
                            "nome": item["nome"],
                            "horario": item["horario"],
                            "ativo": item["ativo"]
                        }
                    )
                    # print(f"Inserted {item['nome']}")
            
            connection.commit()
            print(f"Processed {len(data)} sorteios successfully.")
            
        except Exception as e:
            connection.rollback()
            print(f"Error seeding sorteios: {e}")

if __name__ == "__main__":
    populate_sorteios()
