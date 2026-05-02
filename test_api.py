from app import app
with app.test_client() as c:
 response = c.get('/api/summary')
 print(response.get_json())
