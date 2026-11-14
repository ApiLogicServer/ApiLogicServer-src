""" test configuration variables. """


class Config:
    """ api_logic_server_test configuration  """


    # ***********************
    #   what tests to run
    # ***********************

    # STAGE 1 defaults: nothing here needs a container (no Postgres, Keycloak, Kafka, MySQL, SQL Server, image build).
    # To add containers (stage 2), override single flags in your personal env.py - see internal_dev/dev_setup.md.
    default_setting = True  # simplify enable / disable most

    do_install_api_logic_server = default_setting   # verify build wheel and local 
    do_logicbank_test = ""                          # use this testpy version (or '')
    

    do_create_api_logic_project = default_setting   # create the default project
    do_run_api_logic_project = default_setting      # start the server 
    do_test_api_logic_project = default_setting     # run the behave tests (test logic, api)
    do_test_api_logic_project_with_auth = default_setting  # run the behave tests (test logic, api)
    do_test_multi_reln = False            # this suite (airport etc) broken per new parsed response format

    do_create_shipping = default_setting            # run shipping to listen to kafka (might run manually)
    do_run_shipping = False                         # run shipping to listen to kafka (might run manually)
    do_run_nw_kafka = False               # run default project, *with* kafka
    do_test_nw_kafka = False


    do_rebuild_tests = default_setting              # rebuild from model, allembic

    do_multi_database_test = default_setting        # add-db todo, add-auth

    do_allocation_test = default_setting            # create / run / test allocation project

    do_ai_generated_logic_test = False              # SLOW/costs $: see env_val.py for details

    do_ai_generated_full_prompt_test = False        # SLOW/costs $: see env_val.py for details
    do_ai_generated_full_prompt_test_with_behave = False  # see env_val.py for details

    do_budget_app_test = default_setting            # insert_parent test

    do_other_sqlite_databases = default_setting     # classic models

    do_include_exclude = default_setting            # --db_url=table_filters_tests

    do_docker_mysql = False               # requires docker database be running
    do_docker_postgres =  False           # requires docker database be running
    do_docker_postgres_auth = False       # requires docker database be running
    do_docker_sqlserver = False           # requires docker database be running

    do_docker_creation_tests = False      # build docker image, start it and create projects



    # ***********************
    #   platform specific
    # ***********************

    set_venv = 'source ${install_api_logic_server_path}/venv/bin/activate'
    '''typical source "venv/bin/activate" does not persist over cmds, see...
        https://github.com/valhuber/ubuntu-script-venv/blob/main/use-in-script.sh '''

    docker_database_ip = 'localhost'
    ''' for virtual machine access, set this to host IP '''

    container_cli = 'docker'
    ''' 'podman' | 'docker' | 'none': used by the container preflight (postgres, keycloak, kafka); only matters once you
        turn on a container test (stage 2).  'none' = no container CLI on this machine (VM install using the host's
        containers, reached at docker_database_ip): preflight skipped.
        Containers must mount from ApiLogicServer-dev/podman/, never from build_and_test/ (rebuilt) - see internal_dev/dev_setup.md '''

