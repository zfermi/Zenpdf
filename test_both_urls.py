"""
Test both sandbox and production URLs to identify correct environment
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

def test_url(base_url, env_name):
    """Test a specific Pesapal URL"""
    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')

    print(f"\n{'='*70}")
    print(f"Testing {env_name} Environment")
    print(f"{'='*70}")
    print(f"URL: {base_url}")

    url = f"{base_url}/api/Auth/RequestToken"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    payload = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if 'token' in data and data['token']:
                print(f"\n✓ SUCCESS! Valid credentials for {env_name}")
                print(f"Token: {data['token'][:50]}...")
                return True
            else:
                print(f"\n✗ Failed: {data.get('error', {}).get('message', 'Unknown error')}")
                return False
        else:
            print(f"\n✗ Failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"\n✗ Request failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("PESAPAL ENVIRONMENT DETECTION")
    print("=" * 70)

    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')

    print(f"\nCredentials:")
    print(f"Consumer Key: {consumer_key}")
    print(f"Consumer Secret: {consumer_secret}")

    # Test both environments
    sandbox_works = test_url("https://cybqa.pesapal.com/pesapalv3", "SANDBOX")
    production_works = test_url("https://pay.pesapal.com/v3", "PRODUCTION")

    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Sandbox: {'✓ WORKS' if sandbox_works else '✗ FAILED'}")
    print(f"Production: {'✓ WORKS' if production_works else '✗ FAILED'}")

    if not sandbox_works and not production_works:
        print("\n⚠ WARNING: Credentials don't work in either environment!")
        print("\nPossible issues:")
        print("1. Credentials are not activated yet in Pesapal portal")
        print("2. API access not enabled for your account")
        print("3. Credentials copied incorrectly")
        print("\nNext steps:")
        print("- Login to https://developer.pesapal.com/")
        print("- Verify your credentials are correct")
        print("- Check if API access is enabled")
        print("- Make sure you've completed account verification")
    elif production_works:
        print("\n✓ Use PRODUCTION URL in your .env:")
        print("PESAPAL_BASE_URL=https://pay.pesapal.com/v3")
    elif sandbox_works:
        print("\n✓ Use SANDBOX URL in your .env:")
        print("PESAPAL_BASE_URL=https://cybqa.pesapal.com/pesapalv3")

    print("=" * 70)
