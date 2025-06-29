from api_logic_server_cli.cli_args_project import Project
from pathlib import Path
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import logging
import importlib.util
from api_logic_server_cli.create_from_model import api_logic_server_utils as api_logic_server_utils
from shutil import copyfile
import shutil, os
import create_from_model.api_logic_server_utils as create_utils

log = logging.getLogger('create_from_model.model_creation_services')


'''
samples and demos - simulate customizations - https://apilogicserver.github.io/Docs/Doc-Home/#start-install-samples-training
    1. nw - sample code
    2. genai_demo - GenAI (ChatGPT to create model, add rules VSC)
    3. basic_demo - small db, no GenAI (w/ iteration)
    4. sample_ai - CoPilot, no GenAI   (w/ iteration)
    5. Tech AI - just an article, no automated customizations...

Note: many require: rebuild-from-database --project_name=./ --db_url=sqlite:///database/db.sqlite
'''

def add_genai_customizations(project: Project, do_show_messages: bool = True, do_security: bool = True):
    """ Add customizations `prototypes/genai_demo` to genai (default creation)

    0. Initial: create_project_and_overlay_prototypes() -- minor: just creates the readme
            * When done with genai logic prompt, logic is pre-created (in logic/declare_logic.py)
    1. Deep copy prototypes/genai_demo (adds logic and security, and custom end point)


    Args:
    """

    log.debug("\n\n==================================================================")
    nw_messages = ""
    do_security = True  # other demos can explain security, here just make it work
    if do_security:
        if do_show_messages:
            nw_messages = "Add sample_ai / genai_demo customizations - enabling security"
        project.add_auth(is_nw=True, msg=nw_messages)

    # overlay genai_demo := sample_ai + sample_ai_iteration
    nw_path = (project.api_logic_server_dir_path).\
        joinpath('prototypes/genai_demo')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw')
    create_utils.recursive_overwrite(nw_path, project.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'

    if do_show_messages:
        log.info("\nExplore key customization files:")
        log.info(f'..api/customize_api.py')
        log.info(f'..logic/declare_logic.py')
        log.info(f'..security/declare_security.py\n')
        if project.is_tutorial == False:
            log.info(".. all customizations complete\n")

def fix_nw_datamodel(project_directory: str):
    """update sqlite data model for cascade delete, aliases  -- fixme moving to add_cust

    Args:
        project_directory (str): project creation dir
    """
    models_file_name = Path(project_directory).joinpath('database/models.py')
    do_add_manual = True if models_file_name.is_file() and not create_utils.does_file_contain(search_for="manual fix", in_file=models_file_name) else False
    if not do_add_manual:
        log.debug(f'.. .. ..ALREADY SET cascade delete and column alias for sample database database/models.py')
        pass  # should not occur, just being careful
    else:
        log.debug(f'.. .. ..Setting cascade delete and column alias for sample database database/models.py')
        create_utils.replace_string_in_file(in_file=models_file_name,
            search_for='OrderDetailList : Mapped[List["OrderDetail"]] = relationship(back_populates="Order")',
            replace_with='OrderDetailList : Mapped[List["OrderDetail"]] = relationship(cascade="all, delete", back_populates="Order")  # manual fix')
        create_utils.replace_string_in_file(in_file=models_file_name,
            search_for="ShipPostalCode = Column(String(8000))",
            replace_with="ShipZip = Column('ShipPostalCode', String(8000))  # manual fix - alias")
        create_utils.replace_string_in_file(in_file=models_file_name,
            search_for="CategoryName_ColumnName = Column(String(8000))",
            replace_with="CategoryName = Column('CategoryName_ColumnName', String(8000))  # manual fix - alias")

def add_nw_customizations(project: Project, do_show_messages: bool = True, do_security: bool = True):
    """ Add customizations to nw (default creation)

    1. Add-sqlite-security (optionally - not used for initial creation)

    2. Deep copy project_prototype_nw (adds logic)

    3. Create readme files: Tutorial (copy_md), api/integration_defs/readme.md

    4. Add database customizations

    Args:
    """

    log.debug("\n\n==================================================================")
    nw_messages = ""
    if do_security:
        if do_show_messages:
            nw_messages = "Add northwind customizations - enabling security"
        project.add_auth(is_nw=True, msg=nw_messages)

    nw_path = (project.api_logic_server_dir_path).\
        joinpath('prototypes/nw')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw')
    if os.path.isfile(project.project_directory_path.joinpath('ui/admin/admin.yaml')):
        copyfile(src = project.project_directory_path.joinpath('ui/admin/admin.yaml'),
                dst = project.project_directory_path.joinpath('ui/admin/admin_no_customizations.yaml'))
    create_utils.recursive_overwrite(nw_path, project.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'

    project.create_nw_tutorial_and_readme()

    # z_copy_md(project = project, from_doc_file="Sample-Integration.md", to_project_file='integration/Sample-Integration.md')
    create_utils.copy_md(project = project, from_doc_file = "Sample-Integration.md", to_project_file='integration/Sample-Integration.md')

    fix_nw_datamodel(project_directory=project.project_directory)

    if do_show_messages:
        log.info("\nExplore key customization files:")
        log.info(f'..api/customize_api.py')
        log.info(f'..database/customize_models.py')
        log.info(f'..logic/declare_logic.py')
        log.info(f'..security/declare_security.py\n')
        if project.is_tutorial == False:
            log.info(".. all customizations complete\n")


def add_basic_demo_customizations(project: Project, do_show_messages: bool = True):
    """ Add customizations to basic_demo (default creation)

    1. Deep copy prototypes/basic_demo (adds logic and security)

    2. Create readme files: Sample-AI (copy_md), api/integration_defs/readme.md  TODO not done, fix cmts

    Args:
    """

    log.debug("\n\n==================================================================")
    nw_messages = ""
    do_security = False  # disabled - keep clear what "activate security" means for reader
    if do_security:
        if do_show_messages:
            nw_messages = "Add basic_demo customizations - enabling security"
        project.add_auth(is_nw=True, msg=nw_messages)

    nw_path = (project.api_logic_server_dir_path).\
        joinpath('prototypes/basic_demo/customizations')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/basic_demo/customizations')
    create_utils.recursive_overwrite(nw_path, project.project_directory) 

    if do_show_messages:
        log.info("\nExplore key customization files:")
        log.info('\033[94m\033[1m..logic/declare_logic.py\033[0m')
        log.info(f'..security/declare_security.py\n')
        # Make the message blue, bold, and add an attention-getting icon
        log.info('\033[94m\033[1m🔷 Explore MCP (Model Context Protocol): https://apilogicserver.github.io/Docs/Integration-MCP/\033[0m\n')
        log.info('.. restart the server')
        log.info('python integration/mcp/mcp_client_executor.py mcp')
        # log.info(".. Copy/paste this into your terminal (Mac/Linux):")
        # log.info(".. curl -X 'POST' 'http://localhost:5656/api/SysMcp/' -H 'accept: application/vnd.api+json' -H 'Content-Type: application/json' -d '{ \"data\": { \"attributes\": {\"request\": \"List the orders date_shipped is null and CreatedOn before 2023-07-14, and send a discount email (subject: '\\''Discount Offer'\\'') to the customer for each one.\"}, \"type\": \"SysMcp\"}}'")
        log.info('')
        log.info(f'Next Steps: activate security')
        log.info(f'..genai-logic add-auth --db_url=auth')
        if project.is_tutorial == False:
            log.info(".. complete\n")


def add_basic_demo_iteration(project: Project, do_show_messages: bool = True, do_security: bool = True):
    """ Iterate data model for basic_demo (default creation)

    1. Deep copy prototypes/basic_demo/iteration (adds db, logic)

    Args:
    """

    log.debug("\n\n==================================================================")

    nw_path = (project.api_logic_server_dir_path).\
        joinpath('prototypes/basic_demo/iteration')
    create_utils.recursive_overwrite(nw_path, project.project_directory)  # ~/dev/ApiLogicServer/ApiLogicServer-dev/servers/basic_demo
    if do_show_messages:
        log.info("\nNext Step:")
        log.info(f'..genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite')
        log.info(".. complete\n")


def add_sample_ai_customizations(project: Project, do_show_messages: bool = True):
    """ Add customizations to sample_ai (default creation)

    1. Deep copy prototypes/sample_ai (adds logic and security)

    2. Create readme files: Sample-AI (copy_md), api/integration_defs/readme.md  TODO not done, fix cmts

    Args:
    """

    log.debug("\n\n==================================================================")
    nw_messages = ""
    do_security = False  # disabled - keep clear what "activate security" means for reader
    if do_security:
        if do_show_messages:
            nw_messages = "Add sample_ai customizations - enabling security"
        project.add_auth(is_nw=True, msg=nw_messages)

    nw_path = (project.api_logic_server_dir_path).\
        joinpath('prototypes/sample_ai')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw')
    create_utils.recursive_overwrite(nw_path, project.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'

    if do_show_messages:
        log.info("\nExplore key customization files:")
        log.info(f'..api/customize_api.py')
        log.info(f'..logic/declare_logic.py')
        log.info(f'..security/declare_security.py\n')
        log.info(f'Next Steps: activate security')
        log.info(f'..genai-logic add-auth --db_url=auth')
        if project.is_tutorial == False:
            log.info(".. complete\n")


def add_sample_ai_iteration(project: Project, do_show_messages: bool = True, do_security: bool = True):
    """ Iterate data model for sample_ai (default creation)

    1. Deep copy prototypes/sample_ai_iteration (adds db, logic)

    Args:
    """

    log.debug("\n\n==================================================================")

    nw_path = (project.api_logic_server_dir_path).\
        joinpath('prototypes/sample_ai_iteration')  # PosixPath('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/nw')
    create_utils.recursive_overwrite(nw_path, project.project_directory)  # '/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/tutorial/1. Instant_Creation'
    if do_show_messages:
        log.info("\nNext Step:")
        log.info(f'..genai-logic rebuild-from-database --project_name=./ --db_url=sqlite:///database/db.sqlite')
        log.info(".. complete\n")


def add_cust(project: Project, models_py_path: Path, project_name: str):
    ''' determine which project, then call a customizer above '''
    
    log.debug(f"\ncli[add-cust] models_py_path={models_py_path}")
    if not models_py_path.exists():
        raise Exception("Customizations are northwind/genai-specific - models.py does not exist")

    project_is_genai_demo = False
    ''' can't use project.is_genai_demo because this is not the create command...'''
    
    if project.project_directory_path.joinpath('docs/project_is_genai_demo.txt').exists():
        project_is_genai_demo = True
    
    project.abs_db_url, project.nw_db_status, project.model_file_name = create_utils.get_abs_db_url("0. Using Sample DB", project)
    if create_utils.does_file_contain(search_for="CategoryTableNameTest", in_file=models_py_path):
        add_nw_customizations(project=project, do_security=False)
        log.info("\nNext step - add authentication:\n  $ ApiLogicServer add-auth --db_url=auth\n\n")

    # elif project_is_genai_demo and create_utils.does_file_contain(search_for="Customer", in_file=models_py_path):
    #    add_genai_customizations(project=project, do_security=False)

    elif project_name == 'sample_ai' and create_utils.does_file_contain(search_for="CustomerName = Column(Text", in_file=models_py_path):
        cocktail_napkin_path = project.project_directory_path.joinpath('logic/cocktail-napkin.jpg')
        is_customized = cocktail_napkin_path.exists()
        if not is_customized:
            add_sample_ai_customizations(project=project)
        else:
            add_sample_ai_iteration(project=project)

    elif (project_is_genai_demo or project_name == 'basic_demo') and create_utils.does_file_contain(search_for="Customer", in_file=models_py_path):
        cocktail_napkin_path = project.project_directory_path.joinpath('logic/cocktail-napkin.jpg')
        is_customized = cocktail_napkin_path.exists()
        if not is_customized:
            add_basic_demo_customizations(project=project)
        else:
            add_basic_demo_iteration(project=project)

    else:
        raise Exception("Customizations are northwind/genai-specific - models.py has neither CategoryTableNameTest nor Customer")
