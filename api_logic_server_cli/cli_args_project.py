import api_logic_server_cli.create_from_model.uri_info as uri_info
from api_logic_server_cli.cli_args_base import CliArgsBase
from os.path import abspath
from pathlib import Path
import os, logging

class Project(CliArgsBase):  # extends user-visible args with internal values, extended by ProjectRun
    
    def __init__(self):
        
        super(Project, self).__init__()

        self.os_cwd = os.getcwd()
        self.abs_db_url = None
        self.user_db_url = None
        """ retain the actual db_url specified by the user """
        
        self.nw_db_status = None
        """ '', nw, nw+, nw-   blank defaults to nw- """

        self.project_directory = None
        """ string - may have relative /../ """

        self.project_directory_actual = None
        """ string - not relative /../ """

        self.project_directory_path = None
        """ Path (project_directory_actual) """

        self.merge_into_prototype = None
        """ used by codespaces (create project over current) - project_name = ./ """

        self.model_creation_services = None
        """ access to model (bi-directional link - see model_creation_services.py) """

        self.table_descriptions = dict()
        """ table_name:description  -- populated by create_db_from_model """

        self.model_gen_bind_msg = False
        """ sqlacodegen/codegen msg printed """

        self.models_path_dir = 'database'
        """ dir name (str) to write models.py """
        self.model_file_name = "models.py"
        """ name of models file being processed """

        self.default_db = "default = nw.sqlite, ? for help"
        self.default_project_name = "ApiLogicProject"
        self.default_fab_host = "localhost"
        self.default_bind_key_url_separator = "-"  # admin 
        self.is_tutorial = False

        self.project_name_last_node = "TBD"

        running_at = Path(__file__)
        self.api_logic_server_dir_path = running_at.parent.absolute()  # no abspath(f'{abspath(get_api_logic_server_dir())}'))
        """ ...ApiLogicServer-src/api_logic_server_cli """

        self.is_codespaces = os.getenv('CODESPACES')

        self.defaultInterpreterPath = None
        """ set near end - see final_project_fixup """

        self.genai_logic = None  # type list[str]
        """ genai logic to be inserted into logic/declare_logic.py """

        self.genai_tables = 0
        """ number of tables (aks complexity) for genai """

        self.genai_test_data_rows = 0
        """ number of test data rows for genai """

        self.genai_prompt_inserts : str = None
        """ text to be inserted into prompt 
            - "" means infer from db_url (e.g. system/genai/prompt_inserts/sqlite_inserts.prompt)
            - "*" means no inserts
            - otherwise, path to file """


    def print_options(self):
        """ Creating ApiLogicServer with options: (or uri hello) """
        if self.db_url == "?":  # can only test interactively, not from launch
            uri_info.print_uri_info()
            exit(0)

        log = logging.getLogger('api_logic_server_cli.api_logic_server')
        if log.getEffectiveLevel() >= logging.DEBUG:
            print(f'\n\nCreating ApiLogicServer with options:')
            print(f'  --db_url={self.db_url}')
            print(f'  --bind_key={self.bind_key}') 
            print(f'  --bind_url_separator={self.bind_key_url_separator}')
            print(f'  --project_name={self.project_name}   (pwd: {self.os_cwd})')
            print(f'  --api_name={self.api_name}')
            print(f'  --admin_app={self.admin_app}')
            print(f'  --react_admin={self.react_admin}')
            print(f'  --flask_appbuilder={self.flask_appbuilder}')
            print(f'  --from_git={self.from_git}')
            #        print(f'  --db_types={self.db_types}')
            print(f'  --run={self.run}')
            print(f'  --host={self.host}')
            print(f'  --port={self.port}')
            print(f'  --swagger_host={self.swagger_host}')
            print(f'  --not_exposed={self.not_exposed}')
            print(f'  --open_with={self.open_with}')
            print(f'  --use_model={self.use_model}')
            print(f'  --favorites={self.favorites}')
            print(f'  --non_favorites={self.non_favorites}')
            print(f'  --extended_builder={self.extended_builder}')
            print(f'  --multi_api={self.multi_api}')
            print(f'  --infer_primary_key={self.infer_primary_key}')
            print(f'  --opt_locking={self.opt_locking}')
            print(f'  --opt_locking={self.opt_locking_attr}')
            print(f'  --quote={self.quote}')
