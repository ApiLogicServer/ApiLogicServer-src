# podman/keycloak/

Keycloak for local dev and BLT (`docker_postgres_auth` test runs
`add-auth --provider-type=keycloak` against `http://localhost:8080`).

`import/` holds the realm exports (`kcals` realm + users, `master` realm),
copied from `org_git/basic_demo/devops/keycloak/import`. Keycloak imports
them on first start (`--import-realm`, strategy IGNORE_EXISTING).

## Create the container

Run once (or after `podman rm keycloak`), **from this directory** (`ApiLogicServer-dev/podman/keycloak`). Check
`pwd` first: the mount below uses `$PWD`, and podman records it as an absolute path, so running this from a project
under `build_and_test/` brings back the `cannot stat` failure described below. (BLT's container preflight prints this
same command with the full path already filled in.)

```bash
cd <your ApiLogicServer-dev>/podman/keycloak
podman run -d --name keycloak -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=password \
  -v "$PWD/import":/opt/keycloak/data/import \
  quay.io/keycloak/keycloak:23.0.6 \
  start-dev --import-realm --proxy=edge --hostname-strict=false --hostname-strict-https=false
```

Thereafter: `podman start keycloak` / `podman stop keycloak`.

Verify: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/realms/kcals` -> `200`.
Admin console: http://localhost:8080 (admin / password).

## Why here, not a project's devops/keycloak

Sample projects ship `devops/keycloak/docker-compose.yml` with
`$PWD/import:/opt/keycloak/data/import`. Podman records that as an absolute
host path at container-create time. If the container was created from a
project under `build_and_test/`, the next BLT rebuild deletes that dir and
`podman start keycloak` fails with:

    crun: cannot stat `.../devops/keycloak/import`: No such file or directory

Fix: recreate the container with the command above.

## Refreshing the realm

Realm state lives inside the container (dev-mode H2). To pick up changed
realm JSON, replace files in `import/`, then `podman rm -f keycloak` and
re-run the create command.
