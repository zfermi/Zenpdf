"""
Detailed test of Pesapal credentials with full error output
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def test_pesapal_auth():
    """Test Pesapal authentication with detailed output"""

    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')

    # Test different base URLs
    base_urls = [
        'https://cybqa.pesapal.com/pesapalv3',
        'https://pay.pesapal.com/v3',
        'https://cybqa.pesapal.com/pesapal',
        'https://pay.pesapal.com',
    ]

    print("=" * 60)
    print("PESAPAL API 3.0 AUTHENTICATION TEST")
    print("=" * 60)
    print(f"\nConsumer Key: {consumer_key}")
    print(f"Consumer Secret: {consumer_secret}")

    for base_url in base_urls:
        print(f"\n{'=' * 60}")
        print(f"Testing: {base_url}")
        print(f"{'=' * 60}")

        auth_url = f"{base_url}/api/Auth/RequestToken"
        print(f"Auth URL: {auth_url}")

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = {
            'consumer_key': consumer_key,
            'consumer_secret': consumer_secret
        }

        try:
            print(f"\nSending request...")
            response = requests.post(auth_url, json=payload, headers=headers, timeout=30)

            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")

            if response.status_code == 200:
                data = response.json()
                if data.get('token'):
                    print(f"\n✅✅✅ SUCCESS! ✅✅✅")
                    print(f"Access Token: {data['token'][:50]}...")
                    print(f"\nUSE THIS BASE URL: {base_url}")
                    return True
                elif data.get('error'):
                    print(f"❌ API Error: {data.get('error')}")
                    print(f"   Message: {data.get('message', 'N/A')}")
            else:
                print(f"❌ HTTP Error {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    pass

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    return False

if __name__ == '__main__':
    print("\nTesting Pesapal API 3.0 authentication with different URLs...")
    print("This will show exactly what Pesapal is returning.\n")

    success = test_pesapal_auth()

    print(f"\n{'=' * 60}")
    if not success:
        print("NONE OF THE URLs WORKED")
        print("\nPossible issues:")
        print("1. Consumer key/secret are incorrect")
        print("2. Account not activated in Pesapal")
        print("3. Credentials are for a test account that's expired")
        print("4. Need to whitelist your IP in Pesapal dashboard")
        print("\nRecommendation:")
        print("Login to https://developer.pesapal.com")
        print("and generate fresh API credentials")
    print("=" * 60)
