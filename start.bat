@echo off
echo ============================================
echo    TripBox-IntelliOrganizer Startup
echo ============================================
echo.

REM Check if we're in the right directory
if not exist "backend\app.py" (
    echo Error: Please run this script from the project root directory
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r backend\requirements.txt

echo.
echo Setting up database...
cd backend
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database setup complete')"

echo.
echo Creating test user...
python -c "from app import app, db; from models import User; from auth import bcrypt; app.app_context().push(); user = User.query.filter_by(email='test@test.com').first(); print('Test user already exists') if user else [db.session.add(User(email='test@test.com', password=bcrypt.generate_password_hash('test123').decode('utf-8'), name='Test User')), db.session.commit(), print('Test user created: test@test.com / test123')]"

cd ..

echo.
echo ============================================
echo    Setup Complete!
echo ============================================
echo.
echo To start the application:
echo 1. Run: python app.py
echo 2. Open: frontend\index.html in your browser
echo 3. Login: test@test.com / test123
echo.
echo Backend will be available at: http://localhost:5000
echo.
pause 