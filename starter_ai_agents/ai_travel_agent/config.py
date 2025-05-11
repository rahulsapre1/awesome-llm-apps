from typing import List, Dict

# API Configuration
API_RATE_LIMIT = 10  # requests per minute
CACHE_DURATION = 3600  # 1 hour in seconds

# Travel Preferences
BUDGET_RANGES = ["Budget", "Moderate", "Luxury"]
TRAVEL_STYLES = ["Relaxed", "Balanced", "Adventure"]
INTERESTS = ["Culture", "Food", "Nature", "History", "Shopping", "Nightlife", "Art", "Architecture", "Beach", "Mountains"]

# Emergency Information
EMERGENCY_SERVICES = {
    "Police": "112",
    "Ambulance": "112",
    "Fire": "112",
    "Tourist Police": "112"
}

# Weather API Configuration
WEATHER_API_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"

# Map Configuration
MAP_CENTER = [0, 0]  # Default center
MAP_ZOOM = 2  # Default zoom level

# Itinerary Sections
ITINERARY_SECTIONS = [
    "Introduction",
    "Day-by-Day Schedule",
    "Accommodations",
    "Transportation",
    "Local Tips",
    "Emergency Contacts",
    "Budget Breakdown",
    "Weather Forecast",
    "Packing List"
] 