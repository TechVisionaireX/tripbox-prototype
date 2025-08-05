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

class EnhancedChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, location, file
    reply_to_message_id = db.Column(db.Integer, db.ForeignKey('enhanced_chat_message.id'), nullable=True)
    message_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional data
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)
    read_by = db.Column(db.Text, nullable=True)  # JSON array of user IDs who read the message
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String(300), nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON string of options
    is_active = db.Column(db.Boolean, default=True)
    is_finalized = db.Column(db.Boolean, default=False)
    winning_option = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=True)

class PollVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    selected_option = db.Column(db.String(200), nullable=False)
    voted_at = db.Column(db.DateTime, server_default=db.func.now())

class LocationCheckin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    message = db.Column(db.String(300), nullable=True)
    checkin_time = db.Column(db.DateTime, server_default=db.func.now())

class LiveLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    speed = db.Column(db.Float, nullable=True)
    heading = db.Column(db.Float, nullable=True)
    altitude = db.Column(db.Float, nullable=True)
    battery_level = db.Column(db.Float, nullable=True)
    location_name = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
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

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    caption = db.Column(db.String(300))

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # packing, todo, reminder
    text = db.Column(db.String(255), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

class BudgetItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # poll_created, poll_voted, poll_finalized, checkin, pdf_generated
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
