from app import app
from models import db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_test_user():
    with app.app_context():
        # Check if test user already exists
        existing_user = User.query.filter_by(email='test@gmail.com').first()
        if existing_user:
            print("Test user already exists")
            return
        
        # Create test user
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        test_user = User(
            email='test@gmail.com',
            password=hashed_password,
            name='Test User'
        )
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Test user created successfully:")
        print(f"   Email: test@gmail.com")
        print(f"   Password: password123")
        print(f"   Name: Test User")

if __name__ == '__main__':
    create_test_user() 