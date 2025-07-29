#!/bin/bash

echo "🚀 TripBox-IntelliOrganizer Deployment Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ Error: Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r backend/requirements.txt

# Setup database
echo "🗄️  Setting up database..."
cd backend
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
cd ..

# Test backend
echo "🧪 Testing backend..."
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Test health endpoint
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ Backend is running successfully"
else
    echo "❌ Backend health check failed"
    kill $BACKEND_PID
    exit 1
fi

# Create test user
echo "👤 Creating test user..."
curl -X POST http://localhost:5000/api/create-test-user

# Stop backend
kill $BACKEND_PID

echo ""
echo "🎉 Deployment preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start the backend: python app.py"
echo "2. Open frontend/index.html in your browser"
echo "3. Login with: test@test.com / test123"
echo ""
echo "🌐 For production deployment:"
echo "- Backend: Deploy to Render using render.yaml"
echo "- Frontend: Deploy to Netlify/Vercel"
echo ""
echo "🔗 URLs:"
echo "- Backend: http://localhost:5000"
echo "- Frontend: file:///path/to/frontend/index.html" 