"""
Test Pesapal credentials against all possible environments
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

def test_environment(base_url, env_name):
    """Test credentials against a specific Pesapal environment"""

    print(f"\n{'=' * 60}")
    print(f"Testing {env_name}")
    print(f"URL: {base_url}")
    print(f"{'=' * 60}")

    consumer_key = os.getenv('PESAPAL_CONSUMER_KEY')
    consumer_secret = os.getenv('PESAPAL_CONSUMER_SECRET')
    callback_url = os.getenv('PESAPAL_CALLBACK_URL')

    try:
        # Create service
        service = PesapalServiceV2(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            is_demo=True,
            callback_url=callback_url,
            base_url=base_url
        )

        print(f"Service Base URL: {service.base_url}")
        print(f"Post Order URL: {service.post_order_url}")

        # Try to create a test payment
        result = service.create_payment_order(
            user_email="test@example.com",
            user_name="Test User",
            amount=9.99,
            currency="USD",
            order_id=f"TEST-{env_name}-12345",
            description="Test payment"
        )

        redirect_url = result.get('redirect_url', '')

        if redirect_url.startswith('http'):
            print(f"\n✅ SUCCESS! Credentials work with {env_name}")
            print(f"Redirect URL: {redirect_url[:100]}...")
            return True
        else:
            print(f"\n❌ Failed: {redirect_url}")
            return False

    except Exception as e:
        error_msg = str(e)
        if 'consumer_key_unknown' in error_msg.lower():
            print(f"❌ Consumer key not recognized by {env_name}")
        else:
            print(f"❌ Error: {error_msg[:200]}")
        return False

def main():
    """Test credentials against all Pesapal environments"""

    print("=" * 60)
    print("PESAPAL ENVIRONMENT DISCOVERY")
    print("=" * 60)
    print("\nTesting your credentials against all Pesapal environments...")

    # Environments to test
    environments = [
        ("https://demo.pesapal.com", "Demo (demo.pesapal.com)"),
        ("https://cybqa.pesapal.com", "CybQA Sandbox (cybqa.pesapal.com)"),
        ("https://www.pesapal.com", "Production (www.pesapal.com)"),
    ]

    results = {}

    for base_url, env_name in environments:
        results[env_name] = test_environment(base_url, env_name)

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")

    working_env = None
    for env_name, success in results.items():
        status = "✅ WORKS" if success else "❌ FAILED"
        print(f"{status} - {env_name}")
        if success:
            working_env = env_name

    if working_env:
        print(f"\n✅ Your credentials work with: {working_env}")

        # Get the base URL for the working environment
        for base_url, env_name in environments:
            if env_name == working_env:
                print(f"\nUpdate your .env file with:")
                print(f"PESAPAL_BASE_URL={base_url}")

                # Also update Railway
                print(f"\nAnd update Railway environment variable:")
                print(f"PESAPAL_BASE_URL={base_url}")
                break
    else:
        print(f"\n❌ Your credentials don't work with any environment")
        print(f"\nPossible reasons:")
        print(f"  1. Consumer key/secret are incorrect")
        print(f"  2. Your Pesapal account needs to be activated")
        print(f"  3. The credentials are for a different API version")
        print(f"\nNext steps:")
        print(f"  1. Login to your Pesapal account")
        print(f"  2. Verify your API credentials")
        print(f"  3. Make sure your account is approved/activated")
        print(f"  4. Check if you need to use API 3.0 instead of 2.0")

if __name__ == '__main__':
    main()
