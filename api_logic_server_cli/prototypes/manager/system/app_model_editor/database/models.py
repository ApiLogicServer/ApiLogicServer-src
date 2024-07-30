# coding: utf-8
from sqlalchemy import Boolean, Column, ForeignKey, ForeignKeyConstraint, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  June 14, 2024 15:03:30
# Database: sqlite:////Users/tylerband/ontimize/ontimize_yaml_view/database/db.sqlite
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
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *



class Entity(SAFRSBaseX, Base):
    __tablename__ = 'entity'
    _s_collection_name = 'Entity'  # type: ignore
    __bind_key__ = 'None'

    name = Column(String(80), primary_key=True, nullable=False)
    title = Column(String(100))
    pkey = Column(String(100))
    favorite = Column(String(100))
    info_list = Column(Text)
    info_show = Column(Text)
    exclude = Column(Boolean, server_default=text("false"))
    new_template = Column(String(80))
    home_template = Column(String(80))
    detail_template = Column(String(80))
    mode = Column(String(10), server_default=text("'tab'"))
    menu_group = Column(String(25))
    allow_client_generated_ids = True

    # parent relationships (access parent)

    # child relationships (access children)
    EntityAttrList : Mapped[List["EntityAttr"]] = relationship(back_populates="entity")
    TabGroupList : Mapped[List["TabGroup"]] = relationship(foreign_keys='[TabGroup.tab_entity]', back_populates="entity")
    TabGroupList1 : Mapped[List["TabGroup"]] = relationship(foreign_keys='[TabGroup.entity_name]', back_populates="entity1")

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class GlobalSetting(SAFRSBaseX, Base):
    __tablename__ = 'global_settings'
    _s_collection_name = 'GlobalSetting'  # type: ignore
    __bind_key__ = 'None'

    name = Column(String(100), primary_key=True)
    value = Column(String(8000), nullable=False)
    description = Column(Text)
    allow_client_generated_ids = True

    # parent relationships (access parent)

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


class Root(SAFRSBaseX, Base):
    __tablename__ = 'root'
    _s_collection_name = 'Root'  # type: ignore
    __bind_key__ = 'None'

    id = Column(Integer, primary_key=True)
    about_changes = Column(Text)
    api_root = Column(String(1000))
    api_auth_type = Column(String(100))
    api_auth = Column(String(1000))
    about_date = Column(String(100))

    # parent relationships (access parent)

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


class Template(SAFRSBaseX, Base):
    __tablename__ = 'template'
    _s_collection_name = 'Template'  # type: ignore
    __bind_key__ = 'None'

    name = Column(String(100), primary_key=True)
    description = Column(Text)
    allow_client_generated_ids = True

    # parent relationships (access parent)

    # child relationships (access children)
    EntityAttrList : Mapped[List["EntityAttr"]] = relationship(back_populates="template")

    @jsonapi_attr
    def _check_sum_(self):  # type: ignore [no-redef]
        return None if isinstance(self, flask_sqlalchemy.model.DefaultMeta) \
            else self._check_sum_property if hasattr(self,"_check_sum_property") \
                else None  # property does not exist during initialization

    @_check_sum_.setter
    def _check_sum_(self, value):  # type: ignore [no-redef]
        self._check_sum_property = value

    S_CheckSum = _check_sum_


class YamlFiles(SAFRSBaseX, Base):
    __tablename__ = 'yaml_files'
    _s_collection_name = 'YamlFiles'  # type: ignore
    __bind_key__ = 'None'

    name = Column(String(100),primary_key=True, nullable=False)
    content = Column(Text)
    upload_flag = Column(Boolean, server_default=text("FALSE"))
    download_flag = Column(Boolean, server_default=text("FALSE"))
    size = Column(Integer)
    downloaded = Column(Text)

    # parent relationships (access parent)

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


class EntityAttr(SAFRSBaseX, Base):
    __tablename__ = 'entity_attr'
    _s_collection_name = 'EntityAttr'  # type: ignore
    __bind_key__ = 'None'
    __table_args__ = (
        ForeignKeyConstraint(['entity_name'], ['entity.name']),
    )

    entity_name = Column(String(80), primary_key=True, nullable=False)
    attr = Column(String(80), primary_key=True, nullable=False)
    label = Column(String(100))
    issearch = Column(Boolean, server_default=text("false"))
    issort = Column(Boolean, server_default=text("false"))
    thistype = Column(String(50), nullable=False)
    template_name = Column(ForeignKey('template.name'), server_default=text("'text'"))
    tooltip = Column(Text)
    isrequired = Column(Boolean, server_default=text("true"))
    isenabled = Column(Boolean, server_default=text("true"))
    exclude = Column(Boolean, server_default=text("false"))
    visible = Column(Boolean, server_default=text("true"))
    default_value = Column(String(100))
    allow_client_generated_ids = True

    # parent relationships (access parent)
    template : Mapped["Template"] = relationship(back_populates=("EntityAttrList"))
    entity : Mapped["Entity"] = relationship(back_populates=("EntityAttrList"))

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


class TabGroup(SAFRSBaseX, Base):
    __tablename__ = 'tab_group'
    _s_collection_name = 'TabGroup'  # type: ignore
    __bind_key__ = 'None'
    __table_args__ = (
        ForeignKeyConstraint(['entity_name'], ['entity.name']),
    )

    entity_name = Column(String(80), primary_key=True, nullable=False)
    tab_entity = Column(ForeignKey('entity.name'), primary_key=True, nullable=False)
    direction = Column(String(6), primary_key=True, nullable=False)
    label = Column(String(80), primary_key=True, nullable=False)
    fkeys = Column(String(80), nullable=False)
    name = Column(String(80), nullable=False)
    exclude = Column(Boolean, server_default=text("false"))
    allow_client_generated_ids = True

    # parent relationships (access parent)
    entity : Mapped["Entity"] = relationship(foreign_keys='[TabGroup.tab_entity]', back_populates=("TabGroupList"))
    entity1 : Mapped["Entity"] = relationship(foreign_keys='[TabGroup.entity_name]', back_populates=("TabGroupList1"))

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
