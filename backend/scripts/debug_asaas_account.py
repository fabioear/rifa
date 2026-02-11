import httpx
import asyncio
from app.core.config import settings

async def debug_account():
    headers = {
        "access_token": settings.ASAAS_API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"API Key: {settings.ASAAS_API_KEY[:10]}...")
    
    async with httpx.AsyncClient() as client:
        # 1. Get Account Info
        # Note: Asaas doesn't have a direct /account/me endpoint publicly documented for standard keys always, 
        # but /myAccount/commercialInfo or /installments might give clues. 
        # Actually /api/v3/myAccount is valid.
        
        print("\n--- Verificando Conta ---")
        resp = await client.get(f"{settings.ASAAS_API_URL}/myAccount", headers=headers)
        if resp.status_code == 200:
            print(resp.json())
        else:
            print(f"Erro ao buscar conta: {resp.status_code} {resp.text}")

        # 2. Try to create a simple Pix Payment directly
        print("\n--- Tentando Criar Pagamento Pix (Teste Direto) ---")
        
        # Create or find a customer first
        customer_id = None
        resp_cust = await client.get(f"{settings.ASAAS_API_URL}/customers?limit=1", headers=headers)
        if resp_cust.status_code == 200 and resp_cust.json().get("data"):
            customer_id = resp_cust.json()["data"][0]["id"]
            print(f"Usando Cliente existente: {customer_id}")
        else:
            # Create dummy
            payload_cust = {
                "name": "Teste Debug",
                "cpfCnpj": "95751047494"
            }
            resp_create = await client.post(f"{settings.ASAAS_API_URL}/customers", json=payload_cust, headers=headers)
            if resp_create.status_code == 200:
                customer_id = resp_create.json()["id"]
                print(f"Cliente criado: {customer_id}")
            else:
                print(f"Erro ao criar cliente: {resp_create.text}")
                return

        if customer_id:
            from datetime import datetime
            # Test fetching QR Code for the previous Boleto (or new one)
            # Create a new one with UNDEFINED to see behavior
            payload_pay = {
                "customer": customer_id,
                "billingType": "UNDEFINED",
                "value": 10.0,
                "dueDate": datetime.now().strftime("%Y-%m-%d"),
                "description": "Teste Debug Script Undefined"
            }
            resp_pay = await client.post(f"{settings.ASAAS_API_URL}/payments", json=payload_pay, headers=headers)
            print(f"Status Pagamento (UNDEFINED): {resp_pay.status_code}")
            print(f"Body: {resp_pay.text}")
            
            if resp_pay.status_code == 200:
                pay_id = resp_pay.json()["id"]
                print(f"Pagamento Criado: {pay_id}")
                
                # Try getting QR Code
                print("\n--- Tentando obter QR Code ---")
                resp_qr = await client.get(f"{settings.ASAAS_API_URL}/payments/{pay_id}/pixQrCode", headers=headers)
                print(f"Status QR Code: {resp_qr.status_code}")
                print(f"Body QR Code: {resp_qr.text}")

        # 3. Check Wallet/Pix Settings
        print("\n--- Verificando Configurações da Carteira/Pix ---")
        # Check if there is any endpoint to check pix status specifically or wallet config
        # Not documented publicly, but checking 'myAccount/paymentCheckoutConfig' or similar might help
        resp_conf = await client.get(f"{settings.ASAAS_API_URL}/myAccount/paymentCheckoutConfig", headers=headers)
        if resp_conf.status_code == 200:
             print("Configuração Checkout:")
             print(resp_conf.json())
        else:
             print(f"Erro config checkout: {resp_conf.status_code}")

if __name__ == "__main__":
    asyncio.run(debug_account())
