""" test configuration variables. """


class Config:
    """ api_logic_server_test configuration  """


    # ***********************
    #   what tests to run
    # ***********************

    default_setting = True  # simplify enable / disable most    

    do_create_manager = False             # create the manager - FIXME not working
    do_test_genai = default_setting                 # complex iteration
    do_test_iso = default_setting                   # complex iteration
    do_test_auto_conv = default_setting             # ensure project rebuilt, not truncated


    # ***********************
    #   platform specific
    # ***********************

    set_venv = 'source ${install_api_logic_server_path}/venv/bin/activate'
    '''typical source "venv/bin/activate" does not persist over cmds, see...
        https://github.com/valhuber/ubuntu-script-venv/blob/main/use-in-script.sh '''

    docker_database_ip = 'localhost'
    ''' for virtual machine access, set this to host IP '''

