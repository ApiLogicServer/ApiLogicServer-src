# Proposal: OpenAI-free pip/Docker variant (FedEx GENAI797 / FOSS 1033497)

**Date:** 2026-08-12
**Context:** FedEx's GENAI797 AI-governance review (Wynford's CoE use-case submission, Risk Tier Medium, Decision Pending) flags Anthropic Claude for FIRST/EnCORE and leaves the "open-source agentic IDE" unnamed. Once identified as GenAI-Logic/ApiLogicServer, a security reviewer doing dependency (SCA) analysis on the FOSS 1033497 request would see `openai` in the package's dependency manifest — a second, entirely unreviewed AI vendor sitting alongside Claude.

## Proposal

Ship a pip/Docker variant of GenAI-Logic for FedEx that excludes the `openai` package entirely, so the dependency manifest shows zero embedded third-party LLM vendor SDKs. The only AI platform touching FedEx data would then be Claude — already in FedEx's review pipeline — with no equivocation.

## Analysis

- `requirements.txt` pins `openai==1.55.3` as a hard (non-optional) dependency of the core `apilogicserver` package. No `anthropic` package is bundled at all — Claude access happens externally (Claude Code/API), not via a vendored SDK.
- All `import openai` sites fall into **three** categories, confirmed by grep across `ApiLogicServer-src` (an earlier pass on this analysis missed the third — corrected 2026-08-12):
  1. **CLI/dev-time code generation** — `api_logic_server_cli/genai/*.py` (`genai.py`, `genai_svcs.py`, `genai_react_app.py`, `genai_graphics.py`, `genai_logic_builder.py`, `genai_utils.py`, `client.py`). Backs WebGenAI and the `--vibe` code-generation command. Not used by FedEx.
  2. **Optional agentic demo scripts** — `integration/mcp/mcp_client_executor.py`, present in several sample projects (`allocate_dept_account_demo`, `basic_demo_ai_rules-supplier`, and also copied into `demo_customs_clvs`). Standalone script, run manually from the terminal, gated by the `APILOGICSERVER_CHATGPT_APIKEY` env var with an explicit bypass path when unset.
  3. **Runtime "AI Rules"** — declarative business rules that call an AI backend automatically during normal rule firing, not via any manual step. Example: `basic_demo_ai_rules-supplier/logic/logic_discovery/place_order/check_credit.py`, requirement 6 ("Use AI to Set Item field unit_price by finding the optimal Product Supplier..."), wired via `Rule.early_row_event` → `ai_requests/supplier_selection.py`, which calls `openai.chat.completions.create` (`gpt-4o-2024-08-06`) directly. This one **is** live in the running app — it fires on every `Item` insert/`product_id` change, same as any other rule. It degrades gracefully (falls back to deterministic minimum-cost selection if `APILOGICSERVER_CHATGPT_APIKEY` is unset or the API call fails), but the `openai` import itself is unconditional in that module and would raise `ImportError` if the package were absent and that code path were reached.
- **Checked whether GENAI797's actual project uses category 3 — it does not.** `demo_customs_clvs/logic/logic_discovery/clvs_eligibility.py` and `shipment_matching.py` use `early_row_event` only for deterministic logic (customs office assignment, controlled-goods flagging); no `_from_ai` calls and no `openai` import anywhere in that project's `logic/` tree. So category 3 doesn't affect GENAI797 today — but this is a fact specific to the current state of that project, not a general property of the framework. If the FedEx use case later adopts an "AI Rules" pattern for HS classification itself (i.e., requirement 6-style, rather than calling Claude externally), it would need to target Claude instead of OpenAI, or it won't function in an openai-free image.
- No other package in the current 110-package dependency set (per `pip-audit-report-8-12-2026.md`) depends on `openai`, so removing it should not cascade.

## Conclusion

Feasible without breaking GENAI797's current production runtime, confirmed by checking the actual `demo_customs_clvs` logic tree (no AI-Rules usage). Only the optional `--vibe`/WebGenAI CLI commands, the standalone MCP demo script, and any *future* AI-Rules-pattern logic (category 3) would stop working in a stripped image. None of the first two are needed for FedEx's deployed use case; the third is a constraint to flag for Wynford — if GENAI797 or a successor project ever wires AI directly into a rule the way `basic_demo_ai_rules-supplier` does, that rule must call Claude, not OpenAI.

## Implementation options

1. **Slim requirements/Dockerfile** — maintain a FedEx-specific `requirements-runtime.txt` (all current deps minus `openai`) and a corresponding Dockerfile, built and audited separately from the standard distribution.
2. **Post-install strip** — `pip uninstall openai` after the normal install, inside the Docker build step. Simpler, but relies on catching it at every image rebuild rather than the dependency list being the source of truth.

Option 1 is cleaner for repeat FOSS/SCA scans since the manifest itself never lists `openai`.

## Status

Proposal stage — not yet built. Pending Val's decision to proceed; would also fold into the GENAI797 response as an answer to the "Tech Stack and Platform" open question (see `BusDev/GENAI797-response.md`).
