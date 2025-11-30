"""
Test script to verify payment route is accessible
"""
import requests

def test_payment_route():
    """Test if the payment routes are accessible"""

    base_url = "https://bestpdfconverter.online"

    print("=" * 60)
    print("TESTING PAYMENT ROUTES")
    print("=" * 60)

    # Test 1: Check if pricing page loads
    print("\n1. Testing Pricing Page...")
    try:
        response = requests.get(f"{base_url}/pricing", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            if "Upgrade to Premium" in response.text:
                print("   ✓ Pricing page loads")
                print("   ✓ 'Upgrade to Premium' button found")
            else:
                print("   ✗ 'Upgrade to Premium' button not found")
        else:
            print(f"   ✗ Failed to load pricing page")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Check if payment route exists (will redirect to login if not authenticated)
    print("\n2. Testing Payment Subscribe Route...")
    try:
        response = requests.get(
            f"{base_url}/payment/subscribe/premium",
            allow_redirects=False,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"   ✓ Route exists (redirecting to: {redirect_location})")
            if 'login' in redirect_location.lower():
                print("   ✓ Correctly redirects to login (route is protected)")
        elif response.status_code == 500:
            print("   ✗ Server error - likely missing PayPal credentials")
        elif response.status_code == 404:
            print("   ✗ Route not found - blueprint may not be registered")
        else:
            print(f"   ? Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 3: Check if success route exists
    print("\n3. Testing Payment Success Route...")
    try:
        response = requests.get(
            f"{base_url}/payment/success",
            allow_redirects=False,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✓ Route exists (protected)")
        elif response.status_code == 404:
            print("   ✗ Route not found")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 4: Check if cancel route exists
    print("\n4. Testing Payment Cancel Route...")
    try:
        response = requests.get(
            f"{base_url}/payment/cancel",
            allow_redirects=False,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✓ Route exists (protected)")
        elif response.status_code == 404:
            print("   ✗ Route not found")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)
    print("\nIf routes return 404:")
    print("  - App may not have redeployed yet")
    print("  - Check Railway deployment logs")
    print("\nIf routes return 302 (redirect):")
    print("  - Routes are working correctly")
    print("  - Button should work when logged in")
    print("\nIf routes return 500:")
    print("  - PayPal credentials not configured")
    print("  - Add PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_BASE_URL")
    print("\nIf button still doesn't work:")
    print("  - Check browser console for JavaScript errors")
    print("  - Clear browser cache and cookies")
    print("  - Try in incognito/private window")
    print("=" * 60)

if __name__ == '__main__':
    test_payment_route()
