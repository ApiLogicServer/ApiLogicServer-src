import json
import os
import datetime
import base64
import hashlib
import hmac

# Secret key for signing (store securely!)
SECRET_KEY = b"your-secure-secret-key"

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
    print(f"\nlicense_checker.py 0.0: Checking license...")
    license_data = load_license("/config/license.json")
    if not license_data:
        license_data = load_license()
        if not license_data:
            exit(1)

    if not verify_signature(license_data):
        print("License verification failed.")
        exit(1)

    if not is_license_valid(license_data):
        print("License expired or invalid.")
        exit(1)

    print(f"License is valid! Type: {license_data['license_type']}, Expiry: {license_data['expiry']}\n")

if __name__ == "__main__":
    check_license()