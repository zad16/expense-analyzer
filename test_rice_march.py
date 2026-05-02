import json
from app import query_finance_data

def test_rice():
    # rice transactions are in 2026-03
    print("Testing 'rice' as category (no quotes)...")
    res = query_finance_data("list", "2026-03-01", "2026-03-31", search_term="rice")
    print(f"Total spent on rice: {res.get('total_spent')}")
    for row in res.get('results', []):
        print(f"- {row['date']}: {row['transaction_name']} | {row['amount']} | {row['main_category']}")
    
    if res.get('total_spent', 0) > 0:
        print("SUCCESS: Found rice transactions without quotes.")
    else:
        print("FAILURE: No rice transactions found.")

if __name__ == "__main__":
    test_rice()
