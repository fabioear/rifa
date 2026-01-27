import requests
import json
import uuid

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

def test_dashboard():
    token = login()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- Testing Dashboard Resumo ---")
    res = requests.get(f"{BASE_URL}/admin/dashboard/resumo", headers=headers)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- Testing Dashboard Financeiro ---")
    res = requests.get(f"{BASE_URL}/admin/dashboard/financeiro", headers=headers)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- Testing Dashboard Rifas ---")
    res = requests.get(f"{BASE_URL}/admin/dashboard/rifas", headers=headers)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))
    
    print("\n--- Testing Dashboard Usuarios ---")
    res = requests.get(f"{BASE_URL}/admin/dashboard/usuarios", headers=headers)
    print(f"Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    test_dashboard()
