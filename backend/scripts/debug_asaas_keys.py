import sys
import os
import httpx
import asyncio

# Adiciona o diretório pai (backend) ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings

async def list_pix_keys():
    print(f"URL: {settings.ASAAS_API_URL}")
    # Mascarar a chave para exibir
    key_masked = settings.ASAAS_API_KEY[:10] + "..." + settings.ASAAS_API_KEY[-5:]
    print(f"API Key: {key_masked}")

    url = f"{settings.ASAAS_API_URL}/pix/addressKeys"
    headers = {
        "access_token": settings.ASAAS_API_KEY,
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            print("\nConsultando chaves Pix na API do Asaas...")
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nStatus: {response.status_code}")
                print(f"Total de chaves encontradas: {data.get('totalCount', 0)}")
                for key in data.get('data', []):
                    print(f"- Chave: {key.get('key')} | Tipo: {key.get('type')} | Status: {key.get('status')}")
            else:
                print(f"Erro ao consultar chaves: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Erro de conexão: {e}")

if __name__ == "__main__":
    asyncio.run(list_pix_keys())
