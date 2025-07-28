from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, Recommendation
import requests
import os
from datetime import datetime

ai_recommendations_bp = Blueprint('ai_recommendations_bp', __name__)

# Configuration for external APIs
GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', 'your-google-places-api-key')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key')

@ai_recommendations_bp.route('/api/groups/<int:group_id>/ai-recommendations', methods=['POST'])
@jwt_required()
def get_ai_recommendations(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    radius = data.get('radius', 5000)  # 5km default
    types = data.get('types', ['restaurant', 'tourist_attraction', 'lodging'])
    
    recommendations = []
    
    for place_type in types:
        try:
            # Google Places Nearby Search
            places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius,
                'type': place_type,
                'key': GOOGLE_PLACES_API_KEY
            }
            
            response = requests.get(places_url, params=params)
            places_data = response.json()
            
            if places_data.get('status') == 'OK':
                for place in places_data.get('results', [])[:5]:  # Top 5 for each type
                    recommendation = {
                        'name': place.get('name'),
                        'type': place_type,
                        'rating': place.get('rating', 0),
                        'price_level': place.get('price_level', 0),
                        'address': place.get('vicinity'),
                        'photo_reference': place.get('photos', [{}])[0].get('photo_reference') if place.get('photos') else None,
                        'place_id': place.get('place_id'),
                        'location': place.get('geometry', {}).get('location', {}),
                        'is_open': place.get('opening_hours', {}).get('open_now', None)
                    }
                    recommendations.append(recommendation)
                    
        except Exception as e:
            print(f"Error fetching {place_type} recommendations: {e}")
    
    return jsonify({
        'recommendations': recommendations,
        'location': {'latitude': latitude, 'longitude': longitude},
        'total_found': len(recommendations)
    })

@ai_recommendations_bp.route('/api/groups/<int:group_id>/ai-recommendations/save', methods=['POST'])
@jwt_required()
def save_ai_recommendation(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    recommendation = Recommendation(
        group_id=group_id,
        user_id=user_id,
        title=data.get('name'),
        type=data.get('type'),
        comment=f"Rating: {data.get('rating')}/5 - {data.get('address')}"
    )
    
    db.session.add(recommendation)
    db.session.commit()
    
    return jsonify({'message': 'Recommendation saved successfully'}), 201

@ai_recommendations_bp.route('/api/groups/<int:group_id>/ai-recommendations/personalized', methods=['POST'])
@jwt_required()
def get_personalized_recommendations(group_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    preferences = data.get('preferences', [])
    budget = data.get('budget', 'medium')
    duration = data.get('duration', 1)  # days
    location = data.get('location', '')
    
    # Simulated AI recommendations based on preferences
    # In production, this would use OpenAI API or similar
    ai_suggestions = generate_ai_suggestions(preferences, budget, duration, location)
    
    return jsonify({
        'personalized_recommendations': ai_suggestions,
        'preferences_used': preferences,
        'budget_category': budget
    })

def generate_ai_suggestions(preferences, budget, duration, location):
    """Generate AI-powered suggestions based on user preferences"""
    
    # Budget mapping
    budget_ranges = {
        'low': {'food': '$', 'accommodation': '$-$$', 'activities': 'Free-$'},
        'medium': {'food': '$$', 'accommodation': '$$-$$$', 'activities': '$-$$'},
        'high': {'food': '$$$-$$$$', 'accommodation': '$$$-$$$$', 'activities': '$$-$$$'}
    }
    
    # Sample AI-generated suggestions
    suggestions = []
    
    if 'food' in preferences:
        suggestions.extend([
            {
                'category': 'Restaurant',
                'name': f'Local Cuisine in {location}',
                'description': f'Authentic local restaurants within {budget_ranges[budget]["food"]} budget',
                'priority': 'high',
                'estimated_cost': budget_ranges[budget]['food'],
                'time_needed': '1-2 hours'
            }
        ])
    
    if 'adventure' in preferences:
        suggestions.extend([
            {
                'category': 'Activity',
                'name': f'Adventure Sports in {location}',
                'description': f'Exciting outdoor activities for {duration} days',
                'priority': 'medium',
                'estimated_cost': budget_ranges[budget]['activities'],
                'time_needed': '4-8 hours'
            }
        ])
    
    if 'culture' in preferences:
        suggestions.extend([
            {
                'category': 'Cultural Site',
                'name': f'Historical Sites in {location}',
                'description': 'Museums, temples, and cultural landmarks',
                'priority': 'high',
                'estimated_cost': budget_ranges[budget]['activities'],
                'time_needed': '2-4 hours'
            }
        ])
    
    if 'nature' in preferences:
        suggestions.extend([
            {
                'category': 'Nature',
                'name': f'Natural Attractions in {location}',
                'description': 'Parks, beaches, hiking trails, and scenic spots',
                'priority': 'medium',
                'estimated_cost': 'Free-$',
                'time_needed': '3-6 hours'
            }
        ])
    
    return suggestions

@ai_recommendations_bp.route('/api/groups/<int:group_id>/weather', methods=['GET'])
@jwt_required()
def get_weather_info(group_id):
    user_id = int(get_jwt_identity())
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    latitude = request.args.get('lat')
    longitude = request.args.get('lng')
    
    # OpenWeatherMap API (you'll need to get an API key)
    weather_api_key = os.environ.get('OPENWEATHER_API_KEY', 'your-openweather-api-key')
    
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': weather_api_key,
            'units': 'metric'
        }
        
        response = requests.get(weather_url, params=params)
        weather_data = response.json()
        
        if response.status_code == 200:
            return jsonify({
                'weather': {
                    'temperature': weather_data['main']['temp'],
                    'description': weather_data['weather'][0]['description'],
                    'humidity': weather_data['main']['humidity'],
                    'wind_speed': weather_data['wind']['speed'],
                    'location': weather_data['name']
                }
            })
        else:
            return jsonify({'error': 'Weather data not available'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Weather service error: {str(e)}'}), 500 