import requests
import uuid
import pytest
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def login():
    print("--- Login ---")
    response = requests.post(f"{BASE_URL}/login/access-token", data={
        "username": "admin@example.com",
        "password": "admin"
    })
    if response.status_code == 200:
        print("Login Successful")
        return response.json()["access_token"]
    else:
        print(f"Login Failed: {response.text}")
        return None

def test_dashboard(token):
    print("\n--- Testing Dashboard ---")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/admin/dashboard/resumo", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")

def test_finance(token):
    print("\n--- Testing Finance Global ---")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/admin/financeiro", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")

def test_rifa_finance(token, rifa_id):
    print(f"\n--- Testing Finance Rifa {rifa_id} ---")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/admin/financeiro/rifas/{rifa_id}", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")

def test_audit(token):
    print("\n--- Testing Audit ---")
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{BASE_URL}/admin/auditoria", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")

def test_results(token):
    print("\n--- Testing Results ---")
    headers = {"Authorization": f"Bearer {token}"}
    rifas = requests.get(f"{BASE_URL}/rifas/", headers=headers).json()
    if not rifas:
        print("No rifas found")
        return

    rifa = rifas[0]
    rifa_id = rifa["id"]
    print(f"Using Rifa: {rifa['titulo']} ({rifa_id})")

    # 0. Open Rifa (Ensure it's active)
    print("\n--- Opening Rifa ---")
    requests.put(
        f"{BASE_URL}/rifas/{rifa_id}", 
        json={"status": "ativa"},
        headers=headers
    )

    # 1. Simulate Payment for number "01"
    print(f"\n--- Simulating Payment for '01' ---")
    numeros = requests.get(f"{BASE_URL}/rifas/{rifa_id}/numeros", headers=headers).json()
    num_01 = next((n for n in numeros if n["numero"] == "01"), None)
    
    if num_01:
        print(f"Num 01 status: {num_01['status']}")
        if num_01["status"] == "livre":
             # Reserve first
             print("Reserving '01'...")
             res_res = requests.post(f"{BASE_URL}/rifas/{rifa_id}/numeros/01/reservar", headers=headers)
             if res_res.status_code == 200:
                 # Fetch again to get payment_id
                 numeros = requests.get(f"{BASE_URL}/rifas/{rifa_id}/numeros", headers=headers).json()
                 num_01 = next((n for n in numeros if n["numero"] == "01"), None)
        
        if num_01 and num_01.get("payment_id"):
            payment_id = num_01.get("payment_id")
            print(f"Payment ID: {payment_id}")
            
            # Pay via Webhook
            webhook_res = requests.post(
                f"{BASE_URL}/webhooks/picpay",
                json={"payment_id": payment_id, "status": "paid"}
            )
            print(f"Webhook Status: {webhook_res.status_code}")
        else:
            print("Could not get payment_id for '01'")
            
    # 2. Close Rifa
    print("\n--- Closing Rifa ---")
    update_res = requests.put(
        f"{BASE_URL}/rifas/{rifa_id}", 
        json={"status": "encerrada"},
        headers=headers
    )
    print(f"Close Status: {update_res.status_code}")
    
    # 3. Define Result
    print("\n--- Defining Result '01' ---")
    res_def = requests.post(
        f"{BASE_URL}/admin/rifas/{rifa_id}/resultado",
        json={
            "resultado": "01",
            "local_sorteio": "PT-RJ",
            "data_resultado": datetime.utcnow().isoformat()
        },
        headers=headers
    )
    print(f"Define Result Status: {res_def.status_code}")
    print(f"Response: {res_def.text}")
    
    # 4. Apurar Rifa
    print("\n--- Apurar Rifa ---")
    res_apurar = requests.post(
        f"{BASE_URL}/admin/rifas/{rifa_id}/apurar",
        headers=headers
    )
    print(f"Apurar Status: {res_apurar.status_code}")
    print(f"Response: {res_apurar.text}")
    
    # 5. Get Winners
    print("\n--- Get Winners ---")
    ganhadores = requests.get(f"{BASE_URL}/admin/rifas/{rifa_id}/ganhadores", headers=headers)
    print(f"Status: {ganhadores.status_code}")
    print(f"Response: {ganhadores.text}")

if __name__ == "__main__":
    token = login()
    if token:
        test_dashboard(token)
        test_finance(token)
        test_audit(token)
        test_results(token)
