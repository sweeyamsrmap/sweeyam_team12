import requests
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            print("[PASS] Health Check")
        else:
            print(f"[FAIL] Health Check: {r.status_code}")
    except Exception as e:
        print(f"[FAIL] Connection refused: {e}")

def test_auth_flow():
    email = "test@example.com"
    password = "password123"
    name = "Test User"
    
    # Register
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "name": name})
        if r.status_code == 200:
            print("[PASS] Register")
        elif r.status_code == 400 and "already registered" in r.text:
             print("[PASS] Register (User already exists)")
        else:
            print(f"[FAIL] Register: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[fail] Register Exception: {e}")
        return

    # Login
    try:
        r = requests.post(f"{BASE_URL}/auth/token", data={"username": email, "password": password})
        if r.status_code == 200:
            print("[PASS] Login")
            token = r.json()["access_token"]
            return token
        else:
            print(f"[FAIL] Login: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[FAIL] Login Exception: {e}")

def test_chat_flow(token):
    if not token:
        print("[SKIP] Chat Flow (No token)")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Session
    session_id = None
    try:
        r = requests.post(f"{BASE_URL}/chat/sessions", json={"title": "Integration Test Chat"}, headers=headers)
        if r.status_code == 200:
            print("[PASS] Create Session")
            session_id = r.json()["id"]
        else:
            print(f"[FAIL] Create Session: {r.status_code} {r.text}")
            return
    except Exception as e:
        print(f"[FAIL] Create Session Exception: {e}")
        return

    # 2. Send Message
    try:
        msg = {"message": "Hello, create a plan for learning Rust.", "session_id": session_id}
        r = requests.post(f"{BASE_URL}/chat/message", json=msg, headers=headers)
        if r.status_code == 200:
            print(f"[PASS] Send Message (Response: {r.json().get('type', 'unknown')})")
        else:
            print(f"[FAIL] Send Message: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[FAIL] Send Message Exception: {e}")

    # 3. Get History
    try:
        r = requests.get(f"{BASE_URL}/chat/history/{session_id}", headers=headers)
        if r.status_code == 200:
            history = r.json()
            if len(history) >= 2: # User msg + Agent msg
                print("[PASS] Get History")
            else:
                 print(f"[FAIL] Get History: Expected >=2 messages, got {len(history)}")
        else:
            print(f"[FAIL] Get History: {r.status_code} {r.text}")
    except Exception as e:
        print(f"[FAIL] Get History Exception: {e}")

if __name__ == "__main__":
    print("Running Integration Tests...")
    print("Ensure backend is running at localhost:8000")
    test_health()
    token = test_auth_flow()
    test_chat_flow(token)
