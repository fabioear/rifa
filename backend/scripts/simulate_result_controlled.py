import requests
import json
import random
import uuid
import sys
import os
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin" # Assuming default
HEADERS = {}

def login_admin():
    print("Logging in as Admin...")
    response = requests.post(f"{API_URL}/login/access-token", data={
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        token = response.json()["access_token"]
        HEADERS["Authorization"] = f"Bearer {token}"
        print("Admin Logged In Successfully")
        return True
    else:
        print(f"Admin Login Failed: {response.text}")
        return False

def get_rifas():
    print("Fetching active rifas...")
    response = requests.get(f"{API_URL}/rifas/", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return []

def get_paid_numbers(rifa_id):
    print(f"Fetching paid numbers for rifa {rifa_id}...")
    # This endpoint might not exist publicly, using DB directly or assuming we can pick any
    # Actually, as admin we can see all numbers. 
    # But let's try to find a public endpoint or admin endpoint.
    # GET /api/admin/rifas/{rifa_id}/numeros (hypothetical)
    # If not, let's use the public /rifas/{rifa_id} endpoint which usually returns available numbers, 
    # but we need PAID numbers.
    # Let's use the DB session in this script for direct access to find a winner candidate?
    # No, requirement says "simulate_result_controlled.py". It should probably use API.
    # But finding WHO bought WHAT via API might be tricky without a specific endpoint.
    # Let's assume we can pick a number that is NOT available (RESERVADO/PAGO).
    # Or better, let's query the database directly to find a PAGO number to ensure a winner.
    pass

# Direct DB Access for picking a winner candidate
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
from app.db.session import SessionLocal
from app.models import tenant  # noqa: F401
from app.models.rifa import Rifa, RifaStatus, RifaTipo
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.user import User

def pick_winner_candidate_and_close():
    db = SessionLocal()
    try:
        # Find a rifa that has sold numbers
        rifas = db.query(Rifa).filter(Rifa.status == RifaStatus.ATIVA).all()
        
        target_rifa = None
        target_number = None
        
        print(f"Found {len(rifas)} active rifas. Searching for one with sales...")
        
        for rifa in rifas:
            # Check for sold numbers
            sold = db.query(RifaNumero).filter(
                RifaNumero.rifa_id == rifa.id,
                RifaNumero.status == NumeroStatus.PAGO
            ).first()
            
            if sold:
                target_rifa = rifa
                target_number = sold.numero
                print(f"Selected Rifa: {rifa.titulo} (ID: {rifa.id})")
                print(f"Selected Winner Number: {target_number} (User: {sold.user_id})")
                break
        
        if not target_rifa:
            print("No active rifa with sales found. Please run simulation_full.py first.")
            return

        # Close Rifa via API
        print(f"Closing Rifa {target_rifa.id}...")
        res = requests.post(f"{API_URL}/admin/rifas/{target_rifa.id}/fechar", headers=HEADERS)
        if res.status_code != 200:
            print(f"Failed to close rifa: {res.text}")
            return
        print("Rifa Closed Successfully.")
        
        print(f"Tallying Rifa with result: {target_number}...")

        payload = {
            "resultado": target_number,
            "data_resultado": datetime.now().isoformat(),
            "local_sorteio": "Federal"
        }

        res_resultado = requests.post(
            f"{API_URL}/admin/rifas/{target_rifa.id}/resultado",
            headers=HEADERS,
            json=payload,
        )
        if res_resultado.status_code != 200:
            print(f"Failed to create resultado: {res_resultado.text}")
            return

        res_apurar = requests.post(
            f"{API_URL}/admin/rifas/{target_rifa.id}/apurar",
            headers=HEADERS,
        )

        if res_apurar.status_code == 200:
            print("SUCCESS! Rifa apurada.")
            res_ganhadores = requests.get(
                f"{API_URL}/admin/rifas/{target_rifa.id}/ganhadores",
                headers=HEADERS,
            )
            if res_ganhadores.status_code == 200:
                data = res_ganhadores.json()
                print(f"Resultado oficial: {data.get('resultado', {}).get('valor')}")
                print(f"Total de ganhadores: {len(data.get('ganhadores', []))}")
            else:
                print("Rifa apurada, mas não foi possível carregar ganhadores.")
        else:
            print(f"Failed to tally rifa: {res_apurar.text}")

    finally:
        db.close()

if __name__ == "__main__":
    if login_admin():
        pick_winner_candidate_and_close()
