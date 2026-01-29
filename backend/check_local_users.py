import sqlite3
import os

db_path = "sql_app.db"
if not os.path.exists(db_path):
    print(f"Database file {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email, role, is_active, phone FROM users")
        users = cursor.fetchall()
        print(f"Total users: {len(users)}")
        for user in users:
            print(f"- {user}")
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        conn.close()
