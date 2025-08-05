# Live Location Sharing Feature

## Overview

The Live Location Sharing feature allows trip members to share their real-time location with other members of their trip group. This is particularly useful when members get lost or need to meet up at a specific location during their trip.

## Features

### Core Functionality
- **Real-time Location Sharing**: Members can share their GPS coordinates with the group
- **Location History**: Track location history for the past 24 hours
- **Distance Calculation**: Calculate distances between group members
- **Emergency Alerts**: Send emergency location alerts to group members
- **Geofencing**: Create virtual boundaries for location-based notifications

### User Interface
- **Modern Web Interface**: Clean, responsive design with real-time updates
- **Location Cards**: Display member locations with detailed information
- **Interactive Map**: View locations on Google Maps
- **Status Indicators**: Visual indicators for sharing status
- **Mobile Responsive**: Works on all device sizes

## Backend Implementation

### Database Model
```python
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
```

### API Endpoints

#### 1. Update Location
```
POST /api/groups/{group_id}/live-location/update
```
Updates the user's current location for the specified group.

**Request Body:**
```json
{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "accuracy": 10.5,
    "speed": 0.0,
    "heading": 0.0,
    "altitude": 10.0,
    "battery_level": 85.0,
    "location_name": "Coffee Shop"
}
```

**Response:**
```json
{
    "message": "Location updated successfully",
    "location_id": 123,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Get Group Locations
```
GET /api/groups/{group_id}/live-location/members
```
Retrieves all active locations for group members (last 30 minutes).

**Response:**
```json
{
    "locations": [
        {
            "user_id": 1,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "accuracy": 10.5,
            "speed": 0.0,
            "heading": 0.0,
            "altitude": 10.0,
            "timestamp": "2024-01-15T10:30:00Z",
            "battery_level": 85.0,
            "location_name": "Coffee Shop",
            "time_ago": "2 minutes ago"
        }
    ],
    "total_members": 1,
    "group_id": 1
}
```

#### 3. Get Location History
```
GET /api/groups/{group_id}/live-location/history?user_id={user_id}&hours={hours}
```
Retrieves location history for a specific user.

**Query Parameters:**
- `user_id`: Target user ID (defaults to current user)
- `hours`: Number of hours to look back (default: 24)

**Response:**
```json
{
    "history": [
        {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timestamp": "2024-01-15T10:30:00Z",
            "location_name": "Coffee Shop",
            "speed": 0.0,
            "accuracy": 10.5
        }
    ],
    "user_id": 1,
    "hours_covered": 24,
    "total_points": 10
}
```

#### 4. Calculate Distances
```
GET /api/groups/{group_id}/live-location/distance
```
Calculates distances between all group members.

**Response:**
```json
{
    "distances": [
        {
            "user1_id": 1,
            "user2_id": 2,
            "distance_km": 1.5,
            "distance_miles": 0.93
        }
    ],
    "total_members": 2
}
```

#### 5. Emergency Alert
```
POST /api/groups/{group_id}/live-location/emergency
```
Sends an emergency alert with current location.

**Request Body:**
```json
{
    "message": "Emergency! I need help!"
}
```

#### 6. Create Geofence
```
POST /api/groups/{group_id}/live-location/geofence
```
Creates a virtual boundary for location-based notifications.

**Request Body:**
```json
{
    "name": "Hotel Area",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "radius": 100
}
```

## Frontend Implementation

### Key Features
- **Real-time Updates**: Automatic refresh every 10 seconds
- **Geolocation API**: Uses browser's geolocation capabilities
- **Responsive Design**: Works on desktop and mobile devices
- **Interactive UI**: Modern design with smooth animations
- **Error Handling**: Comprehensive error messages and status indicators

### JavaScript Functions

#### Core Functions
```javascript
// Start location sharing
function startLocationSharing()

// Stop location sharing
function stopLocationSharing()

// Update location on server
function updateLocation(position, locationName)

// Refresh member locations
function refreshLocations()

// Display locations in UI
function displayLocations(locations)

// Show alerts to user
function showAlert(message, type)
```

#### Utility Functions
```javascript
// View location on Google Maps
function viewOnMap(lat, lng)

// Get directions to location
function getDirections(lat, lng)

// Update UI based on sharing status
function updateUI()
```

## Security Features

### Authentication
- All endpoints require JWT authentication
- User must be a member of the group to access location data
- Automatic token validation and refresh

### Privacy Protection
- Location data is only shared within the group
- Users can stop sharing at any time
- Location history is limited to 24 hours by default
- No location data is stored permanently without consent

### Data Validation
- Coordinates are validated for reasonable ranges
- Accuracy and speed data is validated
- Malicious data is filtered out

## Usage Instructions

### For Trip Members

1. **Access the Feature**
   - Log into TripBox
   - Navigate to "Live Location" in the sidebar
   - Or directly visit `frontend/live-location.html`

2. **Start Sharing Location**
   - Select your trip group from the dropdown
   - Optionally add a location name (e.g., "Coffee Shop")
   - Click "Start Sharing Location"
   - Grant location permissions when prompted

3. **View Other Members**
   - Locations are automatically refreshed every 10 seconds
   - Click "View on Map" to see location on Google Maps
   - Click "Get Directions" for navigation

4. **Stop Sharing**
   - Click "Stop Sharing" to end location sharing
   - Your location will no longer be visible to others

### For Trip Organizers

1. **Monitor Group Location**
   - View all active members on the live map
   - Check distance calculations between members
   - Monitor location history for planning

2. **Emergency Situations**
   - Members can send emergency alerts
   - Organizers receive immediate notifications
   - Emergency locations are highlighted

## Technical Requirements

### Backend Requirements
- Python 3.7+
- Flask framework
- SQLAlchemy for database operations
- JWT for authentication
- CORS support for cross-origin requests

### Frontend Requirements
- Modern web browser with geolocation support
- JavaScript enabled
- HTTPS connection (required for geolocation)

### Browser Compatibility
- Chrome 50+
- Firefox 55+
- Safari 10+
- Edge 12+

## Testing

### Backend Testing
Run the test script to verify functionality:
```bash
cd backend
python test_live_location.py
```

### Frontend Testing
1. Start the backend server:
   ```bash
   cd backend
   python app.py
   ```

2. Open the frontend:
   ```
   frontend/live-location.html
   ```

3. Test the features:
   - Login with valid credentials
   - Select a trip group
   - Start location sharing
   - Verify location updates
   - Test emergency alerts

## Troubleshooting

### Common Issues

1. **Location Permission Denied**
   - Ensure the site is served over HTTPS
   - Check browser location permissions
   - Try refreshing the page

2. **No Groups Available**
   - Verify user is logged in
   - Check if user is a member of any groups
   - Create a trip and group first

3. **Location Not Updating**
   - Check internet connection
   - Verify server is running
   - Check browser console for errors

4. **Map Not Loading**
   - Ensure internet connection
   - Check if Google Maps is accessible
   - Try refreshing the page

### Error Messages

- **"Geolocation is not supported"**: Browser doesn't support location
- **"Failed to get your location"**: Permission denied or GPS unavailable
- **"Please select a trip group first"**: No group selected
- **"Failed to update location"**: Server error or network issue

## Future Enhancements

### Planned Features
- **Real-time Map Integration**: Embed interactive maps
- **Push Notifications**: Instant alerts for location changes
- **Route Tracking**: Track member movement patterns
- **Location Analytics**: Insights into group movement
- **Offline Support**: Cache locations when offline

### Advanced Features
- **Geofencing Alerts**: Notify when members enter/exit areas
- **Location Privacy**: Granular privacy controls
- **Battery Optimization**: Reduce location update frequency
- **Multi-platform Support**: Mobile app integration

## Contributing

To contribute to the live location feature:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This feature is part of the TripBox application and follows the same licensing terms.

---

**Note**: This feature requires user consent for location sharing and should be used responsibly. Always respect user privacy and provide clear information about how location data is used. 