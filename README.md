# MCP Servers for VS Code Copilot

This project provides two Model Context Protocol (MCP) servers that can be used with VS Code Copilot: a Weather Server and a Google Drive Server.

## Project Structure

```
mcp-servers
├── src
│   ├── weather_server
│   │   ├── __init__.py
│   │   ├── server.py        # MCP weather server
│   │   └── handlers.py      # Weather API functions
│   ├── gdrive_server
│   │   ├── __init__.py
│   │   ├── server.py        # MCP Google Drive server
│   │   ├── handlers.py      # Drive API functions
│   │   └── auth.py          # Google OAuth authentication
│   └── shared
│       ├── __init__.py
│       └── utils.py         # Shared utility functions
├── config
│   ├── weather_config.json  # Weather API configuration
│   ├── gdrive_credentials.json  # Google Drive API credentials
│   └── mcp_settings.json    # MCP server configuration for VS Code
├── tests
│   ├── __init__.py
│   ├── test_weather_server.py
│   └── test_gdrive_server.py
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd /Users/macbook/Projects/MCP/mcp-servers/mcp-servers
pip install -r requirements.txt
```

### 2. Configure Weather Server

1. Get a free API key from [WeatherAPI.com](https:x//www.weatherapi.com/)
2. Update `config/weather_config.json`:
   ```json
   {
     "api_key": "YOUR_ACTUAL_WEATHER_API_KEY",
     "base_url": "https://api.weatherapi.com/v1",
     "default_location": "New York",
     "timeout": 10
   }
   ```

### 3. Configure Google Drive Server

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Drive API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `config/gdrive_credentials.json`

The credentials file should look like:
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID",
    "project_id": "YOUR_PROJECT_ID",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

### 4. Configure VS Code Copilot

Add the MCP server configurations to your VS Code Copilot settings using the provided `config/mcp_settings.json` file. The servers will be available as tools in your Copilot interface.
```json
{
    "mcpServers": {
        "weather": {
            "command": "python",
            "args": [
                "/Users/path/to/your/directory/mcp-servers/src/weather_server/server.py"
            ],
            "env": {
                "api_key": "your-weather-api-key"
                    }
        },
        "gdrive": {
            "command": "python",
            "args": [
                "/Users/path/to/your/directory/mcp-servers/src/gdrive_server/server.py"
            ],
            "env": {
                "GOOGLE_APPLICATION_CREDENTIALS": "//Users/path/to/your/directory/mcp-servers/config/gdrive_credentials.json"
            }
        }
    }
}
```
## Available Tools

### Weather Server Tools
- **get_current_weather**: Get current weather for any location
- **get_weather_forecast**: Get weather forecast for up to 10 days

### Google Drive Server Tools
- **list_files**: List files in your Google Drive with optional search
- **upload_file**: Upload a local file to Google Drive
- **download_file**: Download a file from Google Drive to local storage
- **delete_file**: Delete a file from Google Drive

## Testing the Servers

### Run Individual Server Tests
```bash
# Test weather server
python -m pytest tests/test_weather_server.py -v

# Test Google Drive server  
python -m pytest tests/test_gdrive_server.py -v

# Run all tests
python -m pytest tests/ -v
```

### Test Server Manually
```bash
# Test weather server
python src/weather_server/server.py

# Test Google Drive server
python src/gdrive_server/server.py
```

## Authentication Flow

### Weather Server
- Uses API key authentication
- No additional setup required after API key configuration

### Google Drive Server
- Uses OAuth 2.0 flow
- First run will open browser for authentication
- Subsequent runs use stored refresh token
- Token stored in `config/token.json` (auto-generated)

## Usage with VS Code Copilot

Once configured, you can use these tools directly in VS Code Copilot:

**Weather Examples:**
- "What's the current weather in London?"
- "Get me a 5-day forecast for Tokyo"

**Google Drive Examples:**
- "List my recent files in Google Drive"
- "Upload this document to my Drive"
- "Download the file with ID xyz123"