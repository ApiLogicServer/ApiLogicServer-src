@.github/copilot-instructions.md

## Claude Code — auto-load dev-architecture

At the start of this session, check if any ancestor directory of the current workspace
is literally named `ApiLogicServer-dev` (framework dev checkout signal, not an end-user
Manager clone or Codespaces workspace). If so, silently read
`system/ApiLogicServer-Internal-Dev/dev-architecture.md` and follow its own mandatory
load sequence (see its header) — no need to ask first, just do it. Confirm with ONE
short line, e.g. "Dev-architecture context loaded." Then continue normally — this
never suppresses or replaces the `.github/copilot-instructions.md` welcome/activation
flow above; both can apply to the same first message.

If no such ancestor exists, skip this entirely — do not mention it.
