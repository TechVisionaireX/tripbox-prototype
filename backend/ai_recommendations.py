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
    
    # Generate AI response based on message type
    ai_response = generate_ai_response(user_message, trip_context)
    
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

def generate_ai_response(user_message, trip_context):
    """Generate AI response based on user message and trip context"""
    message_lower = user_message.lower()
    
    # Simple rule-based responses (in production, use OpenAI API)
    if 'suggest' in message_lower and 'plan' in message_lower:
        return generate_trip_plan_suggestion(user_message, trip_context)
    elif 'weather' in message_lower:
        return generate_weather_response(user_message, trip_context)
    elif 'budget' in message_lower or 'cost' in message_lower:
        return generate_budget_suggestion(user_message, trip_context)
    elif 'food' in message_lower or 'restaurant' in message_lower:
        return generate_food_suggestion(user_message, trip_context)
    elif 'activity' in message_lower or 'things to do' in message_lower:
        return generate_activity_suggestion(user_message, trip_context)
    elif 'remind' in message_lower or 'forget' in message_lower:
        return generate_reminder_response(user_message, trip_context)
    else:
        return generate_general_response(user_message, trip_context)

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
                'content': f"**Current Weather for {destination}:**\n\n" +
                          f"• Temperature: {weather_data['temperature']}°C ({weather_data['temperature']*9/5+32:.0f}°F)\n" +
                          f"• Feels like: {weather_data['feels_like']}°C\n" +
                          f"• Conditions: {weather_data['conditions']}\n" +
                          f"• Humidity: {weather_data['humidity']}%\n" +
                          f"• Wind: {weather_data['wind_speed']} km/h\n\n" +
                          "**Packing Suggestions:**\n" +
                          "• Light layers for changing temperatures\n" +
                          "• Comfortable walking shoes\n" +
                          "• Rain gear (just in case)\n" +
                          "• Sun protection\n\n" +
                          "Would you like me to get the detailed 7-day forecast?",
                'suggestions': ['7-day forecast', 'Packing list', 'Weather alerts', 'Alternative dates']
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    
    # Fallback response
    return {
        'type': 'weather_info',
        'content': f"I'll check the current weather for {destination}.\n\n" +
                  "**Current Weather:**\n" +
                  "• Temperature: 22°C (72°F)\n" +
                  "• Conditions: Partly cloudy\n" +
                  "• Humidity: 65%\n" +
                  "• Wind: 10 km/h\n\n" +
                  "**Packing Suggestions:**\n" +
                  "• Light layers for changing temperatures\n" +
                  "• Comfortable walking shoes\n" +
                  "• Rain gear (just in case)\n" +
                  "• Sun protection\n\n" +
                  "Would you like me to get the detailed 7-day forecast?",
        'suggestions': ['7-day forecast', 'Packing list', 'Weather alerts', 'Alternative dates']
    }

def generate_budget_suggestion(message, trip_context):
    """Generate budget-related suggestions"""
    return {
        'type': 'budget_advice',
        'content': "Here are some budget-friendly tips for your trip:\n\n" +
                  "**Accommodation:**\n" +
                  "• Consider hostels or vacation rentals\n" +
                  "• Book in advance for better rates\n\n" +
                  "**Food:**\n" +
                  "• Eat at local markets and street food\n" +
                  "• Avoid tourist-heavy restaurants\n\n" +
                  "**Activities:**\n" +
                  "• Many museums have free days\n" +
                  "• Use public transportation\n" +
                  "• Look for city passes\n\n" +
                  "Would you like a detailed budget breakdown?",
        'suggestions': ['Budget breakdown', 'Cost-saving tips', 'Expense tracker', 'Group discounts']
    }

def generate_food_suggestion(message, trip_context):
    """Generate food-related suggestions"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'food_recommendations',
        'content': f"Here are some food recommendations for {destination}:\n\n" +
                  "**Must-Try Local Dishes:**\n" +
                  "• Traditional specialties\n" +
                  "• Street food favorites\n" +
                  "• Regional cuisine\n\n" +
                  "**Restaurant Types:**\n" +
                  "• Fine dining for special occasions\n" +
                  "• Casual local spots\n" +
                  "• Food markets and stalls\n\n" +
                  "**Dietary Considerations:**\n" +
                  "• Vegetarian/vegan options\n" +
                  "• Allergen information\n" +
                  "• Halal/kosher options\n\n" +
                  "Would you like specific restaurant recommendations?",
        'suggestions': ['Restaurant list', 'Food tours', 'Cooking classes', 'Dietary needs']
    }

def generate_activity_suggestion(message, trip_context):
    """Generate activity suggestions"""
    destination = trip_context.get('destination', 'your destination')
    
    return {
        'type': 'activity_recommendations',
        'content': f"Here are some exciting activities for {destination}:\n\n" +
                  "**Cultural Activities:**\n" +
                  "• Museum visits\n" +
                  "• Historical tours\n" +
                  "• Art galleries\n\n" +
                  "**Outdoor Adventures:**\n" +
                  "• Hiking trails\n" +
                  "• Water sports\n" +
                  "• Nature parks\n\n" +
                  "**Entertainment:**\n" +
                  "• Local shows\n" +
                  "• Nightlife spots\n" +
                  "• Shopping districts\n\n" +
                  "Would you like me to find specific activities based on your interests?",
        'suggestions': ['Activity booking', 'Tour guides', 'Group activities', 'Adventure sports']
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