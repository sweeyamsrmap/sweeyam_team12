import requests
import time

url = "http://localhost:8000/auth/register"
email = f"test_{int(time.time())}@example.com"
data = {
    "email": email,
    "password": "password123",
    "name": "Test User"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
