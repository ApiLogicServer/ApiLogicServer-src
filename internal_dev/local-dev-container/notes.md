# Local Dev Container — Simplify Manager Setup

**Status:** idea, not yet implemented. Started 2026-09-14.

## Problem

Two distinct local-Docker paths exist, with different pain:

1. **Per-project dev containers** ("Reopen in Container" per created project) — works,
   but each project = one more container with an auto-generated name. Fine for a single
   BU trying one project; nasty for Val's dev workflow (many test projects → untrackable
   container sprawl).
2. **Manager-in-Docker** (`https://apilogicserver.github.io/Docs/DevOps-Docker`) — this is
   what's being simplified here. Current documented steps:
   ```
   docker run -it --name api_logic_server --rm --net dev-network \
     -p 5656:5656 -p 5002:5002 -v ${PWD}:/ApiLogicServer \
     apilogicserver/api_logic_server
   $ als start
   $ exit
   % code .                      # on host
   $ chmod a+rwx /workspaces/ApiLogicServer   # inside the reopened container
   $ als create --project-name=nw+ --db-url=nw+
   ```
   Manual steps: enter container → run `als start` → `exit` → reopen VS Code on host →
   accept "Reopen in Container" → chmod. Tricky for a non-developer (BU) audience.

## Motivation

Evaluating whether Manager-in-Docker could be a clean on-ramp for a BU to try
Executable Requirements without a local Python/venv install (PWS / `codespaces_mgr` is
the *other*, already-solved on-ramp — this is specifically the "runs on the BU's own
machine, no GitHub Codespaces dependency" case).

Goal: **zero user responsibility beyond running one `docker run` command.**

## What already exists (found by reading gold source)

- `docker/api_logic_server.Dockerfile` sets `ENV APILOGICSERVER_RUNNING=DOCKER` and ends
  with `CMD ["bash"]` — i.e. today the container just drops to an interactive shell; no
  auto-bootstrap.
- `is_docker()` (in `api_logic_server_cli/cli.py`, `api_logic_server.py`, generated
  project `config/server_setup.py`/`config.py`) checks for `/home/api_logic_server` dir
  OR `APILOGICSERVER_RUNNING == "DOCKER"` — this is the existing local/CS/Docker
  detection Val referenced. Already reliable inside the published image.
- `cli.py`'s `main()` (invoke_without_command) ALREADY has partial logic in this
  direction: if no subcommand given and cwd (minus `venv/`) is empty, it prints
  *"Suggestion - if you've not already created the Manager: genai-logic start"* — but
  only prints, doesn't act.
- `manager.py`'s `create_manager()` (the `als start` implementation) is **already
  docker-safe to run non-interactively**:
  - `if project.is_docker: os.chdir(f'/{volume}')` — creates the Manager at the mounted
    volume root, no venv precondition required (the non-docker path exits(1) if no
    venv found; docker path skips that check).
  - At the end, `if project.is_docker:` branch just logs
    `"Docker Manager created, open code on local host..."` and **skips the
    `open_with`/VS Code launch entirely** — so calling `als start` unattended inside
    the container cannot hang trying to open a GUI that isn't there.
- `api_logic_server_cli/prototypes/manager_docker/.devcontainer/` — an existing,
  separate prototype (distinct from `codespaces_mgr`'s `.devcontainer-codespaces/`) for
  a Manager-in-Docker devcontainer. Its `devcontainer.json` only adds the
  `ms-python.python` extension — **no Claude Code / Copilot extension** is
  recommended/installed. Open gap if this becomes the BU on-ramp: a BU running
  Executable Requirements needs an AI assistant inside that container, not just Python.

## Proposed simplification

Replace the image's `CMD ["bash"]` with an entrypoint script that:
1. Checks whether the mounted volume (`/ApiLogicServer`, or whatever `-v` target) is
   empty.
2. If empty: auto-run `als start --volume <name>` (already safe non-interactive per
   above — no VS Code launch attempt in Docker).
3. Optionally `chmod a+rwx` the mounted dir to remove the documented manual chmod step
   (root cause is likely host-UID vs container `api_logic_server`-user UID mismatch on
   the bind mount).
4. Always fall through to `bash` (or exec the passed CMD) so the container is still
   usable interactively afterward, and re-running against an already-populated volume
   is a no-op passthrough to a shell.

Result: user's only step is the one `docker run ...` command. `code .` + "Reopen in
Container" per project remains a separate, already-working step (or is itself the next
thing to look at, per point 1 above, if BU-facing).

## Open questions / next steps

- Confirm exact chmod root cause (host UID vs container `api_logic_server` UID) before
  deciding between `--user $(id -u):$(id -g)` at `docker run` time vs. entrypoint
  `chown`/`chmod`.
- Decide whether `manager_docker` prototype should be resurrected/extended for this, or
  whether the entrypoint change alone (no devcontainer.json involved) is sufficient for
  the "one docker run command" goal.
- If this becomes a real BU on-ramp: `manager_docker/.devcontainer/devcontainer.json`
  needs an AI assistant extension added — currently only `ms-python.python`.
- Where to surface the two-container-sprawl point (per-project reopen) if BUs create
  more than one project — likely a non-issue for the single-project BU case, worth
  stating explicitly rather than assuming.
