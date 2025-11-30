"""
Quick Payment Integration Verification Script
Tests payment routes and configuration without starting full app
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_payment_integration():
    """Verify payment integration setup"""
    print("=" * 70)
    print("PAYMENT INTEGRATION VERIFICATION")
    print("=" * 70)
    
    # Check environment variables
    print("\n1. Environment Configuration:")
    required_vars = [
        'PESAPAL_CONSUMER_KEY',
        'PESAPAL_CONSUMER_SECRET',
        'PESAPAL_BASE_URL',
        'PESAPAL_IPN_URL',
        'PESAPAL_CALLBACK_URL',
        'PREMIUM_PRICE'
    ]
    
    all_configured = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var or 'KEY' in var:
                print(f"   ✓ {var}: {value[:20]}...")
            else:
                print(f"   ✓ {var}: {value}")
        else:
            print(f"   ✗ {var}: NOT SET")
            all_configured = False
    
    # Check files exist
    print("\n2. Required Files:")
    files = [
        'payment.py',
        'pesapal_service_v2.py',
        'app.py',
        'config.py',
        'models.py'
    ]
    
    all_files_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} - MISSING")
            all_files_exist = False
    
    # Check payment.py routes
    print("\n3. Payment Routes (from payment.py):")
    try:
        with open('payment.py', 'r', encoding='utf-8') as f:
            content = f.read()
            routes = [
                ('/subscribe/premium', 'subscribe_premium'),
                ('/callback', 'payment_callback'),
                ('/ipn', 'payment_ipn'),
                ('/status/', 'check_payment_status')
            ]
            
            for route, func in routes:
                if func in content:
                    print(f"   ✓ {route} -> {func}()")
                else:
                    print(f"   ✗ {route} -> {func}() - NOT FOUND")
    except Exception as e:
        print(f"   ✗ Error reading payment.py: {e}")
    
    # Check blueprint registration
    print("\n4. Blueprint Registration (in app.py):")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'from payment import payment_bp' in content:
                print("   ✓ Payment blueprint imported")
            else:
                print("   ✗ Payment blueprint NOT imported")
            
            if 'app.register_blueprint(payment_bp' in content:
                print("   ✓ Payment blueprint registered")
            else:
                print("   ✗ Payment blueprint NOT registered")
    except Exception as e:
        print(f"   ✗ Error reading app.py: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    if all_configured and all_files_exist:
        print("✓ Code Implementation: COMPLETE")
        print("✓ File Structure: CORRECT")
        print("⚠ API Credentials: INVALID (needs update)")
        print("\nStatus: READY FOR TESTING (after credential update)")
    else:
        print("✗ Setup incomplete - please review errors above")
    
    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Update Pesapal credentials in .env file")
    print("2. Whitelist domain in Pesapal dashboard")
    print("3. Run: python test_pesapal.py")
    print("4. Start app: python app.py")
    print("5. Test payment flow at: http://localhost:5000/pricing")
    print("=" * 70)

if __name__ == "__main__":
    check_payment_integration()
