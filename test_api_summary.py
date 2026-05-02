from app import app
import json

def test_summary():
    app.testing = True
    with app.test_client() as client:
        # First login with the default PIN
        client.post('/login', data={'pin': '1234'})
        
        response = client.get('/api/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify that savings is present
        assert 'savings' in data['current'], "Savings not found in 'current'!"
        print(f"Current Balance (Savings): {data['current']['savings']}")

        # Verify db_info
        if 'db_info' in data:
            print(f"DB Info: {data['db_info']['name']} - {data['db_info']['date']}")

if __name__ == '__main__':
    test_summary()
