import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user import User
from app.models.rifa import Rifa  # Import to register model
from app.core.security import get_password_hash

def create_users():
    db = SessionLocal()
    try:
        # 1. Admin User
        admin_email = "suporte@imperiodasrifas.app.br"
        admin_pass = "Sab3375*"
        
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            print(f"Criando Admin: {admin_email}")
            admin = User(
                email=admin_email,
                password_hash=get_password_hash(admin_pass),
                role="admin",
                is_active=True
            )
            db.add(admin)
        else:
            print(f"Atualizando Admin existente: {admin_email}")
            admin.role = "admin" # Ensure role is admin
            # Optional: Update password if needed, but risky if user changed it. 
            # For dev env, maybe okay, but let's stick to role update.
        
        # 2. Player User
        player_email = "jogador@jogador.com.br"
        player_pass = "jogador"
        
        player = db.query(User).filter(User.email == player_email).first()
        if not player:
            print(f"Criando Player: {player_email}")
            player = User(
                email=player_email,
                password_hash=get_password_hash(player_pass),
                role="player",
                is_active=True
            )
            db.add(player)
        else:
            print(f"Player já existe: {player_email}")

        db.commit()
        print("------------------------------------------------")
        print("✅ Usuários garantidos no banco de dados:")
        print(f"👑 ADMIN:   {admin_email}  | Senha: {admin_pass}")
        print(f"👤 JOGADOR: {player_email}      | Senha: {player_pass}")
        print("------------------------------------------------")

    except Exception as e:
        print(f"❌ Erro ao criar usuários: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_users()
