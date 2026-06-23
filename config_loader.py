import json
import os

def load_config(config_path="config.json"):
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found!")
        return None

    with open(config_path, 'r') as f:
        return json.load(f)

def validate_config(config):
    """Validate that config has required structure"""
    required_keys = ['youtube', 'reddit', 'analysis']
    for key in required_keys:
        if key not in config:
            print(f"Missing required config key: {key}")
            return False
    return True
