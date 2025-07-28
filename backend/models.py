from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    finalized = db.Column(db.Boolean, default=False)


# ---- CLEARLY ADD THESE TWO NEW MODELS BELOW ----

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50))  # e.g. hotel, restaurant, activity
    comment = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))  # e.g., Food, Hotel, Transport
    note = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), default="checklist")
    text = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class BudgetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class LocationCheckin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Temporarily commented out new models to fix deployment
# Will add them back once basic deployment is working

# class LiveLocation(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     group_id = db.Column(db.Integer, nullable=False)
#     user_id = db.Column(db.Integer, nullable=False)
#     latitude = db.Column(db.Float, nullable=False)
#     longitude = db.Column(db.Float, nullable=False)
#     accuracy = db.Column(db.Float)
#     speed = db.Column(db.Float)
#     heading = db.Column(db.Float)
#     altitude = db.Column(db.Float)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     is_active = db.Column(db.Boolean, default=True)
#     battery_level = db.Column(db.Integer)
#     location_name = db.Column(db.String(255))

# class EnhancedChatMessage(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     message = db.Column(db.Text, nullable=False)
#     message_type = db.Column(db.String(50), default='text')  # text, image, location, file
#     reply_to_message_id = db.Column(db.Integer)  # Remove self-referencing foreign key for now
#     is_edited = db.Column(db.Boolean, default=False)
#     edited_at = db.Column(db.DateTime)
#     read_by = db.Column(db.Text)  # JSON array of user IDs who read the message
#     timestamp = db.Column(db.DateTime, server_default=db.func.now())
#     metadata = db.Column(db.Text)  # JSON for additional data
