from enum import Enum
from pathlib import Path

class ExtendedEnum(Enum):
    """
    enum that supports list() to print allowed values

    Thanks: https://stackoverflow.com/questions/29503339/how-to-get-all-values-from-python-enum-class
    """

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class OptLocking(ExtendedEnum):
    """
    Valid Values for OptLocking, e.g.

        Config.OPT_LOCKING == OptLocking.OPTIONAL.value

    Args:
        ExtendedEnum (_type_): _description_
    """
    IGNORED = "ignored"
    OPTIONAL = "optional"
    REQUIRED = "required"

class CliArgsBase():
    """ args provided from CLI; extended by cl_args_project """
    
    def __init__(self):
        self.command = None # type: str
        self.project_name = None # type: str
        """ full nodal name """
        self.db_url = None # type: str
        """ not what was intially specified (e,g, tutorial uses nw, nw-) """
        self.auth_db_url = None # type: str
        """ for creating projects with db_url *and* auth """
        self.auth_provider_type = None # type: str
        """ sql (default), or keycloak """
        self.from_model = None # type
        """ create database from this model (e.g. model from copilot)"""
        self.genai_using = None # type
        """ name of .genai file/dir (ai prompt) --using: to create model, and project """
        self.genai_repaired_response = None
        """ Fixed response; None => ChatGPT API, else defaults system/genai/reference/chatgpt_retry.txt """
        self.genai_version = None
        """ Version number for ChatGPT API, eg gpt-3.5-turbo, gpt-4o (expensive) """
        self.genai_temperature : float = None
        """ ChatGPT API, 0-1, default 0.7 """
        self.genai_use_relns = None
        """ Use relationships in create_db_models """
        self.genai_active_rules = False
        """ Use `logic/active_rules.json` in create_db_models """
        self.bind_key = None # type: str
        self.bind_key_url_separator = None # type: str
        self.api_name = None # type: str
        self.host = None # type: str
        self.port = None # type: str
        self.swagger_host = None # type: str
        self.not_exposed = None # type: str
        self.from_git = None # type: str
        self.db_types = None # type: str
        self.open_with = None # type: str
        self.run = None
        self.use_model = None # type: str
        """ use existing (corrected) database/models.py to create api and app"""
        self.admin_app = None
        self.flask_appbuilder = None
        self.favorites = None # type: str
        """ names of attributes favored to show first on forms"""
        self.non_favorites = None # type: str
        """ names of attributes favored to show *last* on forms"""
        self.react_admin = None
        self.extended_builder = None
        self.include_tables = None
        self.multi_api = None
        self.infer_primary_key = None
        self.opt_locking = None # type: str
        """ <str> in OptLocking.list() """
        self.id_column_alias = None  # type: str
        """ safrs reserves id as property, so use this alias for db cols with that name """
        self.opt_locking_attr = None # type: str
        self.quote = None # type: bool

