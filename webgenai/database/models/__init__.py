from sqlalchemy import Column, DECIMAL, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database.system.SAFRSBaseX import SAFRSBaseX
from flask_login import UserMixin
import safrs, flask_sqlalchemy
import os
from safrs import jsonapi_attr, jsonapi_rpc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy import func
from typing import List
from pathlib import Path
from sqlalchemy.sql import func
from ulid import ULID
from safrs.util import classproperty
from flask import g, has_request_context, abort
from flask_jwt_extended import get_jwt_identity, jwt_required, JWTManager, get_jwt, verify_jwt_in_request
from sqlalchemy import create_engine, text
import logging 
from werkzeug.utils import secure_filename
from pathlib import Path
from sqlalchemy.dialects.sqlite import *

log = logging.getLogger("api_logic_server_app")
log.setLevel(logging.DEBUG) 
db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata


PROJ_ROOT = Path(os.getenv("PROJ_ROOT","/opt/projects"))
FIRST_PORT = 6000
UPLOAD_ROOT = f"{PROJ_ROOT}/wgupload"

def apifab_dec(func):
    """
    Decorator to authorize user, decorates all API endpoints
    """
    def auth_dec(*args, **kwargs):
        if has_request_context():
            # authorize user
            pass
        return func(*args, **kwargs)
    return auth_dec


def secure_filename_webgenai(name):
    """
    Function to secure a filename, used to create a project name and prompt file
    """
    return secure_filename(name) or "genai_apifab"


class BaseModel(SAFRSBaseX, Base):
    __abstract__ = True


from .project import Project

class User(BaseModel):
    __tablename__ = 'users'
    _s_collection_name = 'User'  # type: ignore
    __bind_key__ = 'None'

    custom_decorators = [ apifab_dec ]
    id = Column(String, primary_key=True)
    username = Column(String)
    email = Column(String)

    def __init__(self, *args, **kwargs):
        return BaseModel.__init__(self, *args, **kwargs)

    ProjectList : Mapped[List["Project"]] = relationship(back_populates="user")
    FileList : Mapped[List["File"]] = relationship(back_populates="user")


class File(BaseModel):
    __tablename__ = "files"
    _s_collection_name = 'File'
    custom_decorators = [ apifab_dec ]
    
    id = Column(String(50), primary_key=True)
    name = Column(String(50), default="file")
    Type = Column(Text)
    location = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    user_id = Column(ForeignKey('users.id'))
    project_id = Column(ForeignKey('projects.id'))
    
    user : Mapped["User"] = relationship(back_populates=("FileList"))
    project : Mapped["Project"] = relationship(back_populates=("FileList"))

    @jsonapi_attr
    def path(self):
        return f"{PROJ_ROOT}/uploads/{self.id}/{self.name}"
    
    @jsonapi_attr
    def connection_string(self):
        self.location = f"{UPLOAD_ROOT}/{self.id}/{self.name}"
        if self.name and str(self.name).endswith(".xlsx"):
            return f"excel:///{self.location}"
        return f"sqlite:///{self.location}"