"""
Test script to verify TripBox setup and dependencies
"""
import sys
import os
import importlib

def test_import(module_name, package_name=None):
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        if package_name:
            print(f"   Try: pip install {package_name}")
        return False

def test_directory(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"✅ Created directory: {path}")
        else:
            print(f"✅ Directory exists: {path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create/verify directory {path}: {e}")
        return False

def test_environment():
    required_vars = [
        'DATABASE_URL',
        'JWT_SECRET_KEY',
        'GOOGLE_PLACES_API_KEY',
        'GOOGLE_MAPS_API_KEY',
        'OPENWEATHER_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            print(f"❌ Missing environment variable: {var}")
        else:
            print(f"✅ Found environment variable: {var}")
    
    return len(missing) == 0

def main():
    print("\n=== Testing Python Version ===")
    print(f"Python {sys.version}")

    print("\n=== Testing Core Dependencies ===")
    core_deps = [
        ('flask', 'flask'),
        ('flask_cors', 'flask-cors'),
        ('flask_bcrypt', 'flask-bcrypt'),
        ('flask_jwt_extended', 'flask-jwt-extended'),
        ('flask_sqlalchemy', 'flask-sqlalchemy'),
        ('psycopg2', 'psycopg2-binary'),
        ('dotenv', 'python-dotenv')
    ]
    
    for module, package in core_deps:
        test_import(module, package)

    print("\n=== Testing Advanced Feature Dependencies ===")
    advanced_deps = [
        ('requests', 'requests'),
        ('reportlab', 'reportlab'),
        ('socketio', 'python-socketio'),
        ('eventlet', 'eventlet'),
        ('geopy', 'geopy'),
        ('PIL', 'pillow'),
        ('qrcode', 'qrcode'),
        ('googlemaps', 'googlemaps')
    ]
    
    for module, package in advanced_deps:
        test_import(module, package)

    print("\n=== Testing Directories ===")
    directories = [
        'uploads',
        'instance'
    ]
    
    for directory in directories:
        test_directory(directory)

    print("\n=== Testing Environment Variables ===")
    test_environment()

if __name__ == '__main__':
    main() 