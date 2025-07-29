from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import hashlib
import jwt
import datetime
import os

# Create Flask app
app = Flask(__name__)
CORS(app)  # Allow all CORS

# Simple secret key
app.config['SECRET_KEY'] = 'simple-secret-key-123'

# Database setup
def init_db():
    try:
        # Use absolute path for database
        db_path = os.path.join(os.path.dirname(__file__), 'tripbox.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        
        # Create test user
        test_email = 'test@test.com'
        test_password = hashlib.md5('test123'.encode()).hexdigest()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (test_email,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
                          (test_email, test_password, 'Test User'))
            print("✅ Test user created successfully")
        else:
            print("✅ Test user already exists")
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized at: {db_path}")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

# Initialize database
init_db()

@app.route('/')
def home():
    return jsonify({"message": "TripBox Backend is Running!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "message": "Backend is working"})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Hash password
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        # Check user
        db_path = os.path.join(os.path.dirname(__file__), 'tripbox.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                      (email, hashed_password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Create token
            token = jwt.encode({
                'user_id': user[0],
                'email': user[1],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                "token": token,
                "user": {"id": user[0], "email": user[1], "name": user[3]},
                "message": "Login successful"
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get('email')
        password = data.get('password')
        name = data.get('name', 'User')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        db_path = os.path.join(os.path.dirname(__file__), 'tripbox.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)',
                      (email, hashed_password, name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        # Create token
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "token": token,
            "user": {"id": user_id, "email": email, "name": name},
            "message": "Registration successful"
        })
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/create-test-user', methods=['POST'])
def create_test_user():
    return jsonify({
        "message": "Test user already exists",
        "email": "test@test.com",
        "password": "test123"
    })

@app.route('/api/hello')
def hello():
    return jsonify({"message": "TripBox Backend is Running!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 TripBox Backend Starting...")
    print(f"📍 Running on: http://localhost:{port}")
    print("📧 Test Login: test@test.com / test123")
    app.run(host='0.0.0.0', port=port, debug=False) 