import requests
import random
import time
import uuid
import sys
import os

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api/v1")
WEBHOOK_URL = f"{BASE_URL}/webhooks/picpay" # Assuming this is the path based on routers structure

# Rifa Constants from Prompt
RIFAS = {
    "Federal": {
        "id": "42b29fe2-63b7-4792-965d-eac2b9b2f641",
        "type": "Dezena",
        "range": (0, 99),
        "format": "{:02d}"
    },
    "Grupo": {
        "id": "b30bfb28-fc22-4442-9585-8261b4d5dc3c",
        "type": "Grupo",
        "range": (1, 25),
        "format": "{:02d}"
    },
    "Centena": {
        "id": "b4384fc6-7686-4fe3-950d-fb4eb64dfb4a",
        "type": "Centena",
        "range": (0, 999),
        "format": "{:03d}"
    },
    "Bandeirantes": {
        "id": "3959aa8a-2d0d-433f-b5aa-ad802e753cbf",
        "type": "Milhar",
        "range": (0, 9999),
        "format": "{:04d}"
    }
}

# User Configuration
NUM_USERS = 12 # Minimum 10
USERS = []
TOKENS = {}
USER_IPS = {}

def log(msg, type="INFO"):
    print(f"[{type}] {msg}")

def generate_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def create_user(index):
    """Creates a user with realistic data."""
    # Password requirement: min 6 chars, uppercase, number, special char
    password = "Password123!" 
    email = f"user_sim_{index}@simulation.com"
    ip = generate_ip()
    
    payload = {
        "email": email,
        "password": password
    }
    
    try:
        # Try to create
        resp = requests.post(f"{BASE_URL}/users/", json=payload)
        if resp.status_code in [200, 201]:
            log(f"User created: {email}", "SUCCESS")
        elif resp.status_code == 400 and "already registered" in resp.text:
            log(f"User already exists: {email}", "INFO")
        else:
            log(f"Failed to create user {email}: {resp.status_code} {resp.text}", "ERROR")
    except Exception as e:
        log(f"Exception creating user {email}: {e}", "ERROR")
        
    return {"email": email, "password": password, "ip": ip}

def login_user(user):
    """Authenticates user and stores token."""
    payload = {
        "username": user["email"],
        "password": user["password"]
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/login/access-token", data=payload)
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            TOKENS[user["email"]] = token
            USER_IPS[user["email"]] = user["ip"]
            log(f"Authenticated: {user['email']} (IP: {user['ip']})", "SUCCESS")
            return True
        else:
            log(f"Login failed for {user['email']}: {resp.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"Exception logging in {user['email']}: {e}", "ERROR")
        return False

def buy_number(user_email, rifa_name, number_str):
    """Simulates buying a number: Reserve -> Confirm Payment."""
    if user_email not in TOKENS:
        log(f"User {user_email} has no token", "ERROR")
        return False
        
    rifa = RIFAS[rifa_name]
    rifa_id = rifa["id"]
    token = TOKENS[user_email]
    ip = USER_IPS.get(user_email, "127.0.0.1")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Forwarded-For": ip
    }
    
    # 1. Reserve
    try:
        url = f"{BASE_URL}/rifas/{rifa_id}/numeros/{number_str}/reservar"
        resp = requests.post(url, headers=headers)
        
        if resp.status_code == 200:
            data = resp.json()
            payment_id = data.get("payment_id")
            log(f"Reserved: {rifa_name} #{number_str} by {user_email}", "SUCCESS")
            
            # 2. Simulate Payment Confirmation (Mock Webhook)
            # 80% chance to pay, 20% to leave reserved (which will expire later)
            if random.random() < 0.8 and payment_id:
                confirm_payment(payment_id, rifa_name, number_str)
                return "PAID"
            else:
                log(f"Left Reserved (Unpaid): {rifa_name} #{number_str}", "INFO")
                return "RESERVED"
                
        elif resp.status_code == 400:
            if "unavailable" in resp.text or "já reservado" in resp.text:
                 log(f"Number {number_str} already taken", "WARN")
            elif "não está ativa" in resp.text:
                 log(f"Rifa {rifa_name} is not active", "ERROR")
            else:
                 log(f"Error reserving {number_str}: {resp.text}", "ERROR")
        elif resp.status_code == 429:
             log(f"Rate Limited reserving {number_str}: {resp.text}", "WARN")
        else:
            log(f"Failed to reserve {number_str}: {resp.status_code} {resp.text}", "ERROR")
            
    except Exception as e:
        log(f"Exception buying {number_str}: {e}", "ERROR")
        
    return "FAILED"

def confirm_payment(payment_id, rifa_name, number_str):
    """Calls the webhook to confirm payment."""
    payload = {
        "payment_id": payment_id,
        "status": "paid"
    }
    
    try:
        resp = requests.post(WEBHOOK_URL, json=payload)
        if resp.status_code == 200:
            log(f"Payment Confirmed: {rifa_name} #{number_str}", "SUCCESS")
        else:
            log(f"Payment Confirmation Failed: {resp.status_code} {resp.text}", "ERROR")
    except Exception as e:
        log(f"Exception confirming payment: {e}", "ERROR")

def run_simulation():
    log("🚀 STARTING SIMULATION", "HEADER")
    
    # 1. Create Users
    log("--- Creating Users ---", "HEADER")
    for i in range(1, NUM_USERS + 1):
        u = create_user(i)
        USERS.append(u)
        
    # 2. Login Users
    log("--- Logging in ---", "HEADER")
    for u in USERS:
        login_user(u)
        
    # 3. Simulate Purchases
    log("--- Simulating Purchases ---", "HEADER")
    
    for name, rifa in RIFAS.items():
        log(f"Processing Rifa: {name} ({rifa['type']})", "HEADER")
        
        start, end = rifa["range"]
        fmt = rifa["format"]
        
        # Decide how many numbers to buy for this rifa (e.g., 20 random numbers)
        # For Federal (0-99), we can try to buy 30% of them
        # For Milhar, maybe 50 numbers
        
        total_numbers = end - start + 1
        num_to_buy = min(50, int(total_numbers * 0.4)) # Buy up to 50 or 40%
        
        if name == "Federal": num_to_buy = 40 # Buy 40 numbers (high density)
        if name == "Grupo": num_to_buy = 15 # Buy 15 groups
        
        log(f"Target: Buy {num_to_buy} numbers for {name}", "INFO")
        
        # Pick random numbers without replacement
        available_numbers = list(range(start, end + 1))
        selected_numbers = random.sample(available_numbers, num_to_buy)
        
        for num_int in selected_numbers:
            number_str = fmt.format(num_int)
            
            # Pick a random user
            user = random.choice(USERS)
            
            buy_number(user["email"], name, number_str)
            
            # Small delay to respect rate limits if any
            # Increased to 0.2 to stay safer, but with IP rotation we should be fine with lower delay too.
            # But let's keep it safe.
            time.sleep(0.1)
            
    log("🏁 SIMULATION COMPLETED", "HEADER")

if __name__ == "__main__":
    run_simulation()
