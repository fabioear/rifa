import psycopg2
import os
from dotenv import load_dotenv

# Load backend env
load_dotenv("backend/.env")

url = os.getenv("DATABASE_URL")
print(f"Testing connection to: {url}")

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("Connection SUCCESSFUL!")
    conn.close()
except Exception as e:
    print(f"Connection FAILED: {e}")
