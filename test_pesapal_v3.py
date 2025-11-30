"""
Test Pesapal API 3.0 credentials
"""
import os
import sys
from dotenv import load_dotenv
from pesapal_service import PesapalService

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def test_api_v3():
    """Test credentials with Pesapal API 3.0"""

    print("=" * 60)
    print("PESAPAL API 3.0 TEST")
    print("=" * 60)

    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')
    base_url = os.getenv('PESAPAL_BASE_URL', 'https://cybqa.pesapal.com/pesapalv3')
    callback_url = os.getenv('PESAPAL_CALLBACK_URL')
    ipn_url = os.getenv('PESAPAL_IPN_URL')

    print(f"\nConfiguration:")
    print(f"  Base URL: {base_url}")
    print(f"  Consumer Key: {consumer_key[:10]}...{consumer_key[-4:]}")

    try:
        # Create API 3.0 service
        service = PesapalService(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            base_url=base_url,
            ipn_url=ipn_url,
            callback_url=callback_url
        )

        print(f"\n{'=' * 60}")
        print("Step 1: Testing Authentication (Get Access Token)")
        print(f"{'=' * 60}")

        token = service.get_access_token()

        if token:
            print(f"✅ SUCCESS! Got access token")
            print(f"   Token: {token[:30]}...")
            print(f"\n✅✅ YOUR CREDENTIALS WORK WITH API 3.0! ✅✅")
            print(f"\nThis means you should use:")
            print(f"  - pesapal_service.py (API 3.0)")
            print(f"  - NOT pesapal_service_v2.py (API 2.0)")
            return True
        else:
            print(f"❌ Failed to get access token")
            return False

    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Authentication failed:")
        print(f"   Error: {error_msg}")

        if 'unauthorized' in error_msg.lower() or 'authentication' in error_msg.lower():
            print(f"\n⚠ This means:")
            print(f"  - Your credentials might be invalid")
            print(f"  - Or the base URL is wrong")
        else:
            print(f"\n⚠ Unexpected error occurred")

        return False

if __name__ == '__main__':
    print("\nTesting if your credentials work with Pesapal API 3.0...")
    print("(Your credentials failed with API 2.0, so trying API 3.0)\n")

    success = test_api_v3()

    print(f"\n{'=' * 60}")
    if success:
        print("RESULT: ✅ Use API 3.0 (pesapal_service.py)")
        print("\nNEXT STEPS:")
        print("1. Update payment.py to use API 3.0 service")
        print("2. Redeploy to Railway")
        print("3. Test payment flow")
    else:
        print("RESULT: ❌ Credentials don't work with API 3.0 either")
        print("\nNEXT STEPS:")
        print("1. Login to your Pesapal account")
        print("2. Generate new API credentials")
        print("3. Make sure account is activated/approved")
    print("=" * 60)
