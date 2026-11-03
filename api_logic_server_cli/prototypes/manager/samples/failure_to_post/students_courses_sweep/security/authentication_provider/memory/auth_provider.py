from security.authentication_provider.abstract_authentication_provider import Abstract_Authentication_Provider
from typing import List, Optional
import safrs
from safrs import jsonapi_rpc
from safrs import SAFRSBase
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import create_access_token
from flask import abort

# **********************
# in mem auth provider
# **********************

users = {}

from dataclasses import dataclass

@dataclass
class DataClassUserRole:
    role_name: str


class DataClassUser(safrs.JABase):
    """
    Required machinery for swagger visibility
    """

    def __init__(self, name: str, id: str, client_id: int, password: str):
        self.id = id
        self.password= password
        self.client_id = client_id
        self.name = name
        self.UserRoleList = []

    # called by authentication
    def check_password(self, password=None):
        # print(password)
        return password == self.password

    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def login(self, *args, **kwargs):  # yaml comment => swagger description
        """ # yaml creates Swagger description
            args :
                id: u1
                password: p
        """

        # test using swagger -> try it out (includes sample data, above)

        id = kwargs.get("id", None)
        password = kwargs.get("password", None)

        user = users[id]
        if not user or not user.check_password(password):
            abort(401, "Wrong username or password")

        access_token = create_access_token(identity=user)
        return { "access_token" : access_token}

@dataclass
class DataClassUserZ(SAFRSBase):
    name: str
    client_id: int
    id: str
    password: str
    UserRoleList: Optional [List[DataClassUserRole]] = None

    # called by authentication
    def check_password(self, password=None):
        # print(password)
        return password == self.password

    @classmethod
    @jsonapi_rpc(valid_jsonapi=False)
    def login(cls, *args, **kwargs):
        """
            description: Login - Generate a JWT access token
            args:
                username: user
                password: password
        """
        username = kwargs.get("username", None)
        password = kwargs.get("password", None)

        user = users[id]
        if not user or not user.check_password(password):
            abort(401, "Wrong username or password")

        access_token = create_access_token(identity=user)
        return { "access_token" : access_token}


class Authentication_Provider(Abstract_Authentication_Provider):
    """ Sample auth provider using in-memory data

    This illustrates the basic operation of an auth provider.
    It is mainly used for internal testing, and illustration.
      
    Typically, a real-world  system would use a Keycloak or sql provider.

    Args:
        Abstract_Authentication_Provider (_type_): _description_

    Returns:
        _type_: _description_
    """

    @staticmethod
    def get_user(id: str, password: str) -> object:
        """
        Must return a row object with attributes name and UserRoleList (others as required)
        role_list is a list of row objects with attribute name

        row object is a DotMap (as here) or a SQLAlchemy row
        """
        return users[id]
    

    @staticmethod
    def initialize(api):
        api.expose_object(DataClassUser)

def add_user(name: str, id: int, password: str):
    user = DataClassUser( name=name, id=name, client_id=id, password=password)
    users[name] = user
    return user

sam = add_user("sam", 1, "p")
sam_role_list = [DataClassUserRole(role_name="manager")]
sam.UserRoleList = sam_role_list

aneu = add_user("aneu", 1, "p")
aneu_role_list = [DataClassUserRole(role_name="manager"), DataClassUserRole(role_name="tenant")]
aneu.UserRoleList = aneu_role_list

c1 = add_user("u1", 1, "p")
c1_role_list = [DataClassUserRole(role_name="manager"), DataClassUserRole(role_name="tenant")]
c1.UserRoleList = c1_role_list

c2 = add_user("u2", 2, "p")
c2_role_list = [DataClassUserRole(role_name="manager"), DataClassUserRole(role_name="renter")]
c2.UserRoleList = c1_role_list

m = add_user("mary", 5, "p")
m_role_list = [DataClassUserRole(role_name="manager"), DataClassUserRole(role_name="tenant")]
m.UserRoleList = c1_role_list

sam_row = Authentication_Provider.get_user("sam", "")
print(f'Sam: {sam_row}')

"""
this is a super-simplistic auth_provider, to demonstrate the "provide your own" approach
will typically user provider for sql

to test
1. Create project: nw-
2. Use memory.auth_provider in config.py
3. Disable api/authentication_expose_api.py
"""