"""Keycloak (realm kcals) bearer-token authentication, plus row-level security for the sales role."""
import os
from dataclasses import dataclass

import jwt
from jwt import PyJWKClient

from .models import Customer

KEYCLOAK = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
REALM = os.getenv("KEYCLOAK_REALM", "kcals")
ISSUER = f"{KEYCLOAK}/realms/{REALM}"
# The kcals realm has no user holding a 'sales' role, so these usernames are treated as sales (comma-separated).
SALES_USERS = set(os.getenv("SALES_USERS", "u1").split(","))

_jwks = PyJWKClient(f"{ISSUER}/protocol/openid-connect/certs")


@dataclass
class User:
    name: str
    roles: set

    @property
    def is_sales(self):
        return "sales" in self.roles


def authenticate(token):
    """Verify the token's signature, issuer and expiry; raise jwt.PyJWTError if it is not valid."""
    key = _jwks.get_signing_key_from_jwt(token).key
    claims = jwt.decode(token, key, algorithms=["RS256"], issuer=ISSUER, options={"verify_aud": False})
    name = claims.get("preferred_username", "")
    roles = set(claims.get("realm_access", {}).get("roles", []))
    if name in SALES_USERS:
        roles.add("sales")
    return User(name, roles)


def row_filter(user, model):
    """SQLAlchemy criterion limiting the rows this user may see, or None for all rows."""
    if model is Customer and user.is_sales:
        return (Customer.credit_limit >= 3000) | (Customer.balance > 0)
    return None
