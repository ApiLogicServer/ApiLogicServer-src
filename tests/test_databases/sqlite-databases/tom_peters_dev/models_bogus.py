# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  January 17, 2025 20:15:21
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/servers/t_peters_def/database/db.sqlite
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
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *

if os.getenv('APILOGICPROJECT_NO_FLASK') is None or os.getenv('APILOGICPROJECT_NO_FLASK') == 'None':
    Base = SAFRSBaseX   # enables rules to be used outside of Flask, e.g., test data loading
else:
    Base = TestBase     # ensure proper types, so rules work for data loading
    print('*** Models.py Using TestBase ***')



class Tag(Base):  # type: ignore
    __tablename__ = 'tags'
    _s_collection_name = 'Tag'  # type: ignore

    id = Column(String(36), primary_key=True, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    allow_client_generated_ids = True

    # parent relationships (access parent)

    # child relationships (access children)
    ArticlesTagList : Mapped[List["ArticlesTag"]] = relationship(back_populates="tag1")



class User(Base):  # type: ignore
    __tablename__ = 'users'
    _s_collection_name = 'User'  # type: ignore

    id = Column(String(36), primary_key=True, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(255), nullable=False, unique=True)
    image = Column(String(255), server_default=text("''"))
    bio = Column(Text, server_default=text("''"))
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    allow_client_generated_ids = True

    # parent relationships (access parent)

    # child relationships (access children)
    ArticleList : Mapped[List["Article"]] = relationship(back_populates="user")
    FollowerList : Mapped[List["Follower"]] = relationship(foreign_keys='[Follower.follower]', back_populates="user1")
    FollowerList1 : Mapped[List["Follower"]] = relationship(foreign_keys='[Follower.user]', back_populates="user11")
    CommentList : Mapped[List["Comment"]] = relationship(back_populates="user")
    FavoriteList : Mapped[List["Favorite"]] = relationship(back_populates="user1")

# 'Mapper[Follower(followers)]' has no property 'user11'.  If this property was indicated from other mappers or configure events, ensure registry.configure() has been called.
# KeyError: 'user11'  FIXME

class Article(Base):  # type: ignore
    __tablename__ = 'articles'
    _s_collection_name = 'Article'  # type: ignore

    id = Column(String(36), primary_key=True, unique=True)
    slug = Column(String(255), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    description = Column(String(255), nullable=False)
    favorites_count = Column(Integer, server_default=text("'0'"), nullable=False)
    author = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    allow_client_generated_ids = True

    # parent relationships (access parent)
    user : Mapped["User"] = relationship(back_populates=("ArticleList"))

    # child relationships (access children)
    ArticlesTagList : Mapped[List["ArticlesTag"]] = relationship(back_populates="article1")
    CommentList : Mapped[List["Comment"]] = relationship(back_populates="article1")
    FavoriteList : Mapped[List["Favorite"]] = relationship(back_populates="article1")



class Follower(Base):  # type: ignore
    __tablename__ = 'followers'
    _s_collection_name = 'Follower'  # type: ignore
    __table_args__ = (
        Index('followers_user_follower_unique', 'user', 'follower', unique=True),
    )

    id = Column(String(36), primary_key=True, unique=True)
    user = Column(ForeignKey('users.id'), nullable=False)
    follower = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    allow_client_generated_ids = True

    # parent relationships (access parent)
    user1 : Mapped["User"] = relationship(foreign_keys='[Follower.follower]', back_populates=("FollowerList"))
    user2 : Mapped["User"] = relationship(foreign_keys='[Follower.user]', back_populates=("FollowerList1"))

    # child relationships (access children)



class ArticlesTag(Base):  # type: ignore
    __tablename__ = 'articles_tags'
    _s_collection_name = 'ArticlesTag'  # type: ignore
    __table_args__ = (
        Index('articles_tags_tag_article_unique', 'tag', 'article', unique=True),
    )

    id = Column(String(36), primary_key=True, unique=True)
    article = Column(ForeignKey('articles.id'), nullable=False)
    tag = Column(ForeignKey('tags.id'), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    allow_client_generated_ids = True

    # parent relationships (access parent)
    article1 : Mapped["Article"] = relationship(back_populates=("ArticlesTagList"))
    tag1 : Mapped["Tag"] = relationship(back_populates=("ArticlesTagList"))

    # child relationships (access children)



class Comment(Base):  # type: ignore
    __tablename__ = 'comments'
    _s_collection_name = 'Comment'  # type: ignore

    id = Column(String(36), primary_key=True, unique=True)
    body = Column(Text, nullable=False)
    author = Column(ForeignKey('users.id'), nullable=False)
    article = Column(ForeignKey('articles.id'), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    allow_client_generated_ids = True

    # parent relationships (access parent)
    article1 : Mapped["Article"] = relationship(back_populates=("CommentList"))
    user : Mapped["User"] = relationship(back_populates=("CommentList"))

    # child relationships (access children)



class Favorite(Base):  # type: ignore
    __tablename__ = 'favorites'
    _s_collection_name = 'Favorite'  # type: ignore

    id = Column(String(36), primary_key=True, unique=True)
    user = Column(ForeignKey('users.id'), nullable=False)
    article = Column(ForeignKey('articles.id'), nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    allow_client_generated_ids = True

    # parent relationships (access parent)
    article1 : Mapped["Article"] = relationship(back_populates=("FavoriteList"))
    user1 : Mapped["User"] = relationship(back_populates=("FavoriteList"))

    # child relationships (access children)
