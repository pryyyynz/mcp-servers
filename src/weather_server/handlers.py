import requests
import json
import os


def load_weather_config():
    """Load weather configuration from config file."""
    config_path = os.path.join(os.path.dirname(
        __file__), '../../config/weather_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def get_current_weather(location):
    """Function to fetch current weather data for a given location"""
    config = load_weather_config()
    api_key = config["api_key"]
    url = f"{config['base_url']}/current.json"
    params = {"key": api_key, "q": location}

    response = requests.get(url, params=params, timeout=config["timeout"])
    response.raise_for_status()
    return response.json()


def get_forecast(location, days=3):
    """Function to fetch weather forecast data for a given location"""
    config = load_weather_config()
    api_key = config["api_key"]
    url = f"{config['base_url']}/forecast.json"
    params = {"key": api_key, "q": location, "days": days}

    response = requests.get(url, params=params, timeout=config["timeout"])
    response.raise_for_status()
    return response.json()


def handle_weather_request(request):
    """Function to handle incoming weather requests"""
    # This function can be used for additional request processing if needed
    pass

# For backward compatibility with existing tests


def fetch_current_weather(city):
    """Fetch current weather data for a city (legacy function for tests)"""
    return get_current_weather(city)
