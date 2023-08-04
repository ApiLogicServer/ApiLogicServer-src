from security.authentication_provider.abstract_authentication_provider import Abstract_Authentication_Provider
import sqlalchemy as sqlalchemy
import database.authentication_models as authentication_models
from flask import Flask
import safrs
from safrs.errors import JsonapiError
from dotmap import DotMap  # a dict, but you can say aDict.name instead of aDict['name']... like a row
from sqlalchemy import inspect
from http import HTTPStatus
import logging

# **********************
# sql auth provider
# **********************

db = None
session = None

logger = logging.getLogger(__name__)

class ALSError(JsonapiError):
    
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code


class Authentication_Provider(Abstract_Authentication_Provider):

    @staticmethod
    def get_user(id: str, password: str = "") -> object:
        """
        Must return a row object with attributes:
        
        * name

        * role_list: a list of row objects with attribute name


        Args:
            id (str): _description_
            password (str, optional): _description_. Defaults to "".

        Returns:
            object: row object is a SQLAlchemy row

                * Row Caution: https://docs.sqlalchemy.org/en/14/errors.html#error-bhk3
        """

        def row_to_dotmap(row, row_class):
            rtn_dotmap = DotMap()
            mapper = inspect(row_class)
            for each_column in mapper.columns:
                rtn_dotmap[each_column.name] = getattr(row, each_column.name)
            return rtn_dotmap

        global db, session
        if db is None:
            db = safrs.DB         # Use the safrs.DB for database access
            session = db.session  # sqlalchemy.orm.scoping.scoped_session

        try:
            user = session.query(authentication_models.User).filter(authentication_models.User.id == id).one()
        except Exception as e:
            logger.info(f'*****\nauth_provider FAILED looking for: {id}\n*****\n')
            logger.info(f'excp: {str(e)}\n')
            # raise e
            raise ALSError(f"User {id} is not authorized for this system")
        use_db_row = True
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
