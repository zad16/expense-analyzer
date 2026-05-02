from app import query_db

q = '''SELECT date_created, amount, name, datetime(date_created, 'unixepoch') as utc_date 
FROM transactions 
WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41' 
AND date_created >= 1772303400 AND strftime('%Y-%m', datetime(date_created, 'unixepoch')) = '2026-02'
'''
rows = query_db(q)
if not rows:
    print("No rows found.")
else:
    for r in rows:
        print(dict(r))
