import sqlite3
import glob
import os
from datetime import datetime

BACKUP_DIR = r"G:\My Drive\cashew_backup"

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
    query = "SELECT t.name, t.amount, date(t.date_created, 'unixepoch') as d FROM transactions t WHERE t.name LIKE '%shirt%'"
    res = conn.execute(query).fetchall()
    if not res:
        print("No transactions found containing 'shirt' in the entire database.")
    else:
        for r in res:
            print(dict(r))
    conn.close()
