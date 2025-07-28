# TripBox Advanced Features Setup Guide

## Overview
This guide will help you set up and enable all advanced features in TripBox:
1. Live Location Tracking
2. AI-powered Recommendations
3. Enhanced Real-time Chat
4. PDF Trip Reports

## Prerequisites

### 1. Google Cloud Platform Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable these APIs:
   - Maps JavaScript API
   - Places API
   - Geocoding API
   - Directions API
4. Create API credentials:
   - Create an API key
   - Restrict it to your domains
   - Copy the key for both `GOOGLE_MAPS_API_KEY` and `GOOGLE_PLACES_API_KEY`

### 2. OpenWeather API Setup
1. Go to [OpenWeather](https://openweathermap.org/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy the key for `OPENWEATHER_API_KEY`

### 3. OpenAI API (Optional)
1. Go to [OpenAI](https://platform.openai.com/)
2. Sign up for an account
3. Get your API key
4. Copy the key for `OPENAI_API_KEY`

## Backend Setup

### 1. Environment Variables
Add these to your `.env` file or Render environment variables:
```bash
GOOGLE_PLACES_API_KEY=your_google_places_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional
```

### 2. Install Dependencies
The following packages are required:
```bash
pip install python-socketio==5.11.1
pip install eventlet==0.35.1
pip install geopy==2.4.1
pip install pillow==10.2.0
pip install qrcode==7.4.2
pip install googlemaps==4.10.0
```

These are already added to `requirements.txt`.

## Frontend Setup

### 1. Google Maps Integration
1. Open `frontend/advanced-features.html`
2. Replace `YOUR_GOOGLE_MAPS_API_KEY` with your actual API key:
   ```html
   <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_KEY&libraries=places"></script>
   ```

### 2. Enable Features
1. Add the Advanced Features link to navigation:
   ```html
   <div class="nav-item">
       <a href="advanced-features.html" class="nav-link">
           <i class="fas fa-rocket"></i>
           Advanced Features
       </a>
   </div>
   ```

## Feature Details

### 1. Live Location Tracking
- Uses Google Maps JavaScript API
- Real-time location updates every 30 seconds
- Shows all group members on the map
- Emergency alerts with location
- Location history tracking

### 2. AI Recommendations
- Uses Google Places API for nearby places
- OpenWeather API for weather data
- Optional OpenAI integration for personalized suggestions
- Categories: Food, Activities, Accommodation, etc.

### 3. Enhanced Real-time Chat
- Rich message types (text, location, images)
- Real-time updates
- Read receipts
- Message threading
- Typing indicators

### 4. PDF Trip Reports
- Comprehensive trip summaries
- Includes expenses, photos, and itinerary
- Customizable sections
- Professional formatting

## Testing

### 1. Live Location
1. Open Advanced Features page
2. Click "Start Tracking"
3. Accept location permission
4. Verify your location appears on map
5. Test with multiple users

### 2. AI Recommendations
1. Click "Get Suggestions"
2. Verify nearby places appear
3. Check weather information
4. Test different preferences

### 3. Enhanced Chat
1. Open group chat
2. Send different types of messages
3. Verify real-time updates
4. Test with multiple users

### 4. PDF Reports
1. Select a trip
2. Click "Generate PDF"
3. Verify all sections are included
4. Test download functionality

## Troubleshooting

### Common Issues

1. **Location Not Working**
   - Check browser location permissions
   - Verify Google Maps API key
   - Check browser console for errors

2. **Recommendations Not Loading**
   - Verify API keys in environment
   - Check rate limits
   - Look for API errors in backend logs

3. **Chat Issues**
   - Check WebSocket connection
   - Verify user authentication
   - Check browser console

4. **PDF Generation Fails**
   - Check ReportLab installation
   - Verify file permissions
   - Check server logs

## Security Notes

1. **API Keys**
   - Never expose API keys in frontend code
   - Use environment variables
   - Restrict API key usage by domain

2. **Location Data**
   - Only share with group members
   - Clear old location data
   - Allow users to disable tracking

3. **Chat Security**
   - Encrypt sensitive data
   - Validate message types
   - Sanitize user input

## Support

For any issues:
1. Check the troubleshooting section
2. Look for errors in browser console
3. Check backend logs in Render dashboard
4. Review API documentation 