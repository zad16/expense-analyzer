from app import query_db
query_cc = '''SELECT 
  SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income, 
  SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as expenses 
  FROM transactions 
  WHERE paid = 1 AND date_created BETWEEN 1740787200 AND 1743465599 AND wallet_fk = 'c43a7127-daab-4b0c-a47f-f150130d4e41'
'''
r = query_db(query_cc)
inc = r[0]['income'] or 0
exp = r[0]['expenses'] or 0
print(f'March CC -> Income: {inc}, Expenses: {exp}, Diff: {inc - exp}, Net Balance: {inc - exp}')

query_all_time_cc = "SELECT SUM(amount) as bal FROM transactions WHERE paid = 1 AND wallet_fk = 'c43a7127-daab-4b0c-a47f-f150130d4e41'"
r2 = query_db(query_all_time_cc)
print(f"All time CC Balance: {r2[0]['bal']}")
