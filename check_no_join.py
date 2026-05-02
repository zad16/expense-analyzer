from app import query_db, get_latest_db
import time
from datetime import date
start_str = date.today().replace(day=1).strftime('%Y-%m-%d')
end_str = date.today().strftime('%Y-%m-%d')
start_ts = int(time.mktime(time.strptime(start_str, '%Y-%m-%d')))
end_ts = int(time.mktime(time.strptime(end_str, '%Y-%m-%d'))) + 86399
query = f'''SELECT 
  SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income, 
  SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expenses 
  FROM transactions 
  WHERE paid = 1 AND date_created BETWEEN {start_ts} AND {end_ts} AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41'
'''
rows = query_db(query)
print('Without Join (March 2026):')
inc = rows[0]['income'] or 0
exp = rows[0]['expenses'] or 0
print(f"Income: {inc}")
print(f"Expenses: {exp}")
print(f"Diff: {inc - exp}")

q2 = "SELECT SUM(amount) as bal FROM transactions WHERE paid = 1"
r2 = query_db(q2)
print(f"\nAll time ALL WALLETS balance: {r2[0]['bal']}")

q3 = "SELECT SUM(amount) as bal FROM transactions WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41'"
r3 = query_db(q3)
print(f"All time NON-CC balance: {r3[0]['bal']}")

q4 = f'''SELECT SUM(amount) as bal FROM transactions WHERE paid = 1 AND date_created BETWEEN {start_ts} AND {end_ts}'''
r4 = query_db(q4)
print(f"March 2026 ALL WALLETS balance: {r4[0]['bal']}")
