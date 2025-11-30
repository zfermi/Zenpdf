"""
Script to check Pesapal configuration and credentials
"""
import os
import sys
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

def check_config():
    """Check if all required Pesapal configuration is set"""

    print("=" * 60)
    print("PESAPAL CONFIGURATION CHECK")
    print("=" * 60)

    # Required variables
    required_vars = {
        'PESAPAL_CONSUMER_KEY': 'Consumer Key',
        'PESAPAL_CONSUMER_SECRET': 'Consumer Secret',
        'PESAPAL_CALLBACK_URL': 'Callback URL',
        'PESAPAL_IPN_URL': 'IPN URL',
    }

    # Optional variables
    optional_vars = {
        'PESAPAL_BASE_URL': 'Base URL (defaults to production)',
    }

    missing_vars = []

    print("\nRequired Configuration:")
    print("-" * 60)

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            if 'KEY' in var or 'SECRET' in var:
                masked_value = value[:10] + '...' + value[-4:] if len(value) > 14 else '***'
                print(f"✓ {description:30} {masked_value}")
            else:
                print(f"✓ {description:30} {value}")
        else:
            print(f"✗ {description:30} NOT SET")
            missing_vars.append(var)

    print("\nOptional Configuration:")
    print("-" * 60)

    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✓ {description:30} {value}")
        else:
            print(f"  {description:30} (using default)")

    # Check if using demo or production
    base_url = os.getenv('PESAPAL_BASE_URL', 'https://pay.pesapal.com/v3')
    is_demo = 'demo' in base_url.lower() or 'cybqa' in base_url.lower()

    print("\nEnvironment:")
    print("-" * 60)
    print(f"Mode: {'DEMO/SANDBOX' if is_demo else 'PRODUCTION'}")
    print(f"Base URL: {base_url}")

    # Check callback URLs
    callback_url = os.getenv('PESAPAL_CALLBACK_URL')
    ipn_url = os.getenv('PESAPAL_IPN_URL')

    if callback_url:
        if not callback_url.startswith('http'):
            print(f"\n⚠ WARNING: Callback URL should start with http:// or https://")
            print(f"  Current value: {callback_url}")

        if is_demo and 'localhost' not in callback_url and '127.0.0.1' not in callback_url:
            print(f"\n⚠ NOTE: You're using DEMO mode but callback URL is not localhost")
            print(f"  This is OK if you're testing with a deployed instance")

    # Summary
    print("\n" + "=" * 60)
    if missing_vars:
        print("❌ CONFIGURATION INCOMPLETE")
        print(f"\nMissing variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables in:")
        print("  - Railway dashboard (for production)")
        print("  - .env file (for local development)")
        return False
    else:
        print("✅ CONFIGURATION COMPLETE")
        print("\nAll required Pesapal configuration is set.")

        if is_demo:
            print("\nYou're using DEMO mode. Make sure:")
            print("  1. Your consumer key/secret are from the Pesapal demo account")
            print("  2. You can test payments without real money")
        else:
            print("\nYou're using PRODUCTION mode. Make sure:")
            print("  1. Your consumer key/secret are from your live Pesapal account")
            print("  2. Your Pesapal account is verified and approved")
            print("  3. Real payments will be processed")

        return True

if __name__ == '__main__':
    success = check_config()
    sys.exit(0 if success else 1)
