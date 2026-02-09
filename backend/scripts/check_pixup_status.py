import asyncio
import os
import sys
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.pixup_service import pixup_service

async def check_recent_payments():
    print("--- Verificando Pagamentos Recentes na Pixup ---")
    
    # Define intervalo de tempo (últimas 24h)
    # Ajuste o fuso horário se necessário (assumindo UTC para API)
    fim = datetime.utcnow()
    inicio = fim - timedelta(hours=24)
    
    # Formato BACEN: 2020-10-22T00:00:00.000Z
    fmt = "%Y-%m-%dT%H:%M:%S.000Z"
    
    print(f"Buscando de {inicio.strftime(fmt)} até {fim.strftime(fmt)}")
    
    try:
        token = await pixup_service._get_access_token()
        print(f"Token obtido com sucesso.")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Tenta endpoint padrão BACEN /v2/pix
        url = f"{pixup_service.base_url}/v2/pix"
        params = {
            "inicio": inicio.strftime(fmt),
            "fim": fim.strftime(fmt)
        }
        
        print(f"Consultando URL: {url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                pix_list = data.get("pix", [])
                print(f"\nEncontrados {len(pix_list)} pagamentos no período.")
                
                found_any = False
                for p in pix_list:
                    txid = p.get("txid")
                    valor = p.get("valor")
                    endToEndId = p.get("endToEndId")
                    horario = p.get("horario")
                    
                    # Tenta extrair payment_id (Referência)
                    info = p.get("infoAdicionais", [])
                    ref = "N/A"
                    for i in info:
                        if i.get("nome") == "Referência":
                            ref = i.get("valor")
                            
                    print(f"------------------------------------------------")
                    print(f"Data: {horario}")
                    print(f"TXID: {txid}")
                    print(f"Valor: {valor}")
                    print(f"Ref (Payment ID): {ref}")
                    print(f"E2E ID: {endToEndId}")
                    found_any = True
                
                if found_any:
                    print(f"------------------------------------------------")
            else:
                print(f"Erro na resposta: {response.text}")
                
    except Exception as e:
        print(f"Exceção ao executar script: {e}")

if __name__ == "__main__":
    # Carrega .env se necessario (backend ja carrega no config, mas por seguranca)
    load_dotenv()
    asyncio.run(check_recent_payments())
