import safrs
import flask_sqlalchemy
import os
import json
import subprocess

from sqlalchemy import Column, DECIMAL, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from database.system.SAFRSBaseX import SAFRSBaseX
from flask_login import UserMixin
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
from flask import g, has_request_context, abort, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, JWTManager, get_jwt, verify_jwt_in_request
from sqlalchemy import create_engine, text
import logging 
from werkzeug.utils import secure_filename
from pathlib import Path
from sqlalchemy.dialects.sqlite import *
from config.config import Config
import subprocess
from database.models import Base, SAFRSBaseX
import glob

log = safrs.log

WG_SECTIONS_DIR = Path("/opt/webgenai/simple-spa/src/components/sections")
GEN_COMPONENT_SCRIPT = '/opt/webgenai/database/models/util/gen_component.py'
PROJ_ROOT = Path(os.getenv("PROJ_ROOT","/opt/projects/by-ulid"))
ULID_ROOT = PROJ_ROOT

class BaseModel(SAFRSBaseX, Base):
    __abstract__ = True


class SPASection(BaseModel):
    __tablename__ = 'spa_sections'
    _s_collection_name = 'SPASection'
    
    id = Column(String, primary_key=True)
    name = Column(Text, nullable=False)
    title = Column(Text)
    subtitle = Column(Text)
    label = Column(Text)
    Type = Column(Text)
    paragraph = Column(Text)
    content = Column(Text)
    #style = Column(JSON)
    background = Column(Text)
    template = Column(Text)
    order = Column(Integer, default=-1)
    hidden = Column(Boolean, default=False)
    
    page_id = Column(ForeignKey('spa_pages.id'))
    page : Mapped["SPAPage"] = relationship(back_populates=("SectionList"))


class SPAPage(BaseModel):
    __tablename__ = 'spa_pages'
    _s_collection_name = 'SPAPage'
    
    id = Column(String, primary_key=True)
    name = Column(Text, nullable=False)
    contact = Column(Text, nullable=False)
    SectionList : Mapped[List["SPASection"]] = relationship(back_populates="page")


class SPAComponent(BaseModel):
    __tablename__ = 'spa_components'
    _s_collection_name = 'SPAComponent'
    
    id = Column(String, primary_key=True)
    Type = Column(Text)
    prompt = Column(Text)
    name = Column(Text)
    code = Column(Text)
    user_comments = Column(Text)
    ai_comments = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    section_id = Column(ForeignKey('spa_sections.id'))
    parent_id = Column(ForeignKey('spa_components.id'))
    parent : Mapped["SPAComponent"] = relationship(back_populates=("ChildList"))
    parent: Mapped["SPAComponent"] = relationship('SPAComponent', remote_side=[id], backref='ChildList')
    
    def __init__(self, *args, **kwargs):
        kwargs['id'] = self.id = str(ULID())
        if not has_request_context():
            return BaseModel.__init__(self, *args, **kwargs)
        
        log.info(f"Generating component {kwargs}")
        project_id = kwargs.get('project_id')
        if not project_id:
            raise Exception("project_id is required")
        
        if not project_id in os.listdir(ULID_ROOT) and not project_id in __file__:
            raise Exception("project_id is invalid")
        
        type = kwargs.get('Type')
        if type == "template":
            pass
        if type == "prompt":
            pass
        if type == "save":
            return self.save(**kwargs)
        prompt = kwargs.get('prompt')
        if prompt:
            return self.handle_prompt(**kwargs)
        
        return BaseModel.__init__(self, *args, **kwargs)
    
    @jsonapi_rpc(http_methods=['POST'], valid_jsonapi=False)
    def apply(self, *args, **kwargs):
        log.info(f"writing code to file {self.tsx_path}")
        with open(WG_SECTIONS_DIR / f"HighLight.tsx", 'w') as f:
            f.write(self.code)
        with open(self.tsx_path.resolve(), 'w') as f:
            f.write(self.code)
        return self.code
    
    def handle_prompt(self, **kwargs):
        prompt = kwargs.get('prompt')
        project_id = kwargs.get('project_id')
        log.info(f"Handling prompt: '{prompt}'")
        kwargs['Type'] = "prompt"
        # TODO: check project ownership!!!
        output = subprocess.check_output(['python', GEN_COMPONENT_SCRIPT, project_id, prompt, self.id], text=True)
        try:
            log.info(f"Generated component with id '{self.id}': {output}")
            result = json.loads(output)
            with open(result["highlight_tsx"], 'r') as f:
                kwargs["code"] = f.read()
        except Exception as e:
            safrs.log.error(f"Error generating component: {e}")
            raise e
        return BaseModel.__init__(self, **kwargs)
    
    def save(self, **kwargs):
        log.info(f"Save file {self.tsx_path} to {self.id}")
        with open(WG_SECTIONS_DIR / f"HighLight.tsx", 'r') as f:
            kwargs["code"] = f.read()
        kwargs["Type"] = "template"
        return BaseModel.__init__(self, **kwargs)
    
    @jsonapi_attr
    def project_id(self):
        project_id = Path(__file__).parent.parent.parent.name
        return project_id
    
    @jsonapi_attr
    def tsx_path(self):
        #return Path(f"{ULID_ROOT}/{self.project_id}/ui/spa/gen_components/{self.id}/HighLight.tsx")
        return Path(f"{ULID_ROOT}/{self.project_id}/ui/spa/src/components/sections/HighLight.0.tsx")


def add_templates(session):
    # Iterate over all files in the directory
    for file_path in sorted(glob.glob(f"{WG_SECTIONS_DIR}/templates/*tsx")):
        # Extract the filename
        filename = os.path.basename(file_path)
        if SPAComponent.query.filter(SPAComponent.name == filename).first():
            continue
        # Read the file content
        with open(file_path, 'r') as file:
            file_content = file.read()
        log.info(f"Adding template {filename}")
        # Create a new SPAComponent instance
        new_component = SPAComponent(
            name=filename,
            code=file_content,
            project_id="default",
            Type="template",
            prompt="WG System Generated",
        )
        
        # Add the new component to the session and commit
        session.add(new_component)
    session.commit()

from sqlalchemy.orm import sessionmaker, scoped_session
# TODO, move this to a separate file
engine = create_engine("sqlite:///" + str(Path(__file__).parent.parent) + "/db.sqlite")
with engine.connect() as connection:
    Base.metadata.create_all(engine)


# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a scoped session
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Using the engine connection in a 'with' statement
with engine.connect() as connection:
    # Begin a transaction
    with connection.begin() as transaction:
        # Create a new session 
        session = Session(bind=connection)
        add_templates(session)