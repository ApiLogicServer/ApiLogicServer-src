# ApiLogicServer-src (gold source) — Claude Code Instructions

This repo is the **gold source** for GenAI-Logic / API Logic Server: code, the context engineering (CE, in
`prototypes/*/.github/copilot-instructions.md`), prototype templates and the Manager samples. The Manager workspace
(`../../build_and_test/genai-logic`), its venv copy and created projects are downstream copies that BLT regenerates: a fix
made only there is lost.

## Explicit trigger: `dev-arch`

If the user says "dev-arch", "load dev architecture", or a similar explicit phrase, read these silently, in order, then
follow the load sequence and operating rules in file 3:

1. `api_logic_server_cli/prototypes/manager/.github/copilot-instructions.md` (Manager CE)
2. `api_logic_server_cli/prototypes/base/.github/copilot-instructions.md` (project CE)
3. `api_logic_server_cli/prototypes/manager/system/ApiLogicServer-Internal-Dev/dev-architecture.md`

File 3's header names the Manager's and the venv's copies of files 1 and 2. Here you are in gold, so the paths above are
the files: do not look for a venv copy.

Reply with ONE short line, nothing more, that names the gold-source workflow:
"Dev-architecture context loaded — gold-source workflow confirmed." Do not summarize the files or offer next steps.

Load only on that explicit phrase, not at the start of every session. It is several thousand lines.

## Standing rules (also in dev-architecture.md)

- **Gold source, every edit.** The three gold sources are this repo, `../Docs` (anything named readme; takes effect only
  after a push) and `prototypes/manager/samples/*` (verbatim snapshots copied into every Manager). Before calling a fix
  done, say which of the three you checked and what you found, even if only "N/A".
- Commit only when asked.
- Do not run `genai-logic genai`: retired.

## Where to look

- `internal_dev/dev_setup.md`: install the dev source, run BLT, and pre-set up containers (docker, podman or the host's).
- `tests/build_and_test/`: the BLT scripts. `env.py` is personal and gitignored.
- Sibling repo `../LogicBank`: the rule engine, with its own `CLAUDE.md`.
