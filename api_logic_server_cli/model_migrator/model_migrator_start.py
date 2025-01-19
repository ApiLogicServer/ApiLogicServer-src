import os
import sys, logging
from sqlalchemy.sql import text
from typing import List
import sqlalchemy
from dotmap import DotMap
from pathlib import Path


def log(msg: any) -> None:
    print(msg, file=sys.stderr)

log = logging.getLogger("ModelMigrator")


class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ModelMigrator(object):

    def __init__(self, db_url, project_directory, model_creation_services):

        self.db_url = db_url
        self.project_directory = project_directory

        self.number_of_models = 0
        """ various status / debug information """

        self.model_creation_services = model_creation_services
        """ access to meta model, including table_to_class_map """


    def append_expose_services_file(self):
        """ append import to -> append_expose_services_file """
        import_statement = f'\n\n    from api import tvf\n'
        import_statement += f'    tvf.expose_tvfs(api)\n'
        file_name = self.get_os_url(f"{self.project_directory}/api/customize_api.py")
        expose_services_file = open(file_name, 'a')
        expose_services_file.write(import_statement)
        expose_services_file.close()


    def run(self):
        """ call by ApiLogicServer CLI -- migrate LAC model to ALS

        """
        table_to_class = self.model_creation_services.table_to_class_map
        if "UserRole" not in table_to_class:
            log.debug('.. ModelMigrator.run() - running')
            import api_logic_server_cli.model_migrator.reposreader as repo_reader
            # need repos location and project api name (teamspaces/api/{lac_project_name})
            running_at = Path(__file__)
            repos_location = f"{running_at.parent}{os.sep}CALiveAPICreator.repository"
            lac_project_name = "repos" # pass as args.lac_project_name TODO
            repo_reader.start(repos_location, self.project_directory, lac_project_name, table_to_class ) 
            log.debug('.. ModelMigrator.run() - done')


def extended_builder(db_url: str, project_directory: str, model_creation_services):
    """
    Migrate LAC model to ALS.

    See: https://apilogicserver.github.io/Docs/Project-Builders/:
    
    Example

        APILogicServer run --project_name='~/dev/servers/model_migrator_project' \
\b
            --extended_builder='model_migrator' \
\b
            --db_url='nw'


    Args:
        db_url (str): SQLAlchemy db uri
        project_directory (str): project location
    """
    log.info(f'\n\nModelMigrator - args')
    log.info(f'-->url: {db_url} \n-->project_directory: {project_directory}"')
    model_migrator = ModelMigrator(db_url, project_directory, model_creation_services)
    model_migrator.run()
