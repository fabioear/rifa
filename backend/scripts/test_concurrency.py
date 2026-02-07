import asyncio
import httpx
import uuid
from typing import Optional

# Configuração (ajuste conforme necessário para seu ambiente local)
BASE_URL = "http://localhost:8000/api/v1"
RIFA_ID = "" # Será preenchido dinamicamente ou manualmente
NUMERO_ALVO = "01" # Número que ambos tentarão pegar

# Simula login para obter token (precisamos de 2 usuários diferentes)
async def get_token(email: str, password: str) -> str:
    async with httpx.AsyncClient() as client:
        # Tenta login normal
        resp = await client.post(f"{BASE_URL}/login/access-token", data={
            "username": email,
            "password": password
        })
        if resp.status_code == 200:
            return resp.json()["access_token"]
        print(f"Erro login {email}: {resp.text}")
        return None

# Simula a tentativa de reserva
async def attempt_reserve(user_name: str, token: str, rifa_id: str, numero: str):
    print(f"[{user_name}] Tentando reservar número {numero}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{BASE_URL}/rifas/{rifa_id}/numeros/{numero}/reservar",
                headers=headers,
                timeout=10.0
            )
            
            if resp.status_code == 200:
                print(f"✅ [{user_name}] SUCESSO! Reservou o número {numero}.")
                return True
            elif resp.status_code == 409: # Conflict
                print(f"❌ [{user_name}] FALHOU! Número já reservado (409 Conflict).")
                return False
            else:
                print(f"⚠️ [{user_name}] Erro inesperado: {resp.status_code} - {resp.text}")
                return False
                
        except Exception as e:
            print(f"💥 [{user_name}] Exceção: {e}")
            return False

async def main():
    print("--- Teste de Concorrência de Reserva ---")
    
    # 1. Configurar Tokens (Você precisa ter 2 usuários no banco)
    # Use as credenciais que você sabe que existem ou crie usuários de teste antes
    # Assumindo admin e um user comum, ou dois users.
    # Ajuste aqui com credenciais reais do seu banco local
    token_user_a = await get_token("suporte@imperiodasrifas.app.br", "Admin123") # Admin
    token_user_b = await get_token("teste@exemplo.com", "123456") # Outro user (crie se não existir)
    
    if not token_user_a:
        print("Falha ao logar User A. Abortando.")
        return

    # Se não tiver user B, vamos tentar criar ou usar o mesmo só pra testar a logica de bloqueio (mesmo user reservando de novo recebe msg diferente, mas serve pra teste basico se for 409)
    # Mas o ideal é user diferente. Se não tiver, o teste vai mostrar que o mesmo usuário consegue "re-reservar" ou ver msg "já é seu".
    # Vamos assumir que queremos testar o BLOQUEIO.
    
    # 2. Obter uma Rifa Ativa (ou criar)
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token_user_a}"}
        resp = await client.get(f"{BASE_URL}/rifas/", headers=headers)
        rifas = resp.json()
        ativa = next((r for r in rifas if r["status"] == "ATIVA"), None)
        
        if not ativa:
            print("Nenhuma rifa ATIVA encontrada. Crie uma rifa primeiro.")
            return
            
        rifa_id = ativa["id"]
        tipo = ativa["tipo_rifa"]
        print(f"Rifa Alvo: {ativa['titulo']} ({rifa_id}) - Tipo: {tipo}")
        
        # Escolher um número válido para o tipo
        numero_teste = "01"
        if tipo == "milhar": numero_teste = "0001"
        elif tipo == "centena": numero_teste = "001"
    
    print(f"Iniciando disputa pelo número {numero_teste}...")
    
    # 3. Executar reservas "quase" simultâneas
    # User A vai primeiro
    success_a = await attempt_reserve("User A", token_user_a, rifa_id, numero_teste)
    
    if success_a:
        print("Aguardando 1 segundo...")
        await asyncio.sleep(1)
        
        # User B tenta o MESMO número
        # Se não tiver token B, simulamos com o A de novo para ver o comportamento (deve dizer 'já reservado por você')
        # Mas para provar segurança entre usuários, precisamos de token diferente.
        if token_user_b:
            await attempt_reserve("User B", token_user_b, rifa_id, numero_teste)
        else:
            print("Sem token B para testar conflito de outro usuário. Tentando com User A novamente (deve retornar info de pagamento existente)...")
            await attempt_reserve("User A (Re-try)", token_user_a, rifa_id, numero_teste)
            
    # Limpeza (Opcional): Cancelar a reserva para deixar limpo?
    # Deixe reservado para você verificar no frontend se quiser.

if __name__ == "__main__":
    asyncio.run(main())
