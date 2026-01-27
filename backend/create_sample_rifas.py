import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add current directory to path
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models.user import User
from app.models.rifa import Rifa, RifaStatus

def create_sample_rifas():
    db = SessionLocal()
    try:
        # Get Admin User
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("❌ Erro: Nenhum admin encontrado para ser dono das rifas.")
            return

        # Sample Data
        rifas_data = [
            {
                "titulo": "iPhone 15 Pro Max",
                "descricao": "Sorteio de um iPhone 15 Pro Max 256GB. Cor Titânio Natural.",
                "preco_numero": Decimal("0.50"),
                "quantidade_numeros": 10000,
                "data_sorteio": datetime.now() + timedelta(days=7),
                "status": RifaStatus.ATIVA
            },
            {
                "titulo": "Honda CB 300F Twister",
                "descricao": "Moto 0km, emplacada e com tanque cheio!",
                "preco_numero": Decimal("1.00"),
                "quantidade_numeros": 20000,
                "data_sorteio": datetime.now() + timedelta(days=15),
                "status": RifaStatus.ATIVA
            },
            {
                "titulo": "Pix de R$ 5.000,00",
                "descricao": "Dinheiro na conta na hora!",
                "preco_numero": Decimal("0.25"),
                "quantidade_numeros": 50000,
                "data_sorteio": datetime.now() + timedelta(days=3),
                "status": RifaStatus.RASCUNHO
            }
        ]

        created_count = 0
        for data in rifas_data:
            exists = db.query(Rifa).filter(Rifa.titulo == data["titulo"]).first()
            if not exists:
                rifa = Rifa(
                    **data,
                    owner_id=admin.id
                )
                db.add(rifa)
                created_count += 1
                print(f"➕ Criando Rifa: {data['titulo']}")
            else:
                print(f"ℹ️ Rifa já existe: {data['titulo']}")

        db.commit()
        
        # Verify total
        total = db.query(Rifa).count()
        print("------------------------------------------------")
        print(f"✅ Processo concluído.")
        print(f"🆕 Rifas criadas agora: {created_count}")
        print(f"📊 Total de rifas no banco: {total}")
        print("------------------------------------------------")

    except Exception as e:
        print(f"❌ Erro ao criar rifas: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_rifas()
