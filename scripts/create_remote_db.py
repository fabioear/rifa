import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load backend env
load_dotenv("backend/.env")

url = os.getenv("DATABASE_URL")
if not url:
    print("DATABASE_URL not found")
    exit(1)

# Connect to 'postgres' db to create new db
if "/app_db" in url:
    url_postgres = url.replace("/app_db", "/postgres")
else:
    # Fallback/Safety
    print(f"URL format unexpected: {url}")
    exit(1)

print(f"Connecting to postgres DB to create app_db...")

try:
    conn = psycopg2.connect(url_postgres)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    # Check if exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'app_db'")
    exists = cur.fetchone()
    
    if not exists:
        print("Creating database app_db...")
        cur.execute("CREATE DATABASE app_db;")
        print("Database app_db created successfully!")
    else:
        print("Database app_db already exists.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
