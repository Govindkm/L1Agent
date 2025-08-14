"""
Weather tools for the multi-agent system.
"""

import os
import requests
from langchain_core.tools import tool
from utils.observer import log_thinking
from config.settings import get_settings


@tool
def get_weather_data(city: str) -> str:
    """
    Get current weather information for a given city.
    
    Args:
        city: The name of the city to get weather for
        
    Returns:
        Weather information as a formatted string
    """
    log_thinking(
        "WeatherAgent", 
        f"User requested weather for {city}. I need to call the weather API.",
        f"Calling OpenWeatherMap API for {city}"
    )
    
    settings = get_settings()
    api_key = settings.weather_api_key
    
    if not api_key:
        error_msg = "Weather API key not configured. Please set WEATHER_API_KEY in .env file"
        log_thinking("WeatherAgent", "API key missing - cannot fetch weather data", "Return error message")
        return error_msg
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"]
            }
            
            formatted_weather = f"""
Weather Report for {weather_info['city']}, {weather_info['country']}:
🌡️ Temperature: {weather_info['temperature']}°C (feels like {weather_info['feels_like']}°C)
🌤️ Conditions: {weather_info['description'].title()}
💧 Humidity: {weather_info['humidity']}%
💨 Wind Speed: {weather_info['wind_speed']} m/s
            """.strip()
            
            log_thinking(
                "WeatherAgent", 
                f"Successfully retrieved weather data for {city}",
                "Formatting weather information for user"
            )
            return formatted_weather
            
        else:
            error_msg = f"Could not fetch weather data for {city}. Please check the city name."
            log_thinking("WeatherAgent", f"API error: {response.status_code}", "Return error message")
            return error_msg
            
    except Exception as e:
        error_msg = f"Error fetching weather data: {str(e)}"
        log_thinking("WeatherAgent", f"Exception occurred: {str(e)}", "Return error message")
        return error_msg
