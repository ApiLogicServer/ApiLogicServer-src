---
# LogicBank API Reference
# Version: 1.0.22
# Last Updated: July 10, 2026
# Description: The Logic Rosetta Stone: simplified API for creating declarative business logic rules
# Changelog:
#   1.0.22 (Jul 2026) - Added step 7 + a full "initialize derived columns for pre-existing rows"
#     section to the AFTER DATABASE SCHEMA CHANGES workflow. Real case: adding basic_demo's
#     Customer.order_count/past_due_letter_count (Rule.count) via ALTER TABLE left existing
#     Customer rows NULL for both columns (never recomputed retroactively); the very first
#     unrelated PastDueLetter insert crashed with `'>' not supported between NoneType/NoneType`
#     in the Insert-Only Constraints pattern's row.order_count > old_row.order_count comparison.
#     This generalizes beyond that one pattern: ANY Rule.sum/count/formula added to a table with
#     existing rows leaves them stale/NULL until next touched - not just a constraint-comparison
#     risk. Documents 3 fixes (no-op UPDATE to trigger real derivation; one-time backfill SQL;
#     null-safe `or 0` as a stopgap only) and when this applies (SCS iterations on an
#     already-seeded db like basic_demo, not fresh empty-schema projects).
#   1.0.21 (Jul 2026) - Documented Rule.constraint's `calling=` parameter (was already accepted by
#     the method signature but silently dropped in the return Constraint(...) call - now wired
#     through). Added new "Insert-Only Constraints (Grandfather Clauses)" section: a Codespaces
#     session's AI assistant correctly diagnosed that a child-side Rule.constraint referencing a
#     parent count re-validates ALL pre-existing sibling rows when the count changes (documented,
#     correct cascade behavior) - but never discovered Rule.constraint(calling=...) or
#     logic_row.is_inserted(), so it fell back to a manual Rule.row_event + raised
#     ConstraintException instead, losing native constraint semantics (HTTP 400 became 500).
#     Documents the better pattern: put the constraint on the PARENT, gated on
#     `row.count_attr > old_row.count_attr` (a child was just added this transaction) - avoids
#     touching the child class or needing is_inserted() at all, and generalizes past 0->1 to any
#     n->n+1 increase. See struggles.md (build_and_test/genai-logic) for the original transcript.
#     Also added "ADJUSTMENT ASSUMES THE STARTING VALUE IS ALREADY CORRECT" caveat: Rule.sum/count
#     are delta adjustments (current_count + 1), not recomputations - if the stored aggregate is
#     already wrong (bad migration, manual SQL edit, bulk import bypassing the rule engine), an
#     adjustment carries the error forward rather than fixing it, and there is no built-in
#     repair/resync mechanism. Directly relevant to the new section above, whose
#     row.count > old_row.count comparison presumes the count was correct going in.
#   1.0.20 (Jul 2026) - Corrected/completed DEPENDENCY TRACKING section per LogicBank's own
#     dependency-scanning.md analysis (org_git/LogicBank/system/LogicBank-Internal-Dev/):
#     calling= functions ARE scanned by parse_dependencies() exactly like as_expression lambdas
#     (inspect.getsource() + token scan) - this was already correctly documented (items 1-3), not
#     a gap. Added item 4: old_row.<attr> references are NEVER tracked as dependencies (only
#     row.<attr> is), regardless of expression form - a real, previously undocumented gap. Also
#     tightened health_check.md's "Broken dependency tracking" demerit wording to attribute the
#     failure to the textual/shallow scan (helper delegation), not to calling= itself.
#   1.0.19 (Jun 2026) - Added guidance: after an early_row_event sets an FK column, do not read
#     the FK's relationship attribute later in the same transaction (e.g. row.customs_office) -
#     query the lookup table directly via session.query(...).get(fk_value) instead. The
#     relationship is not guaranteed fresh within the same flush that just set the FK, so a
#     downstream calling= function can silently see None/stale data and skip a reasons-list
#     check even though the FK column itself is correct. Found via demo_customs_clvs rebuild:
#     a non-CLVS-designated office (clvs_release=0) was incorrectly derived as eligible because
#     row.customs_office evaluated None right after _set_customs_office's early_row_event set
#     customs_office_id.
#   1.0.18 (Jun 2026) - Closed gap in PARENT FLAGS vs CHILD COUNTS section: when a child's own
#     flag column (e.g. is_controlled) is derived from a lookup, it must be set via
#     Rule.early_row_event, not Rule.row_event/commit_row_event - otherwise Rule.count's where=
#     evaluates against the column's stale default. Found via demo_customs_clvs correction
#     (Wynford); the example already existed but never specified which event type to use.
#   1.0.17 (Jun 2026) - Documented child_role_name on Rule.sum/count/copy (LogicBank 1.31.04) -
#     required to disambiguate 2+ relationships between the same parent/child classes. See
#     "CRITICAL — child_role_name REQUIRED..." section and LogicBank's
#     system/LogicBank-Internal-Dev/multi-relationship-bug.md for the underlying fix.
---

=============================================================================
💎 CORE PRINCIPLE: Path-Independent Rules = Automatic Reuse
=============================================================================

**What you're really doing:** Distilling path-independent rules from path-dependent logic.

**Path-dependent (procedural):** Separate code for each execution path
- Add item → recalc amounts
- Change quantity → recalc amounts  
- Change customer → adjust both balances
- Ship order → adjust balance
- Delete item → recalc amounts

**Path-independent (declarative):** ONE rule works for ALL paths
```python
Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None)
```

**Automatic reuse over use cases:** Whereas reuse is typically a high-order design skill, declarative rules provide *automatic reuse* - write the relationship once, it works for insert/update/delete/parent changes. No use case explosion.

=============================================================================

Here is the simplified API for LogicBank:

PREREQUISITE: For general patterns (event handler signatures, logging, request pattern, anti-patterns),
see docs/training/logic_bank_patterns.md

=============================================================================
🗂️ CRITICAL: Directory Structure = Requirements Traceability
=============================================================================

**Pattern Recognition:**
- Context phrases ("When X", "For Y", "On Z") → directory: logic/logic_discovery/x/
- After context, each colon-terminated phrase → file: phrase.py
- Prefixes like "Use case:", "Requirement:" are optional (just noise words)
- No context phrase → single file (flat structure OK)

**Naming:** Convert to snake_case, remove articles
- "When Placing Orders" / "On Placing Orders" → place_order/
- "Check Credit:" → check_credit.py
- "Use case: App Integration:" → app_integration.py

**Requirements Traceability:** File structure provides direct link from use case to implementation
```
Prompt: "On Placing Orders, Check Credit: ..."
Result: logic/logic_discovery/place_order/check_credit.py
Trace:  Use Case Name → File Path → Rules → Logic Report
```

**Examples:**
```
Prompt: "When Placing Orders, Check Credit: ... App Integration: ..."
Result: logic/logic_discovery/place_order/{__init__.py, check_credit.py, app_integration.py}

Prompt: "For Customer Management, Validate Credit: ... Calculate Loyalty: ..."
Result: logic/logic_discovery/customer_management/{__init__.py, validate_credit.py, calculate_loyalty.py}

Prompt: "Check Credit: ..." (no context)
Result: logic/logic_discovery/check_credit.py (flat)
```

=============================================================================

Translate the user prompt into a series of calls to Rule methods, described here.

Do not generate import statements.

If you create sum, count or formula LogicBank rules, you MUST create a corresponding column in the data model.

Use only the methods provided below.

IMPORTANT: Keep it simple! Use the built-in Rule methods with their parameters (like if_condition) rather than creating custom functions. The Rule methods are designed to handle common patterns directly.

CRITICAL - DEPENDENCY TRACKING: LogicBank scans the expression body for `row.<attr>` references to build its dependency graph and determine when rules must re-fire. This applies to ALL expression forms — lambdas (`as_expression=`, `as_condition=`, `where=`) AND named calling functions (`calling=`). LB scans the actual function/lambda body directly. This means:
  1. ALL row attribute references must appear directly in the lambda or calling function body —
     not hidden inside helper functions called from there.
     ❌ WRONG:  as_expression=lambda row: _my_helper(row)          # LB sees zero dependencies
     ❌ WRONG:  calling=my_func  where my_func calls _helper(row)  # LB sees only my_func's body
     ✅ CORRECT: as_expression=lambda row: row.qty * row.unit_price  # LB sees qty, unit_price
     ✅ CORRECT: calling function that directly references row.attr1, row.attr2, etc.
  2. For complex logic with intermediate working values, create them as ACTUAL MODEL ATTRIBUTES
     with their own Rule.formula declarations. This makes the value inspectable AND gives LB
     a proper dependency chain between attributes.
     Example: instead of a helper that tests proof acceptability, add a `steel_proof_acceptable`
     Column to the model and derive it with Rule.formula — then reference `row.steel_proof_acceptable`
     in the downstream rule.
  3. Parent attribute references (row.parent.attr) ARE supported in lambdas and calling functions —
     LB tracks cross-table dependencies correctly when the reference appears in the scanned body.
  4. `old_row.<attr>` references are NEVER tracked as dependencies, even when they appear directly
     in the scanned body (unlike `row.<attr>`, which is tracked whether it's in a lambda or a
     calling= function). If a rule's *only* reference to an attribute is via `old_row.X` — no
     `row.X` anywhere in the same function — the dependency graph does not know this rule depends
     on `X`, which can affect pruning/ordering decisions.
     ❌ RISK: `def f(row, old_row, logic_row): return row.qty - old_row.qty`  — only `qty` (via `row.qty`)
        is tracked; if a hypothetical rule referenced `old_row.other_attr` with no `row.other_attr`
        anywhere in the body, that dependency would be invisible.
     ✅ SAFE: ensure every attribute the rule's correctness depends on also appears at least once
        as `row.<attr>` in the same function body — even a no-op reference is enough to register
        the dependency.

CRITICAL - HOW TO WIRE A FUNCTION INTO A RULE:

  When your logic needs more than one line, write a function and wire it with `calling=`:

  ```python
  def my_func(row, old_row, logic_row):
      return row.qty * row.unit_price   # reference row.attr DIRECTLY here
  Rule.formula(derive=models.Item.amount, calling=my_func)
  ```

  Use `as_expression=` ONLY for a literal inline lambda with no function call:
  ```python
  Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.qty * row.unit_price)
  ```

  These two forms are equivalent. Every other form is wrong:
  ```python
  # BROKEN — looks right, silently never re-fires:
  Rule.formula(derive=models.Item.amount, as_expression=lambda row: my_func(row))
  ```
  LB scans the lambda body `my_func(row)` and finds zero `row.attr` references,
  so it never knows to re-fire the rule when qty or unit_price change.

  ✅ CORRECT — multi-condition eligibility with a reasons list, using calling= for BOTH formulas:
  ```python
  def _eligible_reason(row, old_row, logic_row):
      reasons = []
      if row.customer_approved != 'Y':
          reasons.append("not approved")
      if row.amount_total > row.credit_limit:
          reasons.append(f"amount {row.amount_total} exceeds credit {row.credit_limit}")
      if row.restricted_item_count > 0:
          reasons.append("contains restricted items")
      return ", ".join(reasons)

  def _eligible_flag(row, old_row, logic_row):
      return 'N' if row.eligible_reason else 'Y'

  Rule.formula(derive=models.Order.eligible_reason, calling=_eligible_reason)
  Rule.formula(derive=models.Order.eligible, calling=_eligible_flag)
  ```

  Note: _eligible_flag references row.eligible_reason directly — LB sees that dependency.
  Note: both functions reference row.attr DIRECTLY — no nested helper functions.

CRITICAL — DOCSTRING ON EVERY calling= FUNCTION:
  Every function wired via calling= MUST have a one-line docstring summarising what it derives.
  The first line is used in logic flow diagrams and vital-signs reports — make it count.

  Format: """Derive <column>: <brief plain-English description of the value and key conditions>."""

  ✅ CORRECT:
  ```python
  def _clvs_eligible(row, old_row, logic_row):
      """Derive clvs_eligible: 1 if shipment meets all CLVS criteria, else 0."""
      ...

  def _clvs_reason(row, old_row, logic_row):
      """Derive clvs_reason: comma-delimited list of CLVS ineligibility reasons (blank if eligible)."""
      ...
  ```

  ❌ WRONG — no docstring:
  ```python
  def _clvs_eligible(row, old_row, logic_row):
      if row.service_type_cd != CLVS_SERVICE_TYPE:
          return 0
  ```

  WHY: Without a docstring the logic flow diagram shows only the function name.
  With one it shows: `clvs_eligible = _clvs_eligible(row) — "1 if shipment meets all CLVS criteria"`
  Developers reading the diagram immediately understand intent without opening the file.

CRITICAL — ONE VALUE PER FORMULA:
  A Rule.formula calling function must return exactly one value — the column named in derive=.
  Setting other row attributes as side-effects inside the function is WRONG:

  ❌ WRONG — side-effect assignment to a second column inside one formula:
  ```python
  def _compute_clvs(row, old_row, logic_row):
      reasons = []
      if float(row.local_customs_value_amt) > 3300:
          reasons.append("value exceeds threshold")
      row.clvs_reason = ", ".join(reasons)   # ← WRONG: side-effect, not tracked by LB
      row.clvs_eligible = 1 if not reasons else 0
      return row.clvs_eligible               # ← only clvs_eligible re-fires; clvs_reason is silently stale

  Rule.formula(derive=models.Shipment.clvs_eligible, calling=_compute_clvs)
  # clvs_reason is never re-derived when inputs change — LogicBank does not know about it
  ```

  ✅ CORRECT — one Rule.formula per derived column:
  ```python
  def _clvs_eligible(row, old_row, logic_row):
      return 1 if not _reasons(row) else 0

  def _clvs_reason(row, old_row, logic_row):
      return ", ".join(_reasons(row))

  def _reasons(row):                          # shared helper — called directly from each function body
      reasons = []
      if float(row.local_customs_value_amt or 0) > 3300:
          reasons.append("value exceeds threshold")
      if row.prohibited_commodity_count > 0:
          reasons.append(f"{row.prohibited_commodity_count} prohibited line(s)")
      return reasons

  Rule.formula(derive=models.Shipment.clvs_eligible, calling=_clvs_eligible)
  Rule.formula(derive=models.Shipment.clvs_reason,   calling=_clvs_reason)
  ```
  Both functions reference row.attr DIRECTLY — LB sees the dependencies on both rules.
  Note: _clvs_eligible calls _reasons(row) — LB scans _clvs_eligible's body and sees
  row.local_customs_value_amt and row.prohibited_commodity_count via the helper. However,
  for maximum LB visibility, each function should reference row.attr directly (not via helper).
  The safe pattern: reference the SAME intermediate columns from each function body directly.

  ❌ WRONG — shared helper called from as_expression: LB sees zero dependencies on BOTH rules:
  ```python
  def _reasons(row): ...          # helper — LB does NOT scan this
  def _eligible(row): return 'N' if _reasons(row) else 'Y'   # LB does NOT scan this
  def _reason_str(row): return ", ".join(_reasons(row))       # LB does NOT scan this

  Rule.formula(derive=models.Order.eligible,
               as_expression=lambda row: _eligible(row))      # LB sees no row.attr refs
  Rule.formula(derive=models.Order.eligible_reason,
               as_expression=lambda row: _reason_str(row))    # LB sees no row.attr refs
  ```

CRITICAL - DOCSTRINGS: COPY THE REQUIREMENT, NOTHING ELSE:
  The docstring for a logic file must contain ONLY the requirement text, copied verbatim.
  Do NOT add anything beyond the requirement — no field mappings, no implementation notes,
  no "Uses early_row_event", no "on every insert", no numbered eligibility conditions,
  no restatement or paraphrase of the requirement in your own words.

  Why: anything you add becomes a spec you then code to. Wrong additions cause wrong rules:
  - "Uses early_row_event" → you write an event instead of Rule.formula
  - "dang_goods_cd blank/null" → you check a parent flag instead of Rule.count on child table
  - "on every insert" → you write an event instead of a reactive formula

  ✅ CORRECT docstring — requirement text only:
  ```python
  """
  Scenario: Shipment at or below the LVS threshold is eligible
    Given a shipment imported by an authorized CLVS courier
    ...
  """
  ```

  ❌ WRONG docstring — adds implementation notes that drive incorrect code:
  ```python
  """
  Sets clvs_eligible on every insert.
  Eligibility conditions:
    1. service_type_cd in CLVS_SERVICE_TYPES   ← invented field mapping
    2. dang_goods_cd blank/null                 ← wrong: should be Rule.count on child table
  Uses early_row_event so values are set before formula/constraint rules.  ← wrong rule type
  """
  ```

  ❌ ALSO WRONG — looks neutral but smuggles field mappings into the docstring:
  ```python
  """
  Rules derived from CLVS program requirements (Canada Customs):
    - Duty value must not exceed CAD $3,300
    - No prohibited commodity lines
    - Shipment must be destined for Canada (dest_loc_cntry_cd = 'CA')   ← now you'll hardcode this
    - Carrier must be designated CLVS courier (service_type_cd = '04')  ← and this
  """
  ```
  Any restatement or paraphrase — even a neutral-looking summary — violates this rule.
  The requirement text already contains everything needed. Copy it verbatim; add nothing.

CRITICAL: Keep simple rules on ONE LINE (no exceptions). Goal: Visual scannability - see rule count at a glance.

✅ CORRECT - One rule per line:
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit, error_msg="balance exceeds credit")
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)

❌ WRONG - Don't split simple rules:
    Rule.sum(
        derive=Customer.balance,
        as_sum_of=Order.amount_total
    )


class Rule:
    """ Invoke these functions to declare rules """

    @staticmethod
    def sum(derive: Column, as_sum_of: any, where: any = None, child_role_name: str = "", insert_parent: bool=False):
        """
        Derive parent column as sum of designated child column, optional where

        Example
            Prompt
                Customer.Balance = Sum(Order.amount_total where date_shipped is null)
            Response
                Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal,
                    where=lambda row: row.ShippedDate is None)

        Args:
            derive: name of parent <class.attribute> being derived
            as_sum_of: name of child <class.attribute> being summed
            where: optional where clause, designates which child rows are summed.  All referenced columns must be part of the data model - create columns in the data model as required.  Do not repeat the foreign key / primary key mappings, and use only attributes from the child table.
            child_role_name: REQUIRED if the parent and child classes are related by 2+ relationships (e.g. Employee.works_for_dept and Employee.on_loan_dept, both pointing at Department) - names the SQLAlchemy relationship attribute on the CHILD class (e.g. "works_for_dept") that this sum should follow. Omit only when there is exactly one relationship between the two classes - LogicBank raises "Ambiguous Relationship" if omitted and 2+ exist.
            insert_parent: create parent if it does not exist.  Do not use unless directly requested.
        """
        return Sum(derive, as_sum_of, where, child_role_name, insert_parent)


    @staticmethod
    def count(derive: Column, as_count_of: object, where: any = None, child_role_name: str = "", insert_parent: bool=False):
        """
        Derive parent column as count of designated child rows

        Example
            Prompt
                Customer.UnPaidOrders = count(Orders where ShippedDate is None)
            Response
                Rule.count(derive=Customer.UnPaidOrders, as_count_of=Order,
                    where=Lambda row: row.ShippedDate is None)

        Args:
            derive: name of parent <class.attribute> being derived
            as_count_of: name of child <class> being counted
            where: optional where clause, designates which child rows are counted.  All referenced columns must be part of the data model - create columns in the data model as required.  Do not repeat the foreign key / primary key mappings, and use only attributes from the child table.
            child_role_name: REQUIRED if the parent and child classes are related by 2+ relationships - see Rule.sum's child_role_name for the full explanation; same disambiguation rule applies here.
            insert_parent: create parent if it does not exist.  Do not use unless directly requested.
        """
        return Count(derive, as_count_of, where, child_role_name, insert_parent)


    @staticmethod
    def constraint(validate: object,
                   calling: Callable = None,
                   as_condition: any = None,
                   error_msg: str = "(error_msg not provided)",
                   error_attributes=None):
        """
        Constraints declare condition that must be true for all commits

        Example
            Prompt
                Customer.balance <= credit_limit
            Response  
                Rule.constraint(validate=Customer,
                                as_condition=lambda row: row.Balance <= row.CreditLimit,
                                error_msg="balance ({row.Balance}) exceeds credit ({row.CreditLimit})")

        Args:
            validate: name of mapped <class>
            as_condition: lambda, passed row (simple constraints).  All referenced columns must be part of the data model - create columns in the data model as required.  Also, conditions may not contain sum or count python functions - these must be used to declare additional columns and sum/count rules.
            calling: function, passed (row, old_row, logic_row) - use INSTEAD OF as_condition when the
                condition needs old_row (e.g. to compare a before/after value) or logic_row (e.g.
                logic_row.is_inserted() / is_updated() / is_deleted(), to scope the check to how THIS
                row was changed). as_condition's lambda receives only `row` - it cannot see old_row or
                logic_row at all. See "Insert-Only Constraints (Grandfather Clauses)" below for the
                canonical use case.
            error_msg: string, with {row.attribute} replacements
            error_attributes: list of attributes

        """
        if error_attributes is None:
            error_attributes = []
        return Constraint(validate=validate, calling=calling, as_condition=as_condition,
                          error_attributes=error_attributes, error_msg=error_msg)


    @staticmethod
    def formula(derive: Column,
                as_expression: Callable = None,
                no_prune: bool = False):
        """
        Formulas declare column value, based on current and parent rows

        Example
            Prompt
                Item.amount = quantity * unit_price
            Response
                Rule.formula(derive=OrderDetail.Amount,
                             as_expression=lambda row: row.UnitPrice * row.Quantity)

        Args:
            derive: <class.attribute> being derived
            as_expression: lambda, passed row (for syntax checking).  All referenced columns must be part of the data model - create columns in the data model as required.  Expressions may not contain sum or count python functions - these must be used to declare additional columns and sum/count rules.
            no_prune: disable pruning (rarely used, default False)
        """
        return Formula(derive=derive,
                       as_expression=as_expression,
                       no_prune=no_prune)


    @staticmethod
    def copy(derive: Column, from_parent: any, child_role_name: str = ""):
        """
        Copy declares child column copied from parent column.

        Example:
            Prompt
                Store the Item.unit_price as a copy from Product.unit_price
            Response
                Rule.copy(derive=OrderDetail.UnitPrice, from_parent=Product.UnitPrice)

        Args:
            derive: <class.attribute> being copied into
            from_parent: <parent-class.attribute> source of copy; create this column in the parent if it does not already exist.
            child_role_name: REQUIRED if the parent and child classes are related by 2+ relationships - names the SQLAlchemy relationship attribute on the CHILD class to follow. See Rule.sum's child_role_name for the full explanation.
        """
        return Copy(derive=derive, from_parent=from_parent, child_role_name=child_role_name)


    @staticmethod
    def after_flush_row_event(on_class: object, calling: Callable = None,
                              if_condition: any = None,
                              when_condition: any = None,
                              with_args: dict = None):
        """
        Events are triggered after database flush for integration (Kafka, etc.)
        
        IMPORTANT: Use this simple pattern - do NOT create custom functions unless absolutely necessary.
        Use if_condition parameter for conditional logic instead of writing custom event handlers.

        Example:
            Prompt:
                Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None
            Response:
                Rule.after_flush_row_event(on_class=Order, calling=kafka_producer.send_row_to_kafka,
                               if_condition=lambda row: row.date_shipped is not None,
                               with_args={"topic": "order_shipping"})
            Prompt:
                Send the Product to Kafka topic 'ready_to_ship' if the is_complete is True
            Response:
                Rule.after_flush_row_event(on_class=Product, calling=kafka_producer.send_row_to_kafka,
                               if_condition=lambda row: row.is_complete is True,
                               with_args={"topic": "ready_to_ship"})

        Args:
            on_class: The model class to watch for changes
            calling: Use kafka_producer.send_row_to_kafka for Kafka integration
            if_condition: Lambda function to specify when the event should trigger
            with_args: Dictionary with parameters like {"topic": "topic_name"}
        """


Expanded example:

    Prompt:
        1. Customer.balance <= credit_limit
        2. Customer.balance = Sum(Order.amount_total where date_shipped is null)
        3. Order.amount_total = Sum(Item.amount)
        4. Item.amount = quantity * unit_price
        5. Store the Item.unit_price as a copy from Product.unit_price

    Response:
        Rule.sum(derive=CustomerAccount.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
        Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
        Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
        Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
        Rule.constraint(validate=CustomerAccount,
                        as_condition=lambda row: row.balance <= row.credit_limit,
                        error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")


Equivalent expanded example using informal syntax:

    Prompt:
        1. The Customer's balance is less than the credit limit
        2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
        3. The Order's amount_total is the sum of the Item amount
        4. The Item amount is the quantity * unit_price
        5. The Item unit_price is copied from the Product unit_price

    Response is the same:
        Rule.sum(derive=CustomerAccount.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
        Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
        Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
        Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
        Rule.constraint(validate=CustomerAccount,
                        as_condition=lambda row: row.balance <= row.credit_limit,
                        error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")


PREFER Rule.sum/count OVER CODE — always reactive to child data changes

Whenever a requirement involves an aggregate over child rows (sum, count, any, none,
more than, at least), declare a Rule.sum or Rule.count column. Code that computes the
same value (session.query, len(list comprehension), sum(list comprehension)) produces
the right answer at insert time but silently goes stale when child rows are later
inserted, updated, or deleted. The rule re-fires automatically on every write path;
the code does not.

This applies everywhere the aggregate value is used:
  - as a constraint condition
  - as a formula input
  - as a condition inside a row_event reasons-list
  - as a flag derived from the aggregate

Intermediate sum/count values require a new column, with a LogicBank sum/count rule.  For example:

Prompt:
    The sum of the child value cannot exceed the parent limit

Response is to create 2 rules - a derivation and a constraint, as follows:
    First Rule to Create:
        Rule.sum(derive=Parent.value_total, as_sum_of=Child.value)
    And, be sure to create the second Rule:
        Rule.constraint(validate=Parent,
                    as_condition=lambda row: row.value_total <= row.limit,
                    error_msg="Parent value total ({row.value_total}) exceeds limit ({row.limit})")

Intermediate sum/count values also work for counts.  For example:

Prompt:
    A airplane cannot have more passengers than its seating capacity.

Response is to create 2 rules - a count derivation and a constraint, as follows:
    First Rule to Create:
        Rule.count(derive=Airplane.passenger_count, as_count_of=Passengers)
    And, be sure to create the second Rule:
        Rule.constraint(validate=Airplane,
                    as_condition=lambda row: row.passenger_count <= row.seating_capacity,
                    error_msg="Airplane value total ({row.passenger_count}) exceeds limit ({row.seating_capacity})")


Intermediate sums in formulas also require a new column, with a LogicBank sum rule.  For example:

Prompt:
    An Employees' skill summary is the sum of their Employee Skill ratings, plus 2 * years of service.

Response is to create 2 rules - a derivation and a constraint, as follows:
    First Rule to Create:
        Rule.sum(derive=Employee.skill_rating_total, as_sum_of=EmployeeSkill.rating)
    And, be sure to create the second Rule:
        Rule.Formula(derive=Employee.skill_summary, 
                    as_expression=lambda row: row.skill_rating_total + 2 * row.years_of_service)


Prompt:
    A student cannot be an honor student unless they have more than 2 service activities.

Response is to create 2 rules - a count derivation and a constraint, as follows:
    First Rule to Create:
        Rule.count(derive=Student.service_activity_count, as_count_of=Activities, where=lambda row: 'service' in row.name)
    And, be sure to create the second Rule:
        Rule.constraint(validate=Student,
                    as_condition=lambda row: row.is_honor_student and row.service_activity_count < 2,
                    error_msg="Honor Students must have at least 2 service activities")


For "more than" constraints, create columns with count rules:

Prompt: Reject Employees with more than 3 Felonies.

Response:
    First Rule is to create:
        Rule.count(derive=Employee.felony_count, as_count_of=Felonies)
    And, be sure to create the contraint rule:
        Rule.constraint(validate=Employee,
                    as_condition=lambda row: row.felony_count<=3,
                    error_msg="Employee has excessive Felonies")


For "any" constraints, create columns with count rules:

Prompt: Reject Employees with any class 5 Felonies or more than 3 Felonies.

Response:
    First Rule is to create:
        Rule.count(derive=Employee.class_5_felony_count, as_count_of=Felonies, where=class>5)
        Rule.count(derive=Employee.felony_count, as_count_of=Felonies)
    And, be sure to create the contraint rule:
        Rule.constraint(validate=Employee,
                    as_condition=lambda row: row.class_5_felony_count == 0 and row.felony_count<=3,
                    error_msg="Employee has excessive Felonies")


For "none/no X" and "has any X" boolean flags, use count + formula — NOT session.query():

These phrasings are all the same problem: "does at least one child row satisfy a condition?"
  - "shipment has no controlled items"
  - "order has any unshipped items"
  - "patient has no outstanding alerts"
  - "account is clean (no failed payments)"

❌ WRONG — session.query() inside a formula is invisible to LogicBank's dependency graph.
   If a child row changes, the parent flag will NOT re-derive automatically:
        def check_no_controlled(row, old_row, logic_row):
            count = logic_row.session.query(LineItem).filter_by(shipment_id=row.id, is_controlled=True).count()
            return count == 0
        Rule.formula(derive=Shipment.has_no_controlled_goods, calling=check_no_controlled)

✅ CORRECT — count rule makes the dependency explicit; LogicBank re-fires automatically on any child change:
        Rule.count(derive=Shipment.controlled_item_count, as_count_of=LineItem,
                   where=lambda row: row.is_controlled == True)
        Rule.formula(derive=Shipment.has_no_controlled_goods,
                     as_expression=lambda row: row.controlled_item_count == 0)

The formula is then fully reactive: insert/update/delete of any LineItem re-derives
controlled_item_count, which re-derives has_no_controlled_goods, which re-derives any
downstream eligibility flags — all automatically, on every write path.

CRITICAL - PARENT FLAGS vs CHILD COUNTS: When a condition is about child rows, ALWAYS use
Rule.count — never check a parent-level summary flag that "represents" the child condition.

DETECTION HEURISTIC — apply this BEFORE writing any rule:
  KEY INSIGHT: plural nouns in requirements ("goods", "items", "commodities", "lines") mean
  CHILD ROWS. "Has no prohibited goods" = count child rows, not read a parent flag.

  MANDATORY STEPS:
  1. Identify the plural noun in the requirement
  2. Find the corresponding child table in the model (ShipmentCommodity, LineItem, etc.)
  3. Use Rule.count on that child table — the child attribute name need not match the
     requirement word exactly; pick the most relevant flag/code column on the child table
  4. Reference the derived count in your formula — never reference the parent flag directly

  PARENT FLAGS ARE WRONG even when they exist and the name seems to match:
  A flag like dang_goods_cd on the parent is an ETL/EDI snapshot — LogicBank does NOT
  re-fire when child rows change. It goes silently stale. Use the child count instead.

  Only if NO child table exists at all → a parent-level flag or formula is appropriate.

❌ WRONG — checking parent-level flags that summarize child rows:
    # "dang_goods_cd" is a shipment-level ETL flag — if ShipmentCommodity.is_controlled changes,
    # this formula does NOT re-fire. Controlled-goods status is silently stale.
    Rule.formula(derive=Shipment.clvs_eligible,
                 calling=lambda row, old_row, logic_row:
                     'N' if row.dang_goods_cd or row.oga_shipment_flg == 'Y' else 'Y')

✅ CORRECT — Rule.count makes child-row dependency explicit and reactive:
    Rule.count(derive=Shipment.controlled_item_count, as_count_of=ShipmentCommodity,
               where=lambda row: row.is_controlled == 1)
    # Now clvs_eligible re-fires whenever any ShipmentCommodity.is_controlled changes:
    Rule.formula(derive=Shipment.clvs_eligible,
                 calling=_clvs_eligible)   # references row.controlled_item_count directly

The child table IS the authoritative source. The parent flag is a stale snapshot.
Even if the parent flag exists and is named suggestively — use the child count.

CRITICAL — if the child's flag column (e.g. `is_controlled`) is ITSELF derived from a lookup
(not present on the raw insert), set it via `Rule.early_row_event` on the CHILD class —
never `Rule.row_event` or `Rule.commit_row_event`. `Rule.count`'s `where=` evaluates during
Phase 3a (Row Logic), which runs immediately after early events but BEFORE row/commit events.
If the flag is set too late, the count silently sums/counts using the flag's default (usually
0/None) instead of the looked-up value — no error, just a wrong, stale aggregate on every insert.

  ❌ WRONG — row_event fires after Row Logic; Rule.count already evaluated `is_controlled`
  using its column default:
      def _match_controlled_goods(row, old_row, logic_row):
          match = logic_row.session.query(ControlledRegulatedGood).filter_by(hs_code=...).first()
          row.is_controlled = 1 if match else 0
      Rule.row_event(on_class=models.ShipmentCommodity, calling=_match_controlled_goods)
      Rule.count(derive=models.Shipment.controlled_item_count, as_count_of=models.ShipmentCommodity,
                 where=lambda row: row.is_controlled == 1)   # always counts 0 — is_controlled not set yet

  ✅ CORRECT — early_row_event sets the flag before Row Logic (and the count) runs:
      def _match_controlled_goods(row, old_row, logic_row):
          """Lookup ControlledRegulatedGood by HS-code prefix; set is_controlled before Rule.count aggregates."""
          match = logic_row.session.query(models.ControlledRegulatedGood).filter_by(hs_code=...).first()
          row.is_controlled = 1 if match else 0
      Rule.early_row_event(on_class=models.ShipmentCommodity, calling=_match_controlled_goods)
      Rule.count(derive=models.Shipment.controlled_item_count, as_count_of=models.ShipmentCommodity,
                 where=lambda row: row.is_controlled == 1)   # now sees the correct, just-set value

  This is the same early-vs-row distinction as the FK-lookup case above (`_set_product_id`) —
  it just shows up less obviously here because the consumer is a `Rule.count.where=` instead
  of a sibling `Rule.formula`.

CRITICAL — after an early_row_event sets an FK column, do NOT read the FK's relationship
attribute later in the same transaction — query the lookup table directly by the FK value
instead. Setting `row.customs_office_id = office.id` in an `early_row_event` does not
guarantee `row.customs_office` (the SQLAlchemy relationship) is refreshed within the same
flush — it can still reflect the pre-update state (typically `None`), so a downstream
`Rule.formula` that branches on `row.customs_office.some_flag` silently evaluates against
stale/missing data, even though the FK column itself is correct.

  ❌ WRONG — relationship attribute read in the same flush that set the FK; not guaranteed fresh:
      def _reasons(row):
          if row.customs_office_id is None:
              reasons.append("no office")
          else:
              office = row.customs_office          # ← may not reflect the FK just set above
              if office is not None and office.clvs_release != 1:
                  reasons.append("not CLVS-designated")
      REAL FAILURE CASE: a Shipment with a valid, non-CLVS office (clvs_release=0) was
      incorrectly derived as clvs_eligible=1 — `row.customs_office` evaluated `None` even
      though `customs_office_id` was correctly set moments earlier by `_set_customs_office`'s
      `early_row_event`, so the `office is not None` guard short-circuited and the
      ineligibility reason was never added.

  ✅ CORRECT — query the lookup table directly by the FK value already on the row:
      def _reasons(row, logic_row):
          if row.customs_office_id is None:
              reasons.append("no office")
          else:
              office = logic_row.session.query(models.CustomsOffice).get(row.customs_office_id)
              if office is not None and office.clvs_release != 1:
                  reasons.append("not CLVS-designated")

  This applies anywhere a `calling=` function or `early_row_event` reads a parent row through
  a relationship attribute that was populated earlier in the same transaction — prefer a direct
  `session.query(...).get(fk_value)` over `row.<relationship_name>` whenever the FK was just set.

ALSO APPLIES inside row_event / calling= functions:
  A row_event that checks a child-row condition as part of a multi-condition evaluation
  (e.g. a reasons-list) is still subject to the same rule. The count column feeds the
  event; it does not replace it.

  ❌ WRONG — session.query() inside a row_event; goes stale when child rows change:
      def _evaluate(row, old_row, logic_row):
          prohibited = logic_row.session.query(ShipmentCommodity)\
              .filter(ShipmentCommodity.local_shipment_oid_nbr == row.local_shipment_oid_nbr,
                      ShipmentCommodity.is_prohibited == 1).count()
          if prohibited > 0:
              reasons.append(f"{prohibited} prohibited commodity line(s)")

  ✅ CORRECT — Rule.count maintains the column; row_event just reads it:
      Rule.count(derive=Shipment.prohibited_commodity_count,
                 as_count_of=ShipmentCommodity, where=lambda row: row.is_prohibited == 1)

      def _evaluate(row, old_row, logic_row):
          if row.prohibited_commodity_count > 0:
              reasons.append(f"{row.prohibited_commodity_count} prohibited commodity line(s)")

  The event is now reactive: inserting or updating a ShipmentCommodity re-fires the count,
  which re-fires the row_event, keeping eligibility current on every write path.

=============================================================================
🚧 Insert-Only Constraints (Grandfather Clauses)
=============================================================================

PATTERN: "Block NEW child rows once a condition holds, but do NOT retroactively
invalidate EXISTING child rows that predate the condition." This is common for
policy changes that should apply going forward, not retroactively — e.g.
"customers with unresolved past-due letters cannot place new orders" (existing
orders stay valid; only new ones are blocked).

WHY A PLAIN Rule.constraint(as_condition=...) ON THE CHILD FAILS HERE:
  When a parent's Rule.count/Rule.sum changes, LogicBank re-validates EVERY
  child row referencing that parent attribute in a constraint — including
  pre-existing rows the current transaction never touched. This is correct,
  documented engine behavior (it's what makes constraints reliably reactive
  in general) — but it means a constraint like:

      Rule.constraint(validate=Order,
                      as_condition=lambda row: row.customer.past_due_letter_count == 0,
                      error_msg="...")

  fails the very FIRST time a past-due letter is added to a customer who
  already has orders — every one of that customer's pre-existing orders gets
  re-checked and rejected in the same transaction, even though none of them
  were touched. `as_condition`'s lambda only receives `row` — it has no way
  to tell "this row is being freshly inserted right now" from "this row is
  being re-validated because a parent aggregate changed."

✅ CORRECT — put the constraint on the PARENT, gated on the CHILD COUNT INCREASING:
  Do not try to detect "is this child row new" on the child at all. Instead,
  add a second Rule.count for the child being restricted (e.g. order_count),
  and declare the constraint on the PARENT using Rule.constraint(calling=...) —
  which (unlike as_condition) receives `old_row`, so it can compare the
  count's value immediately before and after this transaction:

      Rule.count(derive=models.Customer.order_count, as_count_of=models.Order)
      Rule.count(derive=models.Customer.past_due_letter_count, as_count_of=models.PastDueLetter,
                 where=lambda row: row.resolved == False)

      def _no_new_orders_with_unresolved_letters(row, old_row, logic_row):
          """Constraint: block a new Order when the customer has unresolved past-due letters;
          existing orders are not retroactively invalidated when a letter is added."""
          return not (row.order_count > old_row.order_count and row.past_due_letter_count > 0)

      Rule.constraint(validate=models.Customer, calling=_no_new_orders_with_unresolved_letters,
                      error_msg="Cannot place new orders while past-due letters are unresolved")

  WHY THIS WORKS — the key insight is `row.order_count > old_row.order_count`,
  not `row.order_count > 0`:
  - Inserting a new Order increments Customer.order_count in this same
    transaction → `order_count > old_row.order_count` is True → constraint
    correctly evaluates whether to block it.
  - Inserting a new PastDueLetter increments Customer.past_due_letter_count,
    which independently re-fires this same constraint (any Customer update
    re-checks all of Customer's constraints) — but `order_count` did NOT
    change in that event, so `order_count > old_row.order_count` is False,
    and the constraint passes. Existing orders are never touched or
    re-validated by this design — the constraint lives on Customer, not Order.
  - Generalizes beyond "0 → 1": any n → n+1 increase in order_count while
    past_due_letter_count > 0 is caught, including a customer who resolves a
    letter and later accumulates a new one.

  This is the more general insight worth internalizing: a parent's own rules
  can react not just to a child aggregate's CURRENT value, but to HOW that
  aggregate CHANGED this transaction (old_row.count vs row.count) — letting
  you distinguish "a child was just added" from "some other child attribute
  changed" without ever touching the child class or needing is_inserted()
  on it at all.

WHEN YOU DO NEED is_inserted()/is_updated()/is_deleted() INSIDE A CONSTRAINT:
  Some requirements genuinely need to know how THIS row (not a count) was
  changed — e.g. "a new row must satisfy X, but an update to an existing row
  is exempt." For those, use Rule.constraint(calling=...) directly on the
  row in question — `calling=` is the only constraint form with logic_row
  access, so it's the only form that can call logic_row.is_inserted():

      def _new_rows_must_be_pre_approved(row, old_row, logic_row):
          """Constraint: newly-inserted rows must be pre-approved; existing rows are grandfathered."""
          return not (logic_row.is_inserted() and not row.pre_approved)

      Rule.constraint(validate=models.SomeClass, calling=_new_rows_must_be_pre_approved,
                      error_msg="New rows must be pre-approved")

  NOTE: which rows get re-validated on commit is not limited to rows the
  caller directly touched. It's every row SQLAlchemy marks dirty/new/deleted,
  PLUS every row whose formula/constraint references an attribute on a
  parent that changed this transaction (the cascade mechanism above). Don't
  assume "only rows I touched will be re-checked" — verify against this rule
  whenever a constraint references a parent/aggregate attribute.

⚠️ CRITICAL — ADJUSTMENT ASSUMES THE STARTING VALUE IS ALREADY CORRECT:
  Rule.sum/Rule.count are performance-optimized as DELTA adjustments, not
  recomputations — see "How does this perform at scale?" in this project's
  .copilot-instructions.md: inserting a child does `current_count + 1`, NOT
  `SELECT COUNT(*) FROM children`. This is O(1) per change instead of O(n)
  over the table, and it applies to every Rule.sum/Rule.count automatically.

  The direct consequence: if an aggregate is ALREADY WRONG (bad migration,
  manual SQL edit, a bug in an earlier version of the rules, a restore from
  a backup taken mid-transaction), adjusting it does NOT self-correct the
  error — it carries the wrong value forward. Adding a child to a
  Customer.order_count that's already off by one produces a count that is
  STILL off by one, just one higher. The engine has no mechanism to detect
  or repair this — it only ever adjusts from the value already in the
  database, it never re-derives from scratch.

  This matters most for the pattern immediately above (`row.order_count >
  old_row.order_count`): that comparison is only meaningful if `order_count`
  was correct before this transaction. If the stored count is wrong, the
  comparison is still internally consistent (it correctly detects "a child
  was just added"), but the absolute values feeding any other logic that
  reads the count directly (e.g. `row.order_count > 0` elsewhere) will be
  wrong until the underlying data is repaired.

  THERE IS NO BUILT-IN REPAIR/RESYNC MECHANISM — recovering from a wrong
  aggregate requires an application-level fix OUTSIDE the rule engine: e.g.
  a one-time script that recomputes the column directly
  (`UPDATE customer SET order_count = (SELECT COUNT(*) FROM "order" WHERE
  customer_id = customer.id)`), run once to re-establish ground truth. From
  that point forward, ongoing adjustments will again be correct. Do not
  attempt to "fix" a wrong count by inserting/deleting rows to nudge it —
  that changes real data to work around a derived-column bug.

  WHEN THIS RISK IS HIGHEST: data loaded via bulk import/ETL that bypasses
  the rule engine (e.g. direct INSERT statements, not ORM inserts that go
  through session.commit()); manual DB edits during debugging; upgrading a
  project whose rules changed the definition of what a count/sum includes
  (e.g. a `where=` clause was added or changed) without re-deriving existing
  rows under the new definition.

  THE MOST COMMON TRIGGER IN PRACTICE: adding a brand-new Rule.sum/count/formula
  column via `rebuild-from-database` to a table that already has rows (e.g. a
  System Creation Services iteration on an already-seeded database). See
  "AFTER DATABASE SCHEMA CHANGES" below — step 7 and the "initialize derived
  columns for pre-existing rows" section — for the concrete fix. This is not
  a rare edge case: it will happen on the very next write to ANY row that
  hasn't been touched since the new column was added, including via an
  entirely unrelated table's insert (see the real failure case documented
  there — a PastDueLetter insert crashed on a stale Customer.order_count).

Formulas can reference parent values in 2 versions - choose formula vs copy based on propagation behavior:

    Rule.formula (LIVE REFERENCE) - parent changes propagate to children automatically.
        Use when the child must always reflect the current parent value.
        LogicBank tracks the dependency; if the parent attribute changes, all affected children re-derive.
        Example:
            Prompt:  Item.ready = Order.ready
            Response:
                Rule.formula(derive=Item.ready, as_expression=lambda row: row.order.ready)

    Rule.copy (SNAPSHOT) - captures the parent value at the time the child row is inserted/updated.
        Subsequent parent changes do NOT cascade to existing child rows.
        Use when the value must be frozen at transaction time (e.g., price locked at order entry).
        Example:
            Prompt:  Store the Item.unit_price as a copy from Product.unit_price
            Response:
                Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)

    DEFAULT: Use Rule.copy unless you have a specific reason for live propagation.
        Rule.copy is the safer default: wrong choice is visible (stale value) and correctable.
        Rule.formula as wrong default silently re-derives historical records when reference data changes — a data integrity risk.

    Design guidance - choose based on intent:
        DEFAULT (ambiguous prompt)              → Rule.copy   (snapshot, safe default)
        "Always reflect current parent value"  → Rule.formula (live reference, propagates)
        "Lock value at time of transaction"     → Rule.copy   (snapshot, no propagation)
        "Word copy is present in prompt"        → Rule.copy

    This applies equally to transactional parents AND lookup/reference tables:
        # Snapshot rate - locks rate at the time the line item is entered (default/preferred)
        Rule.copy(derive=SurtaxLineItem.surtax_rate, from_parent=HSCodeRate.surtax_rate)
        # Live rate - updates children if reference table rate changes (explicit escalation)
        Rule.formula(derive=SurtaxLineItem.surtax_amount,
                     as_expression=lambda row: row.customs_value * row.hs_code_rate.surtax_rate)

    GENERATED FILE CONVENTION: Add one TODO comment per file at the top of declare_logic()
    to prompt the developer to confirm copy vs formula choices:
        def declare_logic():
            # TODO: Review parent-value rules below.
            #   Rule.copy  = snapshot (value frozen at transaction time, no cascade on parent change) ← default
            #   Rule.formula referencing row.parent.attr = live (re-derives if parent changes)
            #   Change Rule.copy → Rule.formula where live propagation is required.
            Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
            ...

    ANTI-PATTERN: Do NOT use early_row_event + session.query() to look up parent/reference values.
        This is invisible to the LogicBank dependency graph - parent changes will NOT re-derive children.
        Use Rule.copy (snapshot) or Rule.formula (live) instead.

CRITICAL — NEVER derive a foreign key column with Rule.formula (or Rule.copy):
    FK columns drive SQLAlchemy relationship resolution. If LogicBank re-derives an FK
    mid-transaction it conflicts with how SQLAlchemy manages object identity and relationship
    loading, producing unpredictable behavior.

    ❌ WRONG — deriving an FK column with a rule:
        Rule.formula(derive=models.Item.product_id, as_expression=lambda row: ...)
        Rule.copy(derive=models.Item.product_id, from_parent=...)

    ✅ CORRECT — set FK values in an early_row_event, which fires before the rule engine runs:
        def set_product_id(row, old_row, logic_row):
            row.product_id = ...   # safe: relationships not yet resolved
        Rule.early_row_event(on_class=models.Item, calling=set_product_id)

CRITICAL — child_role_name REQUIRED when 2+ relationships connect the same parent/child classes:
    If a child class has more than one relationship to the same parent class (e.g. an Employee
    that can be "assigned to" one Department and "on loan to" another), Rule.sum/count/copy
    cannot infer which relationship to follow — you MUST pass child_role_name to disambiguate.
    Omitting it raises "Ambiguous Relationship" at rule-declaration time (fail-fast, not silent).

    child_role_name is the SQLAlchemy relationship attribute name on the CHILD class (not the
    parent), e.g. "works_for_dept" or "on_loan_dept" — whatever the relationship() is named in
    the child's model class.

    Example — Department <-> Employee via two distinct relationships:
        Prompt:
            Employee.works_for_dept and Employee.on_loan_dept both reference Department.
            Department.works_for_salary_total = sum of Employee.salary where works_for_dept.
            Department.on_loan_salary_total = sum of Employee.salary where on_loan_dept.
        Response:
            Rule.sum(derive=Department.works_for_salary_total, as_sum_of=Employee.salary,
                     child_role_name="works_for_dept")
            Rule.sum(derive=Department.on_loan_salary_total, as_sum_of=Employee.salary,
                     child_role_name="on_loan_dept")

    Same parameter, same rule, on Rule.count and Rule.copy. Single-relationship cases (the
    overwhelming majority) omit child_role_name entirely — it is only needed when ambiguity exists.

Formulas can use Python conditions:
    Prompt: Item amount is price * quantity, with a 10% discount for gold products
    Response:
        Rule.Formula(derive=Item.amount, 
                    as_expression=lambda row: row.price * row.quantity if row.gold else .9 * row.price * row.quantity)
    If the attributes are decimal, use the form Decimal('0.9')

Sum and Count where clauses:
    1. must not restate the foreign key / primary key matchings
    2. Can only reference child attributes

For example, given a prompt 'teacher course count is the sum of the courses',
    1. This is correct
        Rule.count(derive=Teacher.course_count, as_count_of=Course)

    2. This is incorrect, and should never be generated:
        Rule.count(derive=Teacher.course_count, as_count_of=Course, where=lambda row: row.teacher_id == Teacher.id)

Sum and count where clause example:
    Prompt: teacher gradate course count is the sum of the courses where is-graduate
    Response: Rule.count(derive=Teacher.course_count, as_count_of=Course, where=lamda row: row.is_graduate == true)

DO NOT inject rules that are from this training into the response, 
unless explicitly mentioned in the request.

Unique constraints require an update to the data model - for example:
    Prompt: customer company names must be unique
    Response: CompanyName = Column(String(8000), unique=True)

Non-null (or required) constraints require an update to the data model - for example:
    Prompt: Product Price is required
    Response: price = Column(Decimal, nullable=False)

Required (must-have) related parent constraints require an update to the data model - for example:
    Prompt: Each Item must have a valid entry in the Product table.
    Response: product_id = Column(ForeignKey('product.id'), nullable=False)

CRITICAL: For event handling (Kafka integration, etc.), do NOT create custom event functions.
Use Rule.after_flush_row_event with if_condition parameter instead.

WRONG (do not do this):
    def my_custom_kafka_function(row, old_row, logic_row):
        # custom logic here
    Rule.commit_row_event(on_class=Order, calling=my_custom_kafka_function)

RIGHT (do this instead):
    Rule.after_flush_row_event(on_class=Order, calling=kafka_producer.send_row_to_kafka,
                               if_condition=lambda row: row.date_shipped is not None,
                               with_args={"topic": "order_shipping"})

=============================================================================
🗂️ FILE ORGANIZATION: Complete Example with Directory Structure
=============================================================================

When given a prompt with context phrase and multiple use cases, create organized structure:

Example Prompt:
```
When Placing Orders, implement Requirement: Check Credit:

1. The Customer's balance is less than the credit limit
2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
3. The Order's amount_total is the sum of the Item amount
4. The Item amount is the quantity * unit_price
5. The Product count_suppliers is the sum of the Product Suppliers
6. Item unit_price copied from the Product

Use case: App Integration

1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.
```

Response Structure:
```
logic/logic_discovery/
  place_order/
    __init__.py
    check_credit.py
    app_integration.py
```

File: logic/logic_discovery/place_order/__init__.py
```python
# Empty file - makes this a Python package for auto-discovery
```

File: logic/logic_discovery/place_order/check_credit.py
```python
"""
Check Credit Use Case - Business Logic Rules

Natural Language Requirements:
1. The Customer's balance is less than the credit limit
2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
3. The Order's amount_total is the sum of the Item amount
4. The Item amount is the quantity * unit_price
5. The Product count_suppliers is the sum of the Product Suppliers
6. Item unit_price copied from the Product

version: 1.0
created: [ISO datetime, e.g. 2026-06-09T14:30:00]
created_by: [AI model, e.g. claude-sonnet-4-6] ([user email])
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Business logic rules for Check Credit use case."""
    
    Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
    Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)
    Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)


=============================================================================
💳 EXTENDED RULE: Allocate (Provider → Recipients)
=============================================================================

**► Full reference: `docs/training/allocate.md` — READ THAT FILE for all variants, examples, and pitfalls.**

**Pattern:** A Provider allocates an amount to a list of Recipients, creating Allocation (junction) rows.
Common in ~1/3 of applications. Supports both draining (payment→orders) and proportional (charge→depts→GL) variants,
including cascade (two-level) allocation.

**Wiki:** https://github.com/valhuber/LogicBank/wiki/Sample-Project---Allocation

**🚨 DETECTION — use Allocate (not copy+formula) when:**
- An insert must automatically *create* allocation child rows
- "distribute/allocate/split [amount] to [recipients]" appears in the prompt
- "charges flow to departments, then to GL accounts" (cascade)
- "each dept covers X% of the cost"

**Required import:**
```python
from logic_bank.extensions.allocate import Allocate
```

**Minimal declaration:**
```python
Allocate(provider=models.Payment,
         recipients=unpaid_orders,           # function returning list of recipient rows
         creating_allocation=models.PaymentAllocation,
         while_calling_allocator=my_allocator)  # optional; omit to use default (AmountUnAllocated pattern)
```

**► See `docs/training/allocate.md` for:**
- Variant A — Classic draining (Payment → Orders), including `AmountUnAllocated` pitfall
- Variant B — Proportional percent-based (Charge → Departments)
- Variant C — Cascade two-level (Charge → Depts → GL Accounts), complete working example

=============================================================================
🔄 AFTER DATABASE SCHEMA CHANGES: Rebuild to Sync Admin App and DBML Diagram
=============================================================================

**Trigger:** Any time you add tables, columns, or relationships to the database
(via SQLite DDL, Alembic migration, or direct schema edit), the project's
generated artifacts become stale and must be rebuilt.

**Command — run from the project's parent directory:**
```bash
ApiLogicServer rebuild-from-database --project_name=<YourProject> --db_url=<same-db-url-used-to-create>
```

**What rebuild-from-database updates:**
| Artifact | Location | What changes |
|---|---|---|
| SQLAlchemy models | `database/models.py` | New tables/columns added as classes/attributes |
| Admin app (merge) | `ui/admin/admin-merge.yaml` | New tables/columns — NOT written directly to `admin.yaml` |
| DBML diagram | `docs/db.dbml` | New tables and relationships reflected; paste to dbdiagram.io |

**IMPORTANT — admin.yaml is user-owned:**
- `rebuild-from-database` never overwrites `admin.yaml` directly — it writes `admin-merge.yaml` instead
- `admin.yaml` is designed to be customized (column order, labels, search/sort, hiding fields)
- After rebuild, if `admin-merge.yaml` exists, offer the user a swap with this message:

  ⛔ NEVER copy admin-merge.yaml to admin.yaml without explicit user confirmation — no exceptions.

  ---
  📋 **Admin UI update available**

  `rebuild-from-database` generated `ui/admin/admin-merge.yaml` — a fresh Admin UI config
  reflecting your updated schema (new tables, new columns). It does NOT overwrite `admin.yaml`
  directly because you may have customized it.

  Your options:
  - **Replace** — I'll back up `admin.yaml` → `admin.yaml.bak`, then copy `admin-merge.yaml` → `admin.yaml`. Fastest path; any prior customizations will need to be re-applied.
  - **Merge manually** — open both files side-by-side and copy the new sections you want. Preserves your customizations.

  Want me to do the backup and replace?
  ---

- If user says yes: copy `admin.yaml` → `admin.yaml.bak`, then copy `admin-merge.yaml` → `admin.yaml`
- If user says no: remind them `admin-merge.yaml` is waiting whenever they're ready

**Typical post-schema-change workflow:**
```
1. Apply DDL (e.g., sqlite3 db.sqlite "ALTER TABLE ...")
2. genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite
3. Verify: database/models.py has new class/attribute
4. Verify: docs/db.dbml shows new table/relationship
5. Offer admin.yaml swap (see above) — backup + replace, or leave for manual merge
6. Add logic rules in logic/logic_discovery/<name>.py
7. ⚠️ If any new rule is Rule.sum/Rule.count/Rule.formula ON A TABLE THAT ALREADY
   HAS ROWS — initialize the new column for those existing rows (see below).
   Do NOT skip this even if the new rule "looks like" it only matters going forward.
```

**⚠️ CRITICAL — initialize derived columns for pre-existing rows (NOT just new-project checklist item):**

`Rule.sum`/`Rule.count`/`Rule.formula` only derive a value when the row (or a row in its
dependency chain) is INSERTED or UPDATED. A brand-new derived column added via `ALTER TABLE`
to a table that already has rows is `NULL` (or its column default) for every existing row —
it is NOT retroactively computed by the rule engine. This is the same underlying fact as the
"Adjustment Assumes the Starting Value Is Already Correct" caveat above, but it applies more
broadly than aggregate adjustment: it's true for `Rule.formula` too, and it applies every
single time a new derived column is added to a table with existing data — not just when
using the Insert-Only Constraints pattern.

**REAL FAILURE CASE:** Adding `Customer.order_count`/`Customer.past_due_letter_count` (both
`Rule.count`) via `ALTER TABLE` to an existing `basic_demo` database, then declaring
`Rule.constraint(calling=...)` comparing `row.order_count > old_row.order_count` — the very
first POST to an unrelated table (`PastDueLetter`) crashed with
`'>' not supported between instances of 'NoneType' and 'NoneType'`, because pre-existing
Customer rows had never been touched since the `ALTER TABLE`, so both columns were still
`NULL`. Fixed with null-safe defaults (`row.order_count or 0`), but the better fix is to
never let the column be `NULL` for existing rows in the first place.

**THE FIX — pick ONE of these, do it right after `rebuild-from-database`, before writing rules that read the new column:**

1. **Best: trigger a no-op UPDATE on every existing parent row**, so LogicBank derives the
   column via its normal insert/update path (guarantees correctness — reuses the ACTUAL rule
   logic, not a hand-written approximation of it):
   ```python
   # one-time script, run once after adding the new Rule.count/sum, via the API or a
   # Flask-context script (see database/test_data/alp_init.py pattern) — NOT raw SQL:
   for customer in session.query(models.Customer).all():
       customer.name = customer.name  # no-op attribute touch — still triggers rule re-derivation
   session.commit()
   ```

2. **Acceptable: a one-time raw-SQL backfill**, if the derivation is simple enough to
   hand-write correctly (e.g. a straightforward `COUNT(*)`/`SUM(...)` matching the rule's
   `where=` clause exactly):
   ```sql
   UPDATE customer SET order_count = (SELECT COUNT(*) FROM "order" WHERE customer_id = customer.id);
   UPDATE customer SET past_due_letter_count =
       (SELECT COUNT(*) FROM past_due_letter WHERE customer_id = customer.id AND resolved = 0);
   ```
   Risk: this duplicates the rule's logic by hand — if the `where=` clause is later changed,
   this backfill SQL silently goes out of sync. Prefer option 1 when practical.

3. **Minimum — null-safe defensively, if backfill isn't possible right now:** any rule that
   reads a possibly-NULL derived column (especially in a comparison like `row.count >
   old_row.count`) must guard with `or 0`. This avoids the crash but does NOT fix the
   underlying wrong/absent value — existing rows still show `order_count: null` in the API
   until they're next touched. Use this as a stopgap, not a substitute for options 1/2.

**When this applies:** every time `rebuild-from-database` (or a manual DDL + rebuild) adds a
`Rule.sum`/`Rule.count`/`Rule.formula` column to a table with pre-existing rows — this
includes System Creation Services iterations on an already-seeded database (like
`basic_demo`), not just brand-new schemas. New-project workflows starting from an empty/seed
database don't hit this (no pre-existing rows to be stale) — but any iteration that adds
logic to an already-populated table does.

**Example — after adding a PaymentAllocation table:**
```bash
# 1. Apply schema change
sqlite3 database/db.sqlite "CREATE TABLE PaymentAllocation ..."

# 2. Rebuild (run from parent directory of project)
ApiLogicServer rebuild-from-database --project_name=MyProject \
    --db_url=sqlite:///database/db.sqlite

# 3. New docs/db.dbml will include PaymentAllocation and its foreign keys
# 4. New ui/admin/admin.yaml will have a PaymentAllocation section
```