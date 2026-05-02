from app import query_finance_data

def test_curly_quotes():
    print("Testing with single curly quotes...")
    res = query_finance_data("list", "2026-03-01", "2026-03-31", search_term="‘rice’")
    print(f"Results: {len(res.get('results', []))}")

    print("Testing with straight single quotes inside...")
    res = query_finance_data("list", "2026-03-01", "2026-03-31", search_term="'rice'")
    print(f"Results: {len(res.get('results', []))}")

if __name__ == "__main__":
    test_curly_quotes()
