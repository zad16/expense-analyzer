from app import query_db
import time

q1 = "SELECT SUM(amount) as bal FROM transactions WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41' AND date_created BETWEEN 1740787200 AND 1743465599"
print("March UTC start/end SUM(amount):", query_db(q1)[0]['bal'])

q2 = "SELECT SUM(amount) as bal FROM transactions WHERE paid = 1 AND wallet_fk != 'c43a7127-daab-4b0c-a47f-f150130d4e41' AND strftime('%Y-%m', datetime(date_created, 'unixepoch')) = '2026-03'"
print("March strftime SUM(amount):", query_db(q2)[0]['bal'])

# Check what get_history returns for 2026-03
from app import get_history
for h in get_history():
    if 'March 2026' in h['month']:
        print("get_history March 2026:", h)
