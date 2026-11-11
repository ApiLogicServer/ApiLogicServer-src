# Assessment: Removing the OpenAI Dependency (Provider-Neutral LLM Client, Ollama as Local Option)

Status: assessment only. No code, CE, sample or dependency has been changed.
Date: Nov 10 2026. Author: Claude (for Val).
Framing note: the original request was "move to Ollama". Ollama is a local runtime, not a generic API
spanning local and cloud models. The generic layer is the OpenAI-compatible chat completions protocol, which
Ollama also speaks. So the real choice is a provider-neutral client, with Ollama as the zero-key local option.
Method: static read of `api_logic_server_cli/genai/`, `prototypes/base`, and the
`basic_demo_ai_rules-supplier` sample. Nothing was run, and Ollama is not installed on this machine, so every
statement about Ollama's behavior below is from general knowledge and is marked **(verify)**.

&nbsp;

## 1. Bottom line

1. **Two different things are called "OpenAI" here, and they should get opposite answers.**
   - **Build-time `genai-*` CLI** (`api_logic_server_cli/genai/`, 3,700 lines): remove it, don't port it to
     Ollama. `dev-architecture.md` already lists it as a candidate for removal (Jul 2026), and a local model
     is the weakest possible fit for its job (section 3).
   - **Runtime AI Rules** (`logic/logic_discovery/ai_requests/*`, MCP executor): this is the strategic one.
     Make the LLM endpoint a configuration choice, with Ollama as a first-class local option. Don't make it
     the only one.
2. **"Remove openai" and "support Ollama" are separable, and the first is nearly free.** The runtime path uses
   the `openai` package for exactly one `chat.completions.create` call. Ollama exposes an OpenAI-compatible
   `/v1/chat/completions` endpoint **(verify)**. So the minimal change is
   `OpenAI(api_key=..., base_url=...)`, or plain `urllib`/`requests`, with no SDK at all.
3. **The real risks are not code.** They are (a) CE: roughly 1,900 lines of training docs and a sample teach
   the AI to write OpenAI-specific handlers, so every newly generated project would keep emitting
   OpenAI; (b) demo reliability and Codespaces, where there is no GPU and small local models choose
   suppliers inconsistently; (c) a quality drop on tasks that need structured output.
4. **Recommendation:** a provider-neutral client over the OpenAI-compatible protocol. It uses a local
   Ollama when one answers, accepts any hosted OpenAI-compatible endpoint by configuration, and keeps the
   existing deterministic fallback (min cost) as the last resort. Details in section 6. For providers that
   don't speak that protocol (Claude, Bedrock), a LiteLLM proxy can sit in front of the same base URL.

&nbsp;

## 2. Inventory: where OpenAI actually lives

### 2a. Build-time: `api_logic_server_cli/genai/` (WebGenAI / `genai-logic genai*`)

| File | Lines | OpenAI use |
|---|---|---|
| `client.py` | 27 | `get_ai_client()`: `OpenAI` or `AzureOpenAI`, key from `APILOGICSERVER_CHATGPT_APIKEY`. Single factory. |
| `genai_svcs.py` | 1,111 | `client.beta.chat.completions.parse(messages, response_format=<Pydantic WGResult>, model=...)`. The one real call site. Default model `gpt-4o`. A comment mentions a fine-tuned `ft:gpt-4o-...` model. |
| `genai.py` | 850 | `import openai`, fine-tune job URLs, temperature plumbing. |
| `genai_utils.py` | 394 | `--fixup`, `--import-genai`, `--rebuild-test-data`. Key and model from env (`APILOGICSERVER_CHATGPT_MODEL`). |
| `genai_logic_builder.py` | 521 | Builds an HTTP `Authorization: Bearer` header from the key itself. A second, hand-rolled auth path. |
| `genai_graphics.py`, `genai_react_app.py`, `genai_mcp.py` | 381 / 290 / 43 | Optional `from openai import OpenAI`. |

Already done: `openai==1.55.3` is no longer a base dependency. It's the optional `ai-rules` extra
(`pyproject.toml:138`), and the openai-free base install was committed in v2.33 / v2.36.

### 2b. Runtime: generated projects

| Item | Where | Notes |
|---|---|---|
| **Supplier-selection handler** | `samples/basic_demo_ai_rules-supplier/logic/logic_discovery/ai_requests/supplier_selection.py` (122 lines) | Lazy `from openai import OpenAI`; `gpt-4o-2024-08-06`; `temperature=0.7`; prompt asks for "ONLY valid JSON", then the code strips markdown fences and `json.loads`. No schema enforcement. Falls back to min cost with no key, an exception, or an invalid supplier id. Records `request`, `reason`, `fallback_used` on a `SysSupplierReq` audit row. |
| **MCP executor** | `prototypes/base/integration/mcp/mcp_client_executor.py`, plus about 18 sample copies | Two `chat.completions.create(model="gpt-4")` calls. Already gated behind a `create_tool_context_from_llm` flag (default off) and a guarded import. |
| **CE / training docs** | `prototypes/base/docs/training/probabilistic_logic.md` (1,114 lines), `probabilistic_logic_guide.md` (483), `probabilistic_template.py` (334), copied into every sample's `docs/training/` | These are the files that make the AI generate handlers like the one above. They say "OpenAI", "API key" and `APILOGICSERVER_CHATGPT_APIKEY`. |
| **Env var** | `APILOGICSERVER_CHATGPT_APIKEY` | Name is vendor-specific, and appears in the handler, MCP executor, CLI and CE. |
| **Sample readme** | `basic_demo_ai_rules-supplier/readme.md:220` | "Sends supplier data ... to OpenAI". |

Not yet inspected: the `Docs` repo pages (WebGenAI, genai-logic docs, the A/B-test and RTP material) and
`docker/webgenie_docker`, `docker/z_old`. Expect additional OpenAI wording there.

&nbsp;

## 3. Build-time `genai-*`: don't port, remove

- Ollama isn't a good replacement for what this pipeline does. It asks a frontier model to emit a very large
  structured object (`WGResult`: models, rules, test data) in one shot. Small and medium local models are
  poor at this. The Jul 2026 audit in `dev-architecture.md` already found there is no semantic repair loop,
  so a weaker model would fail more often with no safety net.
- It depends on OpenAI-only features: `beta.chat.completions.parse` with a Pydantic schema, and a fine-tuned
  `ft:gpt-4o` model. Ollama has structured output via a JSON schema **(verify)**, but the fine-tune has no
  equivalent without a new training pipeline.
- Claude plus the CE (Method 4, System Creation Services) already does this job better, per the same note.
- Removing it deletes the largest block of `openai` code (about 3,700 lines) and shrinks the SCA and
  security surface. The `ai-rules` extra would then only back runtime AI rules.

Open item: `genai-add-mcp-client`, `genai-add-app` (eslint gate) and `genai-graphics` have value
independent of the LLM, per the audit. Decide separately whether to keep them as plain CLI utilities.

&nbsp;

## 4. Runtime AI Rules: the strategic question

### 4a. What a local option (Ollama) gets you

- **No API key, no cloud dependency, no per-call cost.** Fits the demo story, and fits customers with data
  residency or "no data leaves the building" rules, which matters for the governance pitch.
- The supplier prompt includes cost, lead time and region data; local inference keeps that on the box.
- Removes the vendor name from the product's default path (`APILOGICSERVER_CHATGPT_APIKEY`).

### 4b. What a local option costs

| Concern | Detail |
|---|---|
| **Needs a running Ollama process + a pulled model** | Ollama must be installed, running, and have the model downloaded (gigabytes). The "no install, no download" demo rules (Environment-Aware Steps) mean this must degrade, not block. |
| **Codespaces** | No GPU, limited CPU/RAM. A usable model would be small and slow **(verify actual specs)**. A Codespaces user can't realistically run Ollama in the Codespace; they'd point at a remote endpoint or use the fallback. |
| **Quality / consistency** | The handler already trusts free-text JSON ("no markdown, no code blocks") and has an invalid-id fallback. Small models fail that format more often. Output varies run to run (`temperature=0.7`), which makes demo and test assertions flaky. |
| **Latency** | CPU-only local inference can take many seconds per call, inside a database transaction (the early event runs during commit). Worth measuring; a timeout is currently absent. |
| **Reproducibility of reports** | Behave and traceability reports record the AI choice. Non-deterministic local models make before/after comparisons harder. |
| **Support burden** | "Ollama not running", "model not pulled", "wrong model name", "port blocked" become new first-run failure modes. |

### 4c. The existing fallback is the asset

The handler already degrades gracefully (no key, API error or invalid choice leads to min-cost, with
`fallback_used = True` and a reason on the audit row). Any new provider should reuse this unchanged, so
"Ollama isn't there" stays a non-event and the audit trail stays honest about whether AI actually decided.

&nbsp;

## 5. The CE is the biggest lever and the biggest risk

The handler in the sample is itself AI-generated from the CE, not an independent source. Evidence: its sibling
logic files carry `created_by: claude-sonnet-5-5`; the sample was committed as "ai sample by script" (Nov 4
2026) and built by the scripted `demo_ai_rules_supplier` run; and its function names
(`select_supplier_via_ai`, `get_supplier_selection_from_ai`) match the ones in `probabilistic_logic.md`.
(`supplier_selection.py` itself has no `created_by` header; that part is inferred.)

So the sample is the CE's output, and every newly built AI rule comes from the same
`probabilistic_logic*.md` and `probabilistic_template.py`. If those files aren't changed, every new build keeps
emitting `from openai import OpenAI`, whatever the sample looks like. Conversely, once the shape changes, it's
changed in one place (the training docs and template) and flows to every project. The sample is then
regenerated from the updated CE (a blind rebuild), which also serves as the test that the CE change works.

Implication: the migration is mostly a CE edit, and it should land in gold (`prototypes/base/docs/training/`)
first, then regenerate samples through BLT, per the gold-source rule. The AI-facing example needs one shared
way to call the model so each generated handler isn't re-deriving provider logic (see 6).

&nbsp;

## 6. Recommended shape

**A thin, vendor-neutral client that speaks the OpenAI-compatible chat protocol over plain HTTP.**

Terminology: the **LLM client** is code that runs inside the API Logic Server process (and the CLI); there is no
extra process, sidecar or "AI server" shipped with the product. It calls an **endpoint**, a configured URL. What
runs behind that endpoint is the provider's business: a vendor's cloud, or a process the user chose to run
themselves (Ollama, vLLM, a LiteLLM proxy). We never start or manage one.

1. New small module in `prototypes/base` (name TBD, e.g. `integration/ai/llm_client.py`): one function,
   `chat_json(system, user, schema=None) -> dict`, with a timeout, no SDK.
2. Configuration, in `config/default.env` or equivalent: provider base URL, model name, optional key.
   Suggested names (not decided): `APILOGICSERVER_LLM_BASE_URL`, `APILOGICSERVER_LLM_MODEL`,
   `APILOGICSERVER_LLM_API_KEY`. The new client should also accept the old
   `APILOGICSERVER_CHATGPT_APIKEY`, so a user who already exported it needn't reconfigure. (This alias is for
   the new client only; existing generated handlers read the old variable themselves and are unaffected.)
3. Defaults: if nothing is configured, probe `http://localhost:11434` quickly (Ollama's default port
   **(verify)**); if it doesn't answer, use the deterministic fallback and say so in the audit row. Never
   install or download anything, in line with the Environment-Aware Steps rule.
4. Ask for JSON via the endpoint's structured-output option, with the existing fence-stripping and
   invalid-id checks kept as a second line of defense.
5. The handler's own code shrinks to: build candidates, call `chat_json`, validate the id, fall back. The
   `openai` import disappears from generated projects entirely.

Why not "Ollama only": Ollama is a local runtime, not a generic API; hosted models are still the better option for many users, and for Codespaces.
The OpenAI-compatible protocol is spoken by Ollama, OpenAI, Azure OpenAI, vLLM, LM Studio and others
**(verify per provider; Google and Anthropic reportedly offer compatibility layers of uneven completeness)**, so one client covers all of them and the choice becomes a config line, not a code
fork.

Why not LiteLLM or a framework (LangChain etc.) in the base install: the runtime path is a single chat call
returning JSON, so a dependency isn't justified. LiteLLM stays available as an external proxy for providers
outside the compatible set.

Why not the `ollama` Python package: it would swap one vendor SDK for another and keep a dependency on the
install path. Plain HTTP removes the dependency question altogether.

&nbsp;

## 7. Work breakdown (rough, for planning)

| # | Task | Size | Notes |
|---|---|---|---|
| 1 | Decide: remove `genai-*` outright, or keep it behind the `ai-rules` extra for now | decision | Unblocks #6. |
| 2 | Write the vendor-neutral client + config + fallback/alias logic | S | One file; unit-testable against a stub HTTP endpoint, no Ollama needed. |
| 3 | CE: rewrite `probabilistic_logic.md`, `probabilistic_logic_guide.md`, `probabilistic_template.py` to use the client; check `copilot-instructions.md` | M | Highest leverage, and done in gold (`prototypes/base/docs/training/`) first. This is the actual migration, since the samples are CE output. |
| 4 | Regenerate `basic_demo_ai_rules-supplier` from the updated CE (blind rebuild with the `demo_ai_rules_supplier` script); do not hand-edit the handler | S | Doubles as the test that the CE change works: the rebuilt handler must use the client, and behave identically (min-cost fallback) when no endpoint is reachable. Compare against the Nov 4 sample. |
| 5 | MCP executor: same client | S | Behind a default-off flag; low risk. About 18 sample copies refresh through BLT. |
| 6 | Remove or archive `api_logic_server_cli/genai/` and the `ai-rules` extra's genai uses | M | Touches CLI entry points, docs, WebGenAI docker images. Needs an inventory first. |
| 7 | Docs repo, sample readmes, Docker/WebGenAI wording | S-M | Not inspected yet. |
| 8 | Measure on a real Ollama: latency, JSON-validity rate, supplier-choice consistency | S | Informs the default model and the timeout. Not possible from this assessment. |
| 9 | cs-mgr / Docker base image | S | Prototypes are baked into `apilogicserver/api_logic_server`; a manual rebuild is needed for Codespaces to see CE changes. |
| 10 | CE: "migrate AI rules to the LLM client" section, see section 10 | M | Optional convenience for existing projects. Needs a blind test on the Nov 4 supplier sample (OpenAI handler). Written after #3, since it describes the same pattern. |

&nbsp;

## 8. Open questions for Val

1. **Intent:** is the goal vendor independence, cost, data privacy, or removing a dependency from SCA
   scans? The recommendation holds for all four, but which is primary decides whether Ollama is the default or
   just a supported option.
2. **WebGenAI:** is it still in use anywhere? If not, #6 is simply deletion.
3. **Customer expectation:** do any current prospects (e.g. FedEx) expect a hosted model, or an on-prem one?
4. **Default model:** which Ollama model do you want to bless for the supplier demo? That needs a measured
   comparison (#8).
5. **Codespaces story:** accept "AI rules fall back to min-cost unless you configure an endpoint" for
   Codespaces, or provide a hosted default?

&nbsp;

## 9. Not verified

- All Ollama specifics: the OpenAI-compatible route, structured-output support, default port, hardware needs,
  model quality for this task. Treat as hypotheses until tried on a real install.
- Docs-repo and Docker references to OpenAI (not scanned).
- That every `integration/mcp/mcp_client_executor.py` sample copy is identical to the base one (the count of
  about 18 is from a file search, not a diff).

&nbsp;

## Appendix A. What the `ai-rules` extra is

An **extra** is a Python packaging feature: a named, optional group of dependencies inside a package, installed
with a bracketed name.

```
pip install apilogicserver            # base install: no openai package
pip install apilogicserver[ai-rules]  # base + everything listed under "ai-rules"
```

Here it is defined in `pyproject.toml` (about line 138):

```toml
ai-rules = [
    "openai==1.55.3",
]
```

So the `ai-rules` extra means "install the `openai` package, pinned". It exists so that a stock install does not
contain `openai`, which keeps SCA and dependency scans of a normal install from flagging it (see the comment in
`pyproject.toml` and `requirements.txt`). It was split out of the base install in v2.33.

**Who needs it**

| Consumer | Needs `openai`? | Without it |
|---|---|---|
| Runtime AI-rule handlers (e.g. `supplier_selection.py`) | Yes, lazy import | Import fails, handler falls back to min-cost, `fallback_used = True`, reason shows the error |
| MCP executor (`mcp_client_executor.py`) | Only if `create_tool_context_from_llm` is turned on | Import is guarded; nothing breaks while the flag is off |
| Build-time `genai-logic genai*` CLI | Yes | Raises "openai package not installed" |

**What "dropping the extra" means in this document:** deleting that `ai-rules = [...]` block, so that
`[ai-rules]` no longer installs `openai`. This is only safe once nothing shipped needs `openai`: the `genai-*`
CLI is removed, new projects are generated against the provider-neutral client, and existing projects have
moved off it. Old generated handlers rely on the extra, and any such handler fails soft (min-cost fallback),
not hard. **Recommendation: leave the extra in place.** It is already optional, so a stock install has no
`openai` package, and dropping it saves very little. See section 10.

Related: the provider-neutral client proposed in section 6 uses plain HTTP and needs no extra at all.

&nbsp;

## 10. Existing projects: migration by CE, not deprecation

Decision (discussed Nov 10 2026): no deprecation window. With releases about twice a week, a window means
little, because users upgrade in large jumps.

- **Leave the `ai-rules` extra in place.** Existing generated handlers keep working indefinitely, with no
  deadline. The only forcing event is OpenAI retiring a pinned model; the handler already falls back softly
  (min-cost, `fallback_used = True`, reason on the audit row).
- **New projects** get the LLM client from the updated CE (work breakdown #3).
- **Existing projects** can move whenever the user wants, by asking the AI. That is delivered as a CE section
  (work breakdown #10), not a script. Handlers are AI-generated and vary in shape, so a regex or
  deterministic converter would be reliable only on handlers that match the template exactly, and would
  break hand-edited ones silently. An AI following written instructions makes a small, local, diff-style
  edit, which is what the CE already recommends over regenerating from scratch.

**What the CE section contains**

1. **Triggers:** "migrate AI rules", "switch AI calls to Ollama", "remove openai".
2. **Detection:** find handlers using `import openai`, `from openai import`, `OpenAI(`, or
   `APILOGICSERVER_CHATGPT_APIKEY`; list them and confirm with the user.
3. **Before/after example** of the call block.
4. **Scope rule:** change only the call block. Keep the fallback logic, the `Sys*Req` audit columns, the
   docstrings and the early-event wiring.
5. **Edge cases:** hand-edited handlers (show the diff and ask), several handlers in one project, the MCP executor.
6. **Verification:** restart, run the tests (behave, if present), and confirm the min-cost fallback still
   works with no endpoint reachable. The user reads the diff.

**Caveat:** a documented procedure can be skipped or half-followed (this CE has had such cases), so the first
blind run on the Nov 4 supplier sample is the real test. The section should be kept in sync with the updated
`probabilistic_logic*.md`, so there is one description of the pattern and one of the migration.

&nbsp;

## 11. Decisions (Nov 10 2026) and plan

**Decisions**

| Topic | Decision |
|---|---|
| Branch | `neutral-llm`, off `main` (working tree was clean apart from this folder when checked). |
| Retired code | Move `api_logic_server_cli/genai/` and the genai commands from `cli.py` into `internal_dev/genai_retired_PE` (PE = the old prompt-engineering pipeline; CE replaced it). Use `git mv` so history follows. |
| Removed commands | `genai`, `genai-utils`, `genai-logic`, `genai-graphics`, `genai-add-app`, `genai-iterate`. Hidden `genai-cust`, `sample-ai`, `sample-ai-iteration`: still to be checked for use of the genai code. |
| Stub | `genai-create` stays and prints "retired - use your IDE coding assistant". |
| Kept | `genai-add-mcp-client`. Its 43-line `GenMCP` class moves out of `genai/` into its own module; drop the unused `requests` and Pydantic imports. |
| Client | `integration/ai/llm_client.py`, `chat_json(system, user, schema=None)`, plain HTTP, no SDK. Azure: stub with a comment (deployment in URL, `api-version` query parameter, `api-key` header); untested. |
| Existing projects | No deprecation window; the `ai-rules` extra stays; optional CE migration section (section 10). |

**Reference scan results (read-only, before any change)**

Not only the CLI imports `genai/`. These must be handled before the folder can move:

| Importer | What it uses | Needed action |
|---|---|---|
| `api_logic_server_cli/sqlacodegen_wrapper/sqlacodegen_wrapper.py` (about line 443) | `genai_svcs.remove_als_from_models_py` | **Core, non-AI creation path.** Extract this function out of `genai_svcs.py` first. |
| `api_logic_server_cli/create_from_model/dbml.py` (line 15, module level) | `genai_svcs.get_manager_path` | **Core.** Extract the helper; a module-level import means DBML generation breaks outright if the file moves. |
| `api_logic_server_cli/api_logic_server.py` (lines about 1484, 1691-1693) | `GenAI`, `genai.key_module_map()` | The "create project from genai" entry. Remove the branch. |
| `api_logic_server_cli/cli.py` | The commands above, plus `use_genai_module = True` (line 48) | Remove commands; check the flag. |
| `pyproject.toml` (line 95 comment) | Says `genai_svcs.py` defines Pydantic models the base install needs | Check whether anything else still needs Pydantic; update the comment. |
| `tests/genai_tests/` and `tests/build_and_test/build_load_and_test.py` (line 1761 comment, `env_behave_only.py`) | Test suites for the retired commands | Move or retire the genai tests; check BLT does not call them. |

So `genai_svcs.py` is not purely PE: some of its helpers are shared utilities. The first code commit should
extract those, run a normal project creation (and `rebuild-from-database`) to prove nothing regressed, and only
then move the rest.

**Commit order inside `neutral-llm`**

1. Extract shared helpers from `genai_svcs.py` (`remove_als_from_models_py`, `get_manager_path`, anything else
   found), repoint `sqlacodegen_wrapper.py` and `dbml.py`. Check: create a project, `rebuild-from-database`.
2. Move `genai/` and the genai commands into `internal_dev/genai_retired_PE`. Relocate `GenMCP`. Add the
   `genai-create` stub. Remove the `create from genai` branch in `api_logic_server.py`. Check: CLI starts,
   `genai-logic --help`, create, `genai-add-mcp-client`.
3. Retire or move `tests/genai_tests`; confirm BLT does not depend on them.
4. Add `llm_client.py` with a stub-endpoint test.
5. Rewrite the CE training docs and template (gold), plus CE references to the removed commands
   (`genai-add-app`, `genai-add-mcp-client` text stays).
6. Regenerate `basic_demo_ai_rules-supplier` by blind rebuild; `mcp_client_executor_request.py` uses the client.
7. Migration CE section (section 10).

&nbsp;

## 12. What "vendor-neutral" means here (Nov 10 2026)

The two most important providers are Claude and Gemini, so the client has to reach both. Decision: **one protocol,
no native branches yet.** `llm_client` speaks the OpenAI-compatible chat protocol; Claude and Gemini both offer
OpenAI-compatible endpoints, so they are reached by configuration (base URL, model, key), not code.

| Provider | Path | Status |
|---|---|---|
| OpenAI | compat (it is the reference) | One live call worked (Nov 10), via the old key variable. |
| Ollama / vLLM / LM Studio | compat | Stub-tested only; not run against a real Ollama. |
| Claude | Anthropic's OpenAI-compatibility endpoint | **Unverified.** Needs an Anthropic API key (separate from Claude Code login). |
| Gemini (Gemini API key) | Google's OpenAI-compatibility endpoint | **Unverified.** Needs a free AI Studio key. |
| Azure OpenAI, Vertex AI | stub | Auth differs; not testable without a cloud account. |

Compatibility layers are partial. Known unknowns to check on the first live runs: whether `response_format` is
accepted or ignored (the client retries without it on HTTP 400 and strips markdown fences), whether Claude needs
an explicit `max_tokens`, and model-name conventions. If a provider proves unreliable, add a native branch for
that provider only, with a test. The CE configuration examples must be marked "verify before relying on" until
live runs pass. Do not make live calls without Val's go-ahead; an earlier smoke test unintentionally called
OpenAI because the shell had `APILOGICSERVER_CHATGPT_APIKEY` set.
