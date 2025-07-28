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
from app import app, db
with app.app_context():
    try:
        # Drop all tables first to avoid conflicts
        db.drop_all()
        print("Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("Created new tables")
        
        # Verify tables were created
        tables = db.engine.table_names()
        print(f"Created tables: {', '.join(tables)}")
    except Exception as e:
        print(f"Error during database setup: {e}")
        raise e
EOF

echo "=== Build Complete ===" 