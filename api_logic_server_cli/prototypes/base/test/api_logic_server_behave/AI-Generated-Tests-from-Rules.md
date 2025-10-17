# AI-Generated Test Suites: From Business Rules to Executable Tests in Minutes

**How we taught AI to create comprehensive test suites directly from declarative business rules**

*By Val Huber, with Claude (GitHub Copilot)*

---

## The Problem: Testing Business Logic is Hard

You've built your API Logic Server project. You've declared your business rules - sum this, derive that, constrain the other thing. The rules work beautifully. But now you need tests.

Not just "does the GET work" tests. Real tests that validate your **business logic**. Tests that prove:
- Balances update correctly when items are added to orders
- Credit limits are enforced
- Derivations cascade properly
- Constraints catch violations

Writing these tests manually? Time-consuming. Error-prone. And honestly, a bit tedious.

But here's the thing: **Your business rules already describe what should happen.** Why should you have to describe it again in test code?

## The Breakthrough: Rules → Tests, Automatically

What if an AI could read your business rules and generate the test suite for you?

Not generate random tests. Not generate brittle tests. Generate **proper, comprehensive, maintainable tests** that actually validate your logic.

That's what we've achieved. And we did it in a day.

## How It Works

### 1. Start with Declarative Rules

Here's a typical set of rules in API Logic Server:

```python
Rule.constraint(validate=Customer,
    as_condition=lambda row: row.Balance <= row.CreditLimit,
    error_msg="balance ({row.Balance}) exceeds credit limit ({row.CreditLimit})")

Rule.sum(derive=Customer.Balance, 
    as_sum_of=Order.AmountTotal,
    where=lambda row: row.ShippedDate is None)

Rule.sum(derive=Order.AmountTotal,
    as_sum_of=Item.Amount)

Rule.formula(derive=Item.Amount,
    as_expression=lambda row: row.Quantity * row.UnitPrice)
```

These rules say:
- Customer balance is the sum of unshipped order totals
- Order total is the sum of item amounts
- Item amount is quantity × price
- Balance can't exceed credit limit

### 2. AI Generates Behave Scenarios

The AI reads these rules and generates Gherkin scenarios:

```gherkin
Scenario: Customer can place order within credit limit
  Given a customer "Alice" with balance 950 and credit limit 1000
  And a product "Widget" with price 10
  When order is placed with 5 units of "Widget"
  Then the order is created successfully
  And customer balance is 1000

Scenario: Customer cannot exceed credit limit
  Given a customer "Bob" with balance 950 and credit limit 1000
  And a product "Gadget" with price 20
  When order is placed with 10 units of "Gadget"
  Then the order is rejected with credit limit error
  And customer balance remains 950
```

Notice: The AI understood:
- Which rules interact (balance + constraint)
- What constitutes a positive test (within limit)
- What constitutes a negative test (exceeds limit)
- What to assert (balance calculations, error messages)

### 3. AI Implements Step Definitions

Then the AI writes the Python step implementations:

```python
@given('a customer "{name}" with balance {balance:d} and credit limit {credit_limit:d}')
def step_impl(context, name, balance, credit_limit):
    customer_id = get_or_create_test_customer(name, balance, credit_limit)
    context.customer_id = customer_id
    # Creates filler orders to reach target balance (balance is computed, not set!)

@when('order is placed with {quantity:d} units of "{product_name}"')
def step_impl(context, quantity, product_name):
    try:
        order_id = create_test_order(context.customer_id)
        item_id = create_test_item(order_id, context.product_id, quantity)
        context.order_created = True
    except requests.exceptions.HTTPError as e:
        context.order_created = False
        context.error_response = e.response
        # Negative tests need error handling!

@then('customer balance is {expected_balance:d}')
def step_impl(context, expected_balance):
    customer = get_customer(context.customer_id)
    actual_balance = float(customer['data']['attributes']['Balance'])
    assert abs(actual_balance - expected_balance) < 0.01
```

The AI got all the **tricky patterns** right:
- ✅ Aggregate columns (Balance) are computed - never set directly
- ✅ Create filler orders to reach target balance in GIVEN
- ✅ JSON API returns string IDs - convert with `int()`
- ✅ Create order then items separately (no nested creation)
- ✅ Negative tests catch exceptions with try/except
- ✅ Float comparisons use tolerance
- ✅ Unique timestamps prevent data contamination

### 4. Results: 11 Scenarios, 100% Passing

```
11 scenarios passed, 0 failed, 0 skipped
49 steps passed, 0 failed, 0 skipped
```

Tests validate:
- ✅ Orders update customer balance
- ✅ Items update order total
- ✅ Credit limit enforcement
- ✅ Multiple orders for same customer
- ✅ Order shipped doesn't affect balance
- ✅ Order deleted restores balance
- ✅ Quantity changes update amounts
- ✅ Constraint violations properly rejected

## The Secret Sauce: Training Material

How did we teach the AI to do this? We created **comprehensive training documentation** (~1700 lines) that captures:

### Every Bug We Hit (and Fixed)

**Bug #1: Setting Aggregate Columns Directly**
```python
# ❌ WRONG - Aggregates are computed!
customer_data = {
    "Name": name,
    "Balance": 950,  # Can't set this!
    "CreditLimit": 1000
}

# ✅ RIGHT - Create filler orders to reach target
customer_id = create_customer(name, 0, 1000)
if target_balance > 0:
    create_filler_orders(customer_id, target_balance)
```

**Bug #2: JSON Returns String IDs**
```python
# ❌ WRONG - API returns "8" but database expects 8
customer_id = result['data']['id']  # String!

# ✅ RIGHT - Convert to integer
customer_id = int(result['data']['id'])
```

**Bug #3: Test Data Contamination**
```python
# ❌ WRONG - Reuses customers from previous runs
name = "Alice"  # Might exist!

# ✅ RIGHT - Unique timestamp ensures fresh data
name = f"Alice {int(time.time() * 1000)}"
```

And 8 more bugs, all documented with complete fixes.

### Debugging Techniques

**Scenario Logic Logs**

When a test fails, check the scenario logic log:

```bash
ls -lart test/api_logic_server_behave/logs/scenario_logic_logs/ | tail -20
```

- **Empty log (0 bytes)?** Failure in GIVEN/WHEN before logic executes
- **Contains logic?** Failure in assertion or post-logic
- **Compare successful vs failed** to spot differences

### Reference Implementation

Complete, corrected `test_data_helpers.py` with all patterns:
- Unique naming with timestamps
- Integer ID conversion
- No aggregate setting
- Proper error handling
- Descriptive exceptions

## The Impact: Every Project Gets This

This isn't just about one test suite. The training material becomes a **template** for any API Logic Server project.

**User's Project (Any Domain):**
- Healthcare? Tests that patient visits update billing
- Finance? Tests that transactions update account balances
- Inventory? Tests that orders decrement stock levels
- Manufacturing? Tests that production updates materials

**AI Process:**
1. Read the project's `logic/declare_logic.py`
2. Identify rules (sums, formulas, constraints, etc.)
3. Follow patterns from testing.md
4. Generate scenarios matching the rules
5. Implement steps with correct patterns
6. Result: **Complete, working test suite**

## Why This Matters

**Traditional Approach:**
- Write rules in code
- Write tests in code (duplicate effort)
- Tests often miss edge cases
- Maintenance burden when rules change

**GenAI Approach:**
- Write rules **once** (declaratively)
- AI generates tests automatically
- Tests cover positive and negative cases
- Tests update when rules change

**The Multiplier Effect:**

One day of work creating this system prevents:
- ❌ Hundreds of future debugging sessions
- ❌ Aggregate-setting bugs in every project
- ❌ Data contamination in test suites
- ❌ Brittle tests that break on refactor

Instead:
- ✅ Every project gets proper tests from day one
- ✅ Tests validate actual business logic
- ✅ Developers spend time on features, not test boilerplate
- ✅ AI assistants know the patterns

## The Philosophy

This embodies a core principle: **Documentation is more important than specific tests.**

We didn't just fix 11 scenarios. We created a **teaching system** that:
- Shows AI how to think about rules → tests
- Captures all the gotchas and patterns
- Works for any domain, any rules
- Multiplies effort across all future projects

The best code is code that doesn't need to be written. The best tests are tests that write themselves.

## Try It Yourself

The complete training material is in every API Logic Server project:

```
docs/training/testing.md  # Complete guide (~1700 lines)
test/.../test_data_helpers.py  # Reference implementation
```

Create your project with:
```bash
genai-logic create --project_name=my_project --db_url=my_database
# or
genai-logic genai --using='create a system for...'
```

Then ask your AI assistant:
> "Read docs/training/testing.md and generate Behave tests for the rules in logic/declare_logic.py"

Watch it create a complete test suite, with proper patterns, in minutes.

## What's Next?

This is just the beginning. With this foundation:
- **Test generation from natural language**: "Test that high-value orders require approval"
- **Coverage analysis**: "Which rules don't have tests yet?"
- **Test maintenance**: "Update tests when I change this rule"
- **Domain-specific patterns**: Healthcare tests, financial tests, etc.

The vision: **Declare your business logic. Get everything else automatically.**

Rules → API → UI → Tests → Documentation

All generated. All consistent. All maintainable.

That's the power of declarative business rules combined with AI.

---

## About This Article

This article was written collaboratively by Val Huber (human) and Claude (AI) working together in VS Code with GitHub Copilot. The testing system described was built in a single day of pair programming, demonstrating the same human-AI collaboration it enables.

**Learn more:**
- API Logic Server: https://apilogicserver.github.io
- GenAI Logic: https://github.com/ApiLogicServer/ApiLogicServer-src
- Try it: `pip install genai-logic`

---

*"The best architecture is one where business logic is declared once, and everything else follows automatically."* - Val Huber
