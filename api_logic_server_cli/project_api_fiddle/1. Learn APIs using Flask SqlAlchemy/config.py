"""Flask configuration variables."""
from os import environ, path
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

#  for complete flask_sqlachemy config parameters and session handling,
#  read: file flask_sqlalchemy/__init__.py AND flask/config.py
'''
app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///:memory:')
app.config.setdefault('SQLALCHEMY_BINDS', None)
app.config.setdefault('SQLALCHEMY_NATIVE_UNICODE', None)
app.config.setdefault('SQLALCHEMY_ECHO', False)
app.config.setdefault('SQLALCHEMY_RECORD_QUERIES', None)
app.config.setdefault('SQLALCHEMY_POOL_SIZE', None)
app.config.setdefault('SQLALCHEMY_POOL_TIMEOUT', None)
app.config.setdefault('SQLALCHEMY_POOL_RECYCLE', None)
app.config.setdefault('SQLALCHEMY_MAX_OVERFLOW', None)
app.config.setdefault('SQLALCHEMY_COMMIT_ON_TEARDOWN', False)
'''

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, "default.env"))
app_logger = logging.getLogger('api_logic_server_app')


class Config:
    """Set Flask configuration from .env file."""

    # General Config
    SECRET_KEY = environ.get("SECRET_KEY")
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get("FLASK_ENV")
    DEBUG = environ.get("DEBUG")

    running_at = Path(__file__)
    project_abs_dir = running_at.parent.absolute()

    # Database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{str(project_abs_dir.joinpath('database/db.sqlite'))}"
    # override SQLALCHEMY_DATABASE_URI here as required

    app_logger.debug(f'config.py - SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}')

    # as desired, use env variable: export SQLALCHEMY_DATABASE_URI='sqlite:////Users/val/dev/servers/docker_api_logic_project/database/db.sqliteXX'
    if os.getenv('SQLALCHEMY_DATABASE_URI'):  # e.g. export SECURITY_ENABLED=true
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
        app_logger.debug(f'.. overridden from env variable: {SQLALCHEMY_DATABASE_URI}')


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = False

