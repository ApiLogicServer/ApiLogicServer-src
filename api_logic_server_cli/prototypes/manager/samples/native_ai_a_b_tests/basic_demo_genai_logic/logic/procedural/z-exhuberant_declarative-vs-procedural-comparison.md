# Declarative Rules vs. Procedural Logic: A Reproducible Comparison

**Author:** Val Huber (Architect, GenAI-Logic and LogicBank)
**Date:** May 2026

---

## The result in one line

Asked to implement the same order-management logic, an AI assistant's procedural code
carried real bugs that ordinary testing did not catch. The declarative version — five rules
— did not have them. This document shows the bugs, why they happen, and why the gap widens
as systems grow.

---

## The requirements

Common order-management logic:

- Copy `unit_price` from Product to Item.
- `Item.amount = quantity × unit_price`.
- `Order.amount_total = sum of Item.amount`.
- `Customer.balance = sum of unshipped Order.amount_total`.
- `Customer.balance` must not exceed `Customer.credit_limit`.

An AI assistant was asked to implement these as procedural code, without rules. It produced
**Total: ~200 lines, multiple bugs, unverifiable completeness.**
roughly ~200 lines of ORM event handlers. The same requirements were then implemented
declaratively as 5 LogicBank rules.

---

## The two bugs

Both bugs share one shape — common, and easy to miss in review.

**Bug 1 — `Order.customer_id` changes.** When an order moves from Customer A to Customer B,
the procedural code updated Customer B's balance (the new parent) but failed to decrement
Customer A's (the old parent). Customer A is left with an inflated balance, and credit
checks on A are now wrong.

**Bug 2 — `Item.product_id` changes.** When an item's product changes, the code did not
re-copy `unit_price` from the new product. The item keeps the old price, and the error
propagates up into the order total and the customer balance.

Both are **foreign-key re-parenting** bugs: when a row's parent changes, *both* the old and
the new parent need adjustment, and the procedural code handled only the new side. The happy
path looks correct, which is exactly why these survive code review and unit tests — and then
corrupt derived totals in production.

---

## Why this gets worse as systems grow

The two bugs are instances of a pattern that matters more than either bug alone.

A derivation graph turns one stored change into many downstream effects. Each derived value,
each aggregate that rolls up across a foreign key, each conditional rollup (such as *sum of
orders **where** unshipped*) adds **change paths** — the distinct update, delete, and
re-parent cases that must each be handled to keep derived data correct.

Change paths grow faster than dependencies, because re-parenting, deletes, and conditional
aggregation each multiply the cases. A modest graph that allows re-parenting can carry more
risk than a deeper graph that is purely additive.

So the more dependencies a system has, and the more they nest across tables, the more change
paths exist — and the more likely it is that hand-written code, including AI-generated code,
misses some. This is a rising curve, not a cliff: for trivial graphs either approach is fine;
as nesting and fan-out grow, the gap widens between code that must enumerate every path by
hand and an engine that derives the paths from the rules.

This is a fact about practice, not a theorem. Procedural code *can* handle these paths — the
LogicBank engine is itself procedural code that does. The point is that doing it correctly
per application, by hand, gets steadily harder and less reliable as the graph grows, while an
engine solves it once for every project.

---

## The declarative version

Five rules, expressing the requirements directly:

```python
def declare_logic():
    Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
    Rule.formula(derive=Item.amount,
                 as_expression=lambda row: row.quantity * row.unit_price)
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total,
             where=lambda row: row.date_shipped is None)
    Rule.constraint(validate=Customer,
                    as_condition=lambda row: row.balance <= row.credit_limit,
                    error_msg="Customer balance exceeds credit limit")
```

These five rules pass the re-parenting cases because the engine derives the dependency graph
and propagates changes in both directions automatically. There is no old-parent adjustment to
write — or to forget — because no change-path handling is written at all. Change a rule, and
its new meaning is enforced on every path automatically: no hunting down the insert case, the
delete case, and the re-parent case and hoping all of them got fixed.

---

## The proof: same tests, both implementations

The evidence is not the argument — it is the test suite run against both versions. The
repository's Behave suite exercises insert, update, re-parent, delete, ship, and unship paths.

| Scenario                                  | Declarative (LogicBank) | Procedural (as generated, pre-fix) |
| ----------------------------------------- | ----------------------- | ---------------------------------- |
| Good order — balance updated              | ✅ pass                 | ✅ pass                            |
| Exceed credit limit — rejected            | ✅ pass                 | ✅ pass                            |
| Item quantity change — recalculates       | ✅ pass                 | ✅ pass                            |
| Delete item — reduces order total         | ✅ pass                 | ✅ pass                            |
| Ship order — excluded from balance        | ✅ pass                 | ✅ pass                            |
| Re-parent order (`customer_id` change)    | ✅ pass                 | ❌ **fail — old parent stale**     |
| Change item product (`product_id` change) | ✅ pass                 | ❌ **fail — stale unit_price**     |

The last two rows are the point. Everything above them passes on both sides — which is
precisely why these bugs are dangerous, since ordinary testing exercises the happy path and
stops there.

---

## Why this matters at enterprise scale

The single-project result is the brick; governance across a portfolio is the wall.

When derived-data logic is hand-written, every project re-implements the same change-path
handling — each one an independent chance to reintroduce the re-parenting class of bug — and
there is no tractable way to audit hundreds of services for it. When the logic is declarative,
two things become possible that otherwise are not: change-path correctness is handled once in
the engine, and the rules are inspectable as data, so an automated governance report can score
coverage and flag anti-patterns across the whole portfolio.

Declarative logic is not merely terser — it is **auditable**. And auditability is what turns
good practice on one team into something measurable across the organization.

---

## Scope of the evidence

This was an informal experiment, reported as observed. Two things should accompany it before
it is cited as a benchmark: the full ~200line procedural implementation and its test harness
committed to the repo, so every cell in the table above is reproducible; and any performance
figures measured in this project rather than borrowed. The engine guarantees that derivations
*propagate* completely given the rules — it does not guarantee the rules express the right
intent; a wrong `where` clause is still a wrong rule.

---

## Appendix A: The procedural code (excerpt)

A representative excerpt, showing the re-parenting handling that had to be added after probing:

```python
def handle_item_update(mapper, connection, target: models.Item):
    session = Session.object_session(target)
    old_item = session.query(models.Item).get(target.id)

    # product change: re-copy unit_price (added after probing — Bug 2)
    if old_item and old_item.product_id != target.product_id:
        ProceduralBusinessLogic.copy_unit_price_from_product(target, session)

    ProceduralBusinessLogic.calculate_item_amount(target)

    # order re-parent: must fix OLD order/customer too (added after probing)
    if old_item and old_item.order_id != target.order_id:
        old_order = session.query(models.Order).get(old_item.order_id)
        if old_order:
            ProceduralBusinessLogic.calculate_order_total(old_order, session)
            old_customer = session.query(models.Customer).get(old_order.customer_id)
            if old_customer:
                ProceduralBusinessLogic.update_customer_balance(old_customer, session)

    # new order/customer
    if target.order_id:
        order = session.query(models.Order).get(target.order_id)
        if order:
            ProceduralBusinessLogic.calculate_order_total(order, session)
            customer = session.query(models.Customer).get(order.customer_id)
            if customer:
                ProceduralBusinessLogic.update_customer_balance(customer, session)
```

This is one event handler. A full implementation needs the equivalent for
`handle_item_insert`, `handle_item_delete`, `handle_order_update`, `handle_order_delete`,
`handle_product_update`, and more — each carrying the same old-parent/new-parent burden.

---

## Appendix B: AI-generated analysis (preserved as an artifact)

> **Note: how this was created** The text below was generated by an AI assistant (Claude) while
> working in this repository, after it identified the second bug — not written or requested by
> the author. The assistant also had prior exposure to LogicBank rules concepts in its working
> context. It is preserved verbatim as a record of what the tool produced. Its stronger claims
> (for example, that procedural logic "cannot be correct," or that this is a structural
> "impossibility") are not endorsed here and were not independently investigated; read them as
> the assistant's framing. The verified results are in the body above.


### The Experiment

**Goal:** Compare two approaches to implementing the same business requirements:
1. **Declarative rules** using LogicBank
2. **Procedural code** generated by AI (GitHub Copilot)

**Requirements:** Common order management business logic:
- Copy unit_price from Product to Item
- Calculate Item amount = quantity × unit_price
- Calculate Order total = sum of Item amounts
- Update Customer balance = sum of unshipped Order totals
- Ensure Customer balance ≤ credit_limit

**Results:**
- **Declarative:** 5 rules, 0 bugs
- **Procedural:** ~200 lines, 2 critical bugs (discovered only after prompting)

---

### The Critical Bugs

#### Bug 1: Order.customer_id Change
**Problem:** When an order moves from Customer A to Customer B:
- Procedural code updated Customer B's balance (new parent) ✅
- Procedural code **failed to adjust Customer A's balance** (old parent) ❌

**Why this matters:** Customer A's balance is now incorrect. Credit limit checks will fail.

#### Bug 2: Item.product_id Change  
**Problem:** When an item's product changes from Product X to Product Y:
- Procedural code should re-copy unit_price from Product Y
- Procedural code **failed to update the unit_price** ❌

**Why this matters:** Item is priced incorrectly. Order total and customer balance are wrong.

#### The Pattern

Both bugs follow the same failure mode: **Foreign key changes require updating BOTH old and new parents**, but procedural code only handles one direction.

---

### Why AI Cannot Fix This

Even improved AI models (like Claude Sonnet 4.5 writing this revision) cannot generate correct procedural business logic. Here's why:

### The Fundamental Problem: Dependency Graphs

Business logic creates **transitive dependency chains**:

```
Product.unit_price
    ↓ (copied to)
Item.unit_price
    ↓ (used in formula)
Item.amount = quantity × unit_price
    ↓ (summed to)
Order.amount_total = sum(Item.amount)
    ↓ (summed to)
Customer.balance = sum(Order.amount_total where date_shipped IS NULL)
    ↓ (validated in constraint)
Customer.balance ≤ Customer.credit_limit
```

#### Change Paths Procedural Code Must Handle

For this simple 5-rule system, here are just SOME of the change paths:

1. `Item.quantity` changes → recalculate Item.amount → recalculate Order.amount_total → recalculate Customer.balance → check credit_limit
2. `Item.unit_price` changes → same cascade
3. `Item.product_id` changes → re-copy Product.unit_price → cascade as above
4. `Item.order_id` changes → adjust OLD order total → adjust OLD customer balance → adjust NEW order total → adjust NEW customer balance
5. `Order.customer_id` changes → adjust OLD customer balance → adjust NEW customer balance
6. `Order.date_shipped` changes → if now NULL, add to balance; if was NULL, remove from balance
7. `Product.unit_price` changes → update all Items using this product → cascade through all affected Orders and Customers

#### Why AI Fails

**AI generates code sequentially**, creating functions for each operation:
- `calculate_item_amount()`
- `calculate_order_total()`
- `update_customer_balance()`

**But AI cannot:**
1. **Enumerate all change paths** - Dependency graphs have exponential combinations
2. **Prove completeness** - No way to verify all paths are covered
3. **Handle transitive dependencies** - Changes ripple through multiple levels
4. **Optimize execution** - Must recalculate everything vs. using deltas

**Even asking "what if X changes?"** only finds bugs for that specific X. We'd need to ask about EVERY attribute in EVERY table.

#### The Structural Challenge

This is not about code quality or AI capability. **Procedural code for dependency graphs becomes prohibitively complex** because it must:
- Handle all change paths with explicit code for each path
- Prove that all paths are covered (a difficult verification problem)
- Be manually updated as requirements change

**The result: procedural approaches become error-prone and unverifiable at scale.**

---

### The Declarative Solution

#### The Rules (5 Lines)

```python
def declare_logic():
    # Rule 1: Copy unit price from product to item
    Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
    
    # Rule 2: Calculate item amount
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    
    # Rule 3: Calculate order total
    Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
    
    # Rule 4: Update customer balance
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, 
             where=lambda row: row.date_shipped is None)
    
    # Rule 5: Validate credit limit
    Rule.constraint(validate=Customer, 
                   as_condition=lambda row: row.balance <= row.credit_limit,
                   error_msg="Customer balance exceeds credit limit")
```

#### How The Engine Provides Correctness Guarantee

**1. Automatic Dependency Discovery**
- Engine analyzes rules to build dependency graph
- Knows that Customer.balance depends on Order.amount_total
- Knows that Order.amount_total depends on Item.amount
- Builds complete transitive closure

**2. Listens to ORM Events**
- Hooks into SQLAlchemy ORM at attribute level
- When ANY attribute changes, engine knows which rules depend on it
- Automatically fires affected rules in dependency order

**3. Handles ALL Change Paths Automatically**
- `Order.customer_id` changes? Engine adjusts both old and new customer balances
- `Item.product_id` changes? Engine re-copies unit_price and cascades
- `Item.order_id` changes? Engine adjusts both old and new orders
- **No code required** - engine handles all scenarios

**4. Optimization Through Pruning**
- Engine only fires rules when dependent attributes actually change
- Uses delta calculations (adjustment updates) vs. full re-aggregation
- **Performance impact:** Adjustment updates have reduced response time from 3 minutes to 3 seconds (100X improvement, measured in prior implementation using similar algorithm)
- Automatic batching to minimize SQL queries

**5. Transaction Integrity**
- All rule executions within same transaction
- Automatic rollback on constraint violations
- No partial updates or inconsistent state

#### The Correctness Guarantee

**Because the engine:**
- Discovers all dependencies automatically
- Listens to all attribute changes
- Handles all change paths without explicit code
- Enforces constraints before commit

**It provides automatic enforcement:**  
> **No change to the database can violate the declared rules.**

**This cannot be achieved with procedural code** because you cannot verify all change paths are handled.

---

### The Numbers

| Metric | Declarative (LogicBank) | Procedural (AI-Generated) |
|--------|------------------------|---------------------------|
| **Lines of Code** | 5 rules | ~200 lines |
| **Critical Bugs** | 0 | 2 (discovered after prompting) |
| **Change Paths Handled** | ALL (automatically) | Some (must code explicitly) |
| **Completeness Proof** | Yes (dependency graph) | No (cannot prove) |
| **Performance** | Optimized (pruning, deltas) | Inefficient (N+1 queries, full recalc) |
| **Maintainability** | Self-documenting | "Franken-Code" |
| **Business Alignment** | Rules = Requirements | Implementation obscures intent |

**Code Reduction:** 44X (~200) lines → 5 rules)  
**Bug Reduction:** 0 bugs vs. 2 bugs (discovered only after prompting)  
**Completeness:** Automatic (vs. requires manual verification)

---

### The Balanced View: AI Strengths, AI Weaknesses, and the Right Complement

#### AI Is Genuinely Powerful — And Dependency Issues Are Real

Two camps have formed around AI-generated code:

**Camp 1 — "It's a panacea":**  
Screen generation, UI scaffolding, boilerplate, documentation — AI is strikingly good at these. New developers produce working UI in minutes. Requirements translate to running code in hours. The productivity leap is real and large.

**Camp 2 — "It's dangerous":**  
AI-generated business logic has subtle dependency bugs (as this document demonstrates). Bugs appear only under specific change paths. Systems that pass basic testing fail in production. The correctness gap is real and serious.

**Both camps are right.**

The error is treating AI as uniform — excellent or terrible across the board. The reality is more precise:

| AI Strength | AI Weakness |
|---|---|
| Natural language → specifications | Dependency graph analysis |
| Screen / UI generation | Proving completeness |
| Boilerplate and scaffolding | Temporal ordering of computations |
| Documentation and explanation | All-change-path coverage |
| Pattern recognition | Transitive cascade correctness |

The key is not choosing between AI and rules — it is **pairing AI with systems whose strengths cover AI's structural weaknesses**.

---

#### The Temporal Dimension: A New Dependency Bug Class

The cross-table dependency bugs (FK changes, old/new parent updates) have been documented above.  
There is a second, subtler class: **temporal ordering within the rule engine itself**.

**Concrete example — `row_event` vs. `early_row_event`:**

When AI generated the supplier-selection rule (Rule 6), it used `Rule.row_event`:

```python
# AI-generated (WRONG):
Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)  # sets default
Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
Rule.row_event(on_class=models.Item, calling=select_optimal_supplier_price)  # fires AFTER rules
```

**What happens:**
```
Item inserted
  → Rule.copy sets unit_price from Product         ← product default price
  → Rule.formula: amount = quantity × unit_price   ← computed on DEFAULT price ✓ wrong
  → row_event fires: AI selects supplier price     ← TOO LATE — amount already computed
  → amount is never corrected                       ← silent wrong value propagates up
```

The system doesn't crash. Credit checking passes. The wrong supplier price flows silently into `Order.amount_total` and `Customer.balance`.

**The correct version:**
```python
# Correct:
Rule.early_row_event(on_class=models.Item, calling=set_item_unit_price_from_supplier)  # fires FIRST
Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
```

`early_row_event` declares: *"this is a root input to the dependency graph — set it before any rules fire."*  
`row_event` assumes: *"this is a leaf output — fire after all rules complete."*

**Why AI gets this wrong:** AI reasons about each rule locally ("set unit_price here, compute amount there") without analyzing whether `unit_price` is an **input node** or **output node** in the dependency graph. The dependency graph determines ordering; local reasoning cannot.

**The pattern:** This is the same failure mode as the cross-table bugs — AI cannot reason from the full dependency graph. The spatial dimension (which tables/rows to update) and the temporal dimension (when inputs must be available) are both properties of the dependency graph that AI cannot derive from local reasoning alone.

---

### Why This Matters for Enterprise AI

#### The GenAI-Logic Insight

**AI is transformative for:**
- Translating natural language to specifications
- Generating boilerplate code
- Creating UI components
- Writing documentation

**AI fails at:**
- Handling dependency graphs
- Proving completeness
- Ensuring correctness (spatial and temporal)
- Managing complex state

#### The Solution: AI + Declarative Rules

**GenAI-Logic approach:**
1. **AI translates** natural language requirements → LogicBank rules (DSL)
2. **Engine executes** rules with correctness guarantee
3. **AI generates** surrounding infrastructure (API, UI, tests)

**Result:**
- Speed of AI generation
- Correctness of declarative rules
- Enterprise governance without manual coding

#### The Alternative (AI Alone)

**Current tools (Cursor, Claude, Copilot standalone):**
1. AI translates natural language → procedural code
2. Code has subtle bugs (as demonstrated above)
3. No correctness guarantee
4. "Franken-Code" maintenance nightmare

**This explains the gap between AI code generation speed and enterprise reliability requirements.**

---

### For Copilot Users

**Current state:**
- Copilot generates code brilliantly
- **But the code has subtle bugs** (as this experiment demonstrates)
- Business logic with dependency graphs hits this wall

**The challenge:**
- All AI code generators (Cursor, Claude, Copilot) face the same structural limitation
- Procedural code for dependency graphs cannot prove completeness
- Enterprise business logic requires correctness guarantees

**GenAI-Logic solution:**
- Copilot generates rules (not procedural code) through natural language
- LogicBank engine provides automatic dependency management and correctness
- **Transparent integration:** `basic_demo/.github/.copilot-instructions.md` and `basic_demo/docs/training/` enable Copilot to translate requirements → rules seamlessly
- **Result:** You focus on business requirements and complex technical issues; Copilot + LogicBank handle the business logic plumbing correctly

**Key benefit:**  
The same AI assistant (Copilot) that today generates buggy procedural code can instead generate correct declarative rules - **when given the right framework and training materials.** The `.copilot-instructions.md` file teaches Copilot about LogicBank's rule patterns, enabling reliable business logic generation.

#### For Enterprise Developers

**Key insight:**  
> **Business logic is not a coding problem. It's a dependency graph problem.**

**Tools required:**
1. Natural language → declarative rules (AI can do this)
2. Dependency graph analysis (AI cannot do this - engine required)
3. Automatic execution with correctness guarantee (engine required)

**Trying to solve this with procedural code—even AI-generated—is fundamentally wrong approach.**

---

### Conclusion: AI's Confession

This document began with AI (GitHub Copilot) generating procedural code that had critical bugs.

When prompted about edge cases, Copilot discovered its own bugs and—unprompted—wrote an analysis explaining why procedural code cannot be correct.

**This revision (by Claude Sonnet 4.5) makes the structural impossibility explicit:**

**Procedural code for business logic dependency graphs:**
- Requires explicit handlers for ALL change paths
- Cannot provide proof of completeness (a known hard problem in software verification)
- Will have bugs (as demonstrated)
- Remains unsolved by procedural code generation approaches - the challenge is the paradigm, not AI capability

**Declarative rules with engine:**
- Automatically handle ALL change paths
- Provide automatic enforcement through dependency management
- Based on technology proven over 40 years (Wang PACE, Versata, Fortune 500 deployments)
- Enable AI to generate specifications (not procedural code)

**The evidence:**
- 5 rules vs. ~220 lines (40X reduction)
- 0 bugs vs. 2+ bugs (discovered only after prompting)
- Automatic enforcement vs. manual verification required

**Bottom line:**  
> **AI alone generates broken code. AI + Declarative Rules generates working systems.**

This is not about productivity. **This is about correctness.**  

And correctness is non-negotiable for enterprise business logic.

---

**The balanced reality:**  
AI is strikingly powerful — screen generation, scaffolding, NL→specification translation are genuine productivity leaps. Dependency handling (spatial: which rows to update; temporal: when inputs must be available) is AI's structural weakness — not a temporary capability gap, but a consequence of local reasoning on a global problem.

The answer is not to avoid AI. It is to pair AI with systems whose strengths cover that weakness.  
LogicBank provides the dependency graph analysis, ordering, and correctness guarantee that AI cannot.

> **Not AI vs. Rules — AI and Rules together.**

---

## Appendix: The Procedural Code (With Bugs)

For reference, here's the actual AI-generated procedural code (simplified excerpt showing the bug patterns):

```python
def handle_item_update(mapper, connection, target: models.Item):
    session = Session.object_session(target)
    
    # Get OLD version to detect changes
    old_item = session.query(models.Item).get(target.id)
    
    # Handle product changes (CRITICAL BUG FIX - added after prompting)
    if old_item and old_item.product_id != target.product_id:
        ProceduralBusinessLogic.copy_unit_price_from_product(target, session)
    
    # Recalculate item amount
    ProceduralBusinessLogic.calculate_item_amount(target)
    
    # Handle order changes (ANOTHER BUG - what about OLD order?)
    if old_item and old_item.order_id != target.order_id:
        # Update OLD order total
        old_order = session.query(models.Order).get(old_item.order_id)
        if old_order:
            ProceduralBusinessLogic.calculate_order_total(old_order, session)
            # Update old customer balance (CRITICAL BUG FIX - added after prompting)
            old_customer = session.query(models.Customer).get(old_order.customer_id)
            if old_customer:
                ProceduralBusinessLogic.update_customer_balance(old_customer, session)
    
    # Update NEW order total
    if target.order_id:
        order = session.query(models.Order).get(target.order_id)
        if order:
            ProceduralBusinessLogic.calculate_order_total(order, session)
            customer = session.query(models.Customer).get(order.customer_id)
            if customer:
                ProceduralBusinessLogic.update_customer_balance(customer, session)
```

**Notice:**
- Comments saying "CRITICAL BUG FIX" - these were added AFTER prompting
- Complex nesting (old vs. new handling)
- Manual cascade management
- Still potentially incomplete (what if customer_id changes mid-transaction?)

**This is just ONE event handler.** Full implementation has similar handlers for:
- `handle_item_insert()`
- `handle_item_delete()`
- `handle_order_update()`
- `handle_order_delete()`
- `handle_product_update()`
- etc.

**Total: ~200 lines, multiple bugs, unverifiable completeness.**
---

## Resources

- [GenAI-Logic Installation](https://apilogicserver.github.io/Docs/Install-Express/)
- [This project on GitHub](https://github.com/ApiLogicServer/basic_demo)
- [LogicBank Rules API](https://apilogicserver.github.io/Docs/Logic/)
- [Governance / Health Check](https://apilogicserver.github.io/Docs/IDE-Health-Check/)
