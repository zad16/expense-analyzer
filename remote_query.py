import sqlite3
from datetime import datetime

db_path = '/home/Zaid/expense_analyzer/db/cashew-2026-03-29-17-21-47-863090.sql'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name, amount, date_created FROM transactions ORDER BY date_created DESC LIMIT 5")
rows = cur.fetchall()
for r in rows:
    dt = datetime.fromtimestamp(r[2]).strftime('%Y-%m-%d %H:%M:%S')
    print(f"{r[0]} | {r[1]} | {dt}")
