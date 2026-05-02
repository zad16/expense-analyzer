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
    print(f"Using DB: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check range of date_created
    cursor.execute("SELECT MIN(date_created), MAX(date_created), COUNT(*) FROM transactions")
    mi, ma, count = cursor.fetchone()
    print(f"Total transactions: {count}")
    print(f"Min date_created: {mi}")
    print(f"Max date_created: {ma}")
    
    if mi:
        # Check if it looks like seconds or milliseconds
        if mi > 10**11: # Milliseconds
            print("Detected Milliseconds timestamp.")
            print(f"Min Date: {datetime.fromtimestamp(mi/1000)}")
            print(f"Max Date: {datetime.fromtimestamp(ma/1000)}")
        else:
            print("Detected Seconds timestamp.")
            print(f"Min Date: {datetime.fromtimestamp(mi)}")
            print(f"Max Date: {datetime.fromtimestamp(ma)}")
            
    conn.close()
