"""
Debug Pesapal API authentication
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_auth():
    """Test Pesapal authentication with detailed debugging"""
    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')
    base_url = os.getenv('PESAPAL_BASE_URL')

    print("=" * 70)
    print("PESAPAL AUTHENTICATION DEBUG TEST")
    print("=" * 70)
    print(f"\nConsumer Key: {consumer_key}")
    print(f"Consumer Secret: {consumer_secret}")
    print(f"Base URL: {base_url}")

    # Test authentication endpoint
    url = f"{base_url}/api/Auth/RequestToken"

    print(f"\nAttempting to authenticate...")
    print(f"URL: {url}")

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    payload = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret
    }

    print(f"\nPayload: {payload}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print("\n✓ Authentication successful!")
            print(f"Token: {data.get('token', 'N/A')[:50]}...")
            print(f"Expiry: {data.get('expiryDate', 'N/A')}")
            print(f"Message: {data.get('message', 'N/A')}")
        else:
            print(f"\n✗ Authentication failed!")
            print(f"Error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n✗ Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth()
