from app import app
from models import db, Trip, Group, GroupMember

def fix_missing_groups():
    """Add default groups to trips that don't have them"""
    with app.app_context():
        # Get all trips
        trips = Trip.query.all()
        print(f"Found {len(trips)} trips")
        
        # Get all groups
        groups = Group.query.all()
        print(f"Found {len(groups)} groups")
        
        # Find trips without default groups
        trips_with_groups = set(g.trip_id for g in groups)
        trips_without_groups = [t for t in trips if t.id not in trips_with_groups]
        
        print(f"Trips without default groups: {len(trips_without_groups)}")
        
        for trip in trips_without_groups:
            print(f"Creating default group for Trip {trip.id}: {trip.name}")
            
            # Create default group
            default_group = Group(
                name=f"{trip.name} - Main Group",
                creator_id=trip.user_id,
                trip_id=trip.id
            )
            db.session.add(default_group)
            db.session.commit()
            
            # Add trip creator as first member
            creator_member = GroupMember(
                group_id=default_group.id,
                user_id=trip.user_id
            )
            db.session.add(creator_member)
            db.session.commit()
            
            print(f"✅ Created group {default_group.id} for trip {trip.id}")
        
        print(f"\nFixed {len(trips_without_groups)} trips")

if __name__ == "__main__":
    fix_missing_groups() 