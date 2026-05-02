import sqlite3
import glob
import os
from dotenv import load_dotenv

load_dotenv()
BACKUP_DIR = os.getenv("BACKUP_DIR")

def get_latest_db():
    files = glob.glob(os.path.join(BACKUP_DIR, "*.sql"))
    if not files: return None
    return max(files, key=os.path.getmtime)

db_path = get_latest_db()
if not db_path:
    print("No database found.")
else:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("--- Table Info: transactions ---")
    cursor.execute("PRAGMA table_info(transactions)")
    for row in cursor.fetchall():
        print(dict(row))
        
    print("\n--- Sample Transactions for March ---")
    # 1740787200 is roughly March 1st 2026 (assuming seconds)
    cursor.execute("SELECT * FROM transactions WHERE date_created > 1740787200 LIMIT 5")
    for row in cursor.fetchall():
        print(dict(row))
    
    conn.close()
