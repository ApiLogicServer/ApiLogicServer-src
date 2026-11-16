""" Personal BLT overrides (gitignored), layered over env_mac.py (stage 1 defaults: no containers).
    Only list what differs from the platform file. See internal_dev/dev_setup.md. """

# do_install_api_logic_server = False

# stage 2: containers (docker is on this machine; container_cli defaults to 'docker')
do_run_nw_kafka = True
do_test_nw_kafka = True

do_docker_mysql = True
do_docker_postgres = True
do_docker_postgres_auth = True
do_docker_sqlserver = True

do_docker_creation_tests = True
