import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:5000"
TEST_UUID = str(uuid.uuid4())

def test_knowledge_list():
    print(f"\nTesting Knowledge List (UUID: {TEST_UUID})...")
    url = f"{BASE_URL}/api/knowledge/list"
    headers = {"X-User-UUID": TEST_UUID}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                print("✅ Knowledge list fetched successfully.")
                items = data['data']
                print(f"Found {len(items)} items.")
                for item in items:
                    print(f" - [{item['type']}] {item['title']}")
                
                # Verify public knowledge exists
                public_items = [i for i in items if i['type'] == 'public']
                if len(public_items) > 0:
                    print("✅ Public knowledge items verified.")
                else:
                    print("❌ No public knowledge items found!")
            else:
                print(f"❌ API returned error: {data['msg']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_scl90_questions():
    print("\nTesting SCL-90 Questions...")
    url = f"{BASE_URL}/api/scl90/questions"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                questions = data['data']
                print(f"✅ SCL-90 questions fetched. Count: {len(questions)}")
                if len(questions) == 90:
                    print("✅ Question count is correct (90).")
                else:
                    print(f"❌ Incorrect question count: {len(questions)}")
            else:
                print(f"❌ API returned error: {data['msg']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_analysis_mock():
    print(f"\nTesting Analysis Mock (UUID: {TEST_UUID})...")
    url = f"{BASE_URL}/api/mental_analysis"
    headers = {"Content-Type": "application/json"}
    payload = {
        "uuid": TEST_UUID,
        "text": "我最近感觉压力很大，睡不着觉，不知道该怎么办。"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 200:
                result = data['data']
                print("✅ Analysis successful.")
                print(f"Emotion: {result['emotion']}")
                print(f"Risk: {result['risk']}")
                print("Advice Preview:")
                print(result['advice'][:100] + "...")
                
                if "MOCK" in result['advice']:
                    print("✅ Mock response detected (as expected).")
                else:
                    print("⚠️ Response does not contain 'MOCK' marker (unexpected if LLM is disabled).")
            else:
                print(f"❌ API returned error: {data['msg']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_knowledge_list()
    test_scl90_questions()
    test_analysis_mock()
