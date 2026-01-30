import psycopg2
import os
from dotenv import load_dotenv

# Try to load backend env
load_dotenv("backend/.env")

# Get URL from env or use the one we know fails to see if we can connect to 'postgres' DB
url = os.getenv("DATABASE_URL")
if not url:
    print("DATABASE_URL not found in environment")
    exit(1)

# Replace database name with 'postgres' (default maintenance db)
# Assumes format postgresql://user:pass@host:port/dbname
if "/app_db" in url:
    url = url.replace("/app_db", "/postgres")
elif "/rifa_db" in url:
    url = url.replace("/rifa_db", "/postgres")

print(f"Connecting to: {url}")

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    rows = cur.fetchall()
    print("\nDatabases found:")
    for row in rows:
        print(f"- {row[0]}")
    conn.close()
except Exception as e:
    print(f"\nError connecting: {e}")
