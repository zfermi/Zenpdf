
import sys
import os
from flask import Flask

# Add current directory to path
sys.path.append(os.getcwd())

from app import create_app

def verify_routes():
    print("=" * 70)
    print("VERIFYING FLASK ROUTES")
    print("=" * 70)
    
    try:
        app = create_app('development')
        
        expected_routes = [
            '/payment/subscribe/premium',
            '/payment/callback',
            '/payment/ipn',
            '/payment/status/<order_tracking_id>'
        ]
        
        registered_routes = []
        for rule in app.url_map.iter_rules():
            registered_routes.append(str(rule))
            
        all_found = True
        for route in expected_routes:
            if route in registered_routes:
                print(f"   ✓ Found: {route}")
            else:
                print(f"   ✗ MISSING: {route}")
                all_found = False
                
        print("-" * 70)
        if all_found:
            print("✅ All payment routes are correctly registered.")
        else:
            print("❌ Some routes are missing.")
            
    except Exception as e:
        print(f"❌ Error creating app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_routes()
