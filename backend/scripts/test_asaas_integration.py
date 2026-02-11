import sys
import os
# Adiciona o diretório pai (backend) ao path para importar app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app, base_url="http://localhost")

def test_flow():
    print("=== TESTE DE INTEGRAÇÃO ASAAS ===")
    
    # 1. Login
    print("\n1. Autenticando...")
    # Tenta credenciais padrão conhecidas ou pede para criar
    login_payload = {"username": "suporte@imperiodasrifas.app.br", "password": "Admin123"}
    resp = client.post("/api/v1/login/access-token", data=login_payload)
    
    if resp.status_code != 200:
        print(f"Erro no login: {resp.text}")
        print("Verifique se o usuário 'suporte@imperiodasrifas.app.br' existe.")
        return
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login OK.")

    # 2. Buscar Rifa Ativa
    print("\n2. Buscando Rifa Ativa...")
    resp = client.get("/api/v1/rifas?skip=0&limit=100", headers=headers)
    if resp.status_code != 200:
        print(f"Erro ao buscar rifas: {resp.text}")
        return
        
    rifas = resp.json()
    # Tenta encontrar rifa ativa com preço 10.00 (para garantir valor minimo do Asaas)
    active_rifa = next((r for r in rifas if r["status"] == "ativa" and float(r.get("preco_numero", 0)) == 10.0), None)
    
    if not active_rifa:
        print("Nenhuma rifa ativa de R$ 10,00 encontrada. Tentando criar uma rifa de teste...")
        from datetime import datetime, timedelta
        
        rifa_data = {
            "titulo": "Rifa Teste Asaas 10",
            "descricao": "Rifa automática para teste de integração (R$ 10)",
            "preco_numero": 10.00,
            "quantidade_numeros": 100,
            "tipo_rifa": "dezena",
            "data_sorteio": (datetime.now() + timedelta(days=7)).isoformat(),
            "status": "ativa",
            "local_sorteio": "Loteria Federal"
        }
        
        resp = client.post("/api/v1/rifas/", json=rifa_data, headers=headers)
        if resp.status_code != 200:
             print(f"Erro ao criar rifa de teste: {resp.text}")
             return
             
        active_rifa = resp.json()
        print(f"Rifa de teste criada: {active_rifa['titulo']}")
    
    rifa_id = active_rifa["id"]
    print(f"Rifa selecionada: {active_rifa['titulo']} (ID: {rifa_id})")

    # 3. Buscar Número Livre
    print("\n3. Buscando número livre...")
    resp = client.get(f"/api/v1/rifas/{rifa_id}/numeros", headers=headers)
    numeros = resp.json()
    livre = next((n for n in numeros if n["status"] == "livre"), None)
    
    if not livre:
        print("Todos os números desta rifa estão ocupados.")
        return
    
    numero = livre["numero"]
    print(f"Número selecionado: {numero}")

    # 4. Reservar
    print(f"\n4. Reservando número {numero}...")
    resp = client.post(f"/api/v1/rifas/{rifa_id}/numeros/{numero}/reservar", headers=headers)
    if resp.status_code != 200:
        print(f"Erro ao reservar: {resp.text}")
        # Tenta liberar se for meu
        if "já está reservado" in resp.text:
             print("Número já reservado, tentando usar assim mesmo se for meu...")
    else:
        print("Reserva realizada com sucesso.")

    # 5. Checkout (Chamada ao Asaas)
    print("\n5. Gerando Pagamento no Asaas (Checkout)...")
    payload = {
        "rifa_id": rifa_id,
        "numeros": [numero]
    }
    
    try:
        resp = client.post("/api/v1/pagamentos/checkout", json=payload, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            print("\n✅ SUCESSO! INTEGRAÇÃO FUNCIONANDO!")
            print("-" * 40)
            print(f"Payment ID (Sistema): {data['payment_id']}")
            print(f"Asaas ID            : {data['asaas_id']}")
            print(f"Valor               : R$ {data['amount']}")
            print(f"Pix Copia e Cola    : {data['pix_code'][:50]}...")
            print("-" * 40)
            print("O QR Code foi gerado corretamente pelo Asaas.")
        else:
            print(f"\n❌ ERRO NO CHECKOUT: {resp.status_code}")
            print(resp.text)
            
    except Exception as e:
        print(f"\n❌ EXCEÇÃO: {e}")

if __name__ == "__main__":
    test_flow()
