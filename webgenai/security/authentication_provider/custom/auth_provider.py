import safrs
import os
import uuid
from security.authentication_provider.abstract_authentication_provider import Abstract_Authentication_Provider
from flask import abort
from dataclasses import dataclass

# 
# Simple authentication provider for the containerized version of the webgenie.
# 

@dataclass
class DataClassUserRole:
    role_name: str


class DataClassUser(safrs.JABase):
    """
    Required attributes for authentication susbsystem
    """
    
    UserRoleList = [DataClassUserRole(role_name="sa")] # System Admin role, allows all CRUD operations
    
    def __init__(self, name: str, id: str, client_id: int = None, password: str = None):
        self.id = id
        self.password= password
        self.client_id = client_id
        self.name = name


class Authentication_Provider(Abstract_Authentication_Provider):
    """ 
    Authentication provider, called from authentication.configure_auth
    """
    
    # There is only one user, the admin user, with the password set in the environment variable ADMIN_PASSWORD.
    users = {"admin" : DataClassUser(name="admin", id="admin")}
    # admin.yaml contains the following auth config:
    auth_config = f"authentication:\n  endpoint: http://localhost:{os.getenv('APILOGICPROJECT_PORT', 5657)}/api/auth/login"
    
    @staticmethod  #val - option for auth provider setup
    def configure_auth(flask_app):
        """ 
        Called by authentication.py on server start to initialize JWT_SECRET_KEY
        """
        jwt_secret_key = os.getenv("JWT_SECRET_KEY")
        if not jwt_secret_key:
            jwt_secret_key = str(uuid.uuid4())
            os.environ["JWT_SECRET_KEY"] = jwt_secret_key
        flask_app.config["JWT_SECRET_KEY"] = jwt_secret_key
        flask_app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']

    @classmethod
    def get_user(cls, id: str, token_or_password = None) -> object:
        """
        Retrieve a user by ID.
        """
        if id in cls.users:
            return cls.users[id]
        abort(403, "Invalid Authentication")
    
    @classmethod
    def check_password(cls, user: DataClassUser, password: str):
        """
        Check if the provided password matches the admin password.
        The password is set in the environment variable ADMIN_PASSWORD.
        """
        if password == os.getenv("ADMIN_PASSWORD"):
            return cls.get_user(user.id)
