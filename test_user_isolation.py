"""
Test script to verify user data isolation between different accounts.
This ensures User A cannot see User B's data.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_user_isolation():
    print("=" * 60)
    print("USER DATA ISOLATION TEST")
    print("=" * 60)
    
    # Step 1: Create two test users
    print("\n1. Creating two test users...")
    
    user_a_data = {
        "name": "Test User A",
        "email": "usera@test.com",
        "password": "password123"
    }
    
    user_b_data = {
        "name": "Test User B",
        "email": "userb@test.com",
        "password": "password123"
    }
    
    # Register users (may already exist)
    try:
        requests.post(f"{BASE_URL}/auth/register", json=user_a_data)
        print("✓ User A registered")
    except:
        print("✓ User A already exists")
    
    try:
        requests.post(f"{BASE_URL}/auth/register", json=user_b_data)
        print("✓ User B registered")
    except:
        print("✓ User B already exists")
    
    # Step 2: Login as User A
    print("\n2. Logging in as User A...")
    response_a = requests.post(f"{BASE_URL}/auth/token", data={
        "username": user_a_data["email"],
        "password": user_a_data["password"]
    })
    
    if response_a.status_code != 200:
        print(f"✗ Failed to login as User A: {response_a.text}")
        return
    
    token_a = response_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print(f"✓ User A logged in (token: {token_a[:20]}...)")
    
    # Step 3: Login as User B
    print("\n3. Logging in as User B...")
    response_b = requests.post(f"{BASE_URL}/auth/token", data={
        "username": user_b_data["email"],
        "password": user_b_data["password"]
    })
    
    if response_b.status_code != 200:
        print(f"✗ Failed to login as User B: {response_b.text}")
        return
    
    token_b = response_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    print(f"✓ User B logged in (token: {token_b[:20]}...)")
    
    # Step 4: User A creates a goal
    print("\n4. User A creates a goal...")
    goal_a = requests.post(f"{BASE_URL}/goals/", 
                           json={"text": "User A's Secret Goal", "deadline": "2 weeks"},
                           headers=headers_a)
    
    if goal_a.status_code == 200:
        print(f"✓ User A created goal: {goal_a.json()['text']}")
    else:
        print(f"✗ Failed to create goal for User A")
    
    # Step 5: User A creates a chat session
    print("\n5. User A creates a chat session...")
    session_a = requests.post(f"{BASE_URL}/chat/sessions",
                              json={"title": "User A's Private Chat"},
                              headers=headers_a)
    
    if session_a.status_code == 200:
        print(f"✓ User A created session: {session_a.json()['title']}")
    else:
        print(f"✗ Failed to create session for User A")
    
    # Step 6: Check User A's data
    print("\n6. Fetching User A's data...")
    goals_a = requests.get(f"{BASE_URL}/goals/", headers=headers_a).json()
    sessions_a = requests.get(f"{BASE_URL}/chat/sessions", headers=headers_a).json()
    calendar_a = requests.get(f"{BASE_URL}/calendar/", headers=headers_a).json()
    notifications_a = requests.get(f"{BASE_URL}/notifications/", headers=headers_a).json()
    
    print(f"  - Goals: {len(goals_a)}")
    print(f"  - Chat Sessions: {len(sessions_a)}")
    print(f"  - Calendar Events: {len(calendar_a)}")
    print(f"  - Notifications: {len(notifications_a)}")
    
    # Step 7: Check User B's data (should be empty or different)
    print("\n7. Fetching User B's data...")
    goals_b = requests.get(f"{BASE_URL}/goals/", headers=headers_b).json()
    sessions_b = requests.get(f"{BASE_URL}/chat/sessions", headers=headers_b).json()
    calendar_b = requests.get(f"{BASE_URL}/calendar/", headers=headers_b).json()
    notifications_b = requests.get(f"{BASE_URL}/notifications/", headers=headers_b).json()
    
    print(f"  - Goals: {len(goals_b)}")
    print(f"  - Chat Sessions: {len(sessions_b)}")
    print(f"  - Calendar Events: {len(calendar_b)}")
    print(f"  - Notifications: {len(notifications_b)}")
    
    # Step 8: Verify isolation
    print("\n8. VERIFICATION RESULTS:")
    print("=" * 60)
    
    # Check if User A's goal appears in User B's goals
    user_a_goal_in_b = any(g['text'] == "User A's Secret Goal" for g in goals_b)
    user_a_session_in_b = any(s['title'] == "User A's Private Chat" for s in sessions_b)
    
    if user_a_goal_in_b:
        print("✗ FAILED: User B can see User A's goals!")
        print("  This is a CRITICAL SECURITY ISSUE!")
    else:
        print("✓ PASSED: User B cannot see User A's goals")
    
    if user_a_session_in_b:
        print("✗ FAILED: User B can see User A's chat sessions!")
        print("  This is a CRITICAL SECURITY ISSUE!")
    else:
        print("✓ PASSED: User B cannot see User A's chat sessions")
    
    # Check if User B has their own isolated data
    if len(goals_b) == 0 and len(sessions_b) == 0:
        print("✓ PASSED: User B has empty/isolated data")
    else:
        print(f"ℹ INFO: User B has {len(goals_b)} goals and {len(sessions_b)} sessions (their own data)")
    
    print("\n" + "=" * 60)
    if not user_a_goal_in_b and not user_a_session_in_b:
        print("✓ ALL TESTS PASSED - User data is properly isolated!")
    else:
        print("✗ TESTS FAILED - User data is NOT isolated!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_user_isolation()
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
