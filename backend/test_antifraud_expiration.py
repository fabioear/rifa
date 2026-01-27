import sys
import os
import time
import requests
from datetime import datetime, timedelta, timezone

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from sqlalchemy import text

from app.db.session import SessionLocal
from app.models.rifa_numero import RifaNumero, NumeroStatus
from app.models.antifraud import BlockedEntity, BlockedEntityType
from app.models.user import User
from app.models.tenant import Tenant
from app.core.scheduler import release_expired_reservations, run_antifraud_analysis

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@example.com"  # Using admin for test, but any user works
PASSWORD = "admin"


def get_token():
    response = requests.post(
        f"{BASE_URL}/login/access-token",
        data={"username": EMAIL, "password": PASSWORD},
    )
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        sys.exit(1)
    return response.json()["access_token"]


def main():
    print("--- Testing Anti-Fraud: Excessive Expirations ---")

    # 1. Setup
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    db = SessionLocal()

    # Get Rifa ID (assuming one exists from populate_data)
    rifa_res = requests.get(f"{BASE_URL}/rifas", headers=headers)
    rifas = rifa_res.json()
    if not rifas:
        print("No rifas found. Run populate_data.py first.")
        return

    rifa_id = rifas[0]["id"]
    print(f"Using Rifa ID: {rifa_id}")

    # Resolve user_id directly from DB
    user = db.query(User).filter(User.email == EMAIL).first()
    if not user:
        print(f"User {EMAIL} not found. Run populate_data.py first.")
        return
    user_id = str(user.id)

    # Clean existing active reservations for this user
    db.query(RifaNumero).filter(
        RifaNumero.user_id == user.id,
        RifaNumero.status == NumeroStatus.RESERVADO,
    ).update(
        {
            RifaNumero.status: NumeroStatus.LIVRE,
            RifaNumero.user_id: None,
            RifaNumero.payment_id: None,
            RifaNumero.reserved_until: None,
        },
        synchronize_session=False,
    )
    db.commit()

    # Clear existing blocks for this user (to start fresh)
    db.query(BlockedEntity).filter(
        BlockedEntity.type == BlockedEntityType.USER,
        BlockedEntity.value == user_id,
    ).delete()
    db.commit()
    print(f"Cleared existing blocks for user {user_id}")

    # 2. Loop to generate expirations
    total_expired = 0
    target_expirations = 12
    batch_size = 4

    while total_expired < target_expirations:
        print(f"\nStarting batch... (Current expired: {total_expired})")

        # 2.1 Reserve numbers
        nums_res = requests.get(f"{BASE_URL}/rifas/{rifa_id}/numeros", headers=headers)
        numeros = nums_res.json()
        livres = [n for n in numeros if n["status"] == "livre"]

        if len(livres) < batch_size:
            print("Not enough free numbers to continue test.")
            break

        current_batch = []
        for i in range(batch_size):
            num = livres[i]
            print(f"Reserving {num['numero']}...")
            res = requests.post(
                f"{BASE_URL}/rifas/{rifa_id}/numeros/{num['numero']}/reservar",
                headers=headers,
            )
            if res.status_code == 200:
                current_batch.append(num["numero"])
            elif res.status_code == 400 and "Limite" in res.text:
                print("Hit reservation limit unexpectedly.")
                break
            else:
                print(f"Error reserving: {res.text}")

        if not current_batch:
            print("Could not reserve any numbers in this batch.")
            break

        print(f"Reserved {len(current_batch)} numbers.")

        # 2.2 Force Expiration in DB (mark reserved_until in the past)
        print("Forcing expiration in DB...")
        past_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        db.query(RifaNumero).filter(
            RifaNumero.rifa_id == rifa_id,
            RifaNumero.numero.in_(current_batch),
            RifaNumero.status == NumeroStatus.RESERVADO,
        ).update(
            {RifaNumero.reserved_until: past_time},
            synchronize_session=False,
        )
        db.commit()

        # 2.3 Run Release Job
        print("Running release_expired_reservations job...")
        release_expired_reservations()

        # Check if numbers became LIVRE (Canonical Rule)
        recheck_nums = db.query(RifaNumero).filter(
            RifaNumero.rifa_id == rifa_id,
            RifaNumero.numero.in_(current_batch)
        ).all()
        
        for n in recheck_nums:
            if n.status != NumeroStatus.LIVRE:
                print(f"FAILURE: Number {n.numero} is {n.status}, expected LIVRE")
            else:
                # print(f"Verified: Number {n.numero} returned to LIVRE")
                pass

        total_expired += len(current_batch)
        print(f"Batch complete. Total expired so far: {total_expired}")

        time.sleep(1)

    # 3. Run Analysis
    print("\nRunning Anti-Fraud Analysis...")
    run_antifraud_analysis()

    # 4. Check Block Status
    print("Checking if user is blocked...")
    blocked = db.query(BlockedEntity).filter(
        BlockedEntity.type == BlockedEntityType.USER,
        BlockedEntity.value == user_id,
    ).first()

    if blocked:
        print(f"SUCCESS: User is blocked! Reason: {blocked.reason}")
    else:
        print("FAILURE: User is NOT blocked.")

    db.close()


if __name__ == "__main__":
    main()
