from app import query_finance_data
import json
print(json.dumps(query_finance_data('summary', '2023-01-01', '2027-01-01')))
