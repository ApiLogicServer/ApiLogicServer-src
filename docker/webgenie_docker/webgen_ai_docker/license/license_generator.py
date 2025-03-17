import jwt
import datetime
import uuid
from typing import Optional, Dict, Any


class JWTAPIKeyGenerator:
    def __init__(self, secret_key: str = None):
        """
        Initialize the JWT API Key Generator with a secret key.
        
        Args:
            secret_key: The secret key used to sign the JWT tokens
        """
        self.secret_key =  secret_key or  b"fe3d2e7c-2c19-4992-8d7f-f31a0d0c96c6"
    
    def generate_api_key(
        self,
        name: str,
        license_type: str,
        company_name: str,
        expiration_days: int = 365,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate a JWT API key with the specified claims.
        
        Args:
            name: Name associated with the API key
            license_type: Type of license (e.g., "basic", "premium", "enterprise")
            company_name: Name of the company
            expiration_days: Number of days until the API key expires
            additional_claims: Any additional claims to include in the JWT
            
        Returns:
            Dictionary containing the API key and its details
        """
        # Calculate expiration date
        current_time = datetime.datetime.utcnow()
        expiration_date = current_time + datetime.timedelta(days=expiration_days)
        
        # Create payload with required fields
        payload = {
            "sub": str(uuid.uuid4()),  # Unique identifier for this key
            "iat": current_time,
            "exp": expiration_date,
            "name": name,
            "license_type": license_type,
            "company_name": company_name,
        }
        
        # Add additional claims if provided
        if additional_claims:
            payload |= additional_claims
        
        # Generate the JWT token
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # Return the API key and its details
        return {
            "api_key": token,
            "name": name,
            "license_type": license_type,
            "company_name": company_name,
            "expiration_date": expiration_date.isoformat(),
            "created_at": current_time.isoformat(),
        }
if __name__ == "__main__":
    # Initialize with a secure secret key (in production, store this securely)
    generator = JWTAPIKeyGenerator()
    
    # Generate an API key
    api_key_data = generator.generate_api_key(
        name="API Key for Registration",
        license_type="TRIAL",
        company_name="Acme Corporation",
        expiration_days=90,
        additional_claims={"License_partner": "terramaster"}
    )
    
    print("Generated API Key:")
    print(f"export GENAI_LOGIC_APIKEY={api_key_data['api_key']}")
    print(f"Name: {api_key_data['name']}")
    print(f"License Type: {api_key_data['license_type']}")
    print(f"Company Name: {api_key_data['company_name']}")  