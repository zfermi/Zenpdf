"""
Test script to verify Pesapal integration
"""
import os
import sys
from dotenv import load_dotenv
from pesapal_service import PesapalService

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_pesapal_connection():
    """Test Pesapal API connection"""
    print("=" * 70)
    print("PESAPAL INTEGRATION TEST")
    print("=" * 70)

    # Get credentials from environment
    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')
    base_url = os.getenv('PESAPAL_BASE_URL')
    ipn_url = os.getenv('PESAPAL_IPN_URL')
    callback_url = os.getenv('PESAPAL_CALLBACK_URL')

    print("\n1. Configuration Check:")
    print(f"   Consumer Key: {consumer_key[:20]}..." if consumer_key else "   ❌ Consumer Key not set")
    print(f"   Consumer Secret: {consumer_secret[:10]}..." if consumer_secret else "   ❌ Consumer Secret not set")
    print(f"   Base URL: {base_url}")
    print(f"   IPN URL: {ipn_url}")
    print(f"   Callback URL: {callback_url}")

    if not all([consumer_key, consumer_secret, base_url, ipn_url, callback_url]):
        print("\n❌ ERROR: Missing required configuration!")
        return False

    # Create Pesapal service
    print("\n2. Creating Pesapal Service...")
    try:
        pesapal = PesapalService(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            base_url=base_url,
            ipn_url=ipn_url,
            callback_url=callback_url
        )
        print("   ✓ Service created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create service: {e}")
        return False

    # Test authentication
    print("\n3. Testing OAuth Authentication...")
    try:
        token = pesapal.get_access_token()
        if token:
            print(f"   ✓ Access token obtained: {token[:30]}...")
            print(f"   ✓ Token expires at: {pesapal.token_expiry}")
        else:
            print("   ❌ Failed to get access token")
            return False
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        return False

    # Test IPN registration
    print("\n4. Testing IPN Registration...")
    try:
        ipn_list = pesapal.get_ipn_list()
        if ipn_list:
            print(f"   ✓ Found {len(ipn_list)} registered IPN(s)")
            for ipn in ipn_list:
                print(f"     - IPN ID: {ipn.get('ipn_id')}")
                print(f"       URL: {ipn.get('url')}")
        else:
            print("   ℹ No IPNs registered yet")
            print("   ℹ IPN will be auto-registered on first payment")
    except Exception as e:
        print(f"   ⚠ Warning: Could not get IPN list: {e}")

    print("\n" + "=" * 70)
    print("✅ PESAPAL INTEGRATION TEST PASSED!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Start your Flask application: python app.py")
    print("2. Navigate to: https://bestpdfconverter.online/pricing")
    print("3. Login and click 'Upgrade to Premium'")
    print("4. Use test card: 4111111111111111")
    print("\nTest Cards (Sandbox):")
    print("  Visa:       4111111111111111")
    print("  Mastercard: 5500000000000004")
    print("  Expiry:     Any future date (e.g., 12/25)")
    print("  CVV:        Any 3 digits (e.g., 123)")
    print("=" * 70)

    return True

if __name__ == "__main__":
    try:
        test_pesapal_connection()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
