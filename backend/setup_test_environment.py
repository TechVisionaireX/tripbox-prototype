from app import app
from models import db, User, Trip, Group, GroupMember
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def setup_test_environment():
    with app.app_context():
        # Get or create test user
        test_user = User.query.filter_by(email='test@gmail.com').first()
        if not test_user:
            print("❌ Test user not found. Please run create_test_user.py first.")
            return
        
        print(f"✅ Found test user: {test_user.email}")
        
        # Create a test trip
        test_trip = Trip(
            user_id=test_user.id,
            name='Test Trip',
            start_date='2024-01-01',
            end_date='2024-01-07',
            description='A test trip for expense functionality'
        )
        db.session.add(test_trip)
        db.session.commit()
        
        print(f"✅ Created test trip: {test_trip.name} (ID: {test_trip.id})")
        
        # Create a group for this trip
        test_group = Group(
            name=f"{test_trip.name} - Main Group",
            creator_id=test_user.id,
            trip_id=test_trip.id
        )
        db.session.add(test_group)
        db.session.commit()
        
        print(f"✅ Created test group: {test_group.name} (ID: {test_group.id})")
        
        # Add test user as member of the group
        member = GroupMember(
            group_id=test_group.id,
            user_id=test_user.id
        )
        db.session.add(member)
        db.session.commit()
        
        print(f"✅ Added test user as member of group {test_group.id}")
        
        print("\n📊 Test Environment Summary:")
        print(f"   Trip ID: {test_trip.id}")
        print(f"   Group ID: {test_group.id}")
        print(f"   User ID: {test_user.id}")
        print(f"   User Email: {test_user.email}")
        
        return {
            'trip_id': test_trip.id,
            'group_id': test_group.id,
            'user_id': test_user.id
        }

if __name__ == '__main__':
    setup_test_environment() 