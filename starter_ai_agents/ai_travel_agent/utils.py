import time
from typing import Any, Dict, List
import requests
from datetime import datetime, timedelta
import streamlit as st
from config import API_RATE_LIMIT, CACHE_DURATION, WEATHER_API_ENDPOINT

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.calls = []

    def wait_if_needed(self):
        now = time.time()
        self.calls = [call for call in self.calls if now - call < 60]
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.calls.append(now)

def get_cached_data(key: str) -> Any:
    """Get data from Streamlit's cache."""
    if key in st.session_state:
        cache_time, data = st.session_state[key]
        if time.time() - cache_time < CACHE_DURATION:
            return data
    return None

def set_cached_data(key: str, data: Any):
    """Store data in Streamlit's cache."""
    st.session_state[key] = (time.time(), data)

def get_weather_forecast(location: str, start_date: datetime, num_days: int) -> Dict:
    """Get weather forecast for the travel dates."""
    cache_key = f"weather_{location}_{start_date.strftime('%Y%m%d')}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return cached_data

    # This is a placeholder - you would need to implement actual weather API call
    # and handle the API key properly
    weather_data = {
        "location": location,
        "forecast": [
            {
                "date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                "temperature": "25°C",
                "conditions": "Sunny",
                "precipitation": "0%"
            }
            for i in range(num_days)
        ]
    }
    
    set_cached_data(cache_key, weather_data)
    return weather_data

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency."""
    return f"{currency} {amount:,.2f}"

def calculate_total_cost(activities: List[Dict]) -> float:
    """Calculate total cost of activities."""
    return sum(activity.get("cost", 0) for activity in activities)

def generate_packing_list(weather_data: Dict, travel_style: str, num_days: int) -> List[str]:
    """Generate a packing list based on weather and travel style."""
    # This is a basic implementation - you could make it more sophisticated
    essentials = [
        "Passport/ID",
        "Travel Insurance",
        "Credit Cards",
        "Phone Charger",
        "Medications"
    ]
    
    weather_items = []
    for day in weather_data["forecast"]:
        if "Rain" in day["conditions"]:
            weather_items.append("Umbrella")
        if float(day["temperature"].replace("°C", "")) < 20:
            weather_items.append("Jacket")
    
    style_items = {
        "Relaxed": ["Comfortable Shoes", "Casual Clothes"],
        "Adventure": ["Hiking Boots", "Backpack", "Water Bottle"],
        "Balanced": ["Walking Shoes", "Mix of Casual and Smart Clothes"]
    }
    
    return list(set(essentials + weather_items + style_items.get(travel_style, []))) 