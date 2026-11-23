from security.authentication_provider.abstract_authentication_provider import Abstract_Authentication_Provider
import sqlalchemy as sqlalchemy
import database.database_discovery.authentication_models as authentication_models
from flask import Flask
import safrs
from safrs.errors import JsonapiError
from dotmap import DotMap  # a dict, but you can say aDict.name instead of aDict['name']... like a row
from sqlalchemy import inspect
from http import HTTPStatus
import logging
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
# from flask_jwt_extended import jwt_required
from flask_jwt_extended import jwt_required as jwt_required_ori
import flask_jwt_extended as flask_jwt_extended
from flask import jsonify
import requests  # not working - 404
import json
import sys
import time
import jwt
try:
    from jwt.algorithms import RSAAlgorithm
except ImportError:
    RSAAlgorithm = None  # cryptography not available (e.g., Windows ARM64)
from flask import g


# **********************
# keycloak auth provider
# **********************

def safe_log(value: object) -> str:
    """ Strip CR/LF from a value before logging it, to prevent log injection (CWE-117)
        when the value may come from external/user input (e.g. request args, URL path segments).

        Duplicated from api/system/api_utils.py: this module is imported by config/config.py
        during behave test collection, where features/steps/api.py (a behave step-definitions
        file) shadows the project's api/ package on sys.path, breaking `from api.system...` imports.
    """
    return str(value).replace('\r', '').replace('\n', ' ')

db = None
session = None

logger = logging.getLogger(__name__)

class ALSError(JsonapiError):

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code


class DotMapX(DotMap):
    """ DotMap, with extended support for auth providers """
    def check_password(self, password=None):
        # print(password)
        return password == self.password_hash


class Authentication_Provider(Abstract_Authentication_Provider):

    @staticmethod
    def configure_auth(flask_app: Flask):
        """ Called by authentication.py on server start, to 
        - initialize jwt
        - establish Flask end points for login.

        Args:
            flask_app (Flask): _description_
            database (object): _description_
            method_decorators (object): _description_
        Returns:
            _type_: (no return)
        """
        flask_app.config['JWT_ALGORITHM'] = 'RS256'
        flask_app.config["JWT_PUBLIC_KEY"] = Authentication_Provider.get_jwt_public_key('RS256')
        do_priv_key = False
        if do_priv_key:
            flask_app.config["JWT_PRIVATE_KEY"] = \
                Authentication_Provider.get_jwt_pubkey()
        return

    @staticmethod
    def get_jwt_public_key(alg, kid=None):
        """
            Retrieve the public key of the JWK keypair used by keycloak to sign the JWTs.
            JWTs signed with this key are trusted by ALS.
        """
        from flask import jsonify, request
        from config.config import Args  # circular import error if at top
        
        jwks_uri = Args.instance.keycloak_base_url + '/protocol/openid-connect/certs'
        for i in range(100):
            # we retry a couple of times in case there are connection problems
            try:
                keys = requests.get(jwks_uri).json()['keys']
                break
            except:
                # waiting .. keycloak may still be sleeping
                time.sleep(1)
        else:
            print(f'Failed to load jwks_uri {jwks_uri}')
            sys.exit(1)
        for key in keys:
            # loop over all keys until we find the one we're looking for
            if key['alg'] == alg or key['kid'] == kid:
                logger.info(f"Found JWK: {key['kid']}")
                return RSAAlgorithm.from_jwk(json.dumps(key))
        print(f"Couldn't find key with ALG {alg} or kid {kid}")
        exit(1)

    # @jwt_required   # so, maybe jwt requires no pwd?
    def get_jwt_user(id: str) -> object:  # for experiment: jwt_get_raw_jwt
        from flask_jwt_extended import get_jwt
        from flask import has_request_context
        
        return_jwt = None
        if has_request_context():
            # flask_jwt_extended.verify_jwt_in_request()  # blows stack; if omitted, following fails
            # return_jwt = raw_jwt = flask_jwt_extended.get_jwt()  # You must call `@jwt_required()` or `verify_jwt_in_request()` before using this method
            request_global_debug = g
            return_jwt = g.als_jwt  # it's not set, lost since different request??
        else:
            pass  # TODO - what to do here?
        return return_jwt

    @staticmethod
    def get_user_from_jwt(jwt_data: dict) -> object:
        """return DotMapX (user+roles) from jwt_data

        Args:
            jwt_data (dict): jwt, as saved in password

        Returns:
            object: ApiLogicServer user (with roles) DotMapX object
        """
        rtn_user = DotMapX()
        rtn_user.client_id = 1  # hack until user data in place
        rtn_user.name = jwt_data["preferred_username"]
        rtn_user.password_hash = None

        # get extended properties (e.g, client_id in sample app)
        if  "attributes" in jwt_data:
            # return rtn_user
            attributes = jwt_data['attributes']
            for each_name, each_value in attributes.items():
                rtn_user[each_name] = each_value

        rtn_user.UserRoleList = []
        role_names = jwt_data["realm_access"]["roles"]
        # role_names.append("customer") #Temp role for testing
        for each_role_name in role_names:
            each_user_role = DotMapX()
            each_user_role.role_name = each_role_name
            rtn_user.UserRoleList.append(each_user_role)
        return rtn_user
    
    @staticmethod
    def get_user(id: str, password: str = "") -> object:
        """ Must return a row object or UserAndRole(DotMap) with attributes:
        * name
        * role_list: a list of row objects with attribute name

        Args:
            id (str): the user login id
            password (str, optional): for keycloak, there is no password, so use this for jwt_data.

        Returns:
            object: row object is a SQLAlchemy row
        """        
        from config.config import Args  # circular import error if at top
        
        use_db = False
        if use_db: # old code - get user info from sqlite db
            global db, session
            def row_to_dotmap(row, row_class):
                rtn_dotmap = DotMapX() 
                mapper = inspect(row_class)
                for each_column in mapper.columns:
                    rtn_dotmap[each_column.name] = getattr(row, each_column.name)
                return rtn_dotmap
            if db is None:
                db = safrs.DB         # Use the safrs.DB for database access
                session = db.session  # sqlalchemy.orm.scoping.scoped_session
        
            user = session.query(authentication_models.User).filter(authentication_models.User.id == id).one_or_none()
            if user is None:  #Val - change note to remove try, use 1st user if none (as a temp hack?)
                logger.info(f'*****\nauth_provider: Create user for: {safe_log(id)}\n*****\n')
                user = session.query(authentication_models.User).first()
                return user
            logger.info(f'*****\nauth_provider: User: {user}\n*****\n')
            use_db_row = True  # prior version did not return class with check_password; now fixed
            if use_db_row:
                return user
            else:
                pass
                rtn_user = row_to_dotmap(user, authentication_models.User)
                rtn_user.UserRoleList = []
                user_roles = getattr(user, "UserRoleList")
                for each_row in user_roles:
                    each_user_role = row_to_dotmap(each_row, authentication_models.UserRole)
                    rtn_user.UserRoleList.append(each_user_role)
                return rtn_user  # returning user fails per caution above
        # get user / roles from kc.
        #
        # get_user() is called from two different places in security/system/authentication.py,
        # with two different meanings for `password` — dispatch on its actual type rather than
        # a hardcoded switch (a fixed switch here previously forced every call down the
        # user_lookup_callback branch below, crashing login() with a real password: see
        # basic_demo_eai session notes, Sep 2026, TypeError: string indices must be integers):
        #
        #   1. login()'s POST /api/auth/login: `password` is the real, plaintext password.
        #      Nothing has been verified yet — authenticate it against Keycloak's own token
        #      endpoint, below.
        #   2. user_lookup_callback (runs on every subsequent @jwt_required() request, to
        #      reload the user from the token already presented): `password` is actually
        #      jwt_data, the already-decoded, already-verified JWT claims dict for this
        #      request — nothing to authenticate, just build the User+Roles object.
        if isinstance(password, dict):
            jwt_data: dict = password
            return Authentication_Provider.get_user_from_jwt(jwt_data)

        # Real login: exchange id/password for a token via Keycloak's password grant. A 200
        # response IS the password check — see check_password() below, which trusts this
        # result instead of comparing against a local hash Keycloak never gives us.
        kc_base_url = Args.instance.keycloak_base_url  # e.g. http://localhost:8080/realms/kcals
        client_id = Args.instance.keycloak_client_id
        token_url = f'{kc_base_url}/protocol/openid-connect/token'
        resp = requests.post(token_url, data={
            "grant_type": "password",
            "client_id": client_id,
            "username": id,
            "password": password,
        })
        if resp.status_code != 200:
            logger.info(f"Keycloak login failed for user {safe_log(id)}: {resp.status_code}")
            return None
        access_token = resp.json()["access_token"]
        # Keycloak already verified the credentials (that's what the 200 above means) —
        # decode the claims without re-verifying the signature a second time here.
        claims = jwt.decode(access_token, options={"verify_signature": False})

        # Hand the REAL Keycloak-issued token back to login() (security/system/authentication.py)
        # via request-scoped `g`, instead of it minting a new one with create_access_token():
        # this provider's JWTManager is configured with Keycloak's PUBLIC key only (see
        # configure_auth() above) so it can verify incoming Keycloak tokens, but has no
        # private key to sign a new RS256 token with — create_access_token() would raise
        # RuntimeError: JWT_PRIVATE_KEY must be set. Returning Keycloak's own token is also
        # the more correct design: it's the token user_lookup_callback will verify on every
        # subsequent request anyway.
        g.access_token = access_token
        return Authentication_Provider.get_user_from_jwt(claims)

    @staticmethod
    def check_password(user: object, password) -> bool:
        """checks whether user-supplied password matches

        Keycloak already authenticated the credentials inside get_user() above (a real
        password there means a live call to Keycloak's token endpoint, not a local hash
        compare) — a resolved, truthy user here already proves the login succeeded.

        Args:
            user (object): DotMapX returned by get_user(), or None if Keycloak rejected the login
            password: unused — kept for signature parity with the abstract/SQL providers

        Returns:
            bool: whether the login succeeded
        """
        return user is not None
