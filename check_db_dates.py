import sqlite3, glob, os
db_files = glob.glob('db/*.sql')
if not db_files:
    print('No database files found.')
    import sys
    sys.exit()
db = max(db_files, key=os.path.getmtime)
print('Using database: ' + db)
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
query = 'SELECT strftime(\"%Y-%m\", datetime(date_created, \"unixepoch\")) as month, count(*) as total, SUM(amount) as net FROM transactions GROUP BY month ORDER BY month DESC LIMIT 6'
rows = conn.execute(query).fetchall()
for row in rows:
    print(dict(row))
conn.close()
