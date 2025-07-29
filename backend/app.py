from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

# Create Flask app
app = Flask(__name__)

# Configure CORS for all origins
CORS(app, origins="*", supports_credentials=True)

# Configurations
app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_secret_key_here')

# API routes
@app.route('/api/hello')
def hello():
    return jsonify(message="TripBox backend is running!", version="1.0.0")

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'TripBox backend is running',
        'mode': 'minimal'
    })

@app.route('/api/test')
def test_endpoint():
    return jsonify({
        'success': True,
        'message': 'Backend is working properly',
        'port': str(os.environ.get('PORT', '5000'))
    })

@app.route('/api/login', methods=['POST'])
def login():
    return jsonify({
        'success': True,
        'message': 'Login endpoint working',
        'token': 'test_token_123'
    })

# Frontend serving routes
@app.route('/')
def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def serve_frontend_files(filename):
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    # Handle common frontend routes
    if filename in ['dashboard', 'features', 'advanced-features']:
        return send_from_directory(frontend_path, f'{filename}.html')
    
    # Try to serve the requested file
    try:
        return send_from_directory(frontend_path, filename)
    except:
        # If file not found, serve index.html for SPA behavior
        return send_from_directory(frontend_path, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# For Gunicorn deployment
application = app
