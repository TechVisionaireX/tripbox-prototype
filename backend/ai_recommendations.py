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

# Add conversation memory and advanced features at the top of the file
conversation_history = {}
user_preferences = {}
conversation_context = {}

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
    """Generate sophisticated AI response with advanced conversation capabilities"""
    message_lower = user_message.lower()
    
    # Initialize conversation history if not exists
    if conversation_id and conversation_id not in conversation_history:
        conversation_history[conversation_id] = []
        user_preferences[conversation_id] = {}
        conversation_context[conversation_id] = {
            'current_topic': None,
            'last_question': None,
            'user_style': 'casual',
            'interaction_count': 0
        }
    
    # Update conversation context
    if conversation_id:
        conversation_context[conversation_id]['interaction_count'] += 1
        conversation_history[conversation_id].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
    
    # Extract destination and context
    destination = extract_destination_from_message(user_message, trip_context)
    user_intent = analyze_user_intent(user_message)
    user_style = detect_user_style(user_message)
    
    # Update user preferences
    if conversation_id:
        user_preferences[conversation_id].update({
            'style': user_style,
            'last_destination': destination,
            'preferred_topics': user_preferences[conversation_id].get('preferred_topics', [])
        })
        conversation_context[conversation_id]['user_style'] = user_style
    
    # Generate sophisticated response based on intent and context
    response = generate_sophisticated_response(user_message, user_intent, destination, trip_context, conversation_id)
    
    # Save response to conversation history
    if conversation_id:
        conversation_history[conversation_id].append({
            'role': 'assistant',
            'content': response['content'],
            'timestamp': datetime.now().isoformat()
        })
    
    return response

def extract_destination_from_message(message, trip_context):
    """Extract destination from message or trip context"""
    message_lower = message.lower()
    destination = trip_context.get('destination', '')
    
    if not destination:
        # Common destinations to look for
        destinations = [
            'paris', 'london', 'tokyo', 'new york', 'los angeles', 'rome', 'dubai', 
            'mumbai', 'sydney', 'singapore', 'bangkok', 'seoul', 'beijing', 'amsterdam',
            'berlin', 'madrid', 'barcelona', 'venice', 'florence', 'prague', 'vienna',
            'budapest', 'athens', 'istanbul', 'cairo', 'marrakech', 'cape town',
            'rio de janeiro', 'buenos aires', 'mexico city', 'toronto', 'vancouver'
        ]
        
        for dest in destinations:
            if dest in message_lower:
                destination = dest.title()
                break
    
    return destination

def analyze_user_intent(message):
    """Analyze user intent from message"""
    message_lower = message.lower()
    
    intents = {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'sup', 'yo'],
        'farewell': ['bye', 'goodbye', 'see you', 'end', 'stop', 'quit'],
        'thanks': ['thank', 'thanks', 'appreciate', 'grateful'],
        'help': ['help', 'what can you do', 'capabilities', 'assist', 'support'],
        'weather': ['weather', 'forecast', 'temperature', 'rain', 'sunny', 'hot', 'cold', 'climate', 'packing'],
        'budget': ['budget', 'cost', 'money', 'expensive', 'cheap', 'price', 'save', 'spend', 'dollar', 'euro', 'currency', 'affordable'],
        'food': ['food', 'restaurant', 'eat', 'dining', 'cuisine', 'meal', 'dish', 'local', 'hungry', 'lunch', 'dinner', 'breakfast', 'cafe'],
        'activity': ['activity', 'things to do', 'attraction', 'visit', 'see', 'tour', 'place', 'sight', 'fun', 'entertainment', 'adventure', 'explore'],
        'planning': ['plan', 'itinerary', 'schedule', 'day', 'trip', 'organize', 'arrange', 'prepare'],
        'accommodation': ['hotel', 'accommodation', 'stay', 'sleep', 'room', 'booking', 'lodging', 'hostel'],
        'transport': ['transport', 'transportation', 'travel', 'bus', 'train', 'metro', 'subway', 'taxi', 'car', 'walking'],
        'shopping': ['shopping', 'buy', 'shop', 'market', 'mall', 'store', 'souvenir', 'gift'],
        'safety': ['safety', 'safe', 'danger', 'crime', 'security', 'emergency', 'health'],
        'general_question': ['what', 'how', 'when', 'where', 'why', 'which', 'tell me', 'explain', 'describe'],
        'clarification': ['what do you mean', 'i don\'t understand', 'can you explain', 'clarify'],
        'follow_up': ['and', 'also', 'what about', 'how about', 'what else', 'more']
    }
    
    for intent, keywords in intents.items():
        if any(keyword in message_lower for keyword in keywords):
            return intent
    
    return 'general_question'

def detect_user_style(message):
    """Detect user's communication style"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['please', 'could you', 'would you', 'thank you']):
        return 'polite'
    elif any(word in message_lower for word in ['yo', 'sup', 'hey', 'cool', 'awesome']):
        return 'casual'
    elif any(word in message_lower for word in ['urgent', 'asap', 'quick', 'fast']):
        return 'direct'
    elif len(message.split()) > 20:
        return 'detailed'
    else:
        return 'casual'

def generate_sophisticated_response(message, intent, destination, trip_context, conversation_id):
    """Generate sophisticated response based on intent and context"""
    
    # Get conversation context
    context = conversation_context.get(conversation_id, {})
    preferences = user_preferences.get(conversation_id, {})
    
    # Handle different intents with sophisticated responses
    if intent == 'greeting':
        return generate_sophisticated_greeting(context, preferences, destination)
    elif intent == 'farewell':
        return generate_sophisticated_farewell(context, preferences)
    elif intent == 'thanks':
        return generate_sophisticated_thanks(context, preferences)
    elif intent == 'help':
        return generate_sophisticated_help(context, preferences)
    elif intent == 'weather':
        return generate_sophisticated_weather(message, destination, trip_context)
    elif intent == 'budget':
        return generate_sophisticated_budget(message, destination, trip_context)
    elif intent == 'food':
        return generate_sophisticated_food(message, destination, trip_context)
    elif intent == 'activity':
        return generate_sophisticated_activity(message, destination, trip_context)
    elif intent == 'planning':
        return generate_sophisticated_planning(message, destination, trip_context)
    elif intent == 'accommodation':
        return generate_sophisticated_accommodation(message, destination, trip_context)
    elif intent == 'transport':
        return generate_sophisticated_transport(message, destination, trip_context)
    elif intent == 'shopping':
        return generate_sophisticated_shopping(message, destination, trip_context)
    elif intent == 'safety':
        return generate_sophisticated_safety(message, destination, trip_context)
    elif intent == 'clarification':
        return generate_sophisticated_clarification(message, context)
    elif intent == 'follow_up':
        return generate_sophisticated_follow_up(message, context, destination)
    else:
        return generate_sophisticated_general(message, context, destination)

def generate_sophisticated_greeting(context, preferences, destination):
    """Generate sophisticated greeting response"""
    import random
    
    interaction_count = context.get('interaction_count', 0)
    user_style = context.get('user_style', 'casual')
    
    if interaction_count == 1:
        # First interaction
        greetings = [
            f"Hey there! 👋 I'm your AI travel companion, and I'm excited to help you plan an amazing trip! Whether you're heading to {destination or 'your destination'} or still figuring out where to go, I've got you covered.",
            f"Hello! 🌟 Welcome to your personal travel assistant! I'm here to make your trip planning smooth and enjoyable. {destination and f'Planning for {destination}?' or 'Where are you thinking of traveling?'}",
            f"Hi! ✨ I'm your travel buddy, ready to help you create unforgettable experiences! {destination and f'So {destination} is on your radar?' or 'What destination is calling your name?'}"
        ]
    else:
        # Returning user
        greetings = [
            f"Welcome back! 🎉 Great to see you again! How can I continue helping with your travel plans?",
            f"Hey! 👋 You're back! I'm ready to pick up where we left off. What's on your mind today?",
            f"Hello again! 🌟 I'm here to help you further with your travel adventure. What would you like to work on?"
        ]
    
    greeting = random.choice(greetings)
    
    # Add personalized touch based on user style
    if user_style == 'polite':
        greeting += "\n\nI'm here to assist you with any travel-related questions or planning needs you might have."
    elif user_style == 'direct':
        greeting += "\n\nWhat do you need help with?"
    else:
        greeting += "\n\nI can help with weather, activities, planning, budget, food, accommodation, transport, shopping, and safety tips!"
    
    return {
        'type': 'greeting',
        'content': greeting,
        'suggestions': ['Check weather', 'Plan activities', 'Budget advice', 'Find restaurants', 'Safety tips', 'Help me plan']
    }

def generate_sophisticated_farewell(context, preferences):
    """Generate sophisticated farewell response"""
    import random
    
    user_style = context.get('user_style', 'casual')
    
    farewells = [
        "Safe travels! ✈️ Have an incredible adventure and don't hesitate to come back if you need more help!",
        "Bon voyage! 🌍 Enjoy every moment of your journey and feel free to return anytime for travel assistance!",
        "Take care! 🛡️ Have a wonderful trip and I'll be here when you need travel help again!",
        "Happy travels! 🎒 Enjoy your adventure and remember, I'm always here for travel support!"
    ]
    
    farewell = random.choice(farewells)
    
    if user_style == 'polite':
        farewell += "\n\nThank you for using our travel assistant!"
    elif user_style == 'direct':
        farewell += "\n\nSee you later!"
    
    return {
        'type': 'farewell',
        'content': farewell,
        'suggestions': []
    }

def generate_sophisticated_thanks(context, preferences):
    """Generate sophisticated thanks response"""
    import random
    
    user_style = context.get('user_style', 'casual')
    
    thanks_responses = [
        "You're very welcome! 😊 I'm here to make your trip planning as smooth and enjoyable as possible.",
        "My pleasure! 🌟 Feel free to ask me anything else about your travels - I love helping with travel planning!",
        "Happy to help! ✨ Is there anything else you'd like to know about your trip?",
        "You're welcome! 🎉 I'm always here when you need travel assistance - that's what I'm here for!"
    ]
    
    response = random.choice(thanks_responses)
    
    if user_style == 'polite':
        response += "\n\nIt's truly my pleasure to assist you with your travel needs."
    elif user_style == 'direct':
        response += "\n\nWhat else can I help with?"
    
    return {
        'type': 'thanks',
        'content': response,
        'suggestions': ['More help', 'Weather check', 'Activity ideas', 'Budget tips', 'Continue planning']
    }

def generate_sophisticated_help(context, preferences):
    """Generate sophisticated help response"""
    
    return {
        'type': 'help',
        'content': "I'm your **AI travel companion**! Here's what I can help you with:\n\n" +
                  "**🌤️ Weather & Packing**\n" +
                  "• Real-time weather for any destination\n" +
                  "• Smart packing suggestions based on weather\n" +
                  "• Seasonal clothing recommendations\n" +
                  "• Weather alerts and forecasts\n\n" +
                  "**🎯 Activities & Attractions**\n" +
                  "• Popular tourist attractions and hidden gems\n" +
                  "• Local activities and unique experiences\n" +
                  "• Cultural events and festivals\n" +
                  "• Adventure and outdoor activities\n\n" +
                  "**💰 Budget & Planning**\n" +
                  "• Detailed cost estimates and budget breakdowns\n" +
                  "• Money-saving strategies and tips\n" +
                  "• Currency and payment advice\n" +
                  "• Cost comparison for different options\n\n" +
                  "**🍽️ Food & Dining**\n" +
                  "• Local cuisine recommendations\n" +
                  "• Restaurant suggestions and reviews\n" +
                  "• Food safety and dietary tips\n" +
                  "• Culinary experiences and food tours\n\n" +
                  "**🏨 Accommodation & Transport**\n" +
                  "• Hotel and lodging recommendations\n" +
                  "• Transportation advice and routes\n" +
                  "• Booking tips and strategies\n" +
                  "• Location and safety considerations\n\n" +
                  "**🛡️ Safety & Tips**\n" +
                  "• Travel safety advice and precautions\n" +
                  "• Local customs and cultural etiquette\n" +
                  "• Emergency information and contacts\n" +
                  "• Health and medical considerations\n\n" +
                  "**🎨 Smart Features**\n" +
                  "• Personalized recommendations based on your preferences\n" +
                  "• Context-aware responses that remember our conversation\n" +
                  "• Interactive suggestions and quick actions\n" +
                  "• Comprehensive travel planning assistance\n\n" +
                  "Just ask me anything about your trip - I'm here to make your travel planning amazing! ✨",
        'suggestions': ['Weather check', 'Plan activities', 'Budget advice', 'Find restaurants', 'Safety tips', 'Help me plan']
    }

def generate_sophisticated_weather(message, destination, trip_context):
    """Generate sophisticated weather response"""
    import random
    
    if not destination:
        destination = "your destination"
    
    # Get dynamic weather data
    weather_data = get_weather_for_place(destination) if destination != "your destination" else {
        'temperature': 22,
        'feels_like': 24,
        'description': 'Partly cloudy',
        'humidity': 65,
        'wind_speed': 10,
        'location': destination
    }
    
    # Create sophisticated weather response
    weather_emoji = {
        'sunny': '☀️',
        'partly cloudy': '⛅',
        'cloudy': '☁️',
        'rain': '🌧️',
        'snow': '❄️',
        'storm': '⛈️'
    }
    
    condition_emoji = weather_emoji.get(weather_data['description'].lower(), '🌤️')
    
    response = f"Here's the **current weather** for **{destination}**:\n\n" + \
              f"{condition_emoji} **Conditions**: {weather_data['description']}\n" + \
              f"🌡️ **Temperature**: {weather_data['temperature']}°C ({weather_data['temperature']*9/5+32:.0f}°F)\n" + \
              f"🌤️ **Feels like**: {weather_data['feels_like']}°C\n" + \
              f"💧 **Humidity**: {weather_data['humidity']}%\n" + \
              f"💨 **Wind**: {weather_data['wind_speed']} km/h\n\n"
    
    # Add packing suggestions based on weather
    packing_tips = generate_packing_suggestions(weather_data)
    response += f"**🧳 Smart Packing Suggestions:**\n{packing_tips}\n\n"
    
    # Add activity suggestions based on weather
    activity_tips = generate_weather_based_activities(weather_data)
    response += f"**🎯 Weather-Appropriate Activities:**\n{activity_tips}\n\n"
    
    response += "Would you like me to get the detailed 7-day forecast or help you plan activities based on this weather?"
    
    return {
        'type': 'weather_info',
        'content': response,
        'suggestions': ['7-day forecast', 'Packing list', 'Weather alerts', 'Plan activities', 'Check other destinations']
    }

def generate_packing_suggestions(weather_data):
    """Generate smart packing suggestions based on weather"""
    temp = weather_data['temperature']
    conditions = weather_data['description'].lower()
    
    suggestions = []
    
    if temp < 10:
        suggestions.extend(["• Warm jacket or coat", "• Thermal layers", "• Gloves and scarf", "• Waterproof boots"])
    elif temp < 20:
        suggestions.extend(["• Light jacket or sweater", "• Long-sleeve shirts", "• Comfortable pants", "• Closed-toe shoes"])
    else:
        suggestions.extend(["• Light, breathable clothing", "• Shorts and t-shirts", "• Comfortable walking shoes", "• Sun protection"])
    
    if 'rain' in conditions:
        suggestions.extend(["• Waterproof jacket or umbrella", "• Water-resistant shoes", "• Quick-dry clothing"])
    elif 'sunny' in conditions:
        suggestions.extend(["• Sunscreen and hat", "• Sunglasses", "• Light, airy clothing"])
    
    suggestions.extend(["• Comfortable walking shoes", "• Day bag or backpack", "• Camera or phone for photos"])
    
    return "\n".join(suggestions)

def generate_weather_based_activities(weather_data):
    """Generate activity suggestions based on weather"""
    temp = weather_data['temperature']
    conditions = weather_data['description'].lower()
    
    if temp < 10 or 'rain' in conditions:
        return "• Indoor museums and galleries\n• Cozy cafes and restaurants\n• Shopping centers and markets\n• Cultural indoor activities"
    elif temp > 25 and 'sunny' in conditions:
        return "• Outdoor parks and gardens\n• Beach activities (if applicable)\n• Outdoor dining and picnics\n• Walking tours and sightseeing"
    else:
        return "• Mix of indoor and outdoor activities\n• Walking tours and sightseeing\n• Local cafes and restaurants\n• Cultural experiences"

def generate_sophisticated_budget(message, destination, trip_context):
    """Generate sophisticated budget response"""
    
    if not destination:
        destination = "your destination"
    
    response = f"Here's my **comprehensive budget advice** for {destination}:\n\n" + \
              "**💰 Budget Categories Breakdown:**\n\n" + \
              "**🏨 Accommodation (30-40% of budget):**\n" + \
              "• Budget: $20-60/night (hostels, guesthouses)\n" + \
              "• Mid-range: $80-150/night (hotels, apartments)\n" + \
              "• Luxury: $200+/night (premium hotels)\n\n" + \
              "**🍽️ Food & Dining (20-30% of budget):**\n" + \
              "• Budget: $10-25/day (street food, markets)\n" + \
              "• Mid-range: $30-60/day (restaurants, cafes)\n" + \
              "• Luxury: $80+/day (fine dining)\n\n" + \
              "**🚇 Transportation (10-20% of budget):**\n" + \
              "• Public transport: $5-15/day\n" + \
              "• Taxis/rideshares: $20-50/day\n" + \
              "• Walking: Free!\n\n" + \
              "**🎯 Activities & Entertainment (15-25% of budget):**\n" + \
              "• Free activities: Parks, walking tours, museums (free days)\n" + \
              "• Paid activities: $20-100/day\n" + \
              "• Tours and experiences: $50-200\n\n" + \
              "**💡 Smart Money-Saving Tips:**\n" + \
              "• Book accommodation in advance for better rates\n" + \
              "• Use public transportation instead of taxis\n" + \
              "• Eat at local markets and street food stalls\n" + \
              "• Look for free walking tours and activities\n" + \
              "• Consider city passes for multiple attractions\n" + \
              "• Travel during shoulder seasons for better prices\n\n" + \
              "Would you like me to create a detailed budget breakdown for your specific trip duration and group size?"
    
    return {
        'type': 'budget_advice',
        'content': response,
        'suggestions': ['Create budget', 'Find deals', 'Cost estimates', 'Money tips', 'Budget calculator']
    }

def generate_sophisticated_food(message, destination, trip_context):
    """Generate sophisticated food response with specific restaurant names"""
    
    if not destination:
        destination = "your destination"
    
    # Real restaurant recommendations by destination
    restaurant_recommendations = {
        'London': {
            'fine_dining': [
                'The Ritz London - Classic British luxury dining',
                'Sketch - Michelin-starred modern British cuisine',
                'The Ivy - Iconic British restaurant',
                'Hawksmoor - Premium steakhouse',
                'Dishoom - Modern Indian cuisine'
            ],
            'casual': [
                'Borough Market - Famous food market',
                'Camden Market - Street food paradise',
                'Dishoom - Popular Indian restaurant',
                'Franco Manca - Artisan pizza',
                'Honest Burgers - Quality burgers'
            ],
            'local_favorites': [
                'The Clove Club - Modern British fine dining',
                'Gymkhana - Colonial Indian cuisine',
                'The Ledbury - Two Michelin stars',
                'Barrafina - Spanish tapas',
                'Hoppers - Sri Lankan street food'
            ]
        },
        'Paris': {
            'fine_dining': [
                'Le Jules Verne - Eiffel Tower restaurant',
                'L\'Astrance - Three Michelin stars',
                'Le Comptoir du Relais - Bistro excellence',
                'Septime - Modern French cuisine',
                'L\'Arpège - Three Michelin stars'
            ],
            'casual': [
                'L\'As du Fallafel - Famous falafel',
                'Breizh Café - Authentic crêpes',
                'Du Pain et des Idées - Artisan bakery',
                'Le Chateaubriand - Modern bistro',
                'Frenchie - Contemporary French'
            ],
            'local_favorites': [
                'Le Petit Prince - Traditional bistro',
                'Chez L\'Ami Louis - Classic French',
                'L\'Ami Louis - Historic bistro',
                'Le Comptoir du Relais - Popular spot',
                'Frenchie - Modern French cuisine'
            ]
        },
        'Tokyo': {
            'fine_dining': [
                'Sukiyabashi Jiro - Legendary sushi',
                'Narisawa - Modern Japanese cuisine',
                'Sukiyabashi Jiro Honten - Master sushi',
                'Kozasa - Traditional kaiseki',
                'Sukiyabashi Jiro - World-famous sushi'
            ],
            'casual': [
                'Ichiran Ramen - Famous ramen chain',
                'Tsukiji Outer Market - Fresh seafood',
                'Sukiyabashi Jiro - Sushi excellence',
                'Ichiran - Popular ramen',
                'Tsukiji Market - Fresh fish'
            ],
            'local_favorites': [
                'Sukiyabashi Jiro - Master sushi chef',
                'Ichiran Ramen - Tonkotsu ramen',
                'Tsukiji Outer Market - Fresh sushi',
                'Sukiyabashi Jiro - Omakase experience',
                'Ichiran - Famous ramen'
            ]
        },
        'New York': {
            'fine_dining': [
                'Le Bernardin - Four-star seafood',
                'Eleven Madison Park - Three Michelin stars',
                'Per Se - Thomas Keller\'s restaurant',
                'Daniel - French fine dining',
                'Gramercy Tavern - Danny Meyer\'s restaurant'
            ],
            'casual': [
                'Katz\'s Delicatessen - Famous pastrami',
                'Joe\'s Pizza - Classic NYC pizza',
                'Russ & Daughters - Jewish deli',
                'Shake Shack - Modern burger chain',
                'Magnolia Bakery - Famous cupcakes'
            ],
            'local_favorites': [
                'Katz\'s Delicatessen - Pastrami sandwich',
                'Joe\'s Pizza - NYC pizza',
                'Russ & Daughters - Bagels and lox',
                'Shake Shack - Quality burgers',
                'Magnolia Bakery - Cupcakes'
            ]
        },
        'Rome': {
            'fine_dining': [
                'La Pergola - Three Michelin stars',
                'Imàgo - Rooftop dining',
                'Aroma - Michelin-starred',
                'La Pergola - Fine dining',
                'Imàgo - Luxury dining'
            ],
            'casual': [
                'Roscioli - Famous deli and restaurant',
                'Pizzarium - Gourmet pizza by the slice',
                'Trapizzino - Roman street food',
                'Supplizio - Traditional supplì',
                'Bonci Pizzarium - Artisan pizza'
            ],
            'local_favorites': [
                'Roscioli - Traditional Roman',
                'Pizzarium - Pizza al taglio',
                'Trapizzino - Roman street food',
                'Supplizio - Roman supplì',
                'Bonci Pizzarium - Pizza'
            ]
        },
        'Dubai': {
            'fine_dining': [
                'At.mosphere - Burj Khalifa restaurant',
                'Zuma - Japanese izakaya',
                'Nobu - Japanese-Peruvian fusion',
                'Pierchic - Overwater dining',
                'Al Mahara - Underwater restaurant'
            ],
            'casual': [
                'Ravi Restaurant - Pakistani cuisine',
                'Al Ustad Special Kabab - Persian kebabs',
                'Al Mallah - Lebanese street food',
                'Al Reef Lebanese Bakery - Fresh bread',
                'Al Qasr - Traditional Emirati'
            ],
            'local_favorites': [
                'Ravi Restaurant - Pakistani food',
                'Al Ustad Special Kabab - Persian',
                'Al Mallah - Lebanese',
                'Al Reef Lebanese Bakery - Bread',
                'Al Qasr - Emirati cuisine'
            ]
        }
    }
    
    # Get specific recommendations for the destination
    dest_key = destination.lower()
    recommendations = restaurant_recommendations.get(dest_key, {})
    
    if recommendations:
        response = f"Here are **specific restaurant recommendations** for {destination}:\n\n"
        
        if 'fine_dining' in recommendations:
            response += "**🍽️ Fine Dining & Upscale:**\n"
            for restaurant in recommendations['fine_dining'][:3]:
                response += f"• {restaurant}\n"
            response += "\n"
        
        if 'casual' in recommendations:
            response += "**🍕 Casual & Popular:**\n"
            for restaurant in recommendations['casual'][:3]:
                response += f"• {restaurant}\n"
            response += "\n"
        
        if 'local_favorites' in recommendations:
            response += "**🏪 Local Favorites:**\n"
            for restaurant in recommendations['local_favorites'][:3]:
                response += f"• {restaurant}\n"
            response += "\n"
        
        response += "**💡 Pro Tips:**\n"
        response += "• Book fine dining restaurants 2-3 months in advance\n"
        response += "• Visit markets for authentic local food\n"
        response += "• Try street food for budget-friendly options\n"
        response += "• Ask locals for hidden gems\n\n"
        
        response += "Would you like me to suggest specific dishes to try or help you make reservations?"
        
    else:
        # Generic response for other destinations
        response = f"Here are **food recommendations** for {destination}:\n\n" + \
                  "**🍽️ Local Cuisine to Try:**\n" + \
                  "• Traditional local dishes\n" + \
                  "• Street food specialties\n" + \
                  "• Regional specialties\n" + \
                  "• Seasonal ingredients\n\n" + \
                  "**🏪 Best Places to Eat:**\n" + \
                  "• Local markets and food stalls\n" + \
                  "• Family-run restaurants\n" + \
                  "• Popular local spots\n" + \
                  "• Hidden gems off the tourist path\n\n" + \
                  "**💡 Food Tips:**\n" + \
                  "• Try the daily specials\n" + \
                  "• Ask locals for recommendations\n" + \
                  "• Be adventurous with new flavors\n" + \
                  "• Check food safety and hygiene\n\n" + \
                  "Would you like me to suggest specific restaurants or help you plan a food tour?"
    
    return {
        'type': 'food_recommendations',
        'content': response,
        'suggestions': ['Restaurant list', 'Food tour', 'Local dishes', 'Dietary needs', 'Cooking classes']
    }

def generate_sophisticated_activity(message, destination, trip_context):
    """Generate sophisticated activity response with specific places"""
    
    if not destination:
        destination = "your destination"
    
    # Real attraction recommendations by destination
    attraction_recommendations = {
        'London': {
            'landmarks': [
                'Big Ben and Houses of Parliament',
                'Tower of London - Historic castle',
                'Buckingham Palace - Royal residence',
                'London Eye - Giant observation wheel',
                'Tower Bridge - Iconic bridge'
            ],
            'museums': [
                'British Museum - World-famous artifacts',
                'Natural History Museum - Dinosaur exhibits',
                'Tate Modern - Contemporary art',
                'Victoria and Albert Museum - Art and design',
                'Science Museum - Interactive exhibits'
            ],
            'parks': [
                'Hyde Park - Large royal park',
                'Regent\'s Park - Beautiful gardens',
                'Greenwich Park - Royal Observatory',
                'Kew Gardens - Botanical gardens',
                'St James\'s Park - Royal park'
            ],
            'shopping': [
                'Oxford Street - Major shopping street',
                'Carnaby Street - Fashion district',
                'Covent Garden - Market and entertainment',
                'Camden Market - Alternative shopping',
                'Portobello Road - Antiques market'
            ]
        },
        'Paris': {
            'landmarks': [
                'Eiffel Tower - Iconic iron tower',
                'Arc de Triomphe - Historic monument',
                'Notre-Dame Cathedral - Gothic church',
                'Sacré-Cœur - White basilica',
                'Palace of Versailles - Royal palace'
            ],
            'museums': [
                'Louvre Museum - World\'s largest art museum',
                'Musée d\'Orsay - Impressionist art',
                'Centre Pompidou - Modern art',
                'Musée Rodin - Sculpture garden',
                'Musée de l\'Orangerie - Water lilies'
            ],
            'parks': [
                'Luxembourg Gardens - Beautiful park',
                'Tuileries Garden - Formal gardens',
                'Parc des Buttes-Chaumont - Romantic park',
                'Bois de Vincennes - Large forest',
                'Parc Monceau - Elegant park'
            ],
            'shopping': [
                'Champs-Élysées - Famous avenue',
                'Le Marais - Trendy district',
                'Rue du Commerce - Local shopping',
                'Galeries Lafayette - Department store',
                'Rue de Rivoli - Shopping street'
            ]
        },
        'Tokyo': {
            'landmarks': [
                'Tokyo Skytree - Tallest tower',
                'Tokyo Tower - Iconic red tower',
                'Senso-ji Temple - Ancient temple',
                'Meiji Shrine - Shinto shrine',
                'Imperial Palace - Emperor\'s residence'
            ],
            'museums': [
                'Tokyo National Museum - Japanese art',
                'Mori Art Museum - Contemporary art',
                'Ghibli Museum - Animation museum',
                'Edo-Tokyo Museum - History museum',
                'National Museum of Western Art'
            ],
            'parks': [
                'Ueno Park - Cherry blossoms',
                'Yoyogi Park - Popular park',
                'Shinjuku Gyoen - Beautiful garden',
                'Hamarikyu Gardens - Traditional garden',
                'Rikugien Garden - Stroll garden'
            ],
            'shopping': [
                'Shibuya Crossing - Famous intersection',
                'Harajuku - Youth fashion district',
                'Ginza - Luxury shopping',
                'Akihabara - Electronics district',
                'Asakusa - Traditional district'
            ]
        },
        'New York': {
            'landmarks': [
                'Statue of Liberty - Iconic monument',
                'Empire State Building - Famous skyscraper',
                'Times Square - Bright lights',
                'Brooklyn Bridge - Historic bridge',
                'Central Park - Urban oasis'
            ],
            'museums': [
                'Metropolitan Museum of Art - World-class art',
                'Museum of Modern Art (MoMA) - Modern art',
                'American Museum of Natural History - Dinosaurs',
                'Guggenheim Museum - Modern architecture',
                'Whitney Museum - American art'
            ],
            'parks': [
                'Central Park - 843-acre park',
                'High Line - Elevated park',
                'Bryant Park - Midtown oasis',
                'Prospect Park - Brooklyn\'s park',
                'Washington Square Park - Greenwich Village'
            ],
            'shopping': [
                'Fifth Avenue - Luxury shopping',
                'SoHo - Fashion district',
                'Brooklyn Flea - Vintage market',
                'Chelsea Market - Food and shopping',
                'Williamsburg - Hipster district'
            ]
        },
        'Rome': {
            'landmarks': [
                'Colosseum - Ancient amphitheater',
                'Vatican City - Smallest country',
                'Trevi Fountain - Baroque fountain',
                'Pantheon - Ancient temple',
                'Roman Forum - Ancient ruins'
            ],
            'museums': [
                'Vatican Museums - Art collection',
                'Capitoline Museums - Ancient art',
                'Galleria Borghese - Art gallery',
                'MAXXI - Modern art',
                'Palazzo Barberini - Baroque art'
            ],
            'parks': [
                'Villa Borghese - Large park',
                'Villa Doria Pamphili - Public park',
                'Gianicolo Hill - Panoramic views',
                'Villa Ada - Natural park',
                'Pincian Hill - Historic park'
            ],
            'shopping': [
                'Via del Corso - Main shopping street',
                'Via Condotti - Luxury shopping',
                'Campo de\' Fiori - Market square',
                'Trastevere - Bohemian district',
                'Via del Governo Vecchio - Vintage shops'
            ]
        }
    }
    
    # Get specific recommendations for the destination
    dest_key = destination.lower()
    recommendations = attraction_recommendations.get(dest_key, {})
    
    if recommendations:
        response = f"Here are **specific attractions and activities** in {destination}:\n\n"
        
        if 'landmarks' in recommendations:
            response += "**🏛️ Iconic Landmarks:**\n"
            for landmark in recommendations['landmarks'][:4]:
                response += f"• {landmark}\n"
            response += "\n"
        
        if 'museums' in recommendations:
            response += "**🏛️ World-Class Museums:**\n"
            for museum in recommendations['museums'][:4]:
                response += f"• {museum}\n"
            response += "\n"
        
        if 'parks' in recommendations:
            response += "**🌳 Beautiful Parks & Gardens:**\n"
            for park in recommendations['parks'][:4]:
                response += f"• {park}\n"
            response += "\n"
        
        if 'shopping' in recommendations:
            response += "**🛍️ Shopping & Entertainment:**\n"
            for shopping in recommendations['shopping'][:4]:
                response += f"• {shopping}\n"
            response += "\n"
        
        response += "**💡 Insider Tips:**\n"
        response += "• Book popular attractions online to skip queues\n"
        response += "• Visit museums on free days or discounted hours\n"
        response += "• Take advantage of city passes for multiple attractions\n"
        response += "• Ask locals for hidden gems and off-the-beaten-path spots\n\n"
        
        response += "Would you like me to create a detailed itinerary or suggest specific activities based on your interests?"
        
    else:
        # Generic response for other destinations
        response = f"Here are **amazing activities** to experience in {destination}:\n\n" + \
                  "**🏛️ Cultural & Historical Experiences:**\n" + \
                  "• Visit iconic landmarks and architectural marvels\n" + \
                  "• Explore world-class museums and art galleries\n" + \
                  "• Take guided historical tours with local experts\n" + \
                  "• Attend cultural events, festivals, and performances\n\n" + \
                  "**🌳 Outdoor & Nature Adventures:**\n" + \
                  "• Explore beautiful parks, gardens, and green spaces\n" + \
                  "• Hike scenic trails and nature paths\n" + \
                  "• Take boat tours and water-based activities\n" + \
                  "• Visit scenic viewpoints and perfect photo spots\n\n" + \
                  "Would you like me to create a detailed itinerary or suggest specific activities based on your interests?"
    
    return {
        'type': 'activity_recommendations',
        'content': response,
        'suggestions': ['Create itinerary', 'Popular attractions', 'Hidden gems', 'Adventure activities', 'Cultural experiences']
    }

def generate_sophisticated_planning(message, destination, trip_context):
    """Generate sophisticated planning response"""
    
    if not destination:
        destination = "your destination"
    
    response = f"Here's a **comprehensive travel plan** for {destination}:\n\n" + \
              "**📅 Day 1: Arrival & Orientation**\n" + \
              "• Check into your accommodation and settle in\n" + \
              "• Explore the local neighborhood on foot\n" + \
              "• Try local cuisine for dinner\n" + \
              "• Get familiar with public transportation\n" + \
              "• Pick up a local map and tourist information\n\n" + \
              "**📅 Day 2: Cultural Exploration**\n" + \
              "• Visit main attractions and iconic landmarks\n" + \
              "• Take guided historical and cultural tours\n" + \
              "• Experience local culture and traditions\n" + \
              "• Enjoy evening entertainment and shows\n\n" + \
              "**📅 Day 3: Adventure & Activities**\n" + \
              "• Outdoor activities and adventure experiences\n" + \
              "• Shopping and souvenir hunting\n" + \
              "• Local markets and street food exploration\n" + \
              "• Nightlife and evening activities\n\n" + \
              "**📅 Day 4: Hidden Gems & Local Life**\n" + \
              "• Explore off-the-beaten-path locations\n" + \
              "• Visit local neighborhoods and communities\n" + \
              "• Unique experiences and local interactions\n" + \
              "• Relaxation and reflection time\n\n" + \
              "**💡 Planning Tips:**\n" + \
              "• Book popular attractions in advance\n" + \
              "• Allow flexibility for spontaneous discoveries\n" + \
              "• Consider your energy levels and pace\n" + \
              "• Mix tourist attractions with local experiences\n\n" + \
              "Would you like me to customize this plan based on your specific interests, budget, and travel style?"
    
    return {
        'type': 'trip_plan',
        'content': response,
        'suggestions': ['Customize plan', 'Add activities', 'Check weather', 'Budget breakdown', 'Create detailed itinerary']
    }

def generate_sophisticated_accommodation(message, destination, trip_context):
    """Generate sophisticated accommodation response with specific hotel names"""
    
    if not destination:
        destination = "your destination"
    
    # Real hotel recommendations by destination
    hotel_recommendations = {
        'London': {
            'luxury': [
                'The Ritz London - Classic luxury hotel',
                'Claridge\'s - Mayfair luxury',
                'The Savoy - Thames-side luxury',
                'The Dorchester - Park Lane luxury',
                'The Connaught - Exclusive luxury'
            ],
            'mid_range': [
                'The Zetter - Boutique hotel',
                'citizenM Tower Hill - Modern budget luxury',
                'The Hoxton - Trendy boutique',
                'Mama Shelter - Design hotel',
                'The Ned - Historic luxury'
            ],
            'budget': [
                'YHA London Central - Hostel',
                'Generator London - Design hostel',
                'Safestay London Elephant & Castle - Budget',
                'Palmer\'s Lodge - Victorian hostel',
                'Astor Hyde Park - Budget hostel'
            ]
        },
        'Paris': {
            'luxury': [
                'The Ritz Paris - Historic luxury',
                'Hôtel de Crillon - Palace hotel',
                'Le Bristol - Classic luxury',
                'Four Seasons George V - Luxury',
                'Hôtel Plaza Athénée - Champs-Élysées luxury'
            ],
            'mid_range': [
                'Hôtel du Petit Moulin - Boutique',
                'Hôtel Fabric - Design hotel',
                'Hôtel Les Bains - Trendy',
                'Hôtel Providence - Boutique',
                'Hôtel Thérèse - Charming'
            ],
            'budget': [
                'Generator Paris - Design hostel',
                'St Christopher\'s Inn - Hostel',
                'Hôtel Henriette - Budget boutique',
                'Hôtel Eldorado - Budget',
                'Hôtel des Arts - Budget'
            ]
        },
        'Tokyo': {
            'luxury': [
                'The Ritz-Carlton Tokyo - Luxury',
                'Aman Tokyo - Ultra-luxury',
                'Mandarin Oriental Tokyo - Luxury',
                'Park Hyatt Tokyo - Famous luxury',
                'The Peninsula Tokyo - Luxury'
            ],
            'mid_range': [
                'Hotel Gracery Shinjuku - Godzilla hotel',
                'Hotel Century Southern Tower - Mid-range',
                'Shinjuku Granbell Hotel - Modern',
                'Hotel Sunroute Plaza Shinjuku - Convenient',
                'Hotel Gracery Asakusa - Traditional area'
            ],
            'budget': [
                'UNPLAN Kagurazaka - Hostel',
                'Grids Tokyo Akihabara - Hostel',
                'Bunka Hostel Tokyo - Traditional',
                'Sakura Hostel Asakusa - Budget',
                'K\'s House Tokyo - Hostel'
            ]
        },
        'New York': {
            'luxury': [
                'The Plaza - Historic luxury',
                'The St. Regis New York - Luxury',
                'The Waldorf Astoria - Classic luxury',
                'The Peninsula New York - Luxury',
                'The Ritz-Carlton New York - Luxury'
            ],
            'mid_range': [
                'The Standard High Line - Trendy',
                'Ace Hotel New York - Hip boutique',
                'The Jane Hotel - Historic boutique',
                'The Bowery Hotel - Downtown luxury',
                'The High Line Hotel - Chelsea boutique'
            ],
            'budget': [
                'HI New York City - Hostel',
                'Jazz on the Park - Hostel',
                'Chelsea International Hostel - Budget',
                'Blue Moon Hotel - Budget boutique',
                'Pod 39 - Pod hotel'
            ]
        },
        'Rome': {
            'luxury': [
                'Hotel de Russie - Luxury',
                'The St. Regis Rome - Luxury',
                'Hotel Eden - Luxury',
                'Palazzo Manfredi - Luxury',
                'Hotel de la Ville - Luxury'
            ],
            'mid_range': [
                'Hotel Artemide - Mid-range',
                'Hotel Navona - Boutique',
                'Hotel Campo de\' Fiori - Charming',
                'Hotel Raphael - Historic',
                'Hotel Condotti - Central'
            ],
            'budget': [
                'Yellow Hostel - Hostel',
                'The Beehive - Budget',
                'Hostel Alessandro Downtown - Budget',
                'Hotel Navona - Budget',
                'Hotel Campo de\' Fiori - Budget'
            ]
        }
    }
    
    # Get specific recommendations for the destination
    dest_key = destination.lower()
    recommendations = hotel_recommendations.get(dest_key, {})
    
    if recommendations:
        response = f"Here are **specific accommodation options** in {destination}:\n\n"
        
        if 'luxury' in recommendations:
            response += "**🏨 Luxury Hotels (5-star):**\n"
            for hotel in recommendations['luxury'][:3]:
                response += f"• {hotel}\n"
            response += "\n"
        
        if 'mid_range' in recommendations:
            response += "**🏠 Mid-Range Hotels (3-4 star):**\n"
            for hotel in recommendations['mid_range'][:3]:
                response += f"• {hotel}\n"
            response += "\n"
        
        if 'budget' in recommendations:
            response += "**💰 Budget Options:**\n"
            for hotel in recommendations['budget'][:3]:
                response += f"• {hotel}\n"
            response += "\n"
        
        response += "**💡 Booking Tips:**\n"
        response += "• Book 2-3 months in advance for better rates\n"
        response += "• Check multiple booking sites for best prices\n"
        response += "• Read recent reviews for current conditions\n"
        response += "• Consider location vs. price trade-offs\n\n"
        
        response += "Would you like me to suggest specific hotels based on your budget and preferences?"
        
    else:
        # Generic response for other destinations
        response = f"Here are **accommodation options** for {destination}:\n\n" + \
                  "**🏨 Hotels & Resorts:**\n" + \
                  "• Luxury hotels with full amenities\n" + \
                  "• Boutique hotels with character\n" + \
                  "• Business hotels for convenience\n" + \
                  "• Resort-style accommodations\n\n" + \
                  "**🏠 Alternative Options:**\n" + \
                  "• Vacation rentals and apartments\n" + \
                  "• Hostels for budget travelers\n" + \
                  "• Bed & breakfast establishments\n" + \
                  "• Guesthouses and homestays\n\n" + \
                  "Would you like me to suggest specific hotels or help you find the best area to stay?"
    
    return {
        'type': 'accommodation_advice',
        'content': response,
        'suggestions': ['Hotel recommendations', 'Best areas', 'Booking tips', 'Budget options', 'Luxury stays']
    }

def generate_sophisticated_transport(message, destination, trip_context):
    """Generate sophisticated transport response"""
    
    if not destination:
        destination = "your destination"
    
    response = f"Here's **transportation advice** for {destination}:\n\n" + \
              "**🚇 Public Transportation:**\n" + \
              "• **Metro/Subway**: Fast, efficient, and cost-effective for city travel\n" + \
              "• **Bus Networks**: Extensive coverage to all areas of the city\n" + \
              "• **Tram and Light Rail**: Scenic routes and convenient connections\n" + \
              "• **Train Connections**: Regional and intercity travel options\n\n" + \
              "**🚗 Private Transport:**\n" + \
              "• **Taxi Services**: Convenient for door-to-door service\n" + \
              "• **Ride-Sharing Apps**: Modern alternatives with upfront pricing\n" + \
              "• **Car Rentals**: Freedom to explore at your own pace\n" + \
              "• **Private Drivers**: Personalized service for special occasions\n\n" + \
              "**🚶 Walking & Cycling:**\n" + \
              "• **Pedestrian-Friendly Areas**: Safe and enjoyable walking routes\n" + \
              "• **Bike Rental Services**: Eco-friendly way to explore\n" + \
              "• **Walking Tours**: Guided exploration on foot\n" + \
              "• **Scenic Routes**: Beautiful paths and promenades\n\n" + \
              "**💡 Travel Tips:**\n" + \
              "• Get a travel pass for unlimited rides and savings\n" + \
              "• Download transport apps for real-time information\n" + \
              "• Learn basic transport phrases in the local language\n" + \
              "• Keep emergency numbers and transport information handy\n" + \
              "• Consider walking for short distances to save money\n\n" + \
              "Would you like me to help you plan the best routes or suggest transport passes?"
    
    return {
        'type': 'transport_advice',
        'content': response,
        'suggestions': ['Transport passes', 'Best routes', 'Airport transfer', 'Walking tours', 'Bike rentals']
    }

def generate_sophisticated_shopping(message, destination, trip_context):
    """Generate sophisticated shopping response"""
    
    if not destination:
        destination = "your destination"
    
    response = f"Here are **shopping recommendations** for {destination}:\n\n" + \
              "**🛍️ Shopping Districts:**\n" + \
              "• **Main Shopping Streets**: High-end boutiques and international brands\n" + \
              "• **Local Markets**: Traditional bazaars and artisan shops\n" + \
              "• **Shopping Malls**: Modern retail complexes with diverse options\n" + \
              "• **Designer Boutiques**: Exclusive fashion and luxury items\n\n" + \
              "**🎁 Souvenirs & Gifts:**\n" + \
              "• **Local Handicrafts**: Traditional art and handmade items\n" + \
              "• **Textiles & Clothing**: Regional fabrics and traditional garments\n" + \
              "• **Food & Beverages**: Local specialties and culinary souvenirs\n" + \
              "• **Unique Products**: One-of-a-kind items specific to the region\n\n" + \
              "**💰 Shopping Tips:**\n" + \
              "• Bargain at markets where appropriate and expected\n" + \
              "• Check for authenticity and quality of items\n" + \
              "• Compare prices at different shops and markets\n" + \
              "• Keep receipts for customs and warranty purposes\n" + \
              "• Avoid tourist traps and overpriced souvenir shops\n\n" + \
              "**🕐 Best Shopping Times:**\n" + \
              "• Avoid peak tourist hours for better deals\n" + \
              "• Check market opening times and schedules\n" + \
              "• Look for sales, discounts, and special offers\n" + \
              "• Plan shopping around other activities and sightseeing\n\n" + \
              "Would you like me to suggest specific shopping areas or help you find unique souvenirs?"
    
    return {
        'type': 'shopping_advice',
        'content': response,
        'suggestions': ['Shopping areas', 'Local markets', 'Souvenir ideas', 'Shopping tips', 'Best deals']
    }

def generate_sophisticated_safety(message, destination, trip_context):
    """Generate sophisticated safety response"""
    
    if not destination:
        destination = "your destination"
    
    response = f"Here are **comprehensive safety tips** for {destination}:\n\n" + \
              "**🛡️ General Safety:**\n" + \
              "• Stay aware of your surroundings and trust your instincts\n" + \
              "• Keep valuables secure and avoid displaying expensive items\n" + \
              "• Use well-lit areas at night and avoid isolated locations\n" + \
              "• Be cautious of pickpockets in crowded tourist areas\n\n" + \
              "**🚨 Emergency Information:**\n" + \
              "• Save local emergency numbers in your phone\n" + \
              "• Know the location of nearest hospitals and clinics\n" + \
              "• Identify embassy or consulate locations\n" + \
              "• Locate police stations and tourist information centers\n\n" + \
              "**💳 Financial Safety:**\n" + \
              "• Use ATMs in well-lit, secure locations\n" + \
              "• Keep cards and cash in separate, secure places\n" + \
              "• Notify your bank about travel plans in advance\n" + \
              "• Have backup payment methods and emergency funds\n\n" + \
              "**🏥 Health & Medical:**\n" + \
              "• Check required vaccinations and health requirements\n" + \
              "• Bring necessary medications and prescriptions\n" + \
              "• Know local health facilities and medical services\n" + \
              "• Have comprehensive travel insurance coverage\n\n" + \
              "**🌍 Cultural Awareness:**\n" + \
              "• Respect local customs, traditions, and cultural norms\n" + \
              "• Dress appropriately for the local culture and climate\n" + \
              "• Learn basic phrases in the local language\n" + \
              "• Be mindful of cultural sensitivities and taboos\n\n" + \
              "Would you like me to provide specific safety information for your destination?"
    
    return {
        'type': 'safety_advice',
        'content': response,
        'suggestions': ['Emergency contacts', 'Health info', 'Cultural tips', 'Travel insurance', 'Safety apps']
    }

def generate_sophisticated_clarification(message, context):
    """Generate sophisticated clarification response"""
    
    return {
        'type': 'clarification',
        'content': "I want to make sure I understand you correctly! 🤔\n\n" +
                  "Could you please rephrase your question or provide more specific details about what you're looking for? I'm here to help with:\n\n" +
                  "• **Weather information** for any destination\n" + \
                  "• **Activity recommendations** and attractions\n" + \
                  "• **Budget planning** and cost estimates\n" + \
                  "• **Trip planning** and itineraries\n" + \
                  "• **Accommodation** and transportation options\n" + \
                  "• **Food and dining** suggestions\n" + \
                  "• **Safety tips** and travel advice\n\n" + \
                  "Just let me know what specific aspect you'd like help with!",
        'suggestions': ['Weather check', 'Plan activities', 'Budget advice', 'Find restaurants', 'Safety tips']
    }

def generate_sophisticated_follow_up(message, context, destination):
    """Generate sophisticated follow-up response"""
    
    return {
        'type': 'follow_up',
        'content': f"Great! I'm happy to help you with more details about {destination or 'your trip'}! 🎉\n\n" + \
                  "What specific aspect would you like to explore further? I can provide:\n\n" + \
                  "• **More detailed recommendations** for your interests\n" + \
                  "• **Specific locations and addresses** for the best spots\n" + \
                  "• **Cost estimates and budget breakdowns**\n" + \
                  "• **Alternative options** and backup plans\n" + \
                  "• **Local insider tips** and hidden gems\n" + \
                  "• **Practical advice** for your travel style\n\n" + \
                  "Just let me know what additional information would be most helpful!",
        'suggestions': ['More details', 'Specific locations', 'Cost estimates', 'Alternative options', 'Local tips']
    }

def generate_sophisticated_general(message, context, destination):
    """Generate sophisticated general response"""
    
    return {
        'type': 'general',
        'content': f"I understand you're asking about travel! ✈️\n\n" + \
                  f"For {destination or 'your destination'}, I can help you with:\n\n" + \
                  "• **Weather information** and packing suggestions\n" + \
                  "• **Activity recommendations** and attractions\n" + \
                  "• **Budget planning** and cost estimates\n" + \
                  "• **Trip planning** and itineraries\n" + \
                  "• **Accommodation** and transportation options\n" + \
                  "• **Food and dining** suggestions\n" + \
                  "• **Safety tips** and travel advice\n\n" + \
                  "Try asking me something more specific like:\n" + \
                  "• 'What's the weather like in [destination]?'\n" + \
                  "• 'Suggest activities for [destination]'\n" + \
                  "• 'Help me plan a budget for [destination]'\n" + \
                  "• 'What are the best restaurants in [destination]?'\n\n" + \
                  "I'm here to make your travel planning amazing! 🌟",
        'suggestions': ['Weather check', 'Activity ideas', 'Budget help', 'Food recommendations', 'Safety advice']
    }

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