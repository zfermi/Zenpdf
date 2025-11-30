"""
Test script to verify Pesapal API 2.0 integration
"""
import os
import sys
from dotenv import load_dotenv
from pesapal_service_v2 import PesapalServiceV2

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def test_pesapal_v2_connection():
    """Test Pesapal API 2.0 connection"""
    print("=" * 70)
    print("PESAPAL API 2.0 INTEGRATION TEST")
    print("=" * 70)

    # Get credentials from environment
    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')
    callback_url = os.getenv('PESAPAL_CALLBACK_URL')
    ipn_url = os.getenv('PESAPAL_IPN_URL')

    print("\n1. Configuration Check:")
    print(f"   Consumer Key: {consumer_key}")
    print(f"   Consumer Secret: {consumer_secret}")
    print(f"   Callback URL: {callback_url}")
    print(f"   IPN URL: {ipn_url}")

    if not all([consumer_key, consumer_secret]):
        print("\n❌ ERROR: Missing required configuration!")
        return False

    # Create Pesapal service (demo mode)
    print("\n2. Creating Pesapal API 2.0 Service...")
    try:
        pesapal = PesapalServiceV2(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            is_demo=True,  # Use demo/sandbox
            callback_url=callback_url,
            ipn_url=ipn_url
        )
        print("   ✓ Service created successfully")
        print(f"   ✓ Using endpoint: {pesapal.post_order_url}")
    except Exception as e:
        print(f"   ❌ Failed to create service: {e}")
        return False

    # Test creating a payment order
    print("\n3. Testing Payment Order Creation...")
    try:
        result = pesapal.create_payment_order(
            user_email="test@example.com",
            user_name="Test User",
            amount=9.99,
            currency="USD",
            order_id=f"TEST-ORDER-{int(time.time())}",
            description="Test Payment - Premium Subscription"
        )
        
        if result.get('redirect_url'):
            print("   ✓ Payment order created successfully!")
            print(f"   ✓ Redirect URL: {result['redirect_url'][:80]}...")
            print(f"   ✓ Order ID: {result['order_tracking_id']}")
            
            print("\n" + "=" * 70)
            print("✅ PESAPAL API 2.0 INTEGRATION TEST PASSED!")
            print("=" * 70)
            print("\nNext Steps:")
            print("1. Start your Flask application: python app.py")
            print("2. Navigate to: http://localhost:5000/pricing")
            print("3. Login and click 'Upgrade to Premium'")
            print("4. You will be redirected to Pesapal payment page")
            print("\nTest Cards (Demo):")
            print("  Any card number will work in demo mode")
            print("  Just complete the payment flow to test")
            print("=" * 70)
            return True
        else:
            print("   ❌ No redirect URL in response")
            print(f"   Response: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to create payment order: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import time
    try:
        success = test_pesapal_v2_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
