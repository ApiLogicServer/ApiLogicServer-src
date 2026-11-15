# Retired GenAI (prompt engineering) sections of dev-architecture.md

Archived Nov 15 2026 from `api_logic_server_cli/prototypes/manager/system/ApiLogicServer-Internal-Dev/dev-architecture.md` (version 2.46), verbatim, when the fine-tuned ChatGPT pipeline (`genai-logic genai` family) was retired. The `Ready` flag / `nw_sample` notes inside the PE section were kept in dev-architecture.md, in its section "nw_sample: the Ready Flag and LogicBank Regression Test".

---

## From "AI Integration Architecture - Four Distinct Modes"

### 3. GenAI CLI Services (OpenAI Fine-Tuned ChatGPT)
**Purpose:** Automated project **generation from natural language prompts**  
**Technology:** Fine-tuned ChatGPT (not Claude)  
**Commands:**
- `genai-logic create --using="natural language"` - Generate complete project from prompt
- `genai-logic logic-translate --using-file=docs/logic` - Generate rules from NL requirements

**🚨 Candidate for future removal (Jul 2026):** This was the original AI story — fine-tuned
ChatGPT + prompt engineering, exposed via `genai-logic genai-*` and later wrapped by WebGenAI
as a full web app on top of the same CLI. WebGenAI in particular turned out very complicated:
correct test-data generation and detecting/fixing rule-generation errors were persistent, hard
problems that needed significant machinery to paper over. Claude + Context Engineering (mode 2
below — System Creation Services, Method 4) is now producing materially superior results without
that complexity: no fine-tuning pipeline, no WGResult parsing/repair loop, no separate WebGenAI
build/deploy cycle. Val is considering removing `genai-logic genai-*` (and eventually WebGenAI)
over time. **Not yet acted on** — no code, prompts, or docs have been removed; this is a forward
note for whoever picks up that removal, not a statement that it's deprecated today. See also
`CLAUDE.md`'s standing rule to never run `genai-logic genai` — that predates this note and was
already steering AI assistants away from this path.

**Build update (v2.33, Aug 2026):** `openai` — the package this entire mode depends on — is no
longer a base install dependency; it moved to the `ai-rules` optional extra
(`pip install apilogicserver[ai-rules]`). A stock install/venv now has no `openai` package at all,
so any of the commands below will fail at import time unless that extra was installed. See the
v2.33 changelog entry above for the commit and full detail.

**Command-by-command audit (Jul 2026) — deterministic value vs. pure LLM re-ask:**

| Command | Verdict | Why |
|---|---|---|
| `genai` (core) | Some real value | Generates model code from the LLM's structured JSON, then **actually executes it** to build a SQLite DB — catches real Python/SQLAlchemy exceptions (e.g. "Could not determine join condition") and retries once with `use_relns=False`. Not semantic validation, just "does the generated code run." |
| `genai-utils --fixup` | Pure re-ask | Repackages existing artifacts into a new prompt, resubmits. No static analysis of what's wrong. |
| `genai-utils --import-genai` | Real, but WebGenAI-only | Merges a WebGenAI export's models into `database/models.py`, builds a DB via `runpy`, triggers `rebuild-from-database`. **Goes away entirely once WebGenAI is gone** — it exists solely to consume WebGenAI's export format. |
| `genai-utils --rebuild-test-data` | Real, but crude | `response2code.py` does `ast.parse()` syntax repair on generated test-data rows; wraps inserts in try/except with a dedup set for idempotent retries. No FK/referential-integrity checking. |
| `genai-logic` | Pure re-ask | Splices LLM rule text into a file; no execution/correctness check. Same job an interactive assistant does today with the same training docs open. |
| `genai-graphics` | Real generator, but incomplete pipeline | Jinja-templated dashboard scaffolding; wraps each generated chart query in try/except so one bad query doesn't break the dashboard. **Gap (found Jul 2026, confirmed by Val as the actually-tricky part):** generates `api/api_discovery/dashboard_services.py` + a `/dashboard` endpoint, but does NOT wire it into the Admin App — that requires a manual hand-edit of `ui/admin/home.js` to embed `<iframe src="http://localhost:5656/dashboard">`, documented only in [WebGenAI-CLI.md](https://apilogicserver.github.io/Docs/WebGenAI-CLI/#dashboard-graphics), not discoverable from code. An AI assistant without that doc open will generate the dashboard service correctly and then flail on Admin App integration — exactly what happened when this was tried live. This is a CE gap to close (document the trigger + home.js wiring as a proper CE pattern), not a reason to keep the genai-* pipeline. |
| `genai-add-app` | Mixed | Runs real `eslint` on generated JS (genuine quality gate) — but on failure just re-asks the LLM from scratch, no auto-fix. `--vibe` flag is only a doc-link log message, no content. |
| `genai-add-mcp-client` | Real, trivial | No LLM call at all — copies a template file, splices YAML. Worth keeping as a plain CLI utility independent of the genai-* question. |
| `genai-create`/`genai-iterate` | Bookkeeping only | Prompt-file naming/sequencing for conversation replay; no AI-specific logic. |

**Bottom line of the audit:** there is no rule-correctness or FK/referential-integrity
validation anywhere in this system's "repair loop" — it's exception-catch-and-retry, or
eslint, or `ast.parse()`, never semantic verification that rules fire correctly or that test
data satisfies referential integrity. The hardest problems WebGenAI was built to paper over
(correct test data, detecting/fixing rule-generation errors) were never actually solved
deterministically — which matches the lived experience that motivated this whole note.

**What's genuinely lost if WebGenAI goes away: the self-serve, no-IDE, browser-only
experience** — a non-developer sketching a schema+logic and getting a hosted, running app
without touching a CLI or editor. Every other capability (rule generation, test data,
dashboards, React scaffolding) is already matched or exceeded by an interactive Claude Code
session using this project's CE docs. That's a hosted-frontend problem, not an AI-pipeline
problem: solvable by fronting Claude + CE with a hosted VS Code derivative (code-server /
github.dev-style web IDE) or extending `codespaces_mgr`'s existing Codespaces flow — either
gives a browser-only user the *same* Claude+CE experience developers get locally, rather than
maintaining a second, weaker, ChatGPT/PE-based pipeline just to serve that one audience.

**What it does:** Transforms natural language → working projects:
- Parses NL requirements
- Generates SQLAlchemy models (with derived columns for rules)
- Generates LogicBank rules (sums, formulas, constraints)
- Generates test data
- Returns structured JSON (WGResult with models, rules, test_data)
- Note: this is PE (prompt engineering); the items above are CE (Context Engineering built into projects)

**Example Input:**
```
Create a system with customers, orders, items and products.
Check Credit: Customer.balance = sum of unpaid orders, 
balance must not exceed credit_limit.
```

**Example Output:** Complete project with 4 tables, 5 rules, working API, Admin UI, test data

**Key Insight:** Generates **specifications** (rules), not procedural code. Rules executed by proven engine.

**Prompt Engineering:**
- Templates: `system/genai/prompt_inserts/` (sqlite_inserts.prompt, logic_inserts.prompt, etc.)
- Training examples: `org_git/ApiLogicServer-src/tests/genai_tests/logic_training/`
- Fine-tuning data: logic_training/ft.jsonl


---

## 🤖 GenAI Prompt Engineering Architecture

### Overview: ChatGPT Project Creation Pipeline

The `genai-logic create` command uses **fine-tuned ChatGPT** to translate natural language requirements into complete working projects. The system uses **prompt engineering** to surround user input with structured instructions.

### Key Locations

**Prompt Templates:** `system/genai/prompt_inserts/`
```
├── sqlite_inserts.prompt                    # Main orchestrator for DB creation
├── sqlite_inserts_model_test_hints.prompt   # SQLAlchemy class generation rules
├── logic_inserts.prompt                     # LogicBank rule generation
├── logic_translate.prompt                   # NL → LogicBank translation (existing DB)
├── graphics.prompt                          # Dashboard chart generation
├── response_format.prompt                   # WGResult Pydantic schema
└── web_genai.prompt                         # WebGenAI-specific (15+ tables)
```

**Training Examples:** `org_git/ApiLogicServer-src/tests/genai_tests/logic_training/`
```
├── genai_demo.prompt                        # Check Credit + No Empty Orders
├── ready_flag.prompt                        # Ready Flag pattern (3 use cases)
├── emp_depts.prompt                         # Chain Up: sum salaries, constrain budget
├── graduate.prompt                          # Cardinality: counts with thresholds
├── products.prompt                          # Qualified Any: severity checks
├── honor_society.prompt                     # Complex cardinality with qualified counts
└── *.txt / *_corrected_prompt.txt           # Expected outputs and corrections
```

**Test Examples:** `system/genai/examples/`
```
├── genai_demo/                              # Complete example with iterations
├── airport/                                 # Complex 10+ table system
├── emp_depts/                               # Simple aggregation pattern
└── time_tracking_billing/                   # Real-world scenario
```

### The Prompt Assembly Process

**User Input:**
```
Create a system with customers, orders, items and products.

Use case: Check Credit
1. Customer.balance <= credit_limit
2. Customer.balance = Sum(Order.amount_total where date_shipped is null)
3. Order.amount_total = Sum(Item.amount)
4. Item.amount = quantity * unit_price
5. Item.unit_price = copy from Product.unit_price
```

**System Surrounds With:**

1. **Model Generation Instructions** (`sqlite_inserts_model_test_hints.prompt`):
   - Use autonum keys for ALL tables (including junction tables)
   - Create classes, never tables (Class names singular, capitalized)
   - **CRITICAL:** "If you create sum, count or formula Logic Bank rules, then you MUST create a corresponding column in the data model"
   - No check constraints (logic uses rules instead)
   - Foreign key columns (not relationship names) for test data

2. **Logic Generation Instructions** (`logic_inserts.prompt`):
   - "Use LogicBank to enforce these requirements (do not generate check constraints)"
   - "be sure to update the data model and *all* test data with any attributes used in the logic"

3. **Response Structure** (`response_format.prompt`):
   ```python
   class WGResult(BaseModel):
       models: List[Model]              # SQLAlchemy classes
       rules: List[Rule]                # LogicBank declarations
       test_data: str                   # Python test data creation
       test_data_rows: List[TestDataRow]
       test_data_sqlite: str            # INSERT statements
       graphics: List[Graphic]          # Dashboard queries
       name: str                        # Suggested project name
   ```

**Result:** ChatGPT returns structured JSON with models, rules, and test data that:
- Has `Customer.balance`, `Order.amount_total`, `Order.item_count` columns created automatically
- Contains LogicBank rules for all derivations
- Includes test data with derived attributes pre-initialized

### Key Insight: Model + Logic Co-Generation

**Unlike existing database projects**, GenAI creation can **modify the data model** to support logic:

- **Derived attributes materialize:** `Customer.balance`, `Order.amount_total`, `Product.total_ordered`
- **Count columns appear:** `Order.item_count` for existence checks
- **Qualified counts split:** `Product.notice_count` + `Product.severity_five_count`

This is why the training examples emphasize:
> "If you create sum, count or formula Logic Bank rules, then you MUST create a corresponding column in the data model."

### Training Pattern Categories

The `logic_training/` examples teach ChatGPT these patterns:

1. **Chain Up (Aggregation → Constraint)**
   - `emp_depts`: Department.total_salary = sum(Employee.salary); salary <= budget
   - `genai_demo`: Customer.balance = sum(orders); balance <= credit_limit

2. **Counts as Existence Checks**
   - `genai_demo`: Order.item_count = count(Items); can't ship if == 0
   - Creates both derivation AND validation

3. **Cardinality Patterns (Qualified Any)**
   - `products`: Total notices + severity 5 notices; constraint if orderable
   - `graduate`: Probation count + sick days; constraint for graduation
   - Pattern: Multiple counts (total + qualified) with complex conditions

4. **Ready Flag**
   - `ready_flag`: Multi-use-case with conditional aggregations
   - Customer.balance only sums orders where `ready == True AND date_shipped is None`
   - Product.total_ordered only sums items where `ready == True`
   - **Why `Ready` exists — min-cardinality vs. SAFRS cascade-add timing:** `Ready` was
     originally an engineering workaround, not a pure UX choice. Minimum-cardinality
     constraints ("an Order must have at least one Item") are supported via
     `Rule.commit_row_event` — but reliably enforcing them **at insert time**, through
     SAFRS, has never worked cleanly. When a client posts a parent + children in one
     nested request (Order + Items), the parent's PK is DB-computed (autoincrement).
     Each child needs that PK **cascade-added** — stamped into its own FK column — before
     it counts as "attached." The PK isn't assigned until flush, and SAFRS's nested-insert
     handling + LogicBank's row-logic timing don't reliably line up to guarantee the
     child-count check runs after cascade-add has stamped every child, while still early
     enough to reject the transaction atomically. (`nw_sample`'s own code comment
     confirms half of this: "the after_flush event makes Order.Id available" — even the
     parent's own PK isn't visible to rule code until after flush.)
     **The resolution:** don't enforce cardinality at insert — defer the check to an
     explicit, later state transition (`Ready`, or shipping). See
     `samples/nw_sample/logic/declare_logic.py:187-195` (`do_not_ship_empty_orders`, a
     commit event gated on `Ready == True` or `ShippedDate is not None`, checked against a
     reactive `Rule.count`). What started as a workaround for this SAFRS/cascade-add
     limitation was then recognized as better UX in its own right — orders naturally want
     a draft/staging phase before being finalized for shipping. Full writeup:
     `samples/nw_sample/review.md` ("Origin Story: Min-Cardinality Constraints and Why
     Ready Exists").
   - **`nw_sample` doubles as Val's manual pre-release regression test for LogicBank
     itself** (run before every LB release) — not just a teaching/demo project.
   - **⚠️ CORRECTED (v2.18) — `nw_sample`/`nw_sample_nocust` are freshly generated by
     BLT, not copied-forward pre-built samples.** `manager.py`'s manager-build step
     (`build_manager`) runs `shutil.copytree(prototypes/manager, to_dir)`, which copies
     `prototypes/manager/samples/*` — including `basic_demo_logic_gov`,
     `basic_demo_ai_rules-supplier`, `basic_demo_sample`, `basic_demo_eai`,
     `demo_customs_clvs`, `demo_customs_surtax`, `demo_emp_types`,
     `allocate_dept_account_demo` — as static committed files, verbatim, with no
     regeneration. `nw_sample`/`nw_sample_nocust` are different: BLT then runs
     `command="create"` (`db_url='nw+'` / `'nw'`) against them explicitly, which invokes
     the live generator against current `prototypes/base` gold source. **Net effect:
     `nw_sample`/`nw_sample_nocust` always reflect the latest `prototypes/base` code —
     including refactors like the Jul 2026 declare_logic.py/all_classes_stamping.py
     slimdown — while every other sample under `prototypes/manager/samples/*` is a
     point-in-time snapshot that only updates when someone hand-regenerates it and
     commits the result.** This is the OPPOSITE of what v2.16/v2.17 of this doc implied —
     do not use "nw_sample is hand-curated, so other samples must be too" as a heuristic;
     it's backwards. What IS still true: some patterns in `nw_sample`'s domain code that
     look like tech debt (single large `declare_logic.py` instead of `logic_discovery/`,
     `as_exp=` string param, custom `calling=` Kafka function, wildcard imports) may be
     **deliberately preserved to keep exercising specific LogicBank code paths/timing
     across releases** — not oversights to clean up. Same likely applies to the
     `Ready`/cascade-add pattern above and to
     `test/api_logic_server_behave/features/place_order.feature`'s scenarios (probably
     the actual pass/fail gate, not just documentation). Do not modify `nw_sample`'s
     domain logic, models, or admin.yaml without checking with Val first — see
     `samples/nw_sample/review.md` ("Also: LB Regression Test") for the full caveat.
     **But:** when checking whether a *generator/prototype-level* fix (like the
     declare_logic.py slimdown) has propagated to samples, check `nw_sample` FIRST — it's
     the one place guaranteed to be current — then treat every `prototypes/manager/samples/*`
     project as needing manual regeneration to catch up.

5. **Chain Down (Copy/Formula)**
   - Item.unit_price = copy(Product.unit_price)
   - Item.ready = Order.ready (formula propagation)

### CLI Commands Using This System

**Create from natural language:**
```bash
genai-logic create --project-name=my_system --using="<natural language>"
# Internally: assembles prompts → ChatGPT → parses WGResult → generates project
```

**Translate logic (existing DB):**
```bash
genai-logic logic-translate --project-name=. --using-file=docs/logic
# Uses logic_translate.prompt to convert NL in docs/logic → rules in logic/logic_discovery/
```

### Fine-Tuning Files

**Training Data:** `logic_training/ft.jsonl`
- JSONL format for ChatGPT fine-tuning
- Generated from prompt/response pairs
- ~374KB with all pattern examples

**Script:** `logic_training/create_json_l.py`
- Converts `*.prompt` + `*.txt` → JSONL entries
- Format: system message, user message (prompt), assistant message (response)

### Common Pitfalls (Why Corrections Exist)

Several `*_corrected_prompt.txt` files show typical AI mistakes:

1. **Wrong cardinality:**
   - `airport.prompt`: Asked for "airplane's passengers" but meant "flight's passengers"
   - AI can't count passengers on an Airplane (no direct relationship)
   - Correction: Count passengers on Flight, constrain by Airplane.seating_capacity

2. **Constraint depends on derived flag:**
   - `products.prompt` initially: "product is orderable IF no severity 5 notices"
   - Problem: Makes orderable a derived value, then uses it in constraint
   - Correction: "RAISE ERROR if orderable == True AND has severity 5 notices"
   - Pattern: Flag is input, constraint uses it (not derived from constraint conditions)

3. **Negative condition logic:**
   - Must use: `not(row.flag and bad_condition)`
   - Not: `row.flag → requires good_condition` (harder for AI to translate)

### Why This Architecture?

**Traditional GenAI code generation problems:**
- Generates 200+ lines of procedural code
- Misses corner cases (foreign key changes, cascading updates)
- Creates technical debt (unmaintainable spaghetti)

**Declarative GenAI solution:**
- Generates **specifications** (5 rules), not code (200 lines)
- Rules executed by proven engine (40+ years, 6,000+ deployments)
- Engine handles ALL change paths automatically (no corner cases missed)
- Natural language → DSL → Runtime engine (not NL → procedural code)

**Critical difference:** The AI doesn't need to "think through" all possible change paths. It translates requirements to rules, and the engine provides correctness guarantee through automatic dependency analysis and chaining.

&nbsp;

