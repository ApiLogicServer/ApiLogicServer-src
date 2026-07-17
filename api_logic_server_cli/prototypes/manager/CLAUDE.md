@.github/copilot-instructions.md

## Claude Code — dev-architecture context

**Best-effort auto-load:** at the start of this session, check if any ancestor directory
of the current workspace is literally named `ApiLogicServer-dev` (framework dev checkout
signal, not an end-user Manager clone or Codespaces workspace). If so, silently read
`system/ApiLogicServer-Internal-Dev/dev-architecture.md` and follow its own mandatory
load sequence (see its header) — no need to ask first, just do it. Confirm with ONE
short line, e.g. "Dev-architecture context loaded." Then continue normally — this
never suppresses or replaces the `.github/copilot-instructions.md` welcome/activation
flow above; both can apply to the same first message.

If no such ancestor exists, skip this entirely — do not mention it.

**Reliable fallback trigger:** the auto-load above depends on the model treating it as
an unconditional first action, which doesn't always happen. If the user says "load dev
architecture", "load dev-architecture.md", or any similar explicit phrase — regardless
of whether the auto-load above already ran this session — read
`system/ApiLogicServer-Internal-Dev/dev-architecture.md` now and follow its mandatory
load sequence. Treat this phrase as a hard trigger, not a suggestion: do it even if you
believe the file is already in context.

**Confirmation must be ONE short line, nothing more** — no summary of what the file
contains, no list of what was learned, no restating the trigger back to the user.
Just: "Dev-architecture context loaded." (or equally terse). Do not explain, do not
elaborate, do not offer next steps unless asked.
