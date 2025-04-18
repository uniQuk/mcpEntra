import os
from dotenv import load_dotenv
from pathlib import Path

def load_environment():
    """Load environment variables from .env file if it exists"""
    # Try to load from .env file
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Check required variables
    required_vars = ['TENANT_ID', 'CLIENT_ID', 'CLIENT_SECRET', 'API_KEYS']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"WARNING: The following required environment variables are missing: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
    
    # Print loaded variables (without showing actual values for secrets)
    print("Loaded environment variables:")
    print(f"  TENANT_ID: {'[SET]' if os.getenv('TENANT_ID') else '[NOT SET]'}")
    print(f"  CLIENT_ID: {'[SET]' if os.getenv('CLIENT_ID') else '[NOT SET]'}")
    print(f"  CLIENT_SECRET: {'[SET]' if os.getenv('CLIENT_SECRET') else '[NOT SET]'}")
    print(f"  API_KEYS: {'[SET]' if os.getenv('API_KEYS') else '[NOT SET]'}")
    
    # Return True if all required variables are set
    return not bool(missing_vars)

if __name__ == "__main__":
    load_environment() 