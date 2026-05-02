from app import query_finance_data
import json

res = query_finance_data(
    request_type="list",
    start_date="2023-01-01",
    end_date="2023-12-31",
    keyword="shirt",
    limit="10"
)
print(json.dumps(res, indent=2))
