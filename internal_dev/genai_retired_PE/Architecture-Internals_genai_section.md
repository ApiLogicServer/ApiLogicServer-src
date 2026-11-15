# Retired GenAI (prompt engineering) section of Architecture-Internals.md

Archived Nov 15 2026 from `org_git/Docs/docs/Architecture-Internals.md`, verbatim, when the fine-tuned ChatGPT pipeline (`genai-logic genai` family) was retired.

---

## GenAI Prompt Engineering: Natural Language → Structured Specifications

### The ChatGPT Project Creation Pipeline

The `genai-logic create` command translates natural language requirements into complete working projects using **fine-tuned ChatGPT** with structured prompt engineering.

**Key Principle:** AI generates **declarative specifications** (models + rules), not procedural code. The runtime engines provide correctness guarantees.

### Prompt Engineering Architecture

**Location:** `system/genai/prompt_inserts/`

**Core Templates:**

1. **`sqlite_inserts.prompt`** - Main orchestrator:
   ```
   Use SQLAlchemy to create a sqlite database for: {{prompt}}
   {% include 'sqlite_inserts_model_test_hints.prompt' %}
   {% include 'graphics.prompt' %}
   {% include 'response_format.prompt' %}
   ```

2. **`sqlite_inserts_model_test_hints.prompt`** - Critical generation rules:
   - "If you create sum, count or formula Logic Bank rules, then you **MUST** create a corresponding column in the data model"
   - Use autonum keys for ALL tables (including junction tables)
   - Create classes, never tables (singular names, capitalized)
   - No check constraints (use rules instead)
   - Foreign key columns (not relationship names) for test data

3. **`logic_inserts.prompt`** - Rule generation:
   ```
   Use LogicBank to enforce these requirements (do not generate check constraints);
   be sure to update the data model and *all* test data with any attributes used in the logic
   ```

4. **`response_format.prompt`** - Structured output schema:
   ```python
   class WGResult(BaseModel):
       models: List[Model]              # SQLAlchemy classes
       rules: List[Rule]                # LogicBank declarations  
       test_data: str                   # Python test data creation
       test_data_sqlite: str            # INSERT statements
       graphics: List[Graphic]          # Dashboard queries
       name: str                        # Suggested project name
   ```

### Model + Logic Co-Generation (Key Insight)

**Unlike existing database projects**, GenAI creation **modifies the data model** to support logic:

**Example Input:**
```
Customer.balance = Sum(Order.amount_total where date_shipped is null)
Order.amount_total = Sum(Item.amount)
Order.item_count = Count(Items); can't ship if item_count == 0
```

**ChatGPT Automatically Creates:**
- `Customer` class with `balance` column (Decimal)
- `Order` class with `amount_total` column (Decimal)  
- `Order` class with `item_count` column (Integer)
- Corresponding LogicBank rules for all derivations
- Test data with derived attributes pre-initialized

**Critical Pattern:** Derived attributes **materialize** as database columns. This enables:
- Efficient queries (indexed, no runtime aggregation)
- Scalable performance (pruning, delta adjustments)
- Simple constraints (balance <= credit_limit works on stored value)

### Training Examples: Teaching ChatGPT Rule Patterns

**Location:** `org_git/ApiLogicServer-src/tests/genai_tests/logic_training/`

**Format:** `*.prompt` (input) + `*.txt` (expected output) → `ft.jsonl` (fine-tuning data)

**Pattern Categories:**

1. **Chain Up (Aggregation + Constraint)**
   - `emp_depts.prompt`: Department.total_salary = sum(Employee.salary); total_salary <= budget
   - `genai_demo.prompt`: Customer.balance = sum(Order.amount_total); balance <= credit_limit
   - **Teaches:** Derive first, constrain second (two-step pattern)

2. **Counts as Existence Checks**
   - `genai_demo.prompt`: Order.item_count = Count(Items); constraint: can't ship if item_count == 0
   - **Teaches:** Use count for validation, not just analytics

3. **Cardinality Patterns (Qualified Any)**
   - `products.prompt`: Total notices + severity 5 notices; error if orderable with bad notices
   - `graduate.prompt`: Probation count + sick days count; graduation eligibility constraint
   - **Teaches:** Multiple counts (total + qualified) for complex conditions

4. **Ready Flag (Conditional Aggregations)**
   - `ready_flag.prompt`: Customer.balance = sum(Order.amount_total where ready == True AND date_shipped is None)
   - **Teaches:** Qualified sums with multiple conditions, cascading flags

5. **Chain Down (Copy/Formula Propagation)**
   - Item.unit_price = copy(Product.unit_price) - price change doesn't affect old orders
   - Item.ready = Order.ready (formula propagation)
   - **Teaches:** Difference between copy (point-in-time) and formula (live reference)

### Common AI Mistakes (Corrections)

Several `*_corrected_prompt.txt` files document typical errors:

**1. Wrong Relationship Path** (`airport_corrected_prompt.txt`):
- ❌ Original: "airplane's passengers must be less than seating capacity"
- Problem: No direct Airplane → Passenger relationship
- ✅ Corrected: "**flight's** passengers must be less than its Airplane's seating capacity"
- Lesson: AI needs explicit relationship path

**2. Constraint Depends on Derived Flag** (`products_corrected_prompt.txt`):
- ❌ Original: "product is orderable IF no severity 5 notices"
- Problem: Makes `orderable` derived, then uses it in constraint (circular)
- ✅ Corrected: "RAISE ERROR if product.orderable == True AND has severity 5 notices"
- Lesson: Flag is **input**, constraint validates it (not derived from constraint conditions)

**3. Negative Condition Logic**:
- ❌ Harder: "if student.can_graduate, then must have < 3 probations"
- ✅ Easier: "error if can_graduate == True AND probation_count > 2"
- Pattern: `not(row.flag and bad_condition)` is clearest for AI

### Fine-Tuning Process

**Training Data:** `logic_training/ft.jsonl` (~374KB)
- JSONL format for ChatGPT fine-tuning API
- Generated from 10+ prompt/response pairs
- Format: `{"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}`

**Generation Script:** `logic_training/create_json_l.py`
- Converts pattern examples → training data
- System prompt + user prompt + expected response
- Updates `ft.jsonl` with new examples

### CLI Commands Using This System

**Create from natural language:**
```bash
genai-logic create --project-name=my_system --using="your requirements here"
# Pipeline: assemble prompts → ChatGPT API → parse WGResult → generate project
```

**Translate logic (existing DB):**
```bash
genai-logic logic-translate --project-name=. --using-file=docs/logic
# Uses logic_translate.prompt: NL in docs/logic → rules in logic/logic_discovery/
```

**Add logic to existing project:**
```bash
genai-logic add-logic --using="The Order's amount_total is sum of Item amounts"
# Appends rules to logic/declare_logic.py or logic/logic_discovery/
```

### Why This Architecture Succeeds

**Traditional GenAI Code Generation:**
- Outputs: 200+ lines of procedural code
- Problems: Misses corner cases, violates SOA, creates technical debt
- Example miss: Foreign key change (Order.customer_id) requires adjusting BOTH old and new customer balances

**Declarative GenAI (This System):**
- Outputs: 5 rules (declarative specifications)
- Execution: Proven rules engine (40+ years, 6,000+ deployments)
- Coverage: Engine handles ALL change paths automatically via dependency analysis
- Result: **Correctness guarantee** + 40X code reduction

**Critical Insight:** AI doesn't need to "think through" all possible change paths. It translates requirements → rules, and the **engine provides completeness**.

**Natural Language → DSL → Runtime Engine** (not NL → procedural code)

### Testing Examples

**Location:** `system/genai/examples/`

Each directory contains:
- `*.prompt` - User requirements (various formality levels)
- `*.response_example` - Expected ChatGPT output
- Subdirectories for iterations (`genai_demo_iteration/`, `genai_demo_iteration_discount/`)

**Key Examples:**
- `genai_demo/` - Complete Check Credit + No Empty Orders (primary teaching example)
- `genai_demo_informal.prompt` - Less structured input (tests robustness)
- `ready_flag/` - Multi-use-case with conditional logic
- `airport/` - Complex 10+ table system
- `time_tracking_billing/` - Real-world business scenario

**Purpose:** Validate prompt engineering works across formality levels and complexity ranges.

&nbsp;


