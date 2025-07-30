#!/usr/bin/env python3
"""
Simple Server Startup Script
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("✅ App imported successfully")
    
    print("🚀 Starting server on http://localhost:8080")
    print("📝 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
    
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc() 