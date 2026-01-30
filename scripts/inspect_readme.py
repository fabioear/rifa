import psycopg2
import os
from dotenv import load_dotenv

# Load backend env
load_dotenv("backend/.env")

url = os.getenv("DATABASE_URL")
if "/app_db" in url:
    url = url.replace("/app_db", "/readme_to_recover")
elif "/rifa_db" in url:
    url = url.replace("/rifa_db", "/readme_to_recover")

print(f"Connecting to: {url}")

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM readme LIMIT 5")
    rows = cur.fetchall()
    
    print("\nContent of 'readme' table:")
    for row in rows:
        print(row)

    conn.close()
except Exception as e:
    print(f"\nError: {e}")
