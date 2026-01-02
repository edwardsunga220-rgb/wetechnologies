import requests
import json

# ==========================================
# PASTE YOUR NEW KEYS HERE
# ==========================================
KEY = '4GhwfZhAIHWFcfM+5SuXaplx3FOTwIkY'
SECRET = 'W/o5cg2sMi/PzNTFgd0BT3nWtVA=' 
# ==========================================

def test_connection(env_name, url):
    print(f"\n{'='*50}")
    print(f"TESTING {env_name} ENVIRONMENT")
    print(f"URL: {url}")
    print(f"{'='*50}")
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "consumer_key": KEY,
        "consumer_secret": SECRET
    }
    
    try:
        print(f"⏳ Sending request...")
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        print(f"📬 Status Code: {response.status_code}")
        
        try:
            # Try to parse JSON
            data = response.json()
            # Pretty print the JSON so we can read the error
            print(f"📄 Response Body:\n{json.dumps(data, indent=4)}")
            
            # Check for Token
            if data.get('token'):
                print(f"\n✅ SUCCESS! These are valid {env_name} keys.")
                print(f"🔑 Token received.")
            else:
                print(f"\n❌ FAILURE. The server replied, but gave no token.")
                print("👉 Read the 'error' or 'message' in the JSON above.")
                
        except json.JSONDecodeError:
            print(f"❌ Error: Response was not valid JSON.")
            print(f"Raw Text: {response.text}")

    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")

# --- EXECUTE TESTS ---

# 1. Test Sandbox (Demo)
test_connection("SANDBOX", "https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken")

# 2. Test Live (Production)
test_connection("LIVE", "https://pay.pesapal.com/v3/api/Auth/RequestToken")