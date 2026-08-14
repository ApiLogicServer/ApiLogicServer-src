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

## Implementation options (superseded — see "Recommended approach" below)

1. **Slim requirements/Dockerfile** — maintain a FedEx-specific `requirements-runtime.txt` (all current deps minus `openai`) and a corresponding Dockerfile, built and audited separately from the standard distribution.
2. **Post-install strip** — `pip uninstall openai` after the normal install, inside the Docker build step. Simpler, but relies on catching it at every image rebuild rather than the dependency list being the source of truth.

Both were viable but require maintaining a second, FedEx-specific artifact (file or image) in parallel with the standard distribution, kept in sync by hand forever. Superseded by the `pyproject.toml` extras approach below, which needs no parallel artifact at all.

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

**Superseded by the recommendation below** — this section describes the packaging *mechanics* (still valid — `python -m build` / where NOT to `twine upload`), but the stripped-copy approach it was demonstrated on has been replaced by extras.

## Recommended approach: `openai` as a `pyproject.toml` optional extra

Val asked whether an env var (`DISABLE_OPENAI`) might be enough, specifically to reduce the number of packages/artifacts to maintain long-term. Two separate questions worth untangling — answered directly, then verified by building it.

**A runtime env var doesn't reduce anything Nexus IQ sees.** SCA scans (Nexus IQ, and Nexus IQ is explicitly what triggered the FOSS 1033497 / GENAI797 review) inspect what's *installed and declared* — `pip list`, the dependency manifest, wheel metadata — not which code paths execute at runtime. `openai` would still be present and still show up in the scan with `DISABLE_OPENAI=true` set; the flag only stops the code from calling it. It doesn't touch the actual thing FedEx's reviewers are looking at, and it doesn't reduce the package count either — `openai` is still installed. This pattern (kill-switch env vars for optional vendor integrations) is genuinely common in industry — just not a fix for *this* problem.

**What does reduce packages to maintain: make `openai` an extra, not a hard dependency, in the single canonical `pyproject.toml`.** Built and verified this directly:

```toml
[project.optional-dependencies]
ai-rules = ["openai==1.55.3"]
```
(removed from the base `dependencies` list)

Result, confirmed by inspecting the built wheel's actual `METADATA`: 60 unconditional `Requires-Dist` entries, **zero** mentioning `openai`; one extra-gated entry — `Requires-Dist: openai==1.55.3; extra == "ai-rules"` — under `Provides-Extra: ai-rules`.

This means:
- `pip install apilogicserver` → base install, no `openai`, clean SCA scan. This is what FedEx would install.
- `pip install apilogicserver[ai-rules]` → everyone else who wants WebGenAI/`--vibe`/AI-Rules gets it by adding one suffix at install time.
- **One published package, one build, forever.** No FedEx-specific requirements file, wheel, or Docker image to keep in sync with the mainline product as it evolves — the exact "reduce packages to maintain" goal Val asked about, solved at the source-of-truth level instead of via a parallel artifact.

This is strictly better than the stripped-requirements-file / stripped-wheel approaches documented above — those still work mechanically (both were built and verified) but require a second artifact maintained by hand indefinitely. Extras need no such thing.

**The env var is still worth adding, just as a complement, not a substitute.** Even with the extra in place, a `DISABLE_OPENAI`-style runtime guard would be useful defense-in-depth for anyone who *does* install `[ai-rules]` but wants a hard guarantee no call goes out — pairs naturally with the try/except-guarded-import fix noted above. Doesn't replace keeping `openai` out of the base manifest; the manifest is what a scanner sees.

## What FedEx would actually deploy: the Docker image, not a bare pip install

Val flagged this is what matters most — Wynford/FedEx would run a Docker image, not `pip install apilogicserver` directly. Traced the real build chain rather than assuming:

- `apilogicserver/api_logic_server` (the tag every project Dockerfile is `FROM`) is a **public image on Docker Hub**, built from `ApiLogicServer-src/docker/api_logic_server.Dockerfile`. That Dockerfile does `pip install --no-cache-dir -r requirements.txt` — the full, unmodified requirements file, `openai` included.
- Every individual project (`demo_customs_clvs/devops/docker-image/build_image.dockerfile`, same pattern in every other sample) is just `FROM apilogicserver/api_logic_server` + `COPY` the project code in. It inherits whatever's in the base image — including `openai` — and adds nothing dependency-wise itself.
- So `openai` enters the picture at the shared public base image, not at the per-project layer. Two ways to keep it out of what FedEx scans:
  1. **Change the base image** (gold source: `docker/api_logic_server.Dockerfile` + `requirements.txt`, or the extras approach above) — affects every customer's image, a real product decision.
  2. **Strip it one layer later, in demo_customs_clvs's own project Dockerfile** — `RUN pip uninstall -y openai` immediately after the `FROM` line. This only affects FedEx's image, touches no gold source, and needs no base-image rebuild/republish.

Option 2 is the pragmatic near-term move — it's the file Wynford would actually run `docker build` against. Drafted it: `build_image_no_openai.dockerfile` in this directory, a one-line-added variant of `demo_customs_clvs/devops/docker-image/build_image.dockerfile`.

**Caveat on verification:** no Docker daemon is available in this environment, so `docker build` itself wasn't run. Verified the underlying operation instead — built a venv from the real, unmodified `requirements.txt` (exactly what the base image's own install step does), confirmed `openai` installs, then ran `pip uninstall -y openai` (exactly what the new Dockerfile's `RUN` line does), then re-ran the same `demo_customs_clvs` logic-tree import test against that environment: clean, zero errors. Functionally equivalent to what the image build would do; the one thing not literally exercised is the container layer itself. Worth an actual `docker build` + `docker run` smoke test on a machine with Docker before handing this to Wynford.

## Refined recommendation (2026-08-12): flip the default, don't special-case FedEx

Val's instinct: instead of the base image having `openai` and FedEx's project stripping it out, build the base image *without* it, and let whoever needs it add `RUN pip install openai==1.55.3` themselves — "in the spirit of optional pip install []." Checked this against the real build chain above, and it's not just simpler, it's the same fix as the `pyproject.toml` extras recommendation, just applied to the file that actually drives the Docker build.

The base image's `pip install --no-cache-dir -r requirements.txt` step reads `requirements.txt`, not `pyproject.toml` — so making `openai` optional for Docker specifically means removing it from `requirements.txt` too (alongside the `pyproject.toml` extras change, both already flagged as needing to move together). Do that, and:

- The public `apilogicserver/api_logic_server` base image becomes openai-free **automatically** — no Dockerfile edit needed anywhere in `docker/api_logic_server.Dockerfile`.
- `demo_customs_clvs`'s project Dockerfile needs **zero** changes. No special FedEx variant at all — the stock template just works. `build_image_no_openai.dockerfile` (drafted above) becomes unnecessary under this approach; leaving it in place as a documented fallback in case Val prefers not to change the shared default.
- Whoever *does* need `openai` adds one line to their own project Dockerfile — exactly Val's proposed `RUN pip install openai==1.55.3`.

**Checked the actual blast radius rather than guessing — it's small and specific.** Grepped every Dockerfile that's `FROM apilogicserver/api_logic_server` (or its `_local` variant) for whether it re-declares `openai` itself. Two places currently rely on silently inheriting it from the base image and would need that one line added to keep working:
- `docker/webgenie_docker/webgen_ai_docker/webgenie.Dockerfile`, `webgenie_local.Dockerfile`, `webgenie_local_license.Dockerfile` (WebGenAI's own builds — currently only explicitly add `colorama astor`, relying on the base image for `openai`).
- `api_logic_server_cli/prototypes/manager/samples/basic_demo_ai_rules-supplier/devops/docker-image/build_image.dockerfile` (the AI-Rules sample — same pattern, no explicit `openai` install of its own).

Every other sample's Dockerfile is unaffected — none of them reference `openai`. So the real cost of this approach is exactly one added line in four files, all of which Val controls directly (gold source), versus maintaining a permanent special-case FedEx variant. This is the same "changes the default for everyone, real product decision, not unilateral" caveat as the extras recommendation — just now with the precise list of what it touches instead of an abstract risk.

## Effort estimate (2026-08-12) — is this actually small?

Val asked directly whether this is genuinely a small change: imports, `pyproject.toml`/`requirements.txt`, and the Dockerfiles. Enumerated the real file list rather than estimating.

**Required for the core fix (FedEx/Docker path works):**
- `pyproject.toml` — 1 line moved to `[project.optional-dependencies]`. Already built and verified.
- `requirements.txt` — 1 line removed. Mirrors the above; drives the Docker base image.

That's the entire required change — `demo_customs_clvs` needs nothing else, confirmed earlier.

**Landmine check corrected (2026-08-13) — the original "ruled out" claim was wrong.** The audit above only traced `cli.py`'s own top-level imports and concluded `ApiLogicServer create` was unaffected. It missed a second, deeper import chain: `api_logic_server_cli/sqlacodegen_wrapper/sqlacodegen_wrapper.py`'s `create_models_py()` — called by `ModelCreationServices`, on **every** project `create`, not gated behind any AI command — does `import api_logic_server_cli.genai.genai_svcs as genai_svcs`. `genai_svcs.py` had `from openai import OpenAI` at module top level, so the moment `openai` was actually implemented as extras and removed from the base install/venv, `ApiLogicServer create` crashed with `ModuleNotFoundError: No module named 'openai'` — confirmed live via `tests/build_and_test/blt.sh`, first test (`create_api_logic_project`), full traceback captured. This is exactly the class of regression the "empirical verification" section above was meant to catch, and didn't, because the earlier synthetic import tests (`demo_customs_clvs`'s own `logic/` tree, `mcp_client_executor.py`) never exercised `ApiLogicServer create` itself against a real openai-free venv — they checked the generated project's logic files, not the framework's own project-creation code path.

Fixed (2026-08-13), matching the "wrap the import itself" pattern this doc already recommended at line 49:
- `try/except ImportError` guard added around the `openai` import in all 7 previously-identified files (`genai.py`, `genai_svcs.py`, `genai_react_app.py`, `genai_graphics.py`, `genai_logic_builder.py`, `genai_utils.py`) plus `client.py` (`get_ai_client()`'s `AzureOpenAI`/`OpenAI` imports moved inside the function body, which already requires an API key to reach).
- A second, smaller landmine surfaced by the same test: `genai_svcs.py` defines module-level `pydantic.BaseModel` classes (`WGResult`, `Rule`, `Model`, `Graphic`, `TestDataRow`) that `sqlacodegen_wrapper.py` needs unconditionally — `pydantic` was never a declared dependency of its own, it only worked because `openai`'s SDK transitively installed it. Added `pydantic>=2.0` as a direct base dependency in both `pyproject.toml` and `requirements.txt` (not AI-vendor software, so no equivalent SCA concern).

**Re-verified against the real CLI**, not synthetic imports: `ApiLogicServer create --project-name=nw_test --db_url=nw+` now succeeds with `openai` completely absent from the venv, producing a valid `database/models.py` (parsed with `ast.parse` to confirm). Re-tested with `openai` installed afterward too — unaffected, `create` still succeeds. The `sqlacodegen_wrapper.py`/`genai_svcs.py` chain is the one hidden systemic risk this proposal's original audit missed; it is no longer a risk with these guards in place.

**To avoid breaking currently-working behavior for other users — 4 files, 1 line each:**
`docker/webgenie_docker/webgen_ai_docker/webgenie.Dockerfile`, `webgenie_local.Dockerfile`, `webgenie_local_license.Dockerfile`, and `api_logic_server_cli/prototypes/manager/samples/basic_demo_ai_rules-supplier/devops/docker-image/build_image.dockerfile` — each needs `RUN pip install openai==1.55.3` added, since each currently inherits `openai` from the base image silently.

**"Fix up the imports" — mechanical, not centralized:** checked whether the 7 `api_logic_server_cli/genai/*.py` files funnel through one shared `import openai`, hoping to only need to guard one place. They don't — `genai.py`, `genai_svcs.py`, `genai_react_app.py`, `genai_graphics.py`, `genai_logic_builder.py`, `genai_utils.py`, and `client.py` each import `openai`/`OpenAI` independently at module top level. Same 3-line `try/except ImportError` pattern, 7 times. Not hard, just not a one-touch fix.

**Lowest priority, genuinely optional:** the `mcp_client_executor.py` standalone script has one canonical template (`api_logic_server_cli/prototypes/base/integration/mcp/mcp_client_executor.py`) that the CLI stamps into new projects — guarding that template fixes all *future* projects in one edit. The ~9 copies already baked into existing sample projects in the repo would need individual patching to also get a friendlier error message, but since none of them run automatically (not part of any Docker `CMD`), this is cosmetic, not functional — skippable for now.

**Net:** yes, small. 2 required lines, 4 Dockerfile lines to avoid regressions, ~7 mechanical import guards for a clean error message instead of a raw traceback, and one already-ruled-out landmine. A few hours of careful, well-scoped work — not a big engineering lift. Still a real product/versioning decision (changes default behavior of the public package and Docker image), so worth Val's explicit sign-off before merging, but the size of the change itself is genuinely small.

## Status

**Implemented and verified in gold source (2026-08-13), triggered by a Sonatype/InfoSec scan of the built product (`Infosec_GenAI-Logic_17.3.10-Build-20260813-154704.pdf`) surfacing `openai`-adjacent findings alongside unrelated npm CVEs.** The `pyproject.toml` extras + matching `requirements.txt` change described above is done, not just proposed:

- `pyproject.toml`: `openai==1.55.3` moved to `[project.optional-dependencies] ai-rules`; `pydantic>=2.0` added as a new direct base dependency (see landmine correction above).
- `requirements.txt`: `openai==1.55.3` line removed (commented, with pointer to the extra); `pydantic>=2.0` added.
- `docker/webgenie_docker/webgen_ai_docker/{webgenie,webgenie_local,webgenie_local_license}.Dockerfile` and `api_logic_server_cli/prototypes/manager/samples/basic_demo_ai_rules-supplier/devops/docker-image/build_image.dockerfile`: explicit `RUN pip install openai==1.55.3` added (4 files, as scoped in the effort estimate above).
- All 7 `api_logic_server_cli/genai/*.py` files + `client.py`: `openai` imports guarded (see landmine correction above) — this was not in the original scope but became required once the missed `sqlacodegen_wrapper.py` chain was found.
- Base-install wheel confirmed via direct `METADATA` inspection: 60 unconditional `Requires-Dist` entries, zero mentioning `openai`; one extra-gated `Requires-Dist: openai==1.55.3; extra == "ai-rules"` under `Provides-Extra: ai-rules`.
- **Live-tested via `tests/build_and_test/blt.sh`, not just static inspection** — this is what caught the `sqlacodegen_wrapper.py` regression in the first place. `ApiLogicServer create --project-name=nw_test --db_url=nw+` re-verified afterward against the real installed venv, both with `openai` absent and with it installed; both succeed.
- `build_image_no_openai.dockerfile` (this directory) was the near-term FedEx-specific artifact from the earlier "don't touch mainline" option — **no longer needed**, since the mainline base image is now openai-free by default. Left in place, unused, as a documented fallback only.

**Not yet done, not required for FedEx/this scan:** a real `docker build`/`docker run` smoke test (no Docker daemon available in this environment); the `mcp_client_executor.py` standalone-script guard (explicitly deprioritized above, still true).

Would fold into the GENAI797 response as an answer to the "Tech Stack and Platform" open question (see `BusDev/GENAI797-response.md`).

## Second scan, 2026-08-14: `Infosec_GenAI-Logic_17.3.14` — 16 violations, up from 15

A rebuild + re-release + resubmission to Sonatype came back **worse**, not clean, with the *same* flagged versions from the first report (`lodash 4.17.23`, `Flask-Cors 3.0.9`, `react-scripts`'s CRA-chain CVEs) still present, plus one new one (`glob:11.1.0` now flagged too, `serialize-javascript` and `underscore` also newly implicated). Two separate root causes found, not one:

**1. The npm fix only ever touched 1 of 14 `package.json` files.** `react-admin-template/package.json` (the one `genai-add-app`/Claude-CE React app generation copies from) was the only file patched on 2026-08-13. But the exact same `react-scripts@5.0.1`/CRA vulnerable-dependency pattern is baked into 13 other checked-in React app skeletons: `basic_demo/ui/{my-react-app,my-react-app-cards}`, `basic_demo/customizations/ui/reference_react_app`, `nw/ui/reference_react_app`, and the same three under each of `manager/samples/{basic_demo_sample,basic_demo_ai_rules-supplier,basic_demo_logic_gov}`. None of these are generated *from* `react-admin-template` — they're separate, independently-checked-in copies (12 of the 13 are byte-identical to each other, `nw`'s has a few extra map/tree-view deps). Whatever project the Sonatype scan's `17.3.14` build actually bundled evidently pulled its React app from one of these 13 untouched copies, not from `react-admin-template`.

Fixed 2026-08-14: applied the same `overrides` block to all 13 remaining files.

**2. The original `overrides` values were wrong for two packages** — `lodash: "^4.17.23"` and `nanoid: "^3.3.11"` used the *vulnerable* version itself (or a vulnerable version within range) as the floor, not the patched one. A caret range floor of the vulnerable version is satisfied by that vulnerable version — npm is free to resolve to exactly `4.17.23`/`3.3.17` if nothing else in the tree pressures it higher, and in `react-admin-template`'s tree nothing did (it happened to land on `4.18.1` for unrelated reasons — lucky, not correct). In the 13 other, differently-shaped trees, npm resolved literally to the vulnerable floor, which is why the second Sonatype report caught it: the "fix" was building a version string that included the vulnerable release as a valid target. Corrected via `npm audit`'s actual advisory ranges, not guessed:
- `lodash`: `^4.17.23` → `^4.18.1` (advisory: vulnerable `<=4.17.23`)
- `nanoid`: `^3.3.11` → `^3.3.18` (advisory: vulnerable `<3.3.18`)
- `serialize-javascript`: `^6.0.2` → `^7.0.5` (advisory: vulnerable `<=7.0.4` — `6.0.2` was never actually safe, just not what the *first* Sonatype scan happened to flag)
- Added `underscore: "^1.13.8"` (advisory: vulnerable `<=1.13.7`) — pulled in via `react-scripts` → `bfj` → `jsonpath`, present in every one of the 14 trees, never in the override list at all until now

All 14 files corrected and re-verified (2026-08-14): `npm install` + `npm audit` on every one shows `13 vulnerabilities (9 low, 4 moderate)` — **zero high**, consistent across all 14, and direct `node_modules` inspection confirms 0 occurrences of every version either Sonatype report flagged, across all 14 trees. `package-lock.json` regenerated (not just `package.json`) for all 14, since a scanner reading the checked-in lockfile directly (not running `npm install` itself) would still see the old resolved versions otherwise — this is likely part of why the first "fix" didn't fully register on rescan either.

**Two pre-existing, unrelated bugs found and ruled out as NOT caused by this work** (confirmed by reproducing on git-unmodified originals before touching anything):
- `basic_demo/ui/my-react-app`: `npm run build` fails — `Module not found: '@mui/icons-material/Add'` — `Order.js`/`Item.js`/`Customer.js`/`Product.js` import from `@mui/icons-material` but `package.json` never declares it as a dependency. Not a security issue; a broken build, independent of the CVE fix.
- `nw/ui/reference_react_app`: `npm run build` fails under `CI=true` — `Module not found: 'buffer'` from `js-yaml@3.15.1` (pulled in via `react-scripts`→`babel-jest`→`babel-plugin-istanbul`, unrelated to any overridden package) — webpack 5 dropped the automatic Node core-module polyfills CRA used to include. Both are real product bugs worth fixing separately; flagged here, not fixed, since they're outside the security-fix scope and predate this session.

**Flask-Cors — resolved: the published PyPI release is clean; the scan target is the open question.** Same puzzle as above (`3.0.9` in both the 08-13 and 08-14 reports, byte-identical CVEs, despite `pyproject.toml` correctly pinning `Flask-Cors>=6.0.0` since commit `a0d7614e` on 2026-08-13, with `main` HEAD a clean fast-forward past it — nothing reverted it). Proved directly rather than left as a hypothesis:
1. Built a fresh wheel from current gold source, inspected `METADATA` directly: `Requires-Dist: Flask-Cors>=6.0.0`, unconditional.
2. Downloaded the **actual published PyPI release**, `apilogicserver==17.3.14` (confirmed via `pip index versions apilogicserver` — `17.3.14` genuinely is the live latest), inspected its `METADATA`: same correct `Requires-Dist: Flask-Cors>=6.0.0`, and `openai` correctly gated behind `Provides-Extra: ai-rules`.
3. **Ran the actual install**: fresh venv, `pip install apilogicserver==17.3.14`. Result: `flask-cors` installs at `6.0.5`. `openai` is absent (`pip show openai` → not found).

This rules out gold source, the packaging step, and the published artifact itself — all three are correct. A clean `pip install apilogicserver==17.3.14` right now, today, does not and cannot produce `Flask-Cors 3.0.9`. So the `17.3.14` Sonatype finding cannot be explained by anything in this codebase or on PyPI — the gap is entirely in **what got fed to the scanner and how**. Per Val: Sonatype's process is "install the release, inspect the tar files" — worth confirming with them directly whether that install step used a clean environment against the current release, or reused a cached/prior environment, image layer, or a different (older) artifact than PyPI's `17.3.14`.

## Third finding, 2026-08-14: `venv_setup/requirements-no-cli.txt` — 10 more stale copies, same openai/pydantic gap

Separate from the npm/react-scripts scope above: `api_logic_server_cli/prototypes/base/venv_setup/requirements-no-cli.txt` (and identical/near-identical copies under `prototypes/manager/samples/*` and one `genai_demo` example — 10 files total) is a **full, explicit dependency list**, not a delegator like `prototypes/base/requirements.txt` (which just says `ApiLogicServer` and inherits from `pyproject.toml` automatically — already confirmed correct, no fix needed there). This file predates the 08-13 `openai`-extras fix and was never updated to match — already a known, documented drift pattern (see `dev-architecture.md`'s own notes on this file's `LogicBank` pin going stale previously, same file, same category of bug).

Found: 7 of the 10 had `openai==1.55.3` as an unconditional last line with no gating; none had `pydantic` at all (the same landmine as `pyproject.toml`'s own `sqlacodegen_wrapper.py`→`genai_svcs.py` chain — this file feeds a project-local venv setup path, so the same missing-`pydantic` crash on `create` would apply here too if a user followed this file's setup instructions after `openai` is no longer transitively pulling it in). 3 of the 10 (`basic_demo_ai_rules-supplier`, `basic_demo_sample`, `genai_demo_docs_logic`) are on an older, shorter format (33-34 lines vs. 55+) that never had `openai` at all — broader staleness beyond this fix, not addressed here (out of scope: these need a full pin refresh, not just the openai/pydantic gap).

Fixed 2026-08-14, same pattern as `pyproject.toml`: added `pydantic>=2.0` to all 10; commented out `openai==1.55.3` (with the same "optional, pip install if needed" note) in the 7 that had it. Exception: `basic_demo_ai_rules-supplier` genuinely needs `openai` at runtime (its `ai_requests/*` logic calls it directly, same reasoning as its Dockerfile fix earlier) — added `openai==1.55.3` there explicitly, uncommented, matching the Docker fix.

Not verified via actual `pip install` for these 10 (unlike the npm files and the PyPI release above) — this file isn't wired into any CLI code path (`grep` found no `.py` reference to `requirements-no-cli.txt`), so it's a manual/documented setup helper, not something `genai-logic create` runs automatically. Lower urgency than the npm/react-scripts fix, but worth the same correction for consistency and to close the gap before it's the next thing a stale-file audit turns up.
