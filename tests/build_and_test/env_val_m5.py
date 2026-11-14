""" Val's personal BLT overrides for the M5 Mac, layered over the platform file (tests/build_and_test/env_mac.py).

    INSTALL: copy this file to  tests/build_and_test/env.py  (that name is gitignored; this root copy is just the courier).

    It replaces the old full-Config copy, which pinned  default_setting = True  on every flag - including
    do_docker_mysql, do_docker_sqlserver and do_docker_creation_tests, which the platform file keeps off - so a BLT with
    it needs MySQL, SQL Server and an image build, and its Postgres / Kafka tests need containers.

    STAGE 1 (active, nothing below): no overrides.  The platform defaults need no containers; BLT prints
        BLT env: env_mac.py - stage 1 defaults ...   (or ... + env.py overrides: (none))   and runs 10 tests.
    STAGE 2: uncomment lines one at a time.  BLT's container preflight stops with the exact create command for any
        container that is missing.  Set container_cli to what this machine has.  See internal_dev/dev_setup.md, "Stages". """

# container_cli = 'podman'            # 'podman' | 'docker' | 'none' (none = VM using the host's containers; also set docker_database_ip)

# do_docker_postgres = True           # postgresql-container
# do_docker_postgres_auth = True      # + keycloak (needs postgres too)
# do_run_nw_kafka = True              # broker1
# do_test_nw_kafka = True
