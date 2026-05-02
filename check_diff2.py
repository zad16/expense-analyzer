from app import query_db
import time
from datetime import date

q_diff = """
SELECT date_created, amount, name, datetime(date_created, 'unixepoch') as utc_date 
FROM transactions 
WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41' 
AND (
    (strftime('%Y-%m', datetime(date_created, 'unixepoch')) = '2026-03' AND date_created NOT BETWEEN 1740767400 AND 1743465599)
    OR
    (strftime('%Y-%m', datetime(date_created, 'unixepoch')) != '2026-03' AND date_created BETWEEN 1740767400 AND 1743465599)
)
"""
rows = query_db(q_diff)
if not rows:
    print('No diff rows found.')
else:
    for r in rows:
        print(dict(r))
