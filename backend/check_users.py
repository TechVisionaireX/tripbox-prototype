#!/usr/bin/env python3
"""
Check users in the database
"""
from app import app
from models import db, User

def check_users():
    with app.app_context():
        users = User.query.all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - ID: {user.id}, Email: {user.email}, Name: {user.name}")
            # Don't print passwords for security

if __name__ == "__main__":
    check_users() 