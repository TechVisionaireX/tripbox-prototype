#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Starting TripBox Build ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run setup test
echo "Running setup test..."
python test_setup.py

# Create uploads directory if it doesn't exist
echo "Creating uploads directory..."
mkdir -p uploads
chmod 777 uploads

# Create database tables
echo "Creating database tables..."
python - <<EOF
import os
import sys
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Test database connection with proper SQLAlchemy 2.0 syntax
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
    except Exception as e:
        print(f"⚠️ Warning during database setup: {e}")
        print("🔄 Continuing with deployment...")
        # Don't raise error, continue with deployment
        pass
EOF

echo "=== Build Complete ===" 