from app import query_db

q_2025 = "SELECT SUM(amount) FROM transactions WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41' AND strftime('%Y-%m', datetime(date_created, 'unixepoch')) = '2025-03'"
print("2025-03:", query_db(q_2025))

q_2026 = "SELECT SUM(amount) FROM transactions WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41' AND strftime('%Y-%m', datetime(date_created, 'unixepoch')) = '2026-03'"
print("2026-03:", query_db(q_2026))

q_2026_ts = "SELECT SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income, SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as exp, SUM(amount) as bal FROM transactions WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41' AND date_created >= 1772303400"
print("2026-03 TS:", [dict(r) for r in query_db(q_2026_ts)])

q_2025_ts = "SELECT SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income, SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as exp, SUM(amount) as bal FROM transactions WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41' AND date_created BETWEEN 1740767400 AND 1743465599"
print("2025-03 TS:", [dict(r) for r in query_db(q_2025_ts)])
