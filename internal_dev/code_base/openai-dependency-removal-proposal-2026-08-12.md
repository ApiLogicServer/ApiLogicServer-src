# Proposal: OpenAI-free pip/Docker variant (FedEx GENAI797 / FOSS 1033497)

**Date:** 2026-08-12
**Context:** FedEx's GENAI797 AI-governance review (Wynford's CoE use-case submission, Risk Tier Medium, Decision Pending) flags Anthropic Claude for FIRST/EnCORE and leaves the "open-source agentic IDE" unnamed. Once identified as GenAI-Logic/ApiLogicServer, a security reviewer doing dependency (SCA) analysis on the FOSS 1033497 request would see `openai` in the package's dependency manifest — a second, entirely unreviewed AI vendor sitting alongside Claude.

## Proposal

Ship a pip/Docker variant of GenAI-Logic for FedEx that excludes the `openai` package entirely, so the dependency manifest shows zero embedded third-party LLM vendor SDKs. The only AI platform touching FedEx data would then be Claude — already in FedEx's review pipeline — with no equivocation.

## Analysis

- `requirements.txt` pins `openai==1.55.3` as a hard (non-optional) dependency of the core `apilogicserver` package. No `anthropic` package is bundled at all — Claude access happens externally (Claude Code/API), not via a vendored SDK.
- All `import openai` sites fall into two categories, confirmed by grep across `ApiLogicServer-src`:
  1. **CLI/dev-time code generation** — `api_logic_server_cli/genai/*.py` (`genai.py`, `genai_svcs.py`, `genai_react_app.py`, `genai_graphics.py`, `genai_logic_builder.py`, `genai_utils.py`, `client.py`). Backs WebGenAI and the `--vibe` code-generation command. Not used by FedEx.
  2. **Optional agentic demo scripts** — `integration/mcp/mcp_client_executor.py`, present in several sample projects (`allocate_dept_account_demo`, `basic_demo_ai_rules-supplier`, and also copied into `demo_customs_clvs`). Standalone script, run manually from the terminal, gated by the `APILOGICSERVER_CHATGPT_APIKEY` env var with an explicit bypass path when unset.
- None of these are imported by the Flask app at startup or invoked automatically by a running production API server. A deployed customs-classification service (the GENAI797 production shape) never touches this code path.
- No other package in the current 110-package dependency set (per `pip-audit-report-8-12-2026.md`) depends on `openai`, so removing it should not cascade.

## Conclusion

Feasible without breaking the production runtime. Only the optional `--vibe`/WebGenAI CLI commands and the standalone MCP demo script would stop working in a stripped image — neither is needed for FedEx's deployed use case.

## Implementation options

1. **Slim requirements/Dockerfile** — maintain a FedEx-specific `requirements-runtime.txt` (all current deps minus `openai`) and a corresponding Dockerfile, built and audited separately from the standard distribution.
2. **Post-install strip** — `pip uninstall openai` after the normal install, inside the Docker build step. Simpler, but relies on catching it at every image rebuild rather than the dependency list being the source of truth.

Option 1 is cleaner for repeat FOSS/SCA scans since the manifest itself never lists `openai`.

## Status

Proposal stage — not yet built. Pending Val's decision to proceed; would also fold into the GENAI797 response as an answer to the "Tech Stack and Platform" open question (see `BusDev/GENAI797-response.md`).
