from app import query_finance_data
import json

print("--- Keyword: shirt ---")
res_kw = query_finance_data(
    request_type="summary",
    start_date="2023-01-01",
    end_date="2023-12-31",
    keyword="shirt"
)
print(json.dumps(res_kw, indent=2))

print("\n--- Category: clothing ---")
res_cat = query_finance_data(
    request_type="summary",
    start_date="2023-01-01",
    end_date="2023-12-31",
    category="clothing"
)
print(json.dumps(res_cat, indent=2))
