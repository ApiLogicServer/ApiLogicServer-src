# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask import abort
from safrs import jsonapi_rpc
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import create_access_token

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  June 07, 2024 13:20:13
# Database: sqlite:////~/dev/ApiLogicServer/ApiLogicServer-dev/servers/ApiLogicProject/database/authentication_db.sqlite
# Dialect:  sqlite
#
# mypy: ignore-errors
########################################################################################################################
 
from database.system.SAFRSBaseX import SAFRSBaseX
from flask_login import UserMixin
import safrs, flask_sqlalchemy
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from typing import List

db = SQLAlchemy() 
Baseauthentication = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Baseauthentication.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *



class Role(SAFRSBaseX, Baseauthentication, db.Model, UserMixin):  # type: ignore
    __tablename__ = 'Role'
    _s_collection_name = 'authentication-Role'  # type: ignore
    __bind_key__ = 'authentication'

    name = Column(String(64), primary_key=True)
    allow_client_generated_ids = True

    # parent relationships (access parent)

    # child relationships (access children)
    UserRoleList : Mapped[List["UserRole"]] = relationship(back_populates="Role")

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class User(SAFRSBaseX, Baseauthentication, db.Model, UserMixin):  # type: ignore
    __tablename__ = 'User'
    _s_collection_name = 'authentication-User'  # type: ignore
    __bind_key__ = 'authentication'

    name = Column(String(128))
    client_id = Column(Integer)
    id = Column(String(64), primary_key=True, unique=True)
    username = Column(String(128))
    password_hash = Column(String(200))
    region = Column(String(32))
    allow_client_generated_ids = True

    # parent relationships (access parent)

    # child relationships (access children)
    UserRoleList : Mapped[List["UserRole"]] = relationship(back_populates="user")
    
    # authentication-provider extension - password check
    def check_password(self, password=None):
        # print(password)
        return password == self.password_hash
    
    # authentication-provider extension - login endpoint (e.g., for swagger)

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

        user = cls.query.filter_by(id=username).one_or_none()
        if not user or not user.check_password(password):
            abort(401, "Wrong username or password")

        access_token = create_access_token(identity=user)
        return { "access_token" : access_token}

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class UserRole(SAFRSBaseX, Baseauthentication, db.Model, UserMixin):  # type: ignore
    __tablename__ = 'UserRole'
    _s_collection_name = 'authentication-UserRole'  # type: ignore
    __bind_key__ = 'authentication'

    user_id = Column(ForeignKey('User.id'), primary_key=True)
    notes = Column(Text)
    role_name = Column(ForeignKey('Role.name'), primary_key=True)
    allow_client_generated_ids = True

    # parent relationships (access parent)
    Role : Mapped["Role"] = relationship(back_populates=("UserRoleList"))
    user : Mapped["User"] = relationship(back_populates=("UserRoleList"))

    # child relationships (access children)

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_
