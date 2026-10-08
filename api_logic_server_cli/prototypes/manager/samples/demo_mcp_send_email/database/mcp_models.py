# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  October 08, 2026 08:16:35
# Database: sqlite:////Users/val/dev/genai-logic/ApiLogicServer-dev/build_and_test/genai-logic/demo_mcp_send_email/database/mcp_db.sqlite
# Dialect:  sqlite
#
# mypy: ignore-errors
########################################################################################################################
 
from database.system.SAFRSBaseX import SAFRSBaseX, TestBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy, os
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from typing import List

db = SQLAlchemy() 
Basemcp = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Basemcp.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *

if os.getenv('APILOGICPROJECT_NO_FLASK') is None or os.getenv('APILOGICPROJECT_NO_FLASK') == 'None':
    Base = SAFRSBaseX   # enables rules to be used outside of Flask, e.g., test data loading
else:
    Base = TestBase     # ensure proper types, so rules work for data loading
    print('*** Models.py Using TestBase ***')



class SysMcp(Base):  # type: ignore
    __tablename__ = 'sys_mcp'
    _s_collection_name = 'mcp-SysMcp'  # type: ignore
    __bind_key__ = 'mcp'

    id = Column(Integer, primary_key=True)
    request = Column(String)
    request_prompt = Column(String)
    completion = Column(String)

    # parent relationships (access parent)

    # child relationships (access children)
