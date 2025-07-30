from app import app, db
from models import User

def check_users():
    print("🔍 Checking users in database...")
    
    with app.app_context():
        users = User.query.all()
        print(f"✅ Found {len(users)} users:")
        
        for user in users:
            print(f"   - {user.name} ({user.email}) - ID: {user.id}")
            # Don't print passwords for security

if __name__ == "__main__":
    check_users() 