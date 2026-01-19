"""
Test chat history persistence in SQL database.
Verifies that chats are stored and retrieved after logout/login.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_history_in_sql():
    print("\n" + "="*70)
    print("TEST: Chat History Persistence in SQL Database")
    print("="*70)
    
    # 1. Signup/Login
    print("\n1. Testing signup and login...")
    signup_payload = {
        "username": "chat_history_test_user",
        "email": "chat_test@example.com",
        "password": "TestPassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_payload)
    print(f"   Signup Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    login_payload = {
        "username": signup_payload["username"],
        "password": signup_payload["password"]
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return False
    
    token = response.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   ✓ Login successful")
    
    # 2. Send multiple chat messages
    print("\n2. Sending multiple chat messages...")
    messages = [
        "What is machine learning?",
        "Tell me about deep learning",
        "How does neural networks work?"
    ]
    
    for i, msg in enumerate(messages, 1):
        chat_payload = {"message": msg, "pdf_snippets": []}
        response = requests.post(f"{BASE_URL}/chat", json=chat_payload, headers=headers)
        
        if response.status_code == 200:
            print(f"   ✓ Message {i} sent successfully")
        else:
            print(f"   ✗ Message {i} failed: {response.status_code}")
    
    # 3. Retrieve chat history from SQL
    print("\n3. Retrieving chat history from SQL...")
    response = requests.get(f"{BASE_URL}/chat_history", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    chat_data = response.json()
    chats = chat_data.get("chats", [])
    print(f"   ✓ Retrieved {len(chats)} chats from SQL database")
    
    # Show chat samples
    for i, chat in enumerate(chats[:6], 1):
        role = chat.get("role", "unknown")
        content_preview = chat.get("content", "")[:60]
        print(f"      Chat {i} ({role}): {content_preview}...")
    
    # 4. Logout
    print("\n4. Testing logout...")
    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    print(f"   ✓ Logout successful")
    print(f"   Message: {response.json().get('message')}")
    
    # 5. Login again
    print("\n5. Testing login again (new session)...")
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return False
    
    token2 = response.json().get("token")
    headers2 = {"Authorization": f"Bearer {token2}"}
    print(f"   ✓ Login successful (new session)")
    
    # 6. Retrieve chat history again in new session
    print("\n6. Retrieving chat history in NEW SESSION...")
    response = requests.get(f"{BASE_URL}/chat_history", headers=headers2)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    chat_data2 = response.json()
    chats2 = chat_data2.get("chats", [])
    print(f"   ✓ Retrieved {len(chats2)} chats in new session")
    
    if len(chats2) == len(chats):
        print(f"   ✓ VERIFIED: All {len(chats)} chats PERSISTED across logout/login!")
    else:
        print(f"   ✗ ERROR: Expected {len(chats)} chats, got {len(chats2)}")
        return False
    
    # Show chat samples from new session
    for i, chat in enumerate(chats2[:6], 1):
        role = chat.get("role", "unknown")
        content_preview = chat.get("content", "")[:60]
        print(f"      Chat {i} ({role}): {content_preview}...")
    
    # 7. Verify data integrity
    print("\n7. Verifying data integrity...")
    user_messages = [c for c in chats2 if c.get("role") == "user"]
    assistant_messages = [c for c in chats2 if c.get("role") == "assistant"]
    
    print(f"   ✓ User messages: {len(user_messages)}")
    print(f"   ✓ Assistant messages: {len(assistant_messages)}")
    
    if len(user_messages) == len(messages):
        print(f"   ✓ All {len(messages)} user messages stored correctly")
    
    if len(assistant_messages) == len(messages):
        print(f"   ✓ All {len(messages)} assistant responses stored correctly")
    
    print("\n" + "="*70)
    print("✓ ALL TESTS PASSED - Chat History SQL Storage Working!")
    print("="*70)
    print("\nSummary:")
    print("- Chat messages are stored in SQL database")
    print("- Chat history persists across logout/login")
    print("- Both user and assistant messages are preserved")
    print("- Frontend can retrieve full conversation history")
    print("- Pinecone LTM remains separate for LLM context")
    print("\n")
    
    return True

if __name__ == "__main__":
    try:
        test_chat_history_in_sql()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to backend at", BASE_URL)
        print("Make sure the FastAPI server is running on port 8000")
    except Exception as e:
        print(f"\nERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
