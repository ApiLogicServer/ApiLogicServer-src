""" test configuration variables. """


class Config:
    """ api_logic_server_test configuration  """


    # ***********************
    #   what tests to run
    # ***********************

    default_setting = True  # simplify enable / disable most

    do_install_api_logic_server = default_setting   # verify build wheel and local 
    do_logicbank_test = "" # "1.20.12"                          # use this testpy version (or '')
    

    do_create_api_logic_project = default_setting   # create the default project
    do_run_api_logic_project = default_setting      # start the server 
    do_test_api_logic_project = default_setting     # run the behave tests (test logic, api)
    do_test_api_logic_project_with_auth = default_setting  # run the behave tests (test logic, api)
    do_test_genai = default_setting                 # run the genai tests
    do_test_multi_reln = False            # this suite (airport etc) broken per new parsed response format

    do_create_shipping = default_setting            # run shipping to listen to kafka (might run manually)
    do_run_shipping = False                         # run shipping to listen to kafka (might run manually)
    do_run_nw_kafka = default_setting               # run default project, *with* kafka
    do_test_nw_kafka = default_setting


    do_rebuild_tests = default_setting              # rebuild from model, allembic

    do_multi_database_test = default_setting        # add-db todo, add-auth

    do_allocation_test = default_setting            # create / run / test allocation project

    do_budget_app_test = default_setting            # insert_parent test

    do_other_sqlite_databases = default_setting     # classic models

    do_include_exclude = default_setting            # --db_url=table_filters_tests

    do_docker_mysql = default_setting               # requires docker database be running
    do_docker_postgres =  default_setting           # requires docker database be running
    do_docker_postgres_auth = default_setting       # requires docker database be running
    do_docker_sqlserver = False           # requires docker database be running

    do_docker_creation_tests = default_setting      # build docker image, start it and create projects



    # ***********************
    #   platform specific
    # ***********************

    set_venv = 'source ${install_api_logic_server_path}/venv/bin/activate'
    '''typical source "venv/bin/activate" does not persist over cmds, see...
        https://github.com/valhuber/ubuntu-script-venv/blob/main/use-in-script.sh '''

    docker_database_ip = 'localhost'
    ''' for virtual machine access, set this to host IP '''

