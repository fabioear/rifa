import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"

def login():
    response = requests.post(f"{BASE_URL}/login/access-token", data={
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        print("Login Failed:", response.text)
        exit(1)
    return response.json()["access_token"]

def test_antifraud():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get a Rifa
    rifas = requests.get(f"{BASE_URL}/rifas/", headers=headers).json()
    if not rifas:
        print("No active rifas found. Run populate_data.py first.")
        return
    
    rifa_id = rifas[0]["id"]
    print(f"Testing Anti-Fraud on Rifa: {rifa_id}")
    
    # 2. Try to reserve 6 numbers (Limit is 5)
    print("\n--- Testing Max Simultaneous Reservations (Limit: 5) ---")
    
    # We need available numbers. Let's find 6 available numbers.
    numeros = requests.get(f"{BASE_URL}/rifas/{rifa_id}/numeros", headers=headers).json()
    livres = [n for n in numeros if n["status"] == "livre"]
    
    if len(livres) < 6:
        print("Not enough numbers to test limit.")
        # Try to clean up user reservations if any?
        # Or just proceed with what we have.
    
    count = 0
    for num in livres[:6]:
        num_str = num["numero"]
        print(f"Reserving {num_str}...")
        res = requests.post(f"{BASE_URL}/rifas/{rifa_id}/numeros/{num_str}/reservar", headers=headers)
        
        if res.status_code == 200:
            print(f"Success: {num_str}")
            count += 1
        elif res.status_code == 429:
            print(f"BLOCKED: {num_str} - {res.json()['detail']}")
        else:
            print(f"Error: {res.status_code} - {res.text}")
            
        # Cooldown check needs delay?
        # If we hit cooldown, we should wait.
        if res.status_code == 429 and "Aguarde" in res.json()['detail']:
            print("Hit cooldown, waiting 10s...")
            time.sleep(10) 
            # Retry
            res = requests.post(f"{BASE_URL}/rifas/{rifa_id}/numeros/{num_str}/reservar", headers=headers)
            print(f"Retry status: {res.status_code}")
            if res.status_code == 200: count += 1

    print(f"\nTotal reserved: {count}")
    
    # 3. Test Cooldown specifically
    print("\n--- Testing Cooldown (10s) ---")
    if len(livres) > 10:
        n1 = livres[10]["numero"]
        n2 = livres[11]["numero"]
        
        # Reserve n1
        print(f"Reserving {n1}...")
        requests.post(f"{BASE_URL}/rifas/{rifa_id}/numeros/{n1}/reservar", headers=headers)
        
        # Immediately try n2
        print(f"Reserving {n2} immediately...")
        res = requests.post(f"{BASE_URL}/rifas/{rifa_id}/numeros/{n2}/reservar", headers=headers)
        
        if res.status_code == 429:
            print(f"Success: Request Blocked by Cooldown - {res.json()['detail']}")
        else:
            print(f"Failed: Request passed ({res.status_code}) - {res.text}")

if __name__ == "__main__":
    test_antifraud()
