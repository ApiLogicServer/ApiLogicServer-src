""" test configuration variables. """


class Config:
    """ api_logic_server_test configuration  """


    # ***********************
    #   what tests to run
    # ***********************

    default_setting = True  # simplify enable / disable most

    do_install_api_logic_server = default_setting   # verify build wheel and local 
    do_logicbank_test = ""                          # use this testpy version (or '')
    

    do_create_api_logic_project = default_setting   # create the default project
    do_run_api_logic_project = default_setting      # start the server 
    do_test_api_logic_project = default_setting     # run the behave tests (test logic, api)
    do_test_api_logic_project_with_auth = default_setting  # run the behave tests (test logic, api)
    do_test_genai = default_setting                 # run the genai tests
    do_test_multi_reln = default_setting            # run the genai tests on airport

    do_create_shipping = default_setting            # run shipping to listen to kafka (might run manually)
    do_run_shipping = False               # run shipping to listen to kafka (might run manually)
    do_run_nw_kafka = True               # run default project, *with* kafka
    do_test_nw_kafka = True


    do_rebuild_tests = default_setting              # rebuild from model, allembic

    do_multi_database_test = default_setting        # add-db todo, add-auth

    do_allocation_test = default_setting            # create / run / test allocation project

    do_budget_app_test = default_setting            # insert_parent test

    do_other_sqlite_databases = default_setting     # classic models

    do_include_exclude = default_setting            # --db_url=table_filters_tests

    do_docker_mysql = False               # requires docker database be running
    do_docker_postgres = False            # requires docker database be running
    do_docker_postgres_auth = False       # requires docker database be running
    do_docker_sqlserver = False           # requires docker database be running

    do_docker_creation_tests = False      # build docker image, start it and create projects



    # ***********************
    #   platform specific
    # ***********************

    set_venv = "f:;cd ${install_api_logic_server_path}/venv && Scripts\\activate"
    '''double slashes... '''

    '''
    winds up something like
    f:;cd C:\\Users\\val\\dev\\ApiLogicServer\\ApiLogicServer-dev\\build_and_test\\ApiLogicServer && venv\\Scripts\\activate && python -m pip install C:\\Users\\val\\dev\\ApiLogicServer\\ApiLogicServer-dev\\org_git\\ApiLogicServer-src
    '''
    docker_database_ip = '10.0.0.77'
    ''' for virtual machine access, set this to host IP '''


