# ApiLogicServer-Internal-Dev (internals)

Internal developer tooling. This is ***not*** required to use API Logic Server.
For the architecture, gold-source workflow and changelog, see [dev-architecture.md](dev-architecture.md).

## Stage 1: install and run BLT, SQLite only

No containers, no Kafka, no Keycloak, no `env.py`.

### 1. Install the dev source

Run from the Manager root:

```bash
sh system/ApiLogicServer-Internal-Dev/install-ApiLogicServer-dev.sh [ vscode | charm | x ]
```

This creates `ApiLogicServer-dev/` with `servers/`, `build_and_test/`, `org_git/` (source clones) and `container-volumes/`,
seeded from [container-volumes-template/](container-volumes-template/). It refuses to run if `ApiLogicServer-dev/` already exists.

### 2. Run BLT (Build, Load and Test)

BLT builds the product into a clean Manager (`build_and_test/genai-logic`) and runs the tests against it.
From `ApiLogicServer-src`:

- VS Code: run the **Build Load & Test** launch config (`build-only` variant: **BLT, Hold the Tomato**), or
- terminal:

  ```bash
  cd org_git/ApiLogicServer-src && source venv/bin/activate
  cd tests/build_and_test
  APILOGICSERVER_AUTO_OPEN="" python build_load_and_test.py confirm
  ```

You need no `env.py` and no configuration. With none, BLT uses your platform's defaults (`env_mac.py`, `env_win.py`
or `env_linux.py`): the Postgres, Keycloak, Kafka, MySQL, SQL Server and image-build tests are off, so no container is
needed, and everything else (SQLite-based) runs. It prints `BLT env: ... stage 1 defaults (no containers); no env.py`.

Get this green first. Some devs stay here.

## Stage 2: add containers, then configure `env.py`

Do this only when stage 1 is green and you want the full suite (Postgres, Keycloak, Kafka). Add one container at a time.

1. **Set up the runtime and the containers**, from the Manager `README.md`, section *Containers: Podman or Docker*
   (install the runtime, then steps 2 to 4). Two changes for dev: use `V=<your ApiLogicServer-dev>/container-volumes`
   instead of `$HOME/container-volumes`, and keep `--restart always` so they survive a reboot. Or skip ahead: BLT's
   preflight prints the exact create command for any container a test needs and one is missing.
2. **Configure `tests/build_and_test/env.py`** (personal, gitignored). Plain overrides of the platform defaults, no class.
   Copy this, set `container_cli`, and uncomment a flag when its container is up:

   ```python
   container_cli = 'podman'                 # 'docker' | 'podman' | 'none'
   do_run_nw_kafka = True                   # needs broker1
   do_test_nw_kafka = True                  # needs broker1
   # do_docker_postgres = True              # needs postgresql-container
   # do_docker_postgres_auth = True         # needs postgresql-container and keycloak
   ```

   Run BLT. Add one flag at a time. If a container is missing, the preflight stops and prints the command to create it.

| Flag | Needs | Order |
|---|---|---|
| `do_docker_postgres` | `postgresql-container` | first |
| `do_docker_postgres_auth` | `postgresql-container` and `keycloak` | second |
| `do_run_nw_kafka`, `do_test_nw_kafka` | `broker1` | any time |
| `do_docker_mysql`, `do_docker_sqlserver`, `do_docker_creation_tests` | their own containers / an image build | not covered by the preflight |

A name `env.py` sets that the platform file does not define gets a `WARNING ... (typo?)`. A full `class Config` in `env.py`
(a copy of an `env_*.py`) still works but is used as is, not layered. The detail is in `internal_dev/dev_setup.md` (gold).

### How BLT checks containers

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

#### Volumes: what lives where

| Container | Data | Where it lives |
|---|---|---|
| `postgresql-container`, `mysql-container` | database files | A Docker- or Podman-managed named volume. Nothing on disk to protect; a rebuild never touches it. |
| `broker1` (Kafka) | `kafka/data` | Bind mount from `ApiLogicServer-dev/container-volumes/kafka/data` |
| `keycloak` | realm and user JSON | Bind mount from `ApiLogicServer-dev/container-volumes/keycloak/import` |

Docker and Podman behave the same here: **both** use `container-volumes/` for the Kafka and Keycloak bind mounts (the Docker
path is the one exercised most). For Podman machine setup see [Podman setup](https://apilogicserver.github.io/Docs/DevOps-Podman/).

How `container-volumes/` gets its content: [container-volumes-template/](container-volumes-template/) is the gold copy and
ships with the Manager (so BLT restores it on every rebuild). The installer copies it to the sibling `container-volumes/`;
if `container-volumes/keycloak/import` is missing, the preflight's printed Keycloak command copies it from the template
first. The Keycloak realm and user files come from `container-volumes-template/keycloak/import` (identical to
`prototypes/base/devops/keycloak/import`). Never mount a container from the template folder, and edit the template in gold
(`ApiLogicServer-src`), not in a Manager copy.
