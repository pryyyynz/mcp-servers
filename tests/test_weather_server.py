import unittest
import asyncio
from unittest.mock import patch, MagicMock
from src.weather_server.handlers import fetch_current_weather, get_current_weather


class TestWeatherServer(unittest.TestCase):

    @patch('src.weather_server.handlers.requests.get')
    @patch('src.weather_server.handlers.load_weather_config')
    def test_fetch_current_weather(self, mock_config, mock_get):
        # Mock configuration
        mock_config.return_value = {
            "api_key": "test_key",
            "base_url": "https://api.weatherapi.com/v1",
            "timeout": 10
        }

        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "location": {"name": "London"},
            "current": {"temp_c": 15, "condition": {"text": "Cloudy"}}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test the function
        city = "London"
        weather_data = fetch_current_weather(city)

        self.assertIsInstance(weather_data, dict)
        self.assertIn("location", weather_data)
        self.assertIn("current", weather_data)

    @patch('src.weather_server.handlers.requests.get')
    @patch('src.weather_server.handlers.load_weather_config')
    def test_get_current_weather(self, mock_config, mock_get):
        # Mock configuration
        mock_config.return_value = {
            "api_key": "test_key",
            "base_url": "https://api.weatherapi.com/v1",
            "timeout": 10
        }

        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "location": {"name": "New York"},
            "current": {"temp_c": 20, "condition": {"text": "Sunny"}}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test the function
        city = "New York"
        weather_data = get_current_weather(city)

        self.assertIsInstance(weather_data, dict)
        self.assertIn("location", weather_data)
        self.assertIn("current", weather_data)


if __name__ == '__main__':
    unittest.main()
