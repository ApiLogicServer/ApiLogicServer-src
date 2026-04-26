# -*- coding: utf-8 -*-
"""
create_project_and_overlay_prototypes() - extracted from api_logic_server.py

Clones prototypes/base into the new project directory, then overlays
sample-specific prototype directories (nw, basic_demo, demo_eai, etc.)
and handles sqlite db copy and config substitutions.

Called from ProjectRun.create_project() in api_logic_server.py.
"""

import os
import shutil
import platform
import datetime
import logging
from pathlib import Path
from shutil import copyfile

log = logging.getLogger('create_from_model.model_creation_services')


def create_project_and_overlay_prototypes(project: 'ProjectRun', msg: str) -> str:
    """
    clone prototype to  project directory, copy sqlite db, and remove git folder

    update config/config/config.py - SQLALCHEMY_DATABASE_URI

    process /prototypes directories (eg, nw/nw+/allocation/BudgetApp/basic_demo),
       * inject sample logic/declare_logic and api/customize_api, etc (merge copy over)

    nw, allocation etc databases are resolved in api_logic_server_utils.get_abs_db_url()

    :param project a ProjectRun
    :param msg log.debuged, such as Create Project:
    :return: return_abs_db_url (e.g., reflects sqlite copy to project/database dir)
    """
    # import utilities from parent module at call time to avoid circular imports
    from api_logic_server_cli.api_logic_server import (
        delete_dir, recursive_overwrite, fix_idea_configs,
        fixup_devops_for_postgres_mysql, get_api_logic_server_dir,
        get_windows_path_with_slashes, __version__,
    )
    import create_from_model.api_logic_server_utils as create_utils
    import clone_and_overlay_prototypes.add_cust as sample_mgr
    import clone_and_overlay_prototypes.create_readme as create_readme

    import tempfile
    cloned_from = project.from_git
    tmpdirname = ""
    with tempfile.TemporaryDirectory() as tmpdirname:

        if project.merge_into_prototype:
            pass
        else:
            remove_project_debug = True
            if remove_project_debug and project.project_name != ".":
                delete_dir(os.path.realpath(project.project_directory), "1.")

        from_dir = project.from_git
        api_logic_server_dir_str = str(get_api_logic_server_dir())
        if project.from_git.startswith("https://"):  # warning - very old code, not tested in a long time
            cmd = 'git clone --quiet https://github.com/valhuber/ApiLogicServerProto.git ' + project.project_directory
            cmd = f'git clone --quiet {project.from_gitfrom_git} {project.project_directory}'
            result = create_utils.run_command(cmd, msg=msg)
            delete_dir(f'{project.project_directory}/.git', "3.")
        else:
            if from_dir == "":
                from_dir = (Path(api_logic_server_dir_str)).\
                    joinpath('prototypes/base')
            log.debug(f'{msg} {os.path.realpath(project.project_directory)}')
            log.debug(f'.. ..Clone from {from_dir} ')
            cloned_from = from_dir
            try:
                if project.merge_into_prototype:  # create project over current (e.g., docker, learning center)
                    recursive_overwrite(project.project_directory, str(tmpdirname))  # save, restore @ end
                    delete_dir(str(Path(str(tmpdirname)) / ".devcontainer"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "api"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "database"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "logic"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "security"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "test"), "")
                    delete_dir(str(Path(str(tmpdirname)) / "ui"), "")
                    if os.path.exists(str(Path(str(tmpdirname))  / "api_logic_server_run.py" )):
                        os.remove(str(Path(str(tmpdirname)) / "api_logic_server_run.py"))
                    delete_dir(os.path.realpath(project.project_directory), "")
                    recursive_overwrite(from_dir, project.project_directory)  # ApiLogic Proto -> current (new) project
                else:
                    shutil.copytree(from_dir, project.project_directory)  # normal path (fails if project_directory not empty)
            except OSError as e:
                raise Exception(f'\n==>Error - unable to copy to {project.project_directory} -- see log below'
                    f'\n\n{str(e)}\n\n'
                    f'Suggestions:\n'
                    f'.. Verify the --project_name argument\n'
                    f'.. If you are using Docker, verify the -v argument\n\n')

        if project.nw_db_status in ["nw", "nw+"]:
            log.debug(".. ..Copying nw customizations: logic, custom api, readme, tests, admin app")
            if project.nw_db_status == 'nw':  # nw gets converted to nw-, so this should not occur
                log.error("\n==> System Error: Unexpected customization for nw.  Please contact support.\n")

            sample_mgr.add_nw_customizations(project=project, do_security=False, do_show_messages=False)

        if project.nw_db_status in ["nw+"]:
            log.debug(".. ..Copy in nw+ customizations: readme, perform_customizations")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/nw_plus')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.nw_db_status in ["nw-"]:
            log.debug(".. ..Copy in nw- customizations: readme")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/nw_no_cust')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.nw_db_status in ["nw", "nw+", "nw-"]:
            project.insert_tutorial_into_readme()

        if project.db_url in ['shipping', 'Shipping']:
            log.debug(".. ..Copy in shipping customizations: sa_pydb")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/shipping')
            recursive_overwrite(nw_dir, project.project_directory)

        if 'oracle' in project.db_url:
            log.debug(".. ..Copy in oracle customizations: sa_pydb")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/oracle')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.db_url in ["allocation"]:
            log.debug(".. ..Copy in allocation customizations: readme, logic, tests")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/allocation')
            recursive_overwrite(nw_dir, project.project_directory)

        if project.db_url in ["BudgetApp"]:
            log.debug(".. ..Copy in allocation customizations: readme, logic, tests")
            nw_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/BudgetApp')
            recursive_overwrite(nw_dir, project.project_directory)

        if 'basic_demo' in project.db_url:  # test the url, so it works regardless of (arbitrary) project name
            if old_code := False:
                log.debug(".. ..Copy in basic_demo customizations: readme, logic, tests")
                nw_dir = (Path(api_logic_server_dir_str)).\
                    joinpath('prototypes/basic_demo')
                recursive_overwrite(nw_dir, project.project_directory)
                os.rename(project.project_directory_path / 'readme.md', project.project_directory_path / 'readme_standard.md')
                create_utils.copy_md(project = project, from_doc_file = "Sample-Basic-Demo.md", to_project_file = "readme.md")
                create_utils.copy_md(project = project, from_doc_file = "Sample-Basic-Demo-Vibe.md", to_project_file="readme_vibe.md")
                create_utils.copy_md(project = project, from_doc_file = "Integration-MCP-AI-Example.md", to_project_file="readme_ai_mcp.md")
            else:
                pass

        create_readme.create_readme(project=project, api_logic_server_dir_str=api_logic_server_dir_str)

        if project.db_url == "mysql+pymysql://root:p@localhost:3306/classicmodels":
            log.debug(".. ..Copy in classicmodels customizations")
            proto_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/classicmodels')
            recursive_overwrite(proto_dir, project.project_directory)

        if project.db_url == "postgresql://postgres:p@localhost/postgres":
            log.debug(".. ..Copy in postgres customizations")
            proto_dir = (Path(api_logic_server_dir_str)).\
                joinpath('prototypes/postgres')
            recursive_overwrite(proto_dir, project.project_directory)

        if "sqlite" in project.db_url or project.nw_db_status in ["nw", "nw+"]:
            log.debug(".. ..Copy in sqlite devops")
            proto_dir = (Path(api_logic_server_dir_str)).joinpath('prototypes/sqlite')
            recursive_overwrite(proto_dir, project.project_directory)
            path_to_delete = project.project_directory_path.joinpath('devops/docker-compose-dev-local-nginx')
            delete_dir(os.path.realpath(path_to_delete), "")
            file_to_delete = project.project_directory_path.joinpath('devops/docker-compose-dev-azure/docker-compose-dev-azure.yml')
            os.remove(file_to_delete)

        if project.db_url == 'sqlite:///sample_ai.sqlite':
            create_utils.copy_md(project = project, from_doc_file = "Sample-AI.md", to_project_file='Sample-AI.md')

        if project.is_genai_demo:  # overwrite logic & db, add readme
            genai_demo_dir = (Path(api_logic_server_dir_str)).joinpath('prototypes/genai_demo')
            shutil.move(project.project_directory_path.joinpath('readme.md'),
                        project.project_directory_path.joinpath('readme_standard.md'))
            create_utils.copy_md(project = project, from_doc_file = "Sample-Basic-Demo.md", to_project_file='readme.md')

        if "postgres" or "mysql" in project.db_url:
            fixup_devops_for_postgres_mysql(project)

        create_utils.replace_string_in_file(search_for="creation-date",
                            replace_with=str(datetime.datetime.now().strftime("%B %d, %Y %H:%M:%S")),
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="api_logic_server_version",
                            replace_with=__version__,
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="api_logic_server_template",
                            replace_with=f'{from_dir}',
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="api_logic_server_project_directory",
                            replace_with=f'{project.project_directory}',
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="api_logic_server_api_name",
                            replace_with=f'{project.api_name}',
                            in_file=f'{project.project_directory}/readme.md')
        create_utils.replace_string_in_file(search_for="replace_opt_locking",
                            replace_with=f'{project.opt_locking}',
                            in_file=f'{project.project_directory}/config/config.py')
        create_utils.replace_string_in_file(search_for="replace_opt_locking_attr",
                            replace_with=f'{project.opt_locking_attr}',
                            in_file=f'{project.project_directory}/api/system/opt_locking/opt_locking.py')
        do_fix_docker_for_vscode_dockerfile = False  # not required - multi-arch docker
        if do_fix_docker_for_vscode_dockerfile:
            if platform.machine() in('arm64', 'aarch64'):
                log.debug(f'\n>> .. arm - {platform.machine()}\n')
                create_utils.replace_string_in_file(search_for="apilogicserver/api_logic_server",
                                    replace_with=f'apilogicserver/api_logic_server_local',
                                    in_file=f'{project.project_directory}/.devcontainer/For_VSCode.dockerfile')

        return_abs_db_url = project.abs_db_url
        copy_sqlite = True
        if copy_sqlite == False or "sqlite" not in project.abs_db_url:
            db_uri = get_windows_path_with_slashes(project.abs_db_url)

            import sys
            if sys.version_info >= (3, 13) and db_uri.startswith('postgresql://'):
                db_uri = db_uri.replace('postgresql://', 'postgresql+psycopg://')
                log.debug(f'.. ..Converted PostgreSQL URL for Python 3.13+: {db_uri}')

            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=db_uri,
                                in_file=f'{project.project_directory}/config/config.py')
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=db_uri,
                                in_file=f'{project.project_directory}/database/alembic.ini')
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=db_uri,
                                in_file=f'{project.project_directory}/database/db_debug/db_debug.py')
        else:
            """ sqlite - copy the db (relative fails, since cli-dir != project-dir)
            """
            db_loc = project.abs_db_url.replace("sqlite:///", "")
            target_db_loc_actual = str(project.project_directory_path.joinpath('database/db.sqlite'))
            if True:  # project.is_genai_demo == False:  genai_demo using db from genai, not prototypes
                copyfile(db_loc, target_db_loc_actual)
            config_url = str(project.api_logic_server_dir_path)
            replace_db_url_value = "sqlite:///{str(project_abs_dir.joinpath('database/db.sqlite'))}"
            replace_db_url_value = f"sqlite:///../database/db.sqlite"  # relative for portable sqlite
            replace_db_url_value = "sqlite:///{db_path}"

            if os.name == "nt":  # windows
                target_db_loc_actual = get_windows_path_with_slashes(target_db_loc_actual)
            return_abs_db_url = f'sqlite:///{target_db_loc_actual}'
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=replace_db_url_value,
                                in_file=f'{project.project_directory}/config/config.py')
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=return_abs_db_url,
                                in_file=f'{project.project_directory}/database/alembic.ini')
            create_utils.replace_string_in_file(search_for="replace_db_url",
                                replace_with=return_abs_db_url,
                                in_file=f'{project.project_directory}/database/db_debug/db_debug.py')

            log.debug(f'.. ..Sqlite database setup {target_db_loc_actual}...')
            log.debug(f'.. .. ..From {db_loc}')
            log.debug(f'.. .. ..db_uri set to: {return_abs_db_url} in <project>/config/config.py')
        if project.merge_into_prototype:
            recursive_overwrite(str(tmpdirname), project.project_directory)
        fix_idea_configs(project=project)
    return return_abs_db_url
