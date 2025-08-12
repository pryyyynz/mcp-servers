def log_message(message):
    # Function to log messages
    print(f"[LOG] {message}")

def handle_error(error):
    # Function to handle errors
    print(f"[ERROR] {error}")

def validate_response(response):
    # Function to validate API responses
    if response.status_code != 200:
        handle_error(f"Invalid response: {response.status_code}")
        return False
    return True