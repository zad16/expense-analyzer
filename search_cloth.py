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
    query = """
        SELECT 
            t.name as transaction_name, 
            ABS(t.amount) as amount, 
            c.name as category, 
            date(t.date_created, 'unixepoch') as date 
        FROM transactions t 
        JOIN categories c ON t.category_fk = c.category_pk 
        WHERE (t.name LIKE ? OR c.name LIKE ?) AND t.paid = 1
        ORDER BY t.date_created DESC
    """
    res = conn.execute(query, ('%cloth%', '%cloth%')).fetchall()
    for r in res:
        print(f"Date: {r['date']} | Name: {r['transaction_name']} | Amount: ₹{r['amount']} | Category: {r['category']}")
    conn.close()
