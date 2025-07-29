#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Starting TripBox Build ==="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
echo "Creating uploads directory..."
mkdir -p uploads
chmod 755 uploads

# Create instance directory for database
echo "Creating instance directory..."
mkdir -p instance
chmod 755 instance

# Test imports
echo "Testing imports..."
python -c "
import sys
print('Python version:', sys.version)
try:
    import flask
    print('✅ Flask import successful')
    import flask_cors
    print('✅ Flask-CORS import successful')
    import flask_jwt_extended
    print('✅ Flask-JWT-Extended import successful')
    import flask_bcrypt
    print('✅ Flask-Bcrypt import successful')
    import flask_sqlalchemy
    print('✅ Flask-SQLAlchemy import successful')
    print('✅ All imports successful')
except Exception as e:
    print('❌ Import error:', e)
    sys.exit(1)
"

# Test app creation
echo "Testing app creation..."
python -c "
try:
    from app import app, db
    print('✅ App creation successful')
    with app.app_context():
        db.create_all()
        print('✅ Database tables created')
except Exception as e:
    print('❌ App creation error:', e)
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

echo "✅ Build completed successfully" 