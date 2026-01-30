import psycopg2
import os
from dotenv import load_dotenv

# Load backend env
load_dotenv("backend/.env")

url = os.getenv("DATABASE_URL")
# Force connect to 'postgres'
if "/app_db" in url:
    url = url.replace("/app_db", "/postgres")
elif "/rifa_db" in url:
    url = url.replace("/rifa_db", "/postgres")

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
    
    print("\nTables in postgres DB:")
    tables = [row[0] for row in rows]
    for t in tables:
        print(f"- {t}")
        
    expected = ["users", "rifas", "sorteios"]
    found = [t for t in expected if t in tables]
    
    if found:
        print(f"\nFound expected Rifa tables in 'postgres' DB: {found}")
    else:
        print("\nDid NOT find expected Rifa tables in 'postgres' DB.")

    conn.close()
except Exception as e:
    print(f"\nError: {e}")
