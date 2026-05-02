import sqlite3
import glob
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
BACKUP_DIR = os.getenv("BACKUP_DIR", r"G:\My Drive\cashew_backup")

def get_latest_db():
    files = glob.glob(os.path.join(BACKUP_DIR, "*.sql"))
    if not files: return None
    return max(files, key=os.path.getmtime)

db_path = get_latest_db()
if not db_path:
    print("No database found.")
else:
    print(f"Using DB: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n--- Wallets ---")
    try:
        rows = cursor.execute("SELECT * FROM wallets").fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e: print(e)

    print("\n--- Transaction Wallet Stats ---")
    try:
        rows = cursor.execute("SELECT wallet_fk, COUNT(*) as count, SUM(amount) as total_sum FROM transactions GROUP BY wallet_fk").fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e: print(e)
    
    conn.close()
