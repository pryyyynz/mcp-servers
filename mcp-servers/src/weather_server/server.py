#!/usr/bin/env python3
import mcp.types as types
from pydantic import AnyUrl
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import asyncio
import json
import os
import sys
from typing import Any, Sequence
import requests

# Add the parent directory to the Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


# Load config


def load_weather_config():
    config_path = os.path.join(os.path.dirname(
        __file__), '../../config/weather_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


config = load_weather_config()
server = Server("weather-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available weather tools."""
    return [
        types.Tool(
            name="get_current_weather",
            description="Get current weather for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates"
                    }
                },
                "required": ["location"]
            }
        ),
        types.Tool(
            name="get_weather_forecast",
            description="Get weather forecast for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or coordinates"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of forecast days (1-10)",
                        "default": 3
                    }
                },
                "required": ["location"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls."""
    if name == "get_current_weather":
        location = arguments.get("location")
        weather_data = await get_current_weather(location)
        return [types.TextContent(type="text", text=json.dumps(weather_data, indent=2))]

    elif name == "get_weather_forecast":
        location = arguments.get("location")
        days = arguments.get("days", 3)
        forecast_data = await get_weather_forecast(location, days)
        return [types.TextContent(type="text", text=json.dumps(forecast_data, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def get_current_weather(location: str) -> dict:
    """Fetch current weather data."""
    api_key = config["api_key"]
    url = f"{config['base_url']}/current.json"
    params = {"key": api_key, "q": location}

    response = requests.get(url, params=params, timeout=config["timeout"])
    response.raise_for_status()
    return response.json()


async def get_weather_forecast(location: str, days: int) -> dict:
    """Fetch weather forecast."""
    api_key = config["api_key"]
    url = f"{config['base_url']}/forecast.json"
    params = {"key": api_key, "q": location, "days": days}

    response = requests.get(url, params=params, timeout=config["timeout"])
    response.raise_for_status()
    return response.json()


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    print("Starting weather MCP server...", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        print("Weather server ready for MCP connections", file=sys.stderr)
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
