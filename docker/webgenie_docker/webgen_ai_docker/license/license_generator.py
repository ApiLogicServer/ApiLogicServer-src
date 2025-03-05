import json
import base64
import hashlib
import hmac

SECRET_KEY = b"your-secure-secret-key"

def generate_license(license_key, license_type, expiry_date):
    """Generate a signed license JSON file."""
    license_data = {
        "license_key": license_key,
        "license_type": license_type,
        "expiry": expiry_date
    }

    # Create a secure HMAC signature
    license_string = json.dumps(license_data, sort_keys=True).encode()
    signature = base64.b64encode(hmac.new(SECRET_KEY, license_string, hashlib.sha256).digest()).decode()
    license_data["signature"] = signature

    # Save the license to a file
    with open("license.json", "w") as file:
        json.dump(license_data, file, indent=4)

    print(f"License generated successfully! - {file}")

# Example: Generate a license
generate_license("ABCD-1234-EFGH-5678", "PRO", "2025-12-31")