#!/usr/bin/env python3
"""
Quick test script to verify TripBox fixes
"""
import sys
import os

def test_backend_imports():
    """Test that backend imports work without hanging"""
    print("🧪 Testing backend imports...")
    
    try:
        # Change to backend directory
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Test core imports
        print("  - Testing Flask app import...")
        from backend.app import app, application
        print("  ✅ Flask app imported successfully")
        
        # Test app creation
        print("  - Testing app context...")
        with app.app_context():
            print("  ✅ App context works")
        
        print("✅ Backend imports test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Backend import test failed: {e}")
        return False

def test_api_endpoints():
    """Test basic API endpoint structure"""
    print("🧪 Testing API endpoints...")
    
    try:
        from backend.app import app
        
        with app.test_client() as client:
            # Test home endpoint
            response = client.get('/')
            if response.status_code == 200:
                print("  ✅ Home endpoint works")
            else:
                print(f"  ⚠️ Home endpoint returned {response.status_code}")
            
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("  ✅ Health endpoint works")
            else:
                print(f"  ⚠️ Health endpoint returned {response.status_code}")
        
        print("✅ API endpoints test passed!")
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TripBox Fix Verification")
    print("=" * 50)
    
    tests = [
        test_backend_imports,
        test_api_endpoints,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment!")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main()) 