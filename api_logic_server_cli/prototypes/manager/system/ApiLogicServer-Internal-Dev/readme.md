# ApiLogicServer-Internal-Dev

Internal developer tooling. This is ***not*** required to use API Logic Server.
For the architecture, gold-source workflow and changelog, see [dev-architecture.md](dev-architecture.md).

## Install the dev source

Run from the Manager root:

```bash
sh system/ApiLogicServer-Internal-Dev/install-ApiLogicServer-dev.sh [ vscode | charm | x ]
```

This creates `ApiLogicServer-dev/` with `servers/`, `build_and_test/`, `org_git/` (source clones) and `container-volumes/`,
seeded from [container-volumes-template/](container-volumes-template/). It refuses to run if `ApiLogicServer-dev/` already exists.

## Run BLT (Build, Load and Test)

BLT builds the product into a clean Manager (`build_and_test/genai-logic`) and runs the tests against it.
From `ApiLogicServer-src`:

- VS Code: run the **Build Load & Test** launch config (`build-only` variant: **BLT, Hold the Tomato**), or
- terminal:

  ```bash
  cd org_git/ApiLogicServer-src && source venv/bin/activate
  cd tests/build_and_test
  APILOGICSERVER_AUTO_OPEN="" python build_load_and_test.py confirm
  ```

Which tests run is set by `tests/build_and_test/env.py`. That file is **personal and gitignored**: copy the
`env_*.py` closest to your machine over it (for example `env_val_podman.py`, or `env_val.py` for Docker) and edit.

## Pre-set up BLT: containers (Docker, Podman or the host's)

Some tests need three containers: `postgresql-container` (5432), `keycloak` (8080) and `broker1` (Kafka, 9092).
**BLT never creates containers.** Before building, its container preflight checks the ones your enabled tests need.
A stopped container is started. A missing one, or one that will not start, stops BLT with the exact command to run.

Choose how your machine gets its containers with `container_cli` in `env.py`:

| `container_cli` | Use when | Pre-setup |
|---|---|---|
| `'docker'` (default) | Docker is installed | Start Docker Desktop (or the daemon); create the containers once with the commands BLT prints |
| `'podman'` | Podman is installed, no Docker | `podman machine start`; create the containers once with the commands BLT prints; see [Podman setup](https://apilogicserver.github.io/Docs/DevOps-Podman/) |
| `'none'` | A VM install (e.g. Parallels) that uses the **host's** containers | Run the containers on the host; set `docker_database_ip` in `env.py` to the host's IP. The preflight is skipped, nothing is checked |

Settings in `env.py`: `container_cli`, `docker_database_ip`, and `container_preflight = False` to skip the check
entirely. Turn off the tests you cannot support (`do_docker_postgres`, `do_docker_postgres_auth`,
`do_run_nw_kafka`, `do_test_nw_kafka`); a flag that is off needs no container.

**With `'none'`, nothing on this machine verifies the host.** Check it yourself before BLT, and confirm the Kafka
tests can reach the broker from the VM (they were written for a broker on `localhost`).

**One rule for every container: mount from `ApiLogicServer-dev/container-volumes/`, never from `build_and_test/`.**
Docker and Podman record a bind mount's absolute host path when the container is created. A container created from a
project under `build_and_test/` fails after the next rebuild (`crun: cannot stat ...`), and the keycloak test then
fails with a bare connection error. `container-volumes/` is a sibling of `build_and_test/`, so rebuilds do not touch it. Its
`readme.md` and `keycloak/readme.md` hold the create commands, and the preflight prints the same ones.

`container-volumes/` serves Docker and Podman alike (the Docker path is the one exercised most); for Podman setup see [Podman setup](https://apilogicserver.github.io/Docs/DevOps-Podman/) and the `podman` commands in its `keycloak/readme.md`.

[container-volumes-template/](container-volumes-template/) is the gold copy of that directory. It ships with the Manager, so BLT restores it
on every rebuild. The installer copies it to the sibling `container-volumes/`. Never mount a container from the template folder,
and edit the template in gold (`ApiLogicServer-src`), not in a Manager copy.
