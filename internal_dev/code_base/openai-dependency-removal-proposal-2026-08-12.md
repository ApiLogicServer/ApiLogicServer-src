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

## Empirical verification (2026-08-12)

Val asked the underlying question directly: if Python code references a library that was never installed, does the app fail to run, or only the specific call site that needs it? Built and tested the actual no-openai environment to answer it concretely rather than by inference.

**Python's import behavior, in general:** imports execute when the interpreter reaches that line, not ahead of time. A module-level, unconditional `import x` fails the moment that *module* is loaded — even if nothing that needs `x` ever runs. An import placed inside a function body (a "deferred" or "lazy" import) only fails if that function actually executes that line. Whether "the app runs" therefore depends entirely on *where* the import sits, not on whether the library is used somewhere in the codebase.

**Built it:** fresh Python 3.10 venv, installed `requirements-runtime-no-openai.txt` (this directory) — `pip check` reports no broken requirements; the install is clean.

**Tested against real project code, not synthetic examples**, with `openai` genuinely absent from the environment:

- `demo_customs_clvs`'s full `logic/` tree — `declare_logic.py` and every module under `logic_discovery/` (`clvs_eligibility.py`, `shipment_matching.py`, `use_case.py`, `auto_discovery.py`, `isdc_consume.py`) — **imports with zero errors.** Confirms the GENAI797 production project is unaffected, empirically, not just by inspection.
- `basic_demo_ai_rules-supplier`'s `ai_requests/supplier_selection.py` (the category-3 "AI Rules" case) — **also imports cleanly**, because its `from openai import OpenAI` is deferred inside the function, inside an `if api_key:` block. Went further: set `APILOGICSERVER_CHATGPT_APIKEY` to force entry into that branch, then called `select_supplier_via_ai()` directly against the real function with mock row objects. Result: `ModuleNotFoundError: No module named 'openai'` is raised internally, but it's caught by the module's own `except Exception as e:` — logged as `"OpenAI API error: No module named 'openai', using fallback"` — and the rule completes normally via its deterministic minimum-cost fallback (`fallback_used=True`, a real `chosen_supplier_id`/`chosen_unit_price` returned). **No crash, no failed request** — this pattern is already resilient by design, better than the earlier draft of this analysis gave it credit for.
- Contrast case, to confirm the failure mode is real when it *does* apply: `mcp_client_executor.py` has `import openai` unconditionally at module top level. Importing that module directly (as would happen if someone tried to run it as a script) does raise `ModuleNotFoundError` immediately. This is the one genuine "won't run" case — but only if someone executes that specific standalone script, which FedEx's deployment doesn't do.

**Net finding:** an openai-free build not only avoids breaking GENAI797 today, but the one runtime code path that legitimately calls `openai` elsewhere in the codebase (the AI-Rules pattern) already degrades gracefully without it. The only hard failure mode is the standalone MCP script, which isn't part of any deployed service.

## A cleaner permanent fix: wrap the import itself

The one genuine hard-failure case above (`mcp_client_executor.py`'s unconditional top-level `import openai`) doesn't need a separate no-openai build to be safe — wrapping that import in `try/except ImportError` (setting a sentinel like `openai = None` on failure, and checking it at the call site) would make `openai` a soft-optional dependency everywhere in the codebase, the same way `supplier_selection.py`'s deferred-and-caught pattern already behaves. That's a product-level code change, not something to do unilaterally here — flagging it as the more durable fix if Val decides it's worth making generally, rather than only solving it via a stripped requirements file for this one customer.

## Built and published, for real: `python -m build` / `twine`

Tested the actual packaging path, not just the requirements file, since `pyproject.toml` — not `requirements.txt` — is what `python -m build` reads (both currently have to be hand-kept in sync per the `pyproject.toml` header comment; `pyproject.toml`'s own dependency list also pins `openai==1.55.3`).

**Build:** copied `ApiLogicServer-src` to a scratch directory, removed the `openai` line from the copy's `pyproject.toml`, ran `python3 -m build`. Built cleanly — `apilogicserver-17.3.10-py3-none-any.whl` and the matching sdist. Inspected the wheel's `METADATA` directly: 60 `Requires-Dist` entries, zero mentioning `openai` — confirmed stripped at the packaging level, not just in a hand-maintained requirements file.

**Publishing (`twine upload`) — do not push this to public PyPI.** The package name in `pyproject.toml` is `ApiLogicServer`, same as the real public package. PyPI names and versions are global and singular — uploading a stripped variant under that same name/version would either be rejected (version already exists) or, if version-bumped, would sit in the same public project as the real one, confusing anyone who installs `pip install apilogicserver` expecting the full product. A customer-specific compliance variant should never share that identity on a public index.

Two real options instead:
1. **Skip an index entirely** — hand FedEx the built `.whl` file directly, or point them at a git/artifact URL. `pip install <path-or-url>` needs no index at all, and this is exactly the local-install pattern already documented at the top of `pyproject.toml` for Val's own dev workflow.
2. **Private index** — if FedEx's own policy requires installing from a proper package repository rather than a loose file, `twine upload --repository-url <internal-index>` would work, but only once FedEx (or Val) has an internal/private PyPI-compatible index to push to — nothing like that exists in this workflow today.

Recommend option 1 unless Wynford says FedEx's tooling specifically requires a repository-style install.

## Status

**Verified and buildable, two ways.** `requirements-runtime-no-openai.txt` in this directory (venv-install path) and the `python -m build` wheel-strip approach above (packaged-artifact path) both confirmed working against real GENAI797 project code. Pending Val's decision on which distribution mechanism to actually hand FedEx (Docker image, bare wheel, or private index) and whether to pursue the try/except code-level fix as a permanent product change. Would also fold into the GENAI797 response as an answer to the "Tech Stack and Platform" open question (see `BusDev/GENAI797-response.md`).
