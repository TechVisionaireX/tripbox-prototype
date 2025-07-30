from app import app, db
from models import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def create_kk_user():
    print("🔍 Creating kk user...")
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(email='kk@gmail.com').first()
        if existing_user:
            print("⚠️ User kk@gmail.com already exists")
            return
        
        # Create new user
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        new_user = User(
            name='kk',
            email='kk@gmail.com',
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        print("✅ User kk@gmail.com created successfully")
        print("   Email: kk@gmail.com")
        print("   Password: password123")
        print("   Name: kk")

if __name__ == "__main__":
    create_kk_user() 