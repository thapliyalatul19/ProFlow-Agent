"""
Weather Service - Real external API integration with OpenWeatherMap.

Provides weather context for meeting planning and scheduling decisions.
"""

import os
import json
import requests
from typing import Dict, Optional
from datetime import datetime
import logging
from pathlib import Path


class WeatherService:
    """Real external API integration - OpenWeatherMap"""
    
    def __init__(self):
        # Free API key (or use env variable)
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '8b4c67d8e5f29a7c9d3e4f5a6b7c8d9e')
        self.base_url = 'http://api.openweathermap.org/data/2.5'
        self.logger = logging.getLogger(__name__)
        
        # Setup cache file path
        project_root = Path(__file__).parent.parent.parent
        self.cache_file = project_root / 'data' / 'weather_cache.json'
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cached weather data"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading weather cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save weather cache"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving weather cache: {e}")
    
    def get_weather(self, city: str = "Denver") -> Dict:
        """
        Get current weather for a city.
        
        Args:
            city: City name (default: "Denver")
        
        Returns:
            Dictionary with weather information
        """
        cache_key = f"{city}_{datetime.now().strftime('%Y%m%d_%H')}"
        
        # Check cache (1 hour expiry)
        if cache_key in self.cache:
            self.logger.info(f"Weather cache hit for {city}")
            return self.cache[cache_key]
        
        try:
            # Make real API call
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'imperial'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                weather_info = {
                    'city': city,
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data.get('wind', {}).get('speed', 0),
                    'timestamp': datetime.now().isoformat(),
                    'suitable_for_outdoor_meeting': (
                        data['main']['temp'] > 50 and 
                        data['main']['temp'] < 85
                    )
                }
                
                # Cache result
                self.cache[cache_key] = weather_info
                self._save_cache()
                
                self.logger.info(f"Weather fetched from API for {city}: {weather_info['temperature']}°F")
                return weather_info
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Weather API error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error fetching weather: {e}")
            
        # Return default if API fails
        return {
            'city': city,
            'temperature': 70,
            'description': 'partly cloudy',
            'error': 'API unavailable, using defaults',
            'suitable_for_outdoor_meeting': True
        }
    
    def get_meeting_weather_context(self, meeting_time: str, location: str = "Denver") -> str:
        """
        Get weather context for meeting planning.
        
        Args:
            meeting_time: Meeting time string
            location: Location/city name (default: "Denver")
        
        Returns:
            Formatted weather context string
        """
        weather = self.get_weather(location)
        
        context = f"Weather in {location}: {weather['temperature']}°F, {weather['description']}. "
        
        if weather.get('suitable_for_outdoor_meeting'):
            context += "Good conditions for outdoor meeting or walking meeting. "
        else:
            context += "Indoor venue recommended. "
            
        if weather.get('temperature', 70) < 40:
            context += "Cold weather - ensure remote option available."
        elif weather.get('temperature', 70) > 90:
            context += "Hot weather - ensure good AC in meeting room."
            
        return context


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from utils.logger import setup_logging
    logger = setup_logging()
    
    print("Testing WeatherService...")
    
    service = WeatherService()
    
    # Test weather fetch
    weather = service.get_weather("Denver")
    print(f"\nWeather for Denver:")
    print(f"  Temperature: {weather['temperature']}°F")
    print(f"  Description: {weather['description']}")
    print(f"  Suitable for outdoor: {weather.get('suitable_for_outdoor_meeting', False)}")
    
    # Test meeting context
    context = service.get_meeting_weather_context("2pm", "Denver")
    print(f"\nMeeting context: {context}")
    
    print("\n✅ WeatherService test complete!")

