// API Base URL
const API_BASE = (() => {
    // Check if we're in production (Render deployment)
    if (window.location.hostname.includes('render.com') || window.location.hostname.includes('tripbox-intelliorganizer.onrender.com')) {
        return 'https://tripbox-intelliorganizer.onrender.com';
    }
    // Local development
    return 'http://127.0.0.1:5000';
})();

// Live Location Tracking
class LiveLocationTracker {
    constructor(groupId) {
        this.groupId = groupId;
        this.watchId = null;
        this.map = null;
        this.markers = {};
    }

    async initializeMap(containerId) {
        // Initialize Google Maps
        this.map = new google.maps.Map(document.getElementById(containerId), {
            zoom: 12,
            center: { lat: 0, lng: 0 }
        });

        // Start tracking
        await this.startTracking();
        
        // Start updating other members' locations
        this.startUpdatingLocations();
    }

    async startTracking() {
        if ("geolocation" in navigator) {
            this.watchId = navigator.geolocation.watchPosition(
                async (position) => {
                    const locationData = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        speed: position.coords.speed,
                        heading: position.coords.heading,
                        altitude: position.coords.altitude
                    };

                    // Update own marker
                    this.updateMarker('self', locationData);

                    // Send to backend
                    try {
                        await this.updateLocation(locationData);
                    } catch (error) {
                        console.error('Error updating location:', error);
                    }
                },
                (error) => {
                    console.error('Location error:', error);
                    showMessage('Error getting location. Please enable location services.', 'error');
                },
                {
                    enableHighAccuracy: true,
                    maximumAge: 30000,
                    timeout: 27000
                }
            );
        } else {
            showMessage('Location tracking not supported in your browser', 'error');
        }
    }

    async updateLocation(locationData) {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/live-location/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(locationData)
        });

        if (!response.ok) {
            throw new Error('Failed to update location');
        }
    }

    startUpdatingLocations() {
        // Update other members' locations every 30 seconds
        setInterval(async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/live-location/members`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch member locations');
                }

                const data = await response.json();
                
                // Update markers for all members
                data.locations.forEach(location => {
                    if (location.user_id !== parseInt(localStorage.getItem('userId'))) {
                        this.updateMarker(location.user_id, location);
                    }
                });

            } catch (error) {
                console.error('Error fetching member locations:', error);
            }
        }, 30000);
    }

    updateMarker(userId, location) {
        const position = {
            lat: location.latitude,
            lng: location.longitude
        };

        if (this.markers[userId]) {
            this.markers[userId].setPosition(position);
        } else {
            this.markers[userId] = new google.maps.Marker({
                position: position,
                map: this.map,
                title: userId === 'self' ? 'You' : `Member ${userId}`,
                icon: userId === 'self' ? null : 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
            });
        }

        // Center map on own location
        if (userId === 'self') {
            this.map.setCenter(position);
        }
    }

    stopTracking() {
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    }
}

// AI Recommendations
class AIRecommendations {
    constructor(groupId) {
        this.groupId = groupId;
    }

    async getNearbyRecommendations(latitude, longitude, types = ['restaurant', 'tourist_attraction', 'lodging']) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/ai-recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    latitude,
                    longitude,
                    types
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get recommendations');
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting recommendations:', error);
            throw error;
        }
    }

    async getPersonalizedRecommendations(preferences, budget, duration, location) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/ai-recommendations/personalized`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    preferences,
                    budget,
                    duration,
                    location
                })
            });

            if (!response.ok) {
                throw new Error('Failed to get personalized recommendations');
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting personalized recommendations:', error);
            throw error;
        }
    }

    async saveRecommendation(recommendation) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/ai-recommendations/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(recommendation)
            });

            if (!response.ok) {
                throw new Error('Failed to save recommendation');
            }

            return await response.json();
        } catch (error) {
            console.error('Error saving recommendation:', error);
            throw error;
        }
    }

    async getWeather(latitude, longitude) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/weather?lat=${latitude}&lng=${longitude}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to get weather information');
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting weather:', error);
            throw error;
        }
    }
}

// Enhanced Chat
class EnhancedChat {
    constructor(groupId) {
        this.groupId = groupId;
        this.messageUpdateInterval = null;
    }

    async sendMessage(message, type = 'text', replyToMessageId = null) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/chat/enhanced`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    message,
                    message_type: type,
                    reply_to_message_id: replyToMessageId
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            return await response.json();
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    async getMessages() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/chat/enhanced`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to get messages');
            }

            return await response.json();
        } catch (error) {
            console.error('Error getting messages:', error);
            throw error;
        }
    }

    async markMessageAsRead(messageId) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/groups/${this.groupId}/chat/messages/${messageId}/read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to mark message as read');
            }

            return await response.json();
        } catch (error) {
            console.error('Error marking message as read:', error);
            throw error;
        }
    }

    startMessageUpdates() {
        this.messageUpdateInterval = setInterval(async () => {
            try {
                const messages = await this.getMessages();
                this.updateChatUI(messages);
            } catch (error) {
                console.error('Error updating messages:', error);
            }
        }, 5000);
    }

    stopMessageUpdates() {
        if (this.messageUpdateInterval) {
            clearInterval(this.messageUpdateInterval);
            this.messageUpdateInterval = null;
        }
    }

    updateChatUI(messages) {
        // This should be implemented by the calling code
        // to update the chat UI with new messages
    }
}

// PDF Generation
class PDFGenerator {
    constructor(tripId) {
        this.tripId = tripId;
    }

    async generatePDF() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/trips/${this.tripId}/generate-pdf`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }

            const data = await response.json();
            return data.filename;
        } catch (error) {
            console.error('Error generating PDF:', error);
            throw error;
        }
    }

    async downloadPDF(filename) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE}/api/trips/${this.tripId}/download-pdf/${filename}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to download PDF');
            }

            // Create blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error downloading PDF:', error);
            throw error;
        }
    }
}

// Export classes
window.LiveLocationTracker = LiveLocationTracker;
window.AIRecommendations = AIRecommendations;
window.EnhancedChat = EnhancedChat;
window.PDFGenerator = PDFGenerator; 