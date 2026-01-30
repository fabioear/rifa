import psycopg2
import os
from dotenv import load_dotenv

# Load backend env
load_dotenv("backend/.env")

url = os.getenv("DATABASE_URL")
# We want to check 'readme_to_recover'
if "/app_db" in url:
    url = url.replace("/app_db", "/readme_to_recover")
elif "/rifa_db" in url:
    url = url.replace("/rifa_db", "/readme_to_recover")

print(f"Connecting to: {url}")

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    # List tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    rows = cur.fetchall()
    
    print("\nTables in readme_to_recover:")
    tables = [row[0] for row in rows]
    for t in tables:
        print(f"- {t}")
        
    # Check for specific tables expected in Rifa system
    expected = ["users", "rifas", "sorteios"]
    found = [t for t in expected if t in tables]
    
    if found:
        print(f"\nFound expected Rifa tables: {found}")
    else:
        print("\nDid NOT find expected Rifa tables.")

    conn.close()
except Exception as e:
    print(f"\nError connecting/querying: {e}")
