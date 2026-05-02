from app import query_finance_data, get_latest_db, query_db
from datetime import date
import time

today = date.today()
start_str = today.replace(day=1).strftime("%Y-%m-%d")
end_str = today.strftime("%Y-%m-%d")

res = query_finance_data("summary", start_str, end_str)

print("--- Using query_finance_data ---")
print(f"Income: {res.get('income', 0)}")
print(f"Expenses: {res.get('expenses', 0)}")
print(f"Difference: {res.get('income', 0) - res.get('expenses', 0)}")

db_path = get_latest_db()
print(f"\n--- Manual Query ---")
print(f"Using DB: {db_path}")

start_ts = int(time.mktime(time.strptime(start_str, "%Y-%m-%d")))
end_ts = int(time.mktime(time.strptime(end_str, "%Y-%m-%d"))) + 86399

query = f"SELECT SUM(CASE WHEN t.amount > 0 THEN t.amount ELSE 0 END) as income, SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as expenses FROM transactions t WHERE t.paid = 1 AND t.date_created BETWEEN {start_ts} AND {end_ts} AND t.wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41'"

rows = query_db(query)
if rows and len(rows) > 0:
    income = rows[0]['income'] or 0
    expenses = rows[0]['expenses'] or 0
    print(f"Income: {income}")
    print(f"Expenses: {expenses}")
    print(f"Difference: {income - expenses}")
else:
    print("No rows returned from manual query.")
