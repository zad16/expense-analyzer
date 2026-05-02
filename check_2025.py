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
    # Broad search for 2025
    query = """
        SELECT 
            t.name as transaction_name, 
            t.amount, 
            c.name as category, 
            date(t.date_created, 'unixepoch') as date 
        FROM transactions t 
        JOIN categories c ON t.category_fk = c.category_pk 
        WHERE t.name LIKE '%shirt%' AND t.paid = 1
        AND date >= '2025-01-01' AND date <= '2025-12-31'
    """
    res = conn.execute(query).fetchall()
    if not res:
        print("No transactions found for 'shirt' in 2025.")
        # Check all shopping/clothing categories in 2025
        print("\nChecking all Shopping/Self-care Grooming in 2025:")
        query2 = """
            SELECT t.name, t.amount, c.name as cat, date(t.date_created, 'unixepoch') as d
            FROM transactions t
            JOIN categories c ON t.category_fk = c.category_pk
            WHERE c.name IN ('Shopping', 'Self-care & Grooming')
            AND d >= '2025-01-01' AND d <= '2025-12-31'
            LIMIT 10
        """
        res2 = conn.execute(query2).fetchall()
        for r in res2:
            print(dict(r))
    else:
        for r in res:
            print(dict(r))
    conn.close()
