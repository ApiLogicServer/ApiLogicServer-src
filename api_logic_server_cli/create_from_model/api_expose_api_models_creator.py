import logging
import shutil
import sys
import os
import datetime
from pathlib import Path
from typing import NewType
from shutil import copyfile
import create_from_model.api_logic_server_utils as create_utils

import create_from_model.model_creation_services as create_from_model

log = logging.getLogger(__file__)
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('%(message)s')  # lead tag - '%(name)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.propagate = True
# log.setLevel(logging.DEBUG)

#  MetaData = NewType('MetaData', object)
MetaDataTable = NewType('MetaDataTable', object)

__version__ = "0.2"

def create_expose_api_models(model_creation_services: create_from_model.ModelCreationServices):
    """ create strings for ui/basic_web_app/views.py and api/expose_api_models.py """

    if use_model_driven := True:
        if model_creation_services.project.bind_key == "":  # multi-db -- expose apis by discovery
            shutil.copyfile(model_creation_services.project.api_logic_server_dir_path.joinpath("prototypes/base/api/expose_api_models.py"),
                            Path(model_creation_services.project_directory).joinpath("api/expose_api_models.py"))
            log.debug(f'.. .. ..Model-driven API creation')  # copy above was to upgrade existing projects, eg, import
            return
        
        # model fixup for multi-db... there are 2 cases:
        #   1. database/database_discovery/authentication_models.py
        #   2. database/Todo_models.py
        # important to test - add multi-db AND auth, as in BLT multi-db test.  Unit test: use Run Config ~10...
        # multi-db -- expose apis by discovery-- start with the standard api/expose_api_models.py

        src = model_creation_services.project.api_logic_server_dir_path.joinpath('templates/_bind_expose_api.py')  # debug version
        bind = model_creation_services.project.bind_key
        dest = Path(model_creation_services.project_directory).\
            joinpath(f'api/api_discovery/{model_creation_services.project.bind_key}_expose_api_models.py')
        src = model_creation_services.project.api_logic_server_dir_path.joinpath('templates/_bind_expose_api.py')  # debug version
        copyfile(src, dest)

        create_utils.insert_lines_at(file_name=dest, 
                                    at='database = __import__', 
                                    lines = f'force_import = __import__("database.{bind}_models")\n')
        
        create_utils.replace_string_in_file(search_for="inspect.getmembers(database.models)",
                                            replace_with=f'inspect.getmembers(database.{bind}_models)',
                                            in_file=dest)

        if bind == 'authentication':  # it's in a different dir
            create_utils.replace_string_in_file(search_for='database.authentication_models',
                                                replace_with='database.database_discovery.authentication_models',
                                                in_file=dest)



    else:
        result_apis = ''
        '''
        result_apis += '"""'
        result_apis += ("\nApiLogicServer Generate From Model "
                        + model_creation_services.version + "\n\n"
                        # + "From: " + sys.argv[0] + "\n\n"
                        + "Using Python: " + sys.version + "\n\n"
                        + "At: " + str(datetime.datetime.date()) + "\n\n"
                        + '"""\n\n')
        '''
        port_replace = model_creation_services.project.port if model_creation_services.project.port else "None"
        result_apis += \
            f'\n\ndef expose_models(api, method_decorators = []): \n'
        # result_apis += '    my_host = HOST\n'
        # result_apis += '    if HOST == "0.0.0.0":\n'
        # result_apis += '        my_host = "localhost"  # override default HOST for pc"\n'
        result_apis += '    """\n'
        result_apis += '        Declare API - on existing SAFRSAPI to expose each model - API automation \n'
        result_apis += '        - Including get (filtering, pagination, related data access) \n'
        result_apis += '        - And post/patch/update (including logic enforcement) \n\n'
        result_apis += '        Invoked at server startup (api_logic_server_run) \n\n'
        result_apis += '        You typically do not customize this file \n'
        result_apis += '        - See https://apilogicserver.github.io/Docs/Tutorial/#customize-and-debug \n'
        result_apis += '    """\n'

        sys.path.append(model_creation_services.project.os_cwd)

        for each_resource_name in model_creation_services.resource_list:
            # log.debug("process_each_table: " + each_resource_name)
            if "TRANSFERFUNDx" in each_resource_name:
                log.debug("special table")  # debug stop here
            if model_creation_services.project.not_exposed is not None and each_resource_name + " " in model_creation_services.project.not_exposed:
                # result_apis += "# not_exposed: api.expose_object(models.{resource_name})"
                continue
            if "ProductDetails_V" in each_resource_name:
                log.debug("special table")  # should not occur (--noviews)
            if each_resource_name.startswith("Ab"):
                # result_apis += "# skip admin table: " + resource_name + "\n"
                continue
            elif 'sqlite_sequence' in each_resource_name:
                # result_apis +=  "# skip sqlite_sequence table: " + resource_name + "\n"
                continue
            else:
                models_file = 'models'
                if model_creation_services.project.bind_key != "":
                    models_file = model_creation_services.project.bind_key + "_" + models_file
                result_apis += f'    api.expose_object(database.{models_file}.{each_resource_name}, method_decorators= method_decorators)\n'
        result_apis += f'    return api\n'
        # self.session.close()
        expose_api_models_path = Path(model_creation_services.project_directory).joinpath('api/expose_api_models.py')
        if model_creation_services.project.command.startswith("rebuild"):
            expose_api_models_path = Path(model_creation_services.project_directory).\
                joinpath('api/expose_api_models_created.py')
            log.debug(f'.. .. ..Rebuild - new api at api/expose_api_models_created (merge/replace expose_api_models as nec)')
            src = model_creation_services.project.api_logic_server_dir_path
            src = src.joinpath("prototypes/base/api/expose_api_models.py")
            assert src.is_file()
            shutil.copyfile(src, expose_api_models_path)
            expose_api_models_file = open(expose_api_models_path, 'a')
            expose_api_models_file.write(result_apis)
            expose_api_models_file.close()
        else:  # normal path...
            if model_creation_services.project.bind_key != "":
                expose_api_models_path = Path(model_creation_services.project_directory).\
                    joinpath(f'api/{model_creation_services.project.bind_key}_expose_api_models.py')
                src = model_creation_services.project.api_logic_server_dir_path.\
                        joinpath('prototypes/base/api/expose_api_models.py')
                dest = expose_api_models_path
                copyfile(src, dest)
            expose_api_models_file = open(expose_api_models_path, 'a')
            expose_api_models_file.write(result_apis)
            expose_api_models_file.close()

    return


def create(model_creation_services: create_from_model.ModelCreationServices):
    """ called by ApiLogicServer CLI -- creates api/expose_api_models.py, key input to SAFRS
    """
    create_expose_api_models(model_creation_services)
