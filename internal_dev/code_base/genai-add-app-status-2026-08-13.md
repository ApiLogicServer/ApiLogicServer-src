# Status: `genai-add-app` (React app generation) vs. Claude/CE

**Date:** 2026-08-13
**Context:** Val is gradually moving off OpenAI/prompt-engineering (PE) toward Claude/context-engineering (CE). WebGenAI is a separate, larger piece of that migration — out of scope here. This note covers just one aspect: custom React app generation.

## Current state

`genai-add-app` (CLI command, backed by `api_logic_server_cli/genai/genai_react_app.py`, calls OpenAI) has already been **replaced as the default** by a Claude/CE-based workflow — confirmed live and documented:

- **Published, user-facing doc:** [Admin-Vibe-Sample](https://apilogicserver.github.io/Docs/Admin-Vibe-Sample/) — the recommended path is now telling the IDE AI assistant "Create a new react app named my-app-name from ui/admin/admin.yaml," not running the CLI command.
- **Project CE** (`prototypes/base/.github/copilot-instructions.md`, "Create and Customize React Apps" section, v3.33): direct generation via Claude/Copilot reading `ui/admin/admin.yaml` + `docs/training/admin_app_2_functionality.prompt.md` is the **default method**. `genai-add-app --vibe` is explicitly demoted to "Fallback (only if no AI assistant is available in this environment)."

## Why it wasn't yanked in this session

Val was considering removing `genai-add-app` outright as part of this InfoSec pass (Sonatype scan flagged CVEs in npm deps pulled in via `react-scripts`/CRA in `system/genai/app_templates/react-admin-template/`). Held off because:

- Both the CE default path **and** the `--vibe` fallback copy the same `react-admin-template/package.json`/`package-lock.json` skeleton (`genai_react_app.py`'s `shutil.copytree`) — so patching that template's npm deps (done this session — see `overrides` in `package.json`, verified 0 flagged versions remain, verified against a real generated `nw` project) fixes the Sonatype findings **regardless of which generation method a user takes**.
- That removed the InfoSec urgency that would have forced the yank-now decision. Val's plan to eventually drop `genai-add-app` stands, but as a deliberate migration step on his own timeline, not a forced consequence of this scan.

## Open item, not yet done

`genai-add-app` and its CLI docstring/help text still present the OpenAI path without pointing to the Claude/CE default or noting it's now secondary. If/when Val revisits this: either add a deprecation note to the command's help text pointing at the Admin-Vibe-Sample workflow, or remove the command entirely once he's ready. Not urgent — no InfoSec pressure driving it now.
