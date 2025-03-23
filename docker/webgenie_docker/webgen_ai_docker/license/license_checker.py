import json
import os
import datetime
import base64
import hashlib
import hmac
import jwt
from typing import Optional, Dict, Any

# Secret key for signing (store securely!)
SECRET_KEY = b"fe3d2e7c-2c19-4992-8d7f-f31a0d0c96c6"

def load_license(license_path="license.json"):
    """Load the license file from disk."""
    if not os.path.exists(license_path):
        print(f"License file not found at {license_path}.")
        return None
    try:
        with open(license_path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Invalid license file format.")
        return None

def verify_signature(license_data):
    """Verify that the license signature is valid."""
    signature = license_data.pop("signature", None)  # Extract signature
    if not signature:
        print("Missing signature.")
        return False

    # Create a hash-based message authentication code (HMAC)
    license_string = json.dumps(license_data, sort_keys=True).encode()
    expected_signature = base64.b64encode(hmac.new(SECRET_KEY, license_string, hashlib.sha256).digest()).decode()

    if signature != expected_signature:
        print("Invalid license signature. Possible tampering detected.")
        return False

    return True

def is_license_valid(license_data):
    """Check if the license is still valid (not expired)."""
    expiry_date = license_data.get("expiry")
    if not expiry_date:
        print("No expiry date found in license.")
        return False

    try:
        expiry_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid expiry date format.")
        return False

    if expiry_date < datetime.datetime.now():
        print("License expired.")
        return False

    return True

def check_license():
    """Main function to validate the license."""
    print(f"\nlicense_checker.py 1.0: Checking license...")
    license_key = os.getenv("GENAI_LOGIC_APIKEY")

    if not license_key:
        print("License GENAI_LOGIC_APIKEY not found.")
        exit(1)
    try:
        decoded_payload = verify_api_key(api_key=license_key)
        print("WebGenAI License is valid!")
        print(f"License belongs to: {decoded_payload['company_name']}")
        print(f"License type: {decoded_payload['license_type']}")
        print(f"License expires on: {datetime.datetime.fromtimestamp(decoded_payload['exp']).isoformat()}")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print(f"WebGenAI License validation failed: {str(e)}")
        exit(1)

def verify_api_key(api_key: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT API key.
    
    Args:
        api_key: The JWT API key to verify
        
    Returns:
        The decoded payload if valid
        
    Raises:
        jwt.InvalidTokenError: If the token is invalid
        jwt.ExpiredSignatureError: If the token has expired
    """
    try:
        return jwt.decode(api_key, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as ee:
        raise jwt.ExpiredSignatureError("API key has expired") from ee
    except jwt.InvalidTokenError as it:
        raise jwt.InvalidTokenError("Invalid API key") from it

if __name__ == "__main__":
    check_license()
    '''
    ## GOOD API KEY TEST
    try:
        APIKEY = os.getenv("GENAI_LOGIC_APIKEY")
        decoded_payload = verify_api_key(APIKEY)
        print("API Key is valid!")
        print(f"API Key belongs to: {decoded_payload['company_name']}")
        print(f"License type: {decoded_payload['license_type']}")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print(f"API Key validation failed: {str(e)}")

    # BAD KEY TEST
    try:
        decoded_payload = verify_api_key("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMmZjNTA2ZS1jN2M4LTQ1NjQtYjI4MC01MGM5N") #BAD KEY
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print(f"API Key validation failed: {str(e)}")
'''
