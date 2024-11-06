""" test configuration variables. """


class Config:
    """ api_logic_server_test configuration  """


    # ***********************
    #   what tests to run
    # ***********************

    default_setting = False  # simplify enable / disable most    

    do_create_manager = False                               # create the manager - FIXME not working    do_test_iso = default_setting                   # complex iteration
    do_test_auto_conv = default_setting                     # ensure project rebuilt, not truncated
    do_test_genai_demo = default_setting                 # test genai_demo
    do_genai_test_genai_demo_conversation = default_setting # test genai_demo conversation 
    do_test_genai_demo_informal = default_setting     # test genai_demo informal
    do_multi_rule_logic_bad_gen = True           # test multi-rule logic
    do_multi_rule_logic = default_setting                   # test multi-rule logic
    do_data_fix_iteration = default_setting                 # test data fix iteration
    do_airport_4 = default_setting                          # test airport 4    
    do_students_add_logic = default_setting                 # test students add logic   
    do_test_iso = default_setting                           # unexpected language



    # ***********************
    #   platform specific
    # ***********************

    set_venv = 'source ${install_api_logic_server_path}/venv/bin/activate'
    '''typical source "venv/bin/activate" does not persist over cmds, see...
        https://github.com/valhuber/ubuntu-script-venv/blob/main/use-in-script.sh '''

    docker_database_ip = 'localhost'
    ''' for virtual machine access, set this to host IP '''

