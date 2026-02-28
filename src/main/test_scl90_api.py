import requests
import json
import uuid
import random

BASE_URL = "http://localhost:5000/api"
TEST_UUID = str(uuid.uuid4())
HEADERS = {"X-User-UUID": TEST_UUID}

def test_get_questions():
    print(f"Testing GET {BASE_URL}/scl90/questions...")
    try:
        response = requests.get(f"{BASE_URL}/scl90/questions")
        response.raise_for_status()
        data = response.json()
        if data['code'] == 200 and len(data['data']) == 90:
            print("✅ Get questions successful")
            return data['data']
        else:
            print(f"❌ Get questions failed: {data}")
            return None
    except Exception as e:
        print(f"❌ Get questions error: {e}")
        return None

def test_submit_scl90(questions):
    print(f"Testing POST {BASE_URL}/scl90/submit...")
    answers = {}
    for q in questions:
        answers[str(q['id'])] = random.randint(1, 5)
    
    payload = {
        "answers": answers,
        "uuid": TEST_UUID
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scl90/submit", json=payload, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if data['code'] == 200:
            print("✅ Submit SCL90 successful")
            print(f"   Total Score: {data['data']['total_score']}")
            return True
        else:
            print(f"❌ Submit SCL90 failed: {data}")
            return False
    except Exception as e:
        print(f"❌ Submit SCL90 error: {e}")
        return False

def test_get_history():
    print(f"Testing GET {BASE_URL}/scl90/history...")
    try:
        response = requests.get(f"{BASE_URL}/scl90/history", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if data['code'] == 200:
            print(f"✅ Get history successful. Count: {len(data['data'])}")
            if len(data['data']) > 0:
                return data['data'][0]['id']
            return None
        else:
            print(f"❌ Get history failed: {data}")
            return None
    except Exception as e:
        print(f"❌ Get history error: {e}")
        return None

def test_get_detail(record_id):
    if not record_id:
        print("⚠️ No record ID to test detail")
        return

    print(f"Testing GET {BASE_URL}/scl90/detail/{record_id}...")
    try:
        response = requests.get(f"{BASE_URL}/scl90/detail/{record_id}", headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if data['code'] == 200:
            print("✅ Get detail successful")
            print(f"   Total Score from detail: {data['data']['total_score']}")
            return True
        else:
            print(f"❌ Get detail failed: {data}")
            return False
    except Exception as e:
        print(f"❌ Get detail error: {e}")
        return False

if __name__ == "__main__":
    print(f"🚀 Starting SCL-90 API Test with UUID: {TEST_UUID}")
    questions = test_get_questions()
    if questions:
        if test_submit_scl90(questions):
            latest_id = test_get_history()
            if latest_id:
                test_get_detail(latest_id)
    print("🏁 Test finished")
