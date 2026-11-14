# container-volumes/

> **This is the TEMPLATE** (gold: `ApiLogicServer-src/.../manager/system/ApiLogicServer-Internal-Dev/container-volumes-template/`).
> The dev installer copies it to the sibling `ApiLogicServer-dev/container-volumes/` on a fresh install.
> That sibling is the live location - never mount a container from this template folder:
> it lives in the Manager, which BLT and `create-manager --clean` rebuild.
> Edit the template in gold, not in a Manager copy.


Persistent host directory for docker/podman bind-mount volumes that need to
survive a Manager workspace rebuild (e.g. `genai-logic create-manager --clean`,
or a fresh `build_and_test`/`clean` BLT output).

Sibling of `org_git/`, `build_and_test/`, `servers/` - nothing here is touched
by BLT or Manager rebuilds.

## Rule

A container's bind-mount source must not live under `build_and_test/` (or any
other rebuilt workspace). Podman stores the absolute host path when the
container is created; once a rebuild removes that dir, `podman start` fails
with `crun: cannot stat ...: No such file or directory`. Put such mounts here.

## Services

| Container | Image | Port | Host mount | Setup |
|---|---|---|---|---|
| `keycloak` | quay.io/keycloak/keycloak:23.0.6 | 8080 | `container-volumes/keycloak/import` | [keycloak/readme.md](keycloak/readme.md) |
| `broker1` (kafka) | apache/kafka:3.7.0 | 9092-9093 | intended: `container-volumes/kafka/data`; current container uses anonymous podman volumes | sample's `integration/kafka` compose |
| `postgresql-container` | apilogicserver/postgres:latest | 5432 | podman named volume (no host mount) | - |

BLT uses these via `tests/build_and_test/env.py` (`do_docker_postgres`,
`do_docker_postgres_auth`, `docker_database_ip`, `container_cli`). BLT never
creates containers. Before building, its container preflight starts a stopped
one, or stops and prints the exact command to run (set `container_preflight =
False` in env.py to skip). You can also start them yourself:

```bash
podman machine start          # if not running
podman start postgresql-container broker1 keycloak
podman ps
```

## Adding a service

Organize by service (`container-volumes/<service>/...`). For a sample whose compose file
uses a project-relative mount, point its `volumes:` entry here instead, e.g.:

  volumes:
    - <absolute path of your ApiLogicServer-dev>/container-volumes/kafka/data:/integration/kafka/volume

Add a row to the table above and a `<service>/readme.md` with the exact
create command.

This only matters for this internal dev checkout - general end-user Manager
workspaces aren't repeatedly rebuilt, so their sample compose files keep the
simpler, self-contained project-relative default.
