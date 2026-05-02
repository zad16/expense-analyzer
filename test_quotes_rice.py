import json
from app import query_finance_data

def test_quotes():
    print("Testing 'rice' with single quotes...")
    res = query_finance_data("list", "2026-03-01", "2026-03-31", search_term="'rice'")
    print(f"Results: {len(res.get('results', []))}")
    for r in res.get('results', []):
        print(f"  {r['date']}: {r['transaction_name']}")

    print("\nTesting \"rice\" with double quotes...")
    res2 = query_finance_data("list", "2026-03-01", "2026-03-31", search_term='"rice"')
    print(f"Results: {len(res2.get('results', []))}")

if __name__ == "__main__":
    test_quotes()
