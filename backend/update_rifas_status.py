import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback/Default for local development if not set
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/rifas_db"

print(f"Connecting to database: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

def update_rifas():
    with engine.connect() as connection:
        # Get all rifas ordered by creation time to be deterministic
        # Usando 'titulo' conforme modelo Rifa
        try:
            result = connection.execute(text("SELECT id, titulo FROM rifas ORDER BY created_at"))
            rifas = result.fetchall()
        except Exception as e:
            print(f"Error fetching rifas: {e}")
            return

        print(f"Found {len(rifas)} rifas.")

        # Check valid enum values
        try:
            result = connection.execute(text("SELECT enum_range(NULL::rifastatus)"))
            valid_statuses = result.scalar()
            print(f"Valid RifaStatus enum values in DB: {valid_statuses}")
        except Exception as e:
            print(f"Could not fetch enum values: {e}")
            # Fallback based on Python code if DB query fails, but we should see the output
            # statuses = ["ativa", "encerrada", "rascunho", "apurada"] 

        if len(rifas) < 4:
            print("Warning: Less than 4 rifas found. Updating available ones.")

        statuses = ["ATIVA", "ENCERRADA", "RASCUNHO", "APURADA"] # Will update this list based on DB output
        
        # Mapeamento de status
        # Rifa 1 -> Ativa (Verde)
        # Rifa 2 -> Encerrada (Vermelha - pedido do usuário)
        # Rifa 3 -> Rascunho (Azul - implementado agora)
        # Rifa 4 -> Apurada (Outro)
        
        # Se houver mais rifas do que status, repete o último ou ciclo
        
        try:
            for i, rifa in enumerate(rifas):
                status = statuses[i % len(statuses)]
                rifa_id = rifa[0]
                rifa_title = rifa[1]
                
                print(f"Updating Rifa '{rifa_title}' ({rifa_id}) to status '{status}'")
                
                connection.execute(
                    text("UPDATE rifas SET status = :status WHERE id = :id"),
                    {"status": status, "id": rifa_id}
                )
            
            connection.commit()
            print("Successfully updated rifas statuses.")
            
        except Exception as e:
            connection.rollback()
            print(f"Error updating rifas: {e}")

if __name__ == "__main__":
    update_rifas()
