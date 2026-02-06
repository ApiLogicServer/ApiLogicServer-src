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
from jwt.algorithms import RSAAlgorithm
from flask import g


# **********************
# keycloak auth provider
# **********************

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
                logger.info(f'*****\nauth_provider: Create user for: {id}\n*****\n')
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
        # get user / roles  from kc
        try_kc = 'authentication#user_lookup_callback'  # activate favorite experiment
        if try_kc == 'jwt_create':
            """ To retrieve user info from the jwt, you may want to look into these functions:
            https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html
            as used in security/system/authentication.py 
            """
            user = {"id": id, "password": password}  # is this == kwargs?
            user_identity = DotMapX()
            user_identity.id = id
            user_identity.password = password
            # JWT_PRIVATE_KEY must be set to use asymmetric cryptography algorithm "RS256"
            access_token = create_access_token(identity=user_identity)
            # now decode for user/roles info; also see jwt.io
            jswon_jwt = jsonify(access_token=user)  # this returns something with SQLAlchemy row
            pass 

            # jwt = JWTManager(g_flask_app)  # can't use this...
            # fails with: AssertionError: The setup method 'errorhandler' can no longer be called on the application. It has already handled its first request, any changes will not be applied consistently.
            # Make sure all imports, decorators, functions, etc. needed to set up the application are done before running it.
        elif try_kc == "jwt_get_raw_jwt":  # https://flask-jwt-extended.readthedocs.io/en/3.0.0_release/api/
            # verified_jwt = flask_jwt_extended.verify_jwt_in_request()  # blows stack
            # raw_jwt = flask_jwt_extended.get_jwt()  # You must call `@jwt_required()` or `verify_jwt_in_request()` before using this method
            Authentication_Provider.get_jwt_user(id=id)
            pass
        elif try_kc == 'api':  # get jwt for user info & roles
            KC_BASE = Args.instance.keycloak_base
            data = {
                "grant_type": "password",
                "client_id": "alsclient",
                "username" :f"{id}",
                "password": f"{password}"
            }
            msg_url = f'{KC_BASE}/.well-known/openid-configuration'
            resp = requests.post(msg_url, data)
            if resp.status_code == 200:
                resp_data = json.loads(resp.text)
                # no no access_token = resp_data["access_token"]
                # instead, create user/roles UserRoleList, caller will create jwt
                return jsonify(access_token=access_token)
        elif try_kc == 'authentication#user_lookup_callback':
            # from flask import g
            # jwt_data = g.jwt_data  # saved in authentication#user_lookup_callback()
            jwt_data : dict = password
            rtn_user = Authentication_Provider.get_user_from_jwt(jwt_data)
            return rtn_user
