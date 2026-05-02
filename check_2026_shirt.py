import sqlite3
import glob
import os

BACKUP_DIR = r"G:\My Drive\cashew_backup"

def get_latest_db():
    files = glob.glob(os.path.join(BACKUP_DIR, "*.sql"))
    if not files: return None
    return max(files, key=os.path.getmtime)

db_path = get_latest_db()
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
query = "SELECT t.name, t.amount, c.name as cat, date(t.date_created, 'unixepoch') as d FROM transactions t JOIN categories c ON t.category_fk = c.category_pk WHERE t.name LIKE '%shirt%' AND d LIKE '2026%'"
res = conn.execute(query).fetchall()
for r in res:
    print(dict(r))
conn.close()
