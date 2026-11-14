# Dev setup: install, BLT and containers

Where this lives: `ApiLogicServer-src/internal_dev/dev_setup.md` (gold). It is for the framework developer, not for
users of API Logic Server.

> **Working with Claude here:** say **`dev-arch`** (or "load dev architecture"). It works in two places:
> the **Manager** (`ApiLogicServer-dev/build_and_test/genai-logic`, via its `CLAUDE.md`) and **this repo** (via the
> `CLAUDE.md` at its root). Either loads
> [dev-architecture.md](../api_logic_server_cli/prototypes/manager/system/ApiLogicServer-Internal-Dev/dev-architecture.md):
> the gold-source rule (every edit also lands in `org_git/ApiLogicServer-src` / `org_git/Docs`), the BLT workflow and
> the changelog. It answers with one line naming the gold-source workflow. Prefer this repo for gold edits (no
> downstream copy to mistake for gold); use the Manager to test.

## Layout

```
ApiLogicServer-dev/
  org_git/ApiLogicServer-src/   gold source (this repo)
  org_git/Docs/                 gold for docs and readmes (needs a push to take effect)
  build_and_test/genai-logic/   the BLT Manager: rebuilt by every BLT, never edit it as if it were gold
  clean/genai-logic/            pristine second BLT output, for diffing
  servers/                      scratch projects
  podman/                       rebuild-safe volumes for containers (see below)
```

## Install the dev source

From the Manager root:

```bash
sh system/ApiLogicServer-Internal-Dev/install-ApiLogicServer-dev.sh [ vscode | charm | x ]
```

It creates `ApiLogicServer-dev/` with the folders above, and seeds `podman/` from `podman-template/`. It refuses to run
if `ApiLogicServer-dev/` already exists. Gold:
[installers and template](../api_logic_server_cli/prototypes/manager/system/ApiLogicServer-Internal-Dev/).

## Run BLT (Build, Load and Test)

BLT builds the product into a clean Manager and runs the tests against it. From `ApiLogicServer-src`:

- VS Code: the **Build Load & Test** launch config (`build-only` variant: **BLT, Hold the Tomato**), or
- terminal:

  ```bash
  cd org_git/ApiLogicServer-src && source venv/bin/activate
  cd tests/build_and_test
  APILOGICSERVER_AUTO_OPEN="" python build_load_and_test.py confirm
  ```

Which tests run is set by `tests/build_and_test/env.py`. That file is **personal and gitignored**: copy the closest
`env_*.py` over it (for example `env_val_podman.py`, or `env_val.py` for Docker) and edit.

BLT builds from the working tree of this repo, committed or not. Details: dev-architecture.md, "BLT" section.

## Pre-set up BLT: containers (Docker, Podman or the host's)

Some tests need three containers: `postgresql-container` (5432), `keycloak` (8080) and `broker1` (Kafka, 9092).
**BLT never creates containers.** Before building, its container preflight checks the ones your enabled tests need
(`preflight_containers()` in `tests/build_and_test/build_load_and_test.py`). A stopped container is started. A missing
one, or one that will not start, stops BLT with the exact command to run. A running container that bind-mounts under
`build_and_test/` gets a warning with the recreate command.

Choose how your machine gets its containers with `container_cli` in `env.py`:

| `container_cli` | Use when | Pre-setup |
|---|---|---|
| `'docker'` (default) | Docker is installed | Start Docker Desktop (or the daemon); create the containers once with the commands BLT prints |
| `'podman'` | Podman is installed, no Docker | `podman machine start`; create the containers once with the commands BLT prints; [Podman setup](https://apilogicserver.github.io/Docs/DevOps-Podman/) |
| `'none'` | A VM install (e.g. Parallels) that uses the **host's** containers | Run the containers on the host; set `docker_database_ip` in `env.py` to the host's IP. The preflight is skipped, nothing is checked |

Other settings in `env.py`: `docker_database_ip`, and `container_preflight = False` to skip the check entirely. Turn off
the tests you cannot support (`do_docker_postgres`, `do_docker_postgres_auth`, `do_run_nw_kafka`, `do_test_nw_kafka`);
a flag that is off needs no container.

**With `'none'`, nothing on the VM verifies the host.** Check it yourself before BLT, and confirm the Kafka tests can
reach the broker from the VM (they were written for a broker on `localhost`).

**One rule for every container: mount from `ApiLogicServer-dev/podman/`, never from `build_and_test/`.** Docker and
Podman record a bind mount's absolute host path when the container is created. A container created from a project
under `build_and_test/` fails after the next rebuild (`crun: cannot stat ...`), and the keycloak test then fails with a
bare connection error. `podman/` is a sibling of `build_and_test/`, so rebuilds do not touch it. Its `readme.md` and
`keycloak/readme.md` hold the create commands, and the preflight prints the same ones. The same rule applies to
Docker; the `podman/` name is just the directory (only exercised so far with Podman).

`podman-template/` (in `Internal-Dev/`) is the gold copy of that directory. It ships with the Manager, so BLT restores it
on every rebuild; the installer copies it to the sibling `podman/`. Never mount a container from the template folder,
and edit the template in gold, not in a Manager copy.

## Not yet verified

- The dev installer, run end to end on a fresh machine.
- The preflight's `cannot stat` message and the podman-machine-down branch.
- The mount rule under Docker, and `container_cli = 'none'` on a real VM.
