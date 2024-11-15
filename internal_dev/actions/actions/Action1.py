import logging
from re import X
import shutil
import sys
import os
import pathlib
from pathlib import Path
from typing import NewType, List, Tuple, Dict
import sqlalchemy
import yaml
from sqlalchemy import MetaData, false
import datetime
import api_logic_server_cli.create_from_model.model_creation_services as create_from_model
import api_logic_server_cli.create_from_model.api_logic_server_utils as create_utils
from dotmap import DotMap
from logic_bank.exec_row_logic.logic_row import LogicRow
from api_logic_server_cli.create_from_model.meta_model import Resource

log = logging.getLogger(__name__)


# log.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(f'%(name)s: %(message)s')     # lead tag - '%(name)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.propagate = True


class Action1(object):
    """
    Create Admin user and roles
    """
    
    @staticmethod
    def create_admin_user(flask_app, args):
        """
        Create Admin user and roles
        """
    def __init__(self,
                 action_name: str,
                 logic_row: LogicRow):
        self.action_name = action_name
        self.logic_row : LogicRow = logic_row
        self.run()
    
    def run(self):
        """
        Create Admin user and roles
        """
        log.info("Action running")
        pass
