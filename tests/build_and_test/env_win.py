""" test configuration variables. """


class Config:
    """ api_logic_server_test configuration  """


    # ***********************
    #   what tests to run
    # ***********************

    default_setting = True  # simplify enable / disable most

    do_install_api_logic_server = True   # verify build wheel and local 
    do_logicbank_test = ""                          # use this testpy version (or '')
    

    do_create_api_logic_project = default_setting   # create the default project
    do_run_api_logic_project = default_setting      # start the server 
    do_test_api_logic_project = default_setting     # run the behave tests (test logic, api)
    do_test_api_logic_project_with_auth = default_setting  # run the behave tests (test logic, api)
    do_test_genai = False                           # requires OpenAI API key (not configured on Windows)
    do_test_multi_reln = False            # this suite (airport etc) broken per new parsed response format

    do_create_shipping = default_setting            # run shipping to listen to kafka (might run manually)
    do_run_shipping = False               # run shipping to listen to kafka (might run manually)
    do_run_nw_kafka = False               # run default project, *with* kafka
    do_test_nw_kafka = False


    do_rebuild_tests = default_setting              # rebuild from model, allembic

    do_multi_database_test = default_setting        # add-db todo, add-auth

    do_allocation_test = False              # requires sh/curl (not available on Windows)

    do_ai_generated_logic_test = False              # SLOW/costs $: see env_val.py for details

    do_ai_generated_full_prompt_test = False        # SLOW/costs $: see env_val.py for details
    do_ai_generated_full_prompt_test_with_behave = False  # see env_val.py for details
    do_ai_generated_logic_test = False              # SLOW/costs $: AI writes charge_distribution.py
                                                     # from a prompt, verified against allocate_dept_
                                                     # account_demo's Behave suite. Confidence check for
                                                     # the rules CE, not the engine — flip to True when
                                                     # validating logic_bank_api.md/allocate.md changes.
                                                     # time: 169->716 (nearly 8 min)

    do_ai_generated_full_prompt_test = False         # SLOW/costs $: AI builds the WHOLE project (DDL +
                                                     # all logic) from samples/prompts/allocation.prompt.md
                                                     # (same file that built allocate_dept_account_demo),
                                                     # self-verified (curl + als.log, or self-authored
                                                     # Behave suite — see flag below). Sibling of
                                                     # do_ai_generated_logic_test above — tests whether
                                                     # full-narrative context (vs. one isolated file/clause)
                                                     # reinforces the model into deriving rollups/constraints
                                                     # on its own. Added Aug 18 2026.

    do_ai_generated_full_prompt_test_with_behave = False  # False (default, fast): the build pass
                                                     # self-verifies via curl + logs/als.log rule-fire
                                                     # trace — one headless call, no Behave authoring.
                                                     # True (slow): second headless pass writes a full
                                                     # Behave suite from its own rules and runs that —
                                                     # the only BLT coverage of AI-driven Behave-suite
                                                     # generation itself. Flip to True when validating
                                                     # that capability specifically.

    do_budget_app_test = default_setting            # insert_parent test

    do_other_sqlite_databases = default_setting     # classic models

    do_include_exclude = default_setting            # --db_url=table_filters_tests

    do_docker_mysql = default_setting               # requires docker database be running
    do_docker_postgres = False            # requires docker database be running
    do_docker_postgres_auth = False       # requires docker database be running
    do_docker_sqlserver = False           # requires docker database be running

    do_docker_creation_tests = False      # build docker image, start it and create projects



    # ***********************
    #   platform specific
    # ***********************

    set_venv = "c:;cd ${install_api_logic_server_path}/venv && Scripts\\activate"
    '''double slashes... '''

    '''
    winds up something like
    c:;cd C:\\Users\\val\\dev\\ApiLogicServer\\ApiLogicServer-dev\\build_and_test\\ApiLogicServer && venv\\Scripts\\activate && python -m pip install C:\\Users\\val\\dev\\ApiLogicServer\\ApiLogicServer-dev\\org_git\\ApiLogicServer-src
    '''
    docker_database_ip = '10.0.0.154'
    ''' for virtual machine access, set this to host IP '''

