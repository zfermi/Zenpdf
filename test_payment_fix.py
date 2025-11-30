"""
Test script to verify Pesapal payment integration fix
"""
import os
import sys
from dotenv import load_dotenv
from pesapal_service_v2 import PesapalServiceV2

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def test_pesapal_service():
    """Test the Pesapal service initialization and URL generation"""

    print("=" * 60)
    print("PESAPAL PAYMENT INTEGRATION TEST")
    print("=" * 60)

    # Get configuration
    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')
    base_url = os.getenv('PESAPAL_BASE_URL', 'https://cybqa.pesapal.com/pesapalv3')
    callback_url = os.getenv('PESAPAL_CALLBACK_URL')
    ipn_url = os.getenv('PESAPAL_IPN_URL')

    if not all([consumer_key, consumer_secret, callback_url]):
        print("❌ Missing required configuration!")
        return False

    # Determine if demo mode
    is_demo = 'demo' in base_url.lower() or 'cybqa' in base_url.lower()

    print(f"\nConfiguration:")
    print(f"  Configured Base URL: {base_url}")
    print(f"  Mode: {'DEMO' if is_demo else 'PRODUCTION'}")
    print(f"  Consumer Key: {consumer_key[:10]}...{consumer_key[-4:]}")

    # Create service
    service = PesapalServiceV2(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        is_demo=is_demo,
        callback_url=callback_url,
        ipn_url=ipn_url,
        base_url=base_url
    )

    print(f"\nGenerated URLs:")
    print(f"  Service Base URL: {service.base_url}")
    print(f"  Post Order URL: {service.post_order_url}")
    print(f"  Query Status URL: {service.query_status_url}")

    # Verify URLs match
    expected_base = base_url.replace('/v3', '').replace('/pesapalv3', '')

    if service.base_url == expected_base:
        print(f"\n✅ Base URL matches configuration")
    else:
        print(f"\n❌ Base URL mismatch!")
        print(f"  Expected: {expected_base}")
        print(f"  Got: {service.base_url}")
        return False

    # Test creating a payment order (will fail with invalid credentials but should show proper error)
    print(f"\n" + "=" * 60)
    print("Testing payment order creation...")
    print("=" * 60)

    try:
        result = service.create_payment_order(
            user_email="test@example.com",
            user_name="Test User",
            amount=9.99,
            currency="USD",
            order_id="TEST-12345",
            description="Test payment"
        )

        redirect_url = result.get('redirect_url', '')
        print(f"\n✅ Payment order created successfully!")
        print(f"  Redirect URL: {redirect_url[:80]}...")

        if redirect_url.startswith('problem:'):
            print(f"\n⚠ WARNING: Received error URL from Pesapal:")
            print(f"  {redirect_url}")
            print(f"\nThis might mean:")
            print(f"  1. Consumer key/secret are invalid for {service.base_url}")
            print(f"  2. The Pesapal account is not properly configured")
            print(f"  3. The environment (demo/prod) doesn't match your credentials")
            return False

        return True

    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Payment order creation failed:")
        print(f"  Error: {error_msg}")

        if 'consumer_key_unknown' in error_msg or 'problem:' in error_msg:
            print(f"\n⚠ This error indicates:")
            print(f"  1. The consumer key is not recognized by {service.base_url}")
            print(f"  2. You may be using credentials for a different Pesapal environment")
            print(f"\nSuggested fixes:")
            print(f"  - If using cybqa.pesapal.com, get credentials from Pesapal demo")
            print(f"  - If using demo.pesapal.com, update PESAPAL_BASE_URL")
            print(f"  - Verify your Pesapal account is set up correctly")

        return False

if __name__ == '__main__':
    success = test_pesapal_service()
    print(f"\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ TESTS FAILED - See errors above")
    print("=" * 60)
