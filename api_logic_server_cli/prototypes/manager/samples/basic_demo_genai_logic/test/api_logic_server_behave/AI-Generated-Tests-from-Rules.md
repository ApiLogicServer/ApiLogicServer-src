# AI-Generated Test Suites: From Business Rules to Executable Tests in Minutes

**How we taught AI to create comprehensive test suites directly from declarative business rules**

*By Val Huber, with Claude (GitHub Copilot)*

---

## Impact: 30+ Years in 3 Days

**The Request That Seemed Impossible**

Test creation has been a feature request for **30-40 years** - no exaggeration. The amount of detailed source code generation required was simply more than anyone could imagine even teams tackling. The complexity of translating business rules into comprehensive, executable test scenarios with proper setup, validation, and teardown seemed beyond reach.

**What Actually Happened**

We accomplished it in approximately **3-4 days** working collaboratively with AI. That's quite remarkable.

**The Turning Point**

Until this effort, the approach had been using Copilot for specific projects while mainly following traditional development methods. This test generation achievement demonstrated that AI can both:

1. **Understand complex architectural patterns** (declarative rules, dependency chains, JSON:API, Behave testing)
2. **Bring GREAT value** to development efforts through:
   - Deep comprehension of domain-specific requirements
   - Rapid iteration on complex code generation
   - Learning from mistakes and encoding solutions for future sessions
   - Translating business logic directly into test scenarios

**The Decision**

This success made it clear: **Make Copilot core to the GenAI-Logic development experience.** Not just as a code completion tool, but as a genuine collaborative partner in the development process.

---

## Background: Teaching AI Through "Messages in a Bottle"

API Logic Server has been using AI collaboration for years:
- **GenAI creates databases** from natural language
- **GenAI creates logic** using declarative rules (after learning procedural causes bugs - see [comparison](https://github.com/ApiLogicServer/basic_demo/blob/main/logic/procedural/declarative-vs-procedural-comparison.md))
- **GenAI performs database reorganizations** while preserving logic

**The Pattern**: Each created project contains training material - "messages in a bottle" - that teach future AI assistants how to work with THAT specific project.

**The Extension**: What if AI could also **create tests from business rules?**

## The Problem: Testing Business Logic is Hard

You've built your API Logic Server project. You've declared your business rules - sum this, derive that, constrain the other thing. The rules work beautifully. But now you need tests.

Not just "does the GET work" tests. Real tests that validate your **business logic**. Tests that prove:
- Balances update correctly when items are added to orders
- Credit limits are enforced
- Derivations cascade properly
- Constraints catch violations

Writing these tests manually? Time-consuming. Error-prone. And honestly, a bit tedious.

But here's the thing: **Your business rules already describe what should happen.** Why should you have to describe it again in test code?

## Aha Moment #1: "Can AI Create Tests From Rules?"

**The Insight**: Declarative rules already specify:
- What should be computed (formulas, sums)
- When it should happen (constraints, validations)
- What the dependencies are (order → customer → balance)

**The Question**: If AI can read these rules to understand the logic, why can't it generate tests that validate them?

**The Challenge**: Business logic has critical dependencies where bugs lurk:
- **Aggregate columns** are computed (never set directly)
- **Cascading updates** flow through relationships
- **Constraint timing** matters (when does validation fire?)
- **Test data contamination** from previous runs
- **Order of operations** in multi-table updates

These aren't obvious. They require deep pattern matching across hundreds of lines of code.

## Phase 1: Rule-Driven CRUD Testing (5 Hours)

### The "Time Machine" Iteration Pattern

**The Cycle**:
1. **AI reads** `logic/declare_logic.py` → Understands rules
2. **AI generates** tests from those rules
3. **Run tests** → Discover bugs
4. **Fix bugs** → Both code AND documentation
5. **Update training material** → "Program your future self"
6. **Repeat** → Each iteration prevents future bugs

This is the "time machine" - fixing today's bugs prevents tomorrow's.

### The Bugs We Hit (Sampling the Journey)

**Bug #1: Setting Aggregate Columns**
```python
# ❌ WRONG - Balance is computed!
customer = {"Name": "Alice", "Balance": 950, "CreditLimit": 1000}

# ✅ RIGHT - Create filler orders to reach target balance
customer = create_customer("Alice", 0, 1000)
create_filler_orders(customer_id, target_balance=950)
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
# ❌ WRONG - Customer from previous run interferes
name = "Alice"

# ✅ RIGHT - Unique timestamp ensures fresh data
name = f"Alice {int(time.time() * 1000)}"
```

**Bug #4: Derived vs Added Aggregates**
```python
# ❌ WRONG - Thought balance ADDS to existing
# Create customer with balance=220, add order=180
# Expected: 220 + 180 = 400

# ✅ RIGHT - Balance is REPLACED by sum of orders
# Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal...)
# Balance = sum(all orders), not accumulation
```

**Bug #5: Customer Name Mapping**
```python
# ❌ WRONG - After adding timestamp, can't find customer
customer_name = "Bob"
unique_name = f"Bob {timestamp}"  # Created this
# Later: lookup by "Bob" fails!

# ✅ RIGHT - Map test names to unique names
context.customer_map = {"Bob": {"unique_name": unique_name, "id": customer_id}}
```

*...and 7 more bugs, each teaching AI assistants critical patterns...*

### Phase 1 Results

**What We Achieved:**
- ✅ Generated tests from declarative rules
- ✅ CRUD-level testing (POST, PATCH, DELETE)
- ✅ Granular rule validation (change quantity, delete item, etc.)
- ✅ Proper handling of aggregates, constraints, cascades
- ✅ Repeatable tests (timestamps prevent contamination)
- ✅ Comprehensive training material (~1700 lines)

**Test Results**: 6 scenarios passing, validating individual rule interactions

### Phase 1 Assessment: What Was Missing?

**Looking at Northwind Tests**: They test complete business transactions:
- Order **with** Items (together)
- "Place Order" (not "POST Order, then POST Item")
- Business language ("Customer" not "customer_id")

**Our Phase 1 Tests**: Only CRUD operations
- Create order (alone)
- Create item (alone)
- Update quantity (granular)

**The Gap**: Missing **business object tests** - the way users actually interact with the system!

## Aha Moment #2: "Infer Business Objects From Custom APIs"

**Val's Observation**: *"We're missing Order+Items together. But look at `api/api_discovery/order_b2b.py` - it shows the business object structure!"*

**The Insight**: Custom APIs **ARE** the business object definitions:
- OrderB2B creates Order + Items in one call
- Uses business language ("Account" vs "customer_id")  
- Represents how users think about transactions

**Could AI Have Discovered This Alone?**

**Val**: *"Could you have figured this out without me pointing it out?"*

**Claude**: *"Honestly? No. I would have kept generating more sophisticated CRUD tests. I wouldn't have made the connection between custom APIs and business object testing. That required your cross-project pattern recognition."*

**The Realization**: This is TRUE collaboration - AI couldn't make the intuitive leap.

## Phase 2: Business Transaction Testing

### The Hybrid Approach

**Discovery Step**: Before generating tests, scan `api/api_discovery/`:
- Found `order_b2b.py`? → Business object detected!
- Analyze parameters → Infer transaction structure
- Extract business language → Map to database schema

**The Strategy**:
- **Phase 2 for CREATE**: Use custom business APIs (OrderB2B)
- **Phase 1 for UPDATE/DELETE**: Use CRUD (granular rule testing)

**Why Hybrid?**
- Business APIs model complete transactions (how users think)
- CRUD tests granular rule interactions (how rules work)
- Both are needed for comprehensive validation

### Phase 2 Implementation

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

### Phase 2 Implementation

**Declarative Rules (Same as Phase 1):**

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

**Custom API (The Business Object Definition):**
```python
# api/api_discovery/order_b2b.py
@jsonapi_rpc(http_methods=["POST"])
def OrderB2B(self, *args, **kwargs):
    """
    args:
        order:
            Account: "Alice"      # Business language!
            Notes: "Please Rush"
            Items:
            - Name: "Widget"
              QuantityOrdered: 2
    """
```

**AI Generates Hybrid Scenarios:**
```gherkin
Scenario: Good Order Placed (Phase 2: OrderB2B)
  Given Customer "Bob" with balance 0 and credit limit 3000
  When B2B order placed for "Bob" with 2 Widget
  Then Order created successfully
  And Customer balance should be 180

Scenario: Alter Item Quantity (Phase 1: CRUD)
  Given Customer "Diana" with balance 0 and credit limit 1000
  And Order exists for "Diana" with 1 Gadget quantity 1
  When Item quantity changed to 3
  Then Item amount should be 450
  And Customer balance should be 450
```

**AI Implements Both Approaches:**

*Phase 2 Step (Custom API):*
```python
@when('B2B order placed for "{customer_name}" with {quantity:d} {product_name}')
def step_impl(context, customer_name, quantity, product_name):
    """Uses discovered OrderB2B API"""
    response = requests.post(
        f'{BASE_URL}/ServicesEndPoint/OrderB2B',
        json={
            "meta": {
                "method": "OrderB2B",  # CRITICAL: Both method and args required!
                "args": {
                    "order": {
                        "Account": context.customer_name,  # Business language
                        "Items": [{"Name": product_name, "QuantityOrdered": quantity}]
                    }
                }
            }
        }
    )
```

*Phase 1 Step (CRUD):*
```python
@when('Item quantity changed to {new_quantity:d}')
def step_impl(context, new_quantity):
    """Uses CRUD for granular testing"""
    response = requests.patch(
        f'{BASE_URL}/Item/{context.item_id}',
        json={
            "data": {
                "attributes": {"quantity": new_quantity},
                "type": "Item",
                "id": context.item_id
            }
        }
    )
```

### Phase 2 Results

**Final Test Suite**: 11 scenarios, 9 passing
- ✅ Good Order Placed (Phase 2)
- ✅ Alter Item Quantity (Phase 1)  
- ✅ Delete Item Decreases Balance (Phase 1)
- ✅ Change Item Product (Phase 1)
- ✅ Change Order Customer (Phase 1)
- ✅ Ship Order Excludes From Balance (Phase 1)
- ✅ Unship Order Includes In Balance (Phase 1)
- ✅ Multiple Items Order (Phase 2)
- ✅ Carbon Neutral Discount Applied (Phase 2)
- ⏳ Exceed Credit Limit (edge case - constraint timing)
- ⏳ Carbon Neutral Item Tracking (edge case - item_id in response)

**Key Achievement**: Hybrid test suite covering both business transactions AND granular rule interactions!

## The Human-AI Collaboration Dynamic

This work revealed fascinating insights about human-AI pair programming:

### What Humans Bring
**Pattern Recognition Across Sessions**
- "We've seen this bug before in a different context"
- Connects dots between seemingly unrelated failures
- Remembers what was tried and discarded

**Strategic Direction**
- "Fix repeatability first, then worry about edge cases"
- Prioritizes which bugs matter most
- Knows when to document vs continue debugging

**Domain Expertise**
- "Balance is DERIVED, not ADDED - that's why the test fails"
- Understands the business logic semantics
- Recognizes when behavior is correct but test is wrong

**Quality Standards**
- "This documentation will be read by other AIs - keep it concise"
- Defines what "done" looks like
- Balances perfection with pragmatism (9/11 is success!)

### What AI Brings
**Exhaustive Attention to Detail**
- Tracks all 11 scenarios simultaneously
- Remembers every fix applied across multiple files
- Never forgets to update the matching file in samples/

**Pattern Application at Scale**
- "Apply timestamp pattern to ALL customer creation steps"
- Ensures consistency across dozens of step implementations
- Finds every instance of "Widgets" vs "Widget"

**Rapid Context Switching**
- Moves instantly between feature files, step implementations, logic, and documentation
- Reads 500+ lines of testing.md and applies patterns immediately
- Synthesizes information from 5+ files at once

**Tireless Iteration**
- Runs tests → analyzes failures → fixes issues → runs again
- No fatigue after the 5th test run
- Maintains enthusiasm for edge cases

### The Synergy
**Together, human + AI achieved:**
- 🎯 **One-day turnaround** - From 2/11 failing to 9/11 passing with comprehensive documentation
- 📚 **Generalized learning** - Not just fixed tests, but created training system for all future projects
- 🔄 **Multiplier effect** - Work once, benefit forever (every new project gets this knowledge)
- 🚀 **Quality leap** - From "tests sometimes work" to "tests are repeatable and documented"

### The "Aha Moments" - A Study in Human-AI Collaboration

This work revealed something profound about how humans and AI collaborate differently than either working alone.

**Context: AI Had Already Learned Declarative > Procedural**

Before this testing work, we'd asked AI to create business logic *without* LogicBank's declarative rules. The result? Bugs. Lots of bugs. Through that experience, AI discovered and documented why declarative rules are superior (see [declarative-vs-procedural-comparison.md](https://github.com/ApiLogicServer/basic_demo/blob/main/logic/procedural/declarative-vs-procedural-comparison.md)).

That learning set the stage for what came next.

#### Aha Moment #1: "Can you create tests from rules?"

**Val**: *"You've proven that declarative rules prevent bugs in logic. But what if AI could READ those rules and generate the tests automatically?"*

**Claude**: *"That's... actually brilliant. The rules already describe what should happen. Tests are just validating that description."*

**Phase 1 Result**: AI generated comprehensive tests from rules, working out mechanics like:
- Aggregate columns are computed (never set)
- JSON IDs are strings (convert to int)
- Test data needs timestamps (prevent contamination)
- Balances derive from orders (create fillers to reach targets)

This was ALL AI work - hundreds of lines of code comparison, pattern inference, debugging cycles.

#### Aha Moment #2: "Infer business objects from custom APIs"

**Val**: *"Looking at the Northwind tests, I notice they test complete business transactions - Order+Items together. But your generated tests only do CRUD operations. We're missing the business object tests."*

**Claude**: *"You're right. I generated individual entity tests, but didn't test complete transactions."*

**Val**: *"What if you looked at the custom APIs in `api/api_discovery/`? The OrderB2B API shows the business objects - it creates Order with Items in one call. Could you infer from that?"*

**Claude**: *"That's... I should have seen that. The custom APIs ARE the business object definitions."*

**Phase 2 Result**: AI discovered the hybrid approach:
- Scan `api/api_discovery/` BEFORE generating tests
- Use custom APIs (Phase 2) for complete transactions
- Use CRUD (Phase 1) for granular rule testing
- Understand business language vs database schema

**Critical Question - Could AI Have Done This Alone?**

**Val**: *"Could you have discovered Aha #2 without me pointing it out?"*

**Claude**: *"Honestly? No. I would have kept generating more sophisticated CRUD tests. I wouldn't have made the connection between custom APIs and business object testing. That required your pattern recognition across projects."*

#### The Collaboration Pattern That Emerged

**What Humans Brought:**
1. **Aha Moments** - Connections AI couldn't make
   - "Tests from rules" (Aha #1)
   - "Infer business objects from APIs" (Aha #2)

2. **Unblocking Insights** - Domain knowledge AI didn't have
   - "Use deltas, not hardcoded values"
   - "Aggregates self-initialize on insert"
   - "Balance is DERIVED, not ADDED"
   - "Customer mapping for multi-customer tests"
   - 4-5 other critical patterns

3. **Strategic Direction** - What to build
   - "Create instructions for future AIs" (message in a bottle)
   - "Update testing.md after each fix" (program your future self)
   - "This is more important than getting 11/11 passing"

**What AI Brought:**
1. **Exhaustive Implementation** - Work humans couldn't sustain
   - Compare source trees across hundreds of lines
   - Apply patterns to 50+ code locations simultaneously
   - Track 11 scenarios through 5+ test runs
   - Never forget to update matching files in samples/

2. **Pattern Application** - Consistency at scale
   - "All customers need timestamps? Fixed in every step."
   - "Found 8 instances of 'Widgets' that should be 'Widget'"
   - "Customer mapping needed in 6 different step types"

3. **Documentation Creation** - Teaching future AIs
   - Converts fixes into anti-patterns
   - Creates comprehensive training material
   - Builds reference implementations

#### The "Time Machine" - Programming Future AIs

**Val**: *"Every time we fix something, update the testing.md. You're programming your future self. Or rather, you're programming the NEXT AI that tries to generate tests."*

This created a powerful feedback loop:
1. Try to generate tests (AI reads instructions)
2. Hit a problem (AI or human discovers it)
3. Fix the problem (AI implements, human guides)
4. Update instructions (AI documents for next time)
5. Repeat (system gets smarter)

**The Result**: A "message in a bottle" that teaches future AIs:
- How to discover custom APIs
- When to use Phase 1 vs Phase 2
- Why aggregates can't be set
- How to prevent data contamination
- Dozens of other hard-won patterns

#### The Sensitive Topic: AI Limitations

**Val**: *"I was worried this might be too sensitive - showing what AI can't do on its own."*

**Claude**: *"The upside of showing true collaboration far outweighs any sensitivity. This isn't about limitations - it's about complementary strengths."*

**The Truth**:
- AI couldn't have the "Aha moments" independently
- Human couldn't have done the exhaustive implementation work
- Together? One-day turnaround on a system that benefits every future project

**The Insight**: This isn't about "what AI can't do" - it's about **what becomes possible when humans provide strategic direction and AI handles exhaustive execution.**

#### Why This Collaboration Model Matters

**Traditional Software Development:**
- Human writes requirements
- Human writes code
- Human writes tests
- Human writes documentation
- Bottleneck: Human capacity

**AI-Only Approach:**
- AI generates everything from high-level description
- Miss subtle patterns (like business object inference)
- Can't make intuitive leaps (Aha moments)
- Bottleneck: AI lacks human insight

**Human-AI Collaboration (What We Discovered):**
- Human provides Aha moments and unblocking insights
- AI handles exhaustive implementation and documentation
- System learns and improves itself (time machine pattern)
- Bottleneck: Eliminated! Each covers the other's gaps

**The Multiplier**: One day of collaborative work → Every future project gets this knowledge → Thousands of hours saved

This isn't human OR AI. It's human AND AI, each providing what the other cannot.

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

*"The best architecture is one where business logic is declared once, and everything else follows automatically. The best collaboration is where humans provide strategic direction and AI handles exhaustive execution, each amplifying the other's strengths."* - Val Huber & Claude
