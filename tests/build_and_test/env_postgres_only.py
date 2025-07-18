""" PostgreSQL-only test configuration for Python 3.13 compatibility testing. """


class Config:
    """ api_logic_server_test configuration - PostgreSQL-only for Python 3.13 testing """


    # ***********************
    #   what tests to run - PostgreSQL ONLY
    # ***********************

    # Essential setup
    do_install_api_logic_server = True      # verify build wheel and local 
    do_logicbank_test = ""                  # use this testpy version (or '')
    
    # Core project tests - keep these for basic functionality
    do_create_api_logic_project = True      # create the default project
    do_run_api_logic_project = True         # start the server 
    do_test_api_logic_project = True        # run the behave tests (test logic, api)
    do_test_api_logic_project_with_auth = True  # run the behave tests (test logic, api)
    
    # SKIP non-PostgreSQL tests
    do_test_genai = False                   # skip genai tests
    do_test_multi_reln = False              # skip multi-relation tests
    do_create_shipping = False              # skip shipping tests
    do_run_shipping = False                 # skip shipping tests
    do_run_nw_kafka = False                 # skip kafka tests
    do_test_nw_kafka = False                # skip kafka tests
    do_rebuild_tests = False                # skip rebuild tests
    do_multi_database_test = False          # skip multi-database tests
    do_allocation_test = False              # skip allocation tests (SQLite)
    do_budget_app_test = False              # skip budget app tests (SQLite)
    do_other_sqlite_databases = False       # skip other SQLite databases
    do_include_exclude = False              # skip include/exclude tests
    
    # Database-specific tests - ONLY PostgreSQL
    do_docker_mysql = False                 # SKIP MySQL tests
    do_docker_postgres = True               # KEEP PostgreSQL tests ✅
    do_docker_postgres_auth = True          # KEEP PostgreSQL auth tests ✅
    do_docker_sqlserver = False             # SKIP SQL Server tests
    
    # Docker creation tests - keep for completeness
    do_docker_creation_tests = True         # build docker image, start it and create projects


    # ***********************
    #   platform specific
    # ***********************

    set_venv = 'source ${install_api_logic_server_path}/venv/bin/activate'
    '''typical source "venv/bin/activate" does not persist over cmds, see...
        https://github.com/valhuber/ubuntu-script-venv/blob/main/use-in-script.sh '''

    docker_database_ip = 'localhost'
    ''' for virtual machine access, set this to host IP '''
