import os
import json
from pathlib import Path

def load_credentials():
    """Load credentials from secure storage"""
    # Check if we have a JSON credential file (new approach)
    cred_path = Path("credentials/user_credentials.json")
    if cred_path.exists():
        with open(cred_path, 'r') as f:
            return json.load(f)
    else:
        # Return None if no valid credentials found
        return None

def save_credentials(email, password):
    """Save credentials securely"""
    try:
        # Create credentials directory if it doesn't exist
        os.makedirs("credentials", exist_ok=True)
        
        # Save as JSON for better structure (encrypting sensitive data would be added in full implementation)
        cred_data = {
            "email": email,
            "password": password  # In a production version, this should be encrypted
        }
        
        with open("credentials/user_credentials.json", 'w') as f:
            json.dump(cred_data, f)
            
        return True
    except Exception as e:
        print(f"Error saving credentials: {e}")
        return False

def clear_credentials():
    """Remove stored credentials"""
    try:
        if os.path.exists("credentials/user_credentials.json"):
            os.remove("credentials/user_credentials.json")
            
        return True
    except Exception as e:
        print(f"Error clearing credentials: {e}")
        return False