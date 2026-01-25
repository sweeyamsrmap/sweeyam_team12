import requests
import json
import sys

def test_streaming():
    url = "http://localhost:8000/chat/message"
    
    payload = {
        "message": "Tell me a joke about programming",
        "session_id": 1 # Assumes session 1 exists
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer MOCK_OR_REAL_TOKEN"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    print(f"Chunk: {line.decode('utf-8')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_streaming()
