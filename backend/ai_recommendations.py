from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, GroupMember, Recommendation
import requests
import os
from datetime import datetime, timedelta
import json

ai_recommendations_bp = Blueprint('ai_recommendations_bp', __name__)

# Configuration for external APIs
GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', 'your-google-places-api-key')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key')

# Add conversation memory at the top of the file
conversation_history = {}

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

@ai_recommendations_bp.route('/api/groups/<int:group_id>/ai-assistant/chat', methods=['POST'])
@jwt_required()
def ai_assistant_chat(group_id):
    """AI Assistant conversational endpoint"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    user_message = data.get('message', '')
    trip_context = data.get('trip_context', {})
    conversation_id = data.get('conversation_id') # Get conversation_id from request
    
    # Generate AI response based on message type
    ai_response = generate_ai_response(user_message, trip_context, conversation_id)
    
    return jsonify({
        'response': ai_response,
        'message_type': 'ai_assistant',
        'timestamp': datetime.now().isoformat()
    })

@ai_recommendations_bp.route('/api/groups/<int:group_id>/ai-assistant/suggestions', methods=['POST'])
@jwt_required()
def get_smart_suggestions(group_id):
    """Get smart suggestions based on trip context"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    destination = data.get('destination', '')
    dates = data.get('dates', {})
    interests = data.get('interests', [])
    budget = data.get('budget', 'medium')
    group_size = data.get('group_size', 1)
    
    suggestions = generate_smart_suggestions(destination, dates, interests, budget, group_size)
    
    return jsonify({
        'suggestions': suggestions,
        'destination': destination,
        'generated_at': datetime.now().isoformat()
    })

@ai_recommendations_bp.route('/api/groups/<int:group_id>/ai-assistant/reminders', methods=['GET'])
@jwt_required()
def get_smart_reminders(group_id):
    """Get smart reminders for the trip"""
    user_id = int(get_jwt_identity())
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    trip_data = request.args.get('trip_data', '{}')
    trip_context = json.loads(trip_data)
    
    reminders = generate_smart_reminders(trip_context)
    
    return jsonify({
        'reminders': reminders,
        'generated_at': datetime.now().isoformat()
    })

@ai_recommendations_bp.route('/api/groups/<int:group_id>/ai-assistant/weather-alerts', methods=['GET'])
@jwt_required()
def get_weather_alerts(group_id):
    """Get weather alerts and packing suggestions"""
    user_id = int(get_jwt_identity())
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    latitude = request.args.get('lat')
    longitude = request.args.get('lng')
    trip_dates = request.args.get('dates', '{}')
    
    weather_alerts = generate_weather_alerts(latitude, longitude, json.loads(trip_dates))
    
    return jsonify({
        'weather_alerts': weather_alerts,
        'generated_at': datetime.now().isoformat()
    })

def generate_ai_response(user_message, trip_context, conversation_id=None):
    """Generate AI response based on user message and trip context with conversation memory"""
    message_lower = user_message.lower()
    
    # Initialize conversation history if not exists
    if conversation_id and conversation_id not in conversation_history:
        conversation_history[conversation_id] = []
    
    # Add user message to history
    if conversation_id:
        conversation_history[conversation_id].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
    
    # Extract destination from message or trip context
    destination = trip_context.get('destination', '')
    if not destination:
        # Try to extract destination from the message
        for word in message_lower.split():
            if any(city in word for city in ['paris', 'london', 'tokyo', 'new york', 'los angeles', 'rome', 'dubai', 'mumbai', 'sydney', 'singapore', 'bangkok', 'seoul', 'beijing']):
                destination = word
                break
    
    # Check for conversation context and greetings
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
        return generate_greeting_response(user_message, trip_context, conversation_id)
    elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return generate_thanks_response(user_message, trip_context, conversation_id)
    elif any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'end']):
        return generate_farewell_response(user_message, trip_context, conversation_id)
    elif any(word in message_lower for word in ['help', 'what can you do', 'capabilities', 'assist']):
        return generate_help_response(user_message, trip_context, conversation_id)
    elif any(word in message_lower for word in ['weather', 'forecast', 'temperature', 'rain', 'sunny', 'hot', 'cold', 'climate']):
        return generate_weather_response(user_message, trip_context)
    elif any(word in message_lower for word in ['budget', 'cost', 'money', 'expensive', 'cheap', 'price', 'save', 'spend', 'dollar', 'euro', 'currency']):
        return generate_budget_suggestion(user_message, trip_context)
    elif any(word in message_lower for word in ['food', 'restaurant', 'eat', 'dining', 'cuisine', 'meal', 'dish', 'local', 'hungry', 'lunch', 'dinner', 'breakfast']):
        return generate_food_suggestion(user_message, trip_context)
    elif any(word in message_lower for word in ['activity', 'things to do', 'attraction', 'visit', 'see', 'tour', 'place', 'sight', 'fun', 'entertainment', 'adventure']):
        return generate_activity_suggestion(user_message, trip_context)
    elif any(word in message_lower for word in ['plan', 'itinerary', 'schedule', 'day', 'trip', 'organize', 'arrange']):
        return generate_trip_plan_suggestion(user_message, trip_context)
    elif any(word in message_lower for word in ['remind', 'forget', 'checklist', 'pack', 'prepare', 'need', 'bring', 'carry']):
        return generate_reminder_response(user_message, trip_context)
    elif any(word in message_lower for word in ['hotel', 'accommodation', 'stay', 'sleep', 'room', 'booking']):
        return generate_accommodation_suggestion(user_message, trip_context)
    elif any(word in message_lower for word in ['transport', 'transportation', 'travel', 'bus', 'train', 'metro', 'subway', 'taxi']):
        return generate_transport_suggestion(user_message, trip_context)
    elif any(word in message_lower for word in ['shopping', 'buy', 'shop', 'market', 'mall', 'store']):
        return generate_shopping_suggestion(user_message, trip_context)
    elif any(word in message_lower for word in ['safety', 'safe', 'danger', 'crime', 'security']):
        return generate_safety_suggestion(user_message, trip_context)
    else:
        # For any other message, try to provide a helpful response
        return generate_contextual_response(user_message, trip_context, conversation_id)

def generate_greeting_response(message, trip_context, conversation_id=None):
    """Generate a personalized greeting response"""
    import random
    
    greetings = [
        "Hello! I'm your AI travel assistant. How can I help you plan your trip today?",
        "Hi there! I'm here to help make your travel planning easier. What would you like to know?",
        "Hey! Welcome to your personal travel assistant. I can help with weather, activities, planning, and more!",
        "Good to see you! I'm ready to help you with anything travel-related. What's on your mind?"
    ]
    
    # Check if this is a returning user
    if conversation_id and conversation_history.get(conversation_id, []):
        greetings = [
            "Welcome back! How can I continue helping you with your trip?",
            "Great to see you again! What would you like to work on today?",
            "Hello again! I'm here to help you further with your travel plans."
        ]
    
    greeting = random.choice(greetings)
    
    response = {
        'type': 'greeting',
        'content': f"{greeting}\n\nI can help you with:\n• **Weather information** and packing suggestions\n• **Activity recommendations** and attractions\n• **Budget planning** and cost estimates\n• **Trip planning** and itineraries\n• **Accommodation** and transportation options\n• **Local cuisine** and restaurant suggestions\n• **Safety tips** and travel advice\n\nWhat would you like to explore?",
        'suggestions': ['Check weather', 'Plan activities', 'Budget advice', 'Find restaurants', 'Safety tips']
    }
    
    # Save response to conversation history
    if conversation_id:
        conversation_history[conversation_id].append({
            'role': 'assistant',
            'content': response['content'],
            'timestamp': datetime.now().isoformat()
        })
    
    return response

def generate_thanks_response(message, trip_context, conversation_id=None):
    """Generate a response to thank you messages"""
    import random
    
    thanks_responses = [
        "You're very welcome! I'm here to help make your trip planning as smooth as possible.",
        "My pleasure! Feel free to ask me anything else about your travels.",
        "Happy to help! Is there anything else you'd like to know about your trip?",
        "You're welcome! I'm always here when you need travel assistance."
    ]
    
    response = {
        'type': 'thanks',
        'content': random.choice(thanks_responses),
        'suggestions': ['More help', 'Weather check', 'Activity ideas', 'Budget tips']
    }
    
    if conversation_id:
        conversation_history[conversation_id].append({
            'role': 'assistant',
            'content': response['content'],
            'timestamp': datetime.now().isoformat()
        })
    
    return response

def generate_farewell_response(message, trip_context, conversation_id=None):
    """Generate a farewell response"""
    import random
    
    farewells = [
        "Goodbye! Have a wonderful trip and don't hesitate to come back if you need more help!",
        "See you later! Safe travels and enjoy your adventure!",
        "Take care! I'll be here when you need travel assistance again.",
        "Have a great trip! Feel free to return anytime for more travel help."
    ]
    
    response = {
        'type': 'farewell',
        'content': random.choice(farewells),
        'suggestions': []
    }
    
    if conversation_id:
        conversation_history[conversation_id].append({
            'role': 'assistant',
            'content': response['content'],
            'timestamp': datetime.now().isoformat()
        })
    
    return response

def generate_help_response(message, trip_context, conversation_id=None):
    """Generate a comprehensive help response"""
    response = {
        'type': 'help',
        'content': "I'm your AI travel assistant! Here's what I can help you with:\n\n" +
                  "**🌤️ Weather & Packing**\n" +
                  "• Check current weather for any destination\n" +
                  "• Get packing suggestions based on weather\n" +
                  "• Weather alerts and forecasts\n\n" +
                  "**🎯 Activities & Attractions**\n" +
                  "• Popular tourist attractions\n" +
                  "• Local activities and experiences\n" +
                  "• Hidden gems and off-the-beaten-path spots\n\n" +
                  "**💰 Budget & Planning**\n" +
                  "• Cost estimates and budget tips\n" +
                  "• Money-saving strategies\n" +
                  "• Currency and payment advice\n\n" +
                  "**🍽️ Food & Dining**\n" +
                  "• Local cuisine recommendations\n" +
                  "• Restaurant suggestions\n" +
                  "• Food safety and dietary tips\n\n" +
                  "**🏨 Accommodation & Transport**\n" +
                  "• Hotel and lodging options\n" +
                  "• Transportation advice\n" +
                  "• Booking tips and strategies\n\n" +
                  "**🛡️ Safety & Tips**\n" +
                  "• Travel safety advice\n" +
                  "• Local customs and etiquette\n" +
                  "• Emergency information\n\n" +
                  "Just ask me anything about your trip!",
        'suggestions': ['Weather check', 'Plan activities', 'Budget advice', 'Find restaurants', 'Safety tips']
    }
    
    if conversation_id:
        conversation_history[conversation_id].append({
            'role': 'assistant',
            'content': response['content'],
            'timestamp': datetime.now().isoformat()
        })
    
    return response

def generate_trip_plan_suggestion(message, trip_context):
    """Generate a trip plan suggestion"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'trip_plan',
        'content': f"Here's a suggested plan for {destination}:\n\n" +
                  "**Day 1: Arrival & Orientation**\n" +
                  "• Check into accommodation\n" +
                  "• Explore the local area\n" +
                  "• Try local cuisine for dinner\n\n" +
                  "**Day 2: Cultural Exploration**\n" +
                  "• Visit main attractions\n" +
                  "• Take guided tours\n" +
                  "• Experience local culture\n\n" +
                  "**Day 3: Adventure & Activities**\n" +
                  "• Outdoor activities\n" +
                  "• Shopping and souvenirs\n" +
                  "• Evening entertainment\n\n" +
                  "Would you like me to customize this plan based on your specific interests and budget?",
        'suggestions': ['Customize plan', 'Add activities', 'Check weather', 'Budget breakdown']
    }

def generate_weather_response(message, trip_context):
    """Generate weather-related response"""
    destination = trip_context.get('destination', 'your destination')
    
    # Try to get real weather data if destination is provided
    try:
        if destination and destination != 'your destination':
            # For now, return realistic weather data
            # In production, integrate with OpenWeatherMap API
            weather_data = {
                'temperature': 22,
                'conditions': 'Partly cloudy',
                'humidity': 65,
                'wind_speed': 10,
                'feels_like': 24
            }
            
            return {
                'type': 'weather_info',
                'content': f"Here's the current weather for **{destination}**:\n\n" +
                          f"🌡️ **Temperature**: {weather_data['temperature']}°C ({weather_data['temperature']*9/5+32:.0f}°F)\n" +
                          f"🌤️ **Feels like**: {weather_data['feels_like']}°C\n" +
                          f"☁️ **Conditions**: {weather_data['conditions']}\n" +
                          f"💧 **Humidity**: {weather_data['humidity']}%\n" +
                          f"💨 **Wind**: {weather_data['wind_speed']} km/h\n\n" +
                          "**Packing Suggestions:**\n" +
                          "• Light layers for changing temperatures\n" +
                          "• Comfortable walking shoes\n" +
                          "• Rain gear (just in case)\n" +
                          "• Sun protection\n\n" +
                          "Would you like me to get the detailed 7-day forecast or help you plan activities based on this weather?",
                'suggestions': ['7-day forecast', 'Packing list', 'Weather alerts', 'Plan activities']
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    
    # Fallback response
    return {
        'type': 'weather_info',
        'content': f"I'll check the current weather for **{destination}**.\n\n" +
                  "**Current Weather:**\n" +
                  "🌡️ **Temperature**: 22°C (72°F)\n" +
                  "🌤️ **Conditions**: Partly cloudy\n" +
                  "💧 **Humidity**: 65%\n" +
                  "💨 **Wind**: 10 km/h\n\n" +
                  "**Packing Suggestions:**\n" +
                  "• Light layers for changing temperatures\n" +
                  "• Comfortable walking shoes\n" +
                  "• Rain gear (just in case)\n" +
                  "• Sun protection\n\n" +
                  "Would you like me to get the detailed 7-day forecast or help you plan activities based on this weather?",
        'suggestions': ['7-day forecast', 'Packing list', 'Weather alerts', 'Plan activities']
    }

def generate_budget_suggestion(message, trip_context):
    """Generate budget-related suggestions"""
    return {
        'type': 'budget_advice',
        'content': "Here are some **budget-friendly tips** for your trip:\n\n" +
                  "**🏨 Accommodation:**\n" +
                  "• Consider hostels or vacation rentals\n" +
                  "• Book in advance for better rates\n" +
                  "• Look for deals on booking platforms\n" +
                  "• Consider staying slightly outside city centers\n\n" +
                  "**🍽️ Food & Dining:**\n" +
                  "• Eat at local markets and street food\n" +
                  "• Avoid tourist trap restaurants\n" +
                  "• Cook some meals if you have kitchen access\n" +
                  "• Look for lunch specials\n\n" +
                  "**🚇 Transportation:**\n" +
                  "• Use public transportation\n" +
                  "• Walk when possible\n" +
                  "• Consider city passes for attractions\n" +
                  "• Share rides with other travelers\n\n" +
                  "**🎯 Activities:**\n" +
                  "• Many museums have free days\n" +
                  "• Explore parks and public spaces\n" +
                  "• Take free walking tours\n" +
                  "• Research free events and festivals\n\n" +
                  "Would you like me to help you create a detailed budget breakdown for your specific destination?",
        'suggestions': ['Create budget', 'Find deals', 'Cost estimates', 'Money tips']
    }

def generate_food_suggestion(message, trip_context):
    """Generate food-related suggestions"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'food_recommendations',
        'content': f"Here are some **food recommendations** for {destination}:\n\n" +
                  "**🍽️ Local Cuisine to Try:**\n" +
                  "• Traditional local dishes\n" +
                  "• Street food specialties\n" +
                  "• Regional specialties\n" +
                  "• Seasonal ingredients\n\n" +
                  "**🏪 Best Places to Eat:**\n" +
                  "• Local markets and food stalls\n" +
                  "• Family-run restaurants\n" +
                  "• Popular local spots\n" +
                  "• Hidden gems off the tourist path\n\n" +
                  "**💡 Food Tips:**\n" +
                  "• Try the daily specials\n" +
                  "• Ask locals for recommendations\n" +
                  "• Be adventurous with new flavors\n" +
                  "• Check food safety and hygiene\n\n" +
                  "**🍷 Local Drinks:**\n" +
                  "• Regional wines and beers\n" +
                  "• Traditional beverages\n" +
                  "• Coffee and tea culture\n\n" +
                  "Would you like me to suggest specific restaurants or help you plan a food tour?",
        'suggestions': ['Restaurant list', 'Food tour', 'Local dishes', 'Dietary needs']
    }

def generate_activity_suggestion(message, trip_context):
    """Generate activity-related suggestions"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'activity_recommendations',
        'content': f"Here are some **amazing activities** to do in {destination}:\n\n" +
                  "**🏛️ Cultural & Historical:**\n" +
                  "• Visit famous landmarks and monuments\n" +
                  "• Explore museums and galleries\n" +
                  "• Take guided historical tours\n" +
                  "• Attend cultural events and festivals\n\n" +
                  "**🌳 Outdoor & Nature:**\n" +
                  "• Parks and gardens\n" +
                  "• Hiking and nature trails\n" +
                  "• Boat tours and water activities\n" +
                  "• Scenic viewpoints and photo spots\n\n" +
                  "**🎭 Entertainment & Nightlife:**\n" +
                  "• Local theaters and shows\n" +
                  "• Live music venues\n" +
                  "• Bars and clubs\n" +
                  "• Evening entertainment\n\n" +
                  "**🛍️ Shopping & Markets:**\n" +
                  "• Local markets and bazaars\n" +
                  "• Shopping districts\n" +
                  "• Artisan and craft shops\n" +
                  "• Souvenir shopping\n\n" +
                  "**🎯 Unique Experiences:**\n" +
                  "• Cooking classes\n" +
                  "• Local workshops\n" +
                  "• Adventure activities\n" +
                  "• Photography tours\n\n" +
                  "Would you like me to create a detailed itinerary or suggest specific activities based on your interests?",
        'suggestions': ['Create itinerary', 'Popular attractions', 'Hidden gems', 'Adventure activities']
    }

def generate_reminder_response(message, trip_context):
    """Generate reminder-related response"""
    return {
        'type': 'reminders',
        'content': "Here are some important reminders for your trip:\n\n" +
                  "**Pre-Trip Checklist:**\n" +
                  "• Passport and visas\n" +
                  "• Travel insurance\n" +
                  "• Vaccinations\n" +
                  "• Currency exchange\n\n" +
                  "**Packing Essentials:**\n" +
                  "• Weather-appropriate clothing\n" +
                  "• Travel documents\n" +
                  "• Medications\n" +
                  "• Chargers and adapters\n\n" +
                  "**Smart Reminders:**\n" +
                  "• Check weather forecast\n" +
                  "• Book activities in advance\n" +
                  "• Notify bank of travel\n\n" +
                  "Would you like me to create a custom checklist?",
        'suggestions': ['Create checklist', 'Travel insurance', 'Visa requirements', 'Packing list']
    }

def generate_general_response(message, trip_context):
    """Generate general helpful response"""
    return {
        'type': 'general_help',
        'content': "I'm here to help you plan the perfect trip! I can assist with:\n\n" +
                  "• Trip planning and itineraries\n" +
                  "• Weather forecasts and packing suggestions\n" +
                  "• Budget planning and cost-saving tips\n" +
                  "• Restaurant and activity recommendations\n" +
                  "• Travel reminders and checklists\n\n" +
                  "Just ask me anything about your trip!",
        'suggestions': ['Plan trip', 'Weather check', 'Budget help', 'Activity ideas']
    }

def generate_contextual_response(message, trip_context, conversation_id=None):
    """Generate a contextual response based on conversation history and current message"""
    import random
    
    # Check conversation history for context
    context = ""
    if conversation_id and conversation_history.get(conversation_id, []):
        recent_messages = conversation_history[conversation_id][-3:]  # Last 3 messages
        context = "Based on our conversation, "
    
    # Generate contextual responses
    contextual_responses = [
        f"{context}I understand you're asking about travel. Could you be more specific? I can help with weather, activities, planning, budget, food, accommodation, or safety.",
        f"{context}That's an interesting question about travel! I'd be happy to help you with specific details about your destination, activities, or travel planning.",
        f"{context}I'm here to help with your travel needs. Would you like information about weather, activities, budget planning, or something else?",
        f"{context}Let me help you with that travel question. I can provide specific advice about destinations, activities, planning, or any other travel-related topic."
    ]
    
    response = {
        'type': 'contextual',
        'content': random.choice(contextual_responses),
        'suggestions': ['Weather info', 'Activity ideas', 'Budget tips', 'Food recommendations', 'Safety advice']
    }
    
    if conversation_id:
        conversation_history[conversation_id].append({
            'role': 'assistant',
            'content': response['content'],
            'timestamp': datetime.now().isoformat()
        })
    
    return response

def generate_accommodation_suggestion(message, trip_context):
    """Generate accommodation suggestions"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'accommodation_advice',
        'content': f"Here are **accommodation options** for {destination}:\n\n" +
                  "**🏨 Hotels & Resorts:**\n" +
                  "• Luxury hotels with full amenities\n" +
                  "• Boutique hotels with character\n" +
                  "• Business hotels for convenience\n" +
                  "• Resort-style accommodations\n\n" +
                  "**🏠 Alternative Options:**\n" +
                  "• Vacation rentals and apartments\n" +
                  "• Hostels for budget travelers\n" +
                  "• Bed & breakfast establishments\n" +
                  "• Guesthouses and homestays\n\n" +
                  "**📍 Location Tips:**\n" +
                  "• City center for convenience\n" +
                  "• Quiet neighborhoods for peace\n" +
                  "• Near public transport\n" +
                  "• Safe and well-lit areas\n\n" +
                  "**💡 Booking Tips:**\n" +
                  "• Book in advance for better rates\n" +
                  "• Read recent reviews\n" +
                  "• Check cancellation policies\n" +
                  "• Compare multiple booking sites\n\n" +
                  "Would you like me to suggest specific hotels or help you find the best area to stay?",
        'suggestions': ['Hotel recommendations', 'Best areas', 'Booking tips', 'Budget options']
    }

def generate_transport_suggestion(message, trip_context):
    """Generate transportation suggestions"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'transport_advice',
        'content': f"Here's **transportation advice** for {destination}:\n\n" +
                  "**🚇 Public Transportation:**\n" +
                  "• Metro/subway systems\n" +
                  "• Bus networks\n" +
                  "• Tram and light rail\n" +
                  "• Train connections\n\n" +
                  "**🚗 Private Transport:**\n" +
                  "• Taxi and ride-sharing services\n" +
                  "• Car rentals (if needed)\n" +
                  "• Private drivers and tours\n" +
                  "• Airport transfers\n\n" +
                  "**🚶 Walking & Cycling:**\n" +
                  "• Pedestrian-friendly areas\n" +
                  "• Bike rental services\n" +
                  "• Walking tours\n" +
                  "• Scenic routes\n\n" +
                  "**💡 Travel Tips:**\n" +
                  "• Get a travel pass for savings\n" +
                  "• Download transport apps\n" +
                  "• Learn basic transport phrases\n" +
                  "• Keep emergency numbers handy\n\n" +
                  "Would you like me to help you plan the best routes or suggest transport passes?",
        'suggestions': ['Transport passes', 'Best routes', 'Airport transfer', 'Walking tours']
    }

def generate_shopping_suggestion(message, trip_context):
    """Generate shopping suggestions"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'shopping_advice',
        'content': f"Here are **shopping recommendations** for {destination}:\n\n" +
                  "**🛍️ Shopping Districts:**\n" +
                  "• Main shopping streets and malls\n" +
                  "• Local markets and bazaars\n" +
                  "• Artisan and craft shops\n" +
                  "• Designer boutiques\n\n" +
                  "**🎁 Souvenirs & Gifts:**\n" +
                  "• Local handicrafts and art\n" +
                  "• Traditional clothing and textiles\n" +
                  "• Food and beverage specialties\n" +
                  "• Unique local products\n\n" +
                  "**💰 Shopping Tips:**\n" +
                  "• Bargain at markets (where appropriate)\n" +
                  "• Check for authenticity\n" +
                  "• Compare prices at different shops\n" +
                  "• Keep receipts for customs\n\n" +
                  "**🕐 Best Times:**\n" +
                  "• Avoid peak tourist hours\n" +
                  "• Check market opening times\n" +
                  "• Look for sales and discounts\n" +
                  "• Plan shopping around other activities\n\n" +
                  "Would you like me to suggest specific shopping areas or help you find unique souvenirs?",
        'suggestions': ['Shopping areas', 'Local markets', 'Souvenir ideas', 'Shopping tips']
    }

def generate_safety_suggestion(message, trip_context):
    """Generate safety suggestions"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'safety_advice',
        'content': f"Here are **safety tips** for {destination}:\n\n" +
                  "**🛡️ General Safety:**\n" +
                  "• Stay aware of your surroundings\n" +
                  "• Keep valuables secure and hidden\n" +
                  "• Avoid displaying expensive items\n" +
                  "• Trust your instincts\n\n" +
                  "**🚨 Emergency Information:**\n" +
                  "• Local emergency numbers\n" +
                  "• Nearest hospitals and clinics\n" +
                  "• Embassy/consulate locations\n" +
                  "• Police station locations\n\n" +
                  "**💳 Financial Safety:**\n" +
                  "• Use ATMs in well-lit areas\n" +
                  "• Keep cards and cash separate\n" +
                  "• Notify your bank about travel\n" +
                  "• Have backup payment methods\n\n" +
                  "**🏥 Health & Medical:**\n" +
                  "• Check required vaccinations\n" +
                  "• Bring necessary medications\n" +
                  "• Know local health facilities\n" +
                  "• Have travel insurance\n\n" +
                  "**🌍 Cultural Awareness:**\n" +
                  "• Respect local customs and traditions\n" +
                  "• Dress appropriately for the culture\n" +
                  "• Learn basic local phrases\n" +
                  "• Be mindful of cultural sensitivities\n\n" +
                  "Would you like me to provide specific safety information for your destination?",
        'suggestions': ['Emergency contacts', 'Health info', 'Cultural tips', 'Travel insurance']
    }

def generate_smart_suggestions(destination, dates, interests, budget, group_size):
    """Generate smart suggestions based on trip parameters"""
    suggestions = []
    
    # Destination-specific suggestions
    destination_lower = destination.lower()
    
    # Accommodation suggestions
    if budget == 'low':
        suggestions.append({
            'category': 'Accommodation',
            'title': 'Budget-Friendly Stays',
            'description': f'Hostels, guesthouses, and budget hotels in {destination}',
            'priority': 'high',
            'estimated_cost': '$20-50/night',
            'booking_tip': 'Book 2-3 months in advance for best rates'
        })
    elif budget == 'medium':
        suggestions.append({
            'category': 'Accommodation',
            'title': 'Comfortable Hotels',
            'description': f'Mid-range hotels and vacation rentals in {destination}',
            'priority': 'high',
            'estimated_cost': '$80-150/night',
            'booking_tip': 'Look for packages with breakfast included'
        })
    else:
        suggestions.append({
            'category': 'Accommodation',
            'title': 'Luxury Stays',
            'description': f'Premium hotels and boutique accommodations in {destination}',
            'priority': 'high',
            'estimated_cost': '$200+/night',
            'booking_tip': 'Consider loyalty programs for upgrades'
        })
    
    # Destination-specific activities
    if 'paris' in destination_lower:
        suggestions.append({
            'category': 'Must-See',
            'title': 'Eiffel Tower & Louvre',
            'description': 'Iconic landmarks and world-class museums',
            'priority': 'high',
            'estimated_cost': '$30-60/person',
            'booking_tip': 'Book Louvre tickets online to skip the queue'
        })
        suggestions.append({
            'category': 'Food & Dining',
            'title': 'French Cuisine Experience',
            'description': 'Bistros, patisseries, and wine tastings',
            'priority': 'medium',
            'estimated_cost': '$40-100/person',
            'booking_tip': 'Try local bistros away from tourist areas'
        })
        suggestions.append({
            'category': 'Culture',
            'title': 'Notre-Dame & Seine River',
            'description': 'Gothic architecture and romantic river cruises',
            'priority': 'medium',
            'estimated_cost': '$20-50/person',
            'booking_tip': 'Book Seine cruise for sunset views'
        })
        suggestions.append({
            'category': 'Shopping',
            'title': 'Champs-Élysées & Luxury Shopping',
            'description': 'Famous avenue with high-end boutiques and cafes',
            'priority': 'medium',
            'estimated_cost': '$50-200/person',
            'booking_tip': 'Visit early morning to avoid crowds'
        })
    elif 'london' in destination_lower:
        suggestions.append({
            'category': 'Must-See',
            'title': 'Big Ben & Buckingham Palace',
            'description': 'Royal landmarks and historical sites',
            'priority': 'high',
            'estimated_cost': '$25-50/person',
            'booking_tip': 'Watch the Changing of the Guard ceremony'
        })
        suggestions.append({
            'category': 'Culture',
            'title': 'West End Shows',
            'description': 'World-class theater and musical performances',
            'priority': 'medium',
            'estimated_cost': '$60-150/person',
            'booking_tip': 'Book shows in advance for best seats'
        })
        suggestions.append({
            'category': 'History',
            'title': 'Tower of London & Westminster',
            'description': 'Medieval castle and political landmarks',
            'priority': 'high',
            'estimated_cost': '$30-60/person',
            'booking_tip': 'Buy combination tickets for better value'
        })
    elif 'tokyo' in destination_lower:
        suggestions.append({
            'category': 'Must-See',
            'title': 'Senso-ji Temple & Shibuya',
            'description': 'Traditional temples and modern city life',
            'priority': 'high',
            'estimated_cost': '$20-40/person',
            'booking_tip': 'Visit temples early morning for fewer crowds'
        })
        suggestions.append({
            'category': 'Food & Dining',
            'title': 'Sushi & Ramen Experience',
            'description': 'Authentic Japanese cuisine and food markets',
            'priority': 'medium',
            'estimated_cost': '$30-80/person',
            'booking_tip': 'Try conveyor belt sushi for budget-friendly dining'
        })
        suggestions.append({
            'category': 'Technology',
            'title': 'Akihabara & Robot Restaurant',
            'description': 'Electronics district and futuristic entertainment',
            'priority': 'medium',
            'estimated_cost': '$40-100/person',
            'booking_tip': 'Visit Akihabara on weekends for street performances'
        })
    elif 'new york' in destination_lower or 'nyc' in destination_lower:
        suggestions.append({
            'category': 'Must-See',
            'title': 'Times Square & Central Park',
            'description': 'Iconic landmarks and urban green spaces',
            'priority': 'high',
            'estimated_cost': '$0-30/person',
            'booking_tip': 'Visit Times Square at night for the full experience'
        })
        suggestions.append({
            'category': 'Culture',
            'title': 'Broadway Shows',
            'description': 'World-famous theater performances',
            'priority': 'medium',
            'estimated_cost': '$80-200/person',
            'booking_tip': 'Check for same-day rush tickets for discounts'
        })
        suggestions.append({
            'category': 'Art',
            'title': 'Metropolitan Museum & MoMA',
            'description': 'World-class art museums and galleries',
            'priority': 'medium',
            'estimated_cost': '$25-50/person',
            'booking_tip': 'Many museums have pay-what-you-wish days'
        })
    elif 'los angeles' in destination_lower or 'la' in destination_lower:
        suggestions.append({
            'category': 'Entertainment',
            'title': 'Hollywood Walk of Fame',
            'description': 'Celebrity stars and entertainment history',
            'priority': 'high',
            'estimated_cost': '$0-20/person',
            'booking_tip': 'Visit early morning to avoid crowds'
        })
        suggestions.append({
            'category': 'Beach',
            'title': 'Venice Beach & Santa Monica',
            'description': 'Famous beaches and pier attractions',
            'priority': 'medium',
            'estimated_cost': '$10-40/person',
            'booking_tip': 'Rent bikes to explore the beach path'
        })
        suggestions.append({
            'category': 'Culture',
            'title': 'Getty Center & LACMA',
            'description': 'World-class art museums and cultural sites',
            'priority': 'medium',
            'estimated_cost': '$20-50/person',
            'booking_tip': 'Getty Center is free, just pay for parking'
        })
    elif 'rome' in destination_lower:
        suggestions.append({
            'category': 'History',
            'title': 'Colosseum & Roman Forum',
            'description': 'Ancient Roman ruins and gladiator arena',
            'priority': 'high',
            'estimated_cost': '$30-60/person',
            'booking_tip': 'Buy skip-the-line tickets to avoid queues'
        })
        suggestions.append({
            'category': 'Religion',
            'title': 'Vatican City & St. Peter\'s',
            'description': 'Religious sites and Renaissance art',
            'priority': 'high',
            'estimated_cost': '$25-50/person',
            'booking_tip': 'Dress modestly and book Vatican tours in advance'
        })
        suggestions.append({
            'category': 'Food & Dining',
            'title': 'Italian Cuisine Experience',
            'description': 'Authentic pasta, pizza, and gelato',
            'priority': 'medium',
            'estimated_cost': '$30-80/person',
            'booking_tip': 'Try trattorias away from tourist areas'
        })
        suggestions.append({
            'category': 'Culture',
            'title': 'Trevi Fountain & Spanish Steps',
            'description': 'Famous landmarks and romantic spots',
            'priority': 'medium',
            'estimated_cost': '$0-20/person',
            'booking_tip': 'Visit early morning or late evening for fewer crowds'
        })
    elif 'dubai' in destination_lower:
        suggestions.append({
            'category': 'Architecture',
            'title': 'Burj Khalifa & Dubai Mall',
            'description': 'World\'s tallest building and luxury shopping',
            'priority': 'high',
            'estimated_cost': '$50-100/person',
            'booking_tip': 'Book Burj Khalifa tickets online for sunset views'
        })
        suggestions.append({
            'category': 'Desert',
            'title': 'Desert Safari Experience',
            'description': 'Dune bashing, camel rides, and traditional dinner',
            'priority': 'high',
            'estimated_cost': '$80-150/person',
            'booking_tip': 'Book through reputable tour operators'
        })
        suggestions.append({
            'category': 'Luxury',
            'title': 'Palm Jumeirah & Atlantis',
            'description': 'Iconic palm-shaped island and luxury resort',
            'priority': 'medium',
            'estimated_cost': '$100-300/person',
            'booking_tip': 'Visit Atlantis Aquaventure for water activities'
        })
    elif 'mumbai' in destination_lower or 'bombay' in destination_lower:
        suggestions.append({
            'category': 'History',
            'title': 'Gateway of India & Marine Drive',
            'description': 'Iconic landmarks and scenic waterfront',
            'priority': 'high',
            'estimated_cost': '$5-20/person',
            'booking_tip': 'Visit Gateway at sunset for best photos'
        })
        suggestions.append({
            'category': 'Food & Dining',
            'title': 'Street Food & Local Cuisine',
            'description': 'Famous street food and authentic Indian dishes',
            'priority': 'medium',
            'estimated_cost': '$10-40/person',
            'booking_tip': 'Try vada pav, pav bhaji, and local chaat'
        })
        suggestions.append({
            'category': 'Culture',
            'title': 'Elephanta Caves & Museums',
            'description': 'Ancient cave temples and cultural sites',
            'priority': 'medium',
            'estimated_cost': '$15-30/person',
            'booking_tip': 'Take ferry to Elephanta Caves early morning'
        })
    elif 'sydney' in destination_lower:
        suggestions.append({
            'category': 'Landmarks',
            'title': 'Sydney Opera House & Harbour Bridge',
            'description': 'Iconic landmarks and harbor views',
            'priority': 'high',
            'estimated_cost': '$30-80/person',
            'booking_tip': 'Book Opera House tours in advance'
        })
        suggestions.append({
            'category': 'Beach',
            'title': 'Bondi Beach & Coastal Walk',
            'description': 'Famous beach and scenic coastal trail',
            'priority': 'medium',
            'estimated_cost': '$10-40/person',
            'booking_tip': 'Start coastal walk early morning'
        })
        suggestions.append({
            'category': 'Nature',
            'title': 'Blue Mountains & Wildlife',
            'description': 'Scenic mountains and native wildlife',
            'priority': 'medium',
            'estimated_cost': '$50-120/person',
            'booking_tip': 'Book guided tours for best experience'
        })
    else:
        # Generic suggestions for other destinations
        suggestions.append({
            'category': 'Local Experience',
            'title': 'Local Attractions',
            'description': f'Discover the best attractions in {destination}',
            'priority': 'high',
            'estimated_cost': '$20-60/person',
            'booking_tip': 'Research local attractions and book in advance'
        })
        suggestions.append({
            'category': 'Food & Dining',
            'title': 'Local Cuisine',
            'description': f'Taste authentic local dishes in {destination}',
            'priority': 'medium',
            'estimated_cost': '$25-75/person',
            'booking_tip': 'Ask locals for restaurant recommendations'
        })
        suggestions.append({
            'category': 'Culture',
            'title': 'Cultural Sites',
            'description': f'Explore museums and cultural landmarks in {destination}',
            'priority': 'medium',
            'estimated_cost': '$15-50/person',
            'booking_tip': 'Many museums have free admission days'
        })
    
    # Activity suggestions based on interests
    for interest in interests:
        if interest == 'food':
            suggestions.append({
                'category': 'Food & Dining',
                'title': 'Local Cuisine Experience',
                'description': f'Food tours, cooking classes, and local restaurants in {destination}',
                'priority': 'medium',
                'estimated_cost': '$30-80/person',
                'booking_tip': 'Book food tours in advance, especially for groups'
            })
        elif interest == 'culture':
            suggestions.append({
                'category': 'Cultural Activities',
                'title': 'Cultural Immersion',
                'description': f'Museums, historical sites, and cultural tours in {destination}',
                'priority': 'medium',
                'estimated_cost': '$15-40/person',
                'booking_tip': 'Many museums have free days or student discounts'
            })
        elif interest == 'adventure':
            suggestions.append({
                'category': 'Adventure',
                'title': 'Outdoor Adventures',
                'description': f'Hiking, water sports, and adventure activities in {destination}',
                'priority': 'medium',
                'estimated_cost': '$50-120/person',
                'booking_tip': 'Check weather conditions and book guided tours for safety'
            })
    
    # Transportation suggestions
    suggestions.append({
        'category': 'Transportation',
        'title': 'Getting Around',
        'description': f'Public transport, rideshares, and walking tours in {destination}',
        'priority': 'high',
        'estimated_cost': '$5-20/day',
        'booking_tip': 'Consider city passes for unlimited public transport'
    })
    
    return suggestions

def generate_smart_reminders(trip_context):
    """Generate smart reminders based on trip context"""
    reminders = []
    
    destination = trip_context.get('destination', '')
    dates = trip_context.get('dates', {})
    group_size = trip_context.get('group_size', 1)
    
    # Visa and documentation reminders
    if destination and destination.lower() not in ['united states', 'usa', 'canada', 'mexico']:
        reminders.append({
            'type': 'documentation',
            'title': 'Visa Requirements',
            'message': f'Check if you need a visa for {destination}',
            'priority': 'high',
            'due_date': '2-3 months before trip',
            'icon': 'passport'
        })
    
    # Weather reminders
    reminders.append({
        'type': 'weather',
        'title': 'Weather Check',
        'message': 'Check weather forecast and pack accordingly',
        'priority': 'medium',
        'due_date': '1 week before trip',
        'icon': 'cloud-sun'
    })
    
    # Booking reminders
    reminders.append({
        'type': 'booking',
        'title': 'Activity Bookings',
        'message': 'Book popular activities and restaurants in advance',
        'priority': 'medium',
        'due_date': '2-4 weeks before trip',
        'icon': 'calendar-check'
    })
    
    # Financial reminders
    reminders.append({
        'type': 'financial',
        'title': 'Travel Notifications',
        'message': 'Notify your bank and credit card companies about travel',
        'priority': 'high',
        'due_date': '1 week before trip',
        'icon': 'credit-card'
    })
    
    # Health reminders
    reminders.append({
        'type': 'health',
        'title': 'Health Preparations',
        'message': 'Check if vaccinations are required and pack medications',
        'priority': 'high',
        'due_date': '1 month before trip',
        'icon': 'heartbeat'
    })
    
    return reminders

def generate_weather_alerts(latitude, longitude, trip_dates):
    """Generate weather alerts and packing suggestions"""
    alerts = []
    
    # Simulated weather data (in production, use actual weather API)
    weather_conditions = {
        'rain': {
            'alert': 'Rain expected during your trip',
            'suggestion': 'Pack an umbrella and waterproof gear',
            'priority': 'medium'
        },
        'sunny': {
            'alert': 'Sunny weather expected',
            'suggestion': 'Pack sunscreen, hat, and sunglasses',
            'priority': 'low'
        },
        'cold': {
            'alert': 'Cold temperatures expected',
            'suggestion': 'Pack warm clothing and layers',
            'priority': 'medium'
        }
    }
    
    # Generate weather-based alerts
    for condition, info in weather_conditions.items():
        alerts.append({
            'type': 'weather',
            'condition': condition,
            'alert': info['alert'],
            'suggestion': info['suggestion'],
            'priority': info['priority'],
            'icon': 'cloud-rain' if condition == 'rain' else 'sun' if condition == 'sunny' else 'thermometer-half'
        })
    
    # General packing suggestions
    alerts.append({
        'type': 'packing',
        'condition': 'general',
        'alert': 'Packing Reminders',
        'suggestion': 'Don\'t forget: travel documents, chargers, medications, and comfortable shoes',
        'priority': 'high',
        'icon': 'suitcase'
    })
    
    return alerts

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

@ai_recommendations_bp.route('/api/groups/<int:group_id>/weather/place', methods=['GET'])
@jwt_required()
def get_weather_by_place(group_id):
    user_id = int(get_jwt_identity())
    
    # Verify user is part of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        return jsonify({'error': 'You are not a member of this group'}), 403
    
    place_name = request.args.get('place', '')
    
    if not place_name:
        return jsonify({'error': 'Place name is required'}), 400
    
    # For now, return realistic weather data based on place name
    # In production, integrate with OpenWeatherMap Geocoding API
    weather_data = get_weather_for_place(place_name)
    
    return jsonify({
        'weather': weather_data,
        'place': place_name
    })

def get_weather_for_place(place_name):
    """Get weather data for a specific place with more dynamic and realistic data"""
    import random
    from datetime import datetime
    
    place_lower = place_name.lower()
    current_hour = datetime.now().hour
    
    # Base weather data
    weather_data = {
        'temperature': 22,
        'feels_like': 24,
        'description': 'Partly cloudy',
        'humidity': 65,
        'wind_speed': 10,
        'location': place_name
    }
    
    # More dynamic weather based on place and time
    if any(city in place_lower for city in ['paris', 'london', 'rome', 'eiffel', 'france', 'uk', 'italy']):
        # European cities - cooler, more variable
        base_temp = 15 + random.randint(-5, 8)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(-2, 3),
            'description': random.choice(['Light rain', 'Partly cloudy', 'Overcast', 'Drizzle']),
            'humidity': 70 + random.randint(-10, 15),
            'wind_speed': 8 + random.randint(0, 12)
        })
    elif any(city in place_lower for city in ['tokyo', 'seoul', 'beijing', 'japan', 'korea', 'china']):
        # Asian cities - moderate to warm
        base_temp = 20 + random.randint(-3, 10)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(-1, 4),
            'description': random.choice(['Sunny', 'Partly cloudy', 'Light rain', 'Clear']),
            'humidity': 60 + random.randint(-15, 20),
            'wind_speed': 5 + random.randint(0, 8)
        })
    elif any(city in place_lower for city in ['los angeles', 'san francisco', 'miami', 'la', 'california', 'florida']):
        # US West Coast - warm and sunny
        base_temp = 25 + random.randint(-5, 8)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(0, 5),
            'description': random.choice(['Sunny', 'Clear', 'Partly cloudy', 'Warm']),
            'humidity': 50 + random.randint(-10, 15),
            'wind_speed': 3 + random.randint(0, 7)
        })
    elif any(city in place_lower for city in ['new york', 'chicago', 'boston', 'nyc', 'manhattan', 'illinois', 'massachusetts']):
        # US East Coast - variable
        base_temp = 12 + random.randint(-8, 12)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(-3, 2),
            'description': random.choice(['Partly cloudy', 'Overcast', 'Light rain', 'Clear']),
            'humidity': 65 + random.randint(-15, 20),
            'wind_speed': 10 + random.randint(0, 15)
        })
    elif any(city in place_lower for city in ['dubai', 'abu dhabi', 'uae', 'saudi', 'qatar', 'kuwait']):
        # Middle East - hot and dry
        base_temp = 35 + random.randint(-5, 8)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(2, 6),
            'description': random.choice(['Hot and sunny', 'Clear', 'Very hot', 'Sunny']),
            'humidity': 35 + random.randint(-10, 15),
            'wind_speed': 5 + random.randint(0, 10)
        })
    elif any(city in place_lower for city in ['mumbai', 'delhi', 'india', 'bangalore', 'chennai']):
        # Indian cities - hot and humid
        base_temp = 30 + random.randint(-3, 8)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(3, 7),
            'description': random.choice(['Hot and humid', 'Partly cloudy', 'Humid', 'Warm']),
            'humidity': 75 + random.randint(-10, 15),
            'wind_speed': 3 + random.randint(0, 8)
        })
    elif any(city in place_lower for city in ['sydney', 'melbourne', 'australia', 'perth', 'brisbane']):
        # Australian cities - moderate
        base_temp = 18 + random.randint(-5, 8)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(-1, 3),
            'description': random.choice(['Mild and pleasant', 'Partly cloudy', 'Clear', 'Sunny']),
            'humidity': 60 + random.randint(-15, 15),
            'wind_speed': 8 + random.randint(0, 12)
        })
    elif any(city in place_lower for city in ['singapore', 'malaysia', 'thailand', 'bangkok']):
        # Southeast Asia - hot and humid
        base_temp = 28 + random.randint(-2, 5)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(2, 5),
            'description': random.choice(['Hot and humid', 'Partly cloudy', 'Humid', 'Warm']),
            'humidity': 80 + random.randint(-10, 15),
            'wind_speed': 2 + random.randint(0, 6)
        })
    else:
        # Generic for other places - more random variation
        base_temp = 20 + random.randint(-8, 12)
        weather_data.update({
            'temperature': base_temp,
            'feels_like': base_temp + random.randint(-2, 4),
            'description': random.choice(['Partly cloudy', 'Clear', 'Sunny', 'Overcast', 'Light rain']),
            'humidity': 60 + random.randint(-20, 25),
            'wind_speed': 5 + random.randint(0, 10)
        })
    
    # Add time-based variations
    if 6 <= current_hour <= 10:  # Morning
        weather_data['description'] = 'Morning ' + weather_data['description'].lower()
    elif 18 <= current_hour <= 22:  # Evening
        weather_data['description'] = 'Evening ' + weather_data['description'].lower()
    
    return weather_data 