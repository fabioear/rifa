import psycopg2
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT email, role FROM users")
    rows = cur.fetchall()
    print("Users found in DB (via tunnel):")
    for r in rows:
        print(f"- {r[0]} ({r[1]})")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
