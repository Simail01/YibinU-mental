import requests
import uuid
import json

BASE_URL = "http://localhost:5000/api"
TEST_UUID = str(uuid.uuid4())

def test_knowledge_api():
    print(f"\n🚀 Starting Knowledge API Test with UUID: {TEST_UUID}")
    
    # 1. List initial knowledge (should see public ones)
    print("Testing GET /knowledge/list (Initial)...")
    try:
        resp = requests.get(f"{BASE_URL}/knowledge/list", headers={"X-User-UUID": TEST_UUID})
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            print(f"✅ List successful. Count: {len(data)}")
            for item in data:
                print(f"   - [{item['type']}] {item['title']}")
        else:
            print(f"❌ List failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ List exception: {e}")

    # 2. Add private knowledge
    print("\nTesting POST /knowledge/add...")
    payload = {
        "title": "我的个人测试知识",
        "content": "这是一个测试私有知识库的内容，应该只有我自己能看到。"
    }
    try:
        resp = requests.post(
            f"{BASE_URL}/knowledge/add", 
            json=payload,
            headers={"X-User-UUID": TEST_UUID}
        )
        if resp.status_code == 200:
            print("✅ Add private knowledge successful")
        else:
            print(f"❌ Add failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Add exception: {e}")

    # 3. List again (should include private)
    print("\nTesting GET /knowledge/list (After Add)...")
    try:
        resp = requests.get(f"{BASE_URL}/knowledge/list", headers={"X-User-UUID": TEST_UUID})
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            print(f"✅ List successful. Count: {len(data)}")
            found_private = False
            for item in data:
                print(f"   - [{item['type']}] {item['title']}")
                if item['title'] == payload['title'] and item['type'] == 'private':
                    found_private = True
            
            if found_private:
                print("✅ Found newly added private knowledge!")
            else:
                print("❌ Failed to find private knowledge in list")
        else:
            print(f"❌ List failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ List exception: {e}")

    print("🏁 Knowledge Test finished")

if __name__ == "__main__":
    test_knowledge_api()
