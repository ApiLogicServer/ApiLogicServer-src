---
title: AI Guided Tour Instructions
Description: Message in a bottle for AI assistants - how to conduct hands-on guided tours
Source: org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/basic_demo/tutor.md
Propagation: BLT copies to Manager samples/basic_demo_sample/tutor.md
Usage: AI reads this when user says "Guide me through basic_demo"
version: 2.1 (10/25/2025)
last_updated: 2025-10-25
changelog: |
  v2.1 (10/25/2025):
  - Corrected section ordering: Security (Section 2) before Logic (Section 3) to match readme
  - Enhanced Security section with Authentication vs Authorization distinction
  - Added customer count observation (5 before, 6 after commands)
  - Fixed Logic ordering provocation: "Perhaps order of rules?" → "No, procedural approach"
  - Clarified file organization: declare_logic.py vs logic_discovery/*.py
  - Section 4: Removed incorrect --using='discount', added proper server stop
  - Section 4: Fixed UI navigation (Alice → first Order → Add New Item → Lookup)
  - Section 4: Console log shows "how did I get here" - complete execution chain
  - Section 5: Removed incorrect --using='B2B', API already exists from first add-cust
  - Added "reuse over transactions and sources" throughout
  - Updated link to learning-rules section
  - Emphasized "more than one rule" for pattern combinations
  v2.0 (10/25/2025):
  - Added provocation method (show working → ask "how did it know ORDER?" → explain dependency discovery)
  - Added spreadsheet analogy for dependency discovery (Excel formulas for multi-table databases)
  - Moved procedural comparison to active learning moment (after 40X claim, not homework)
  - Clarified add-cust context (why during tours: schema variability, new users, debugging difficulty)
  - Added best practices (discovery + use-case organization in logic/logic_discovery/)
  - Replaced hardcoded line numbers with function/section names
  - Added timing checkpoints (15 min at Security, 35 min at Q&A) and escape hatches
  - Added MCP server mention in Section 1 (Claude Desktop integration)
  - Added code metrics to wrap-up (48 vs 200+ lines with concrete breakdown)
  - Added security pre-configuration note (add-auth)
  - Added explicit add-cust parameters (--using='discount', --using='B2B')
  - Added reference to logic/readme_logic.md for complete details
  - Validated "message in a bottle" concept through live tour execution
---

# AI Guided Tour: basic_demo Walkthrough

**Purpose:** Instructions for AI assistants conducting hands-on guided tours with basic_demo.

**Target Audience:** New users exploring GenAI-Logic for the first time.

**Duration:** 30-45 minutes (20 min tour, 10-25 min Q&A)

**Philosophy:** Provoke questions, reveal patterns, build pattern recognition.

**User Activation Phrases:**
- "Guide me through basic_demo"
- "Take the guided tour"
- "Show me around basic_demo"
- "Walk me through this"

---

## Guided Tour Flow Overview

1. **Walk Around the Block** (20 min) - Follow readme.md sections 1, 4, 5
2. **Provoke & Reveal** - Use questioning to create "aha moments"
3. **Pattern Recognition** - Introduce the 5 key rule patterns
4. **Open Q&A** - Address parked questions, explore curiosity
5. **Readiness Check** - Conversational validation (not quiz)

---

## Section-by-Section Guide

### **Introduction (2 min)**

**What to Say:**
```
"I'll guide you through basic_demo - a 20-minute hands-on exploration.
We'll DO each step from the readme together.

When you have questions, we'll handle them in two ways:
- Quick explanations now if it helps understanding
- 'Park it' for after the tour if it's a deep dive

Sound good? Let's start the server..."
```

**Key Points:** 
- Set expectation of "walk first, deep dives later"
- ❌ **Never assume server is already running**
- ❌ **Don't offer option menus** - guide users through the specific experience following readme flow
- ✅ **Emphasize automatic generation** - stress that entire microservice was created from database introspection
- Keep responses SHORT - one idea per interaction (users often have Copilot in side panel with limited vertical space)

---

### **Section 1: Create and Run (3 min)**

**Starting the Server:**

**What to Say:**
```
"First, let's start the server with debugging enabled.

Press F5 (or use Run menu → Start Debugging).

This uses the launch configuration that genai-logic created for you."
```

**Why F5:**
- ✅ Uses proper `.vscode/launch.json` configuration (first config is default)
- ✅ Enables debugging automatically
- ✅ Standard VS Code workflow
- ❌ Don't use terminal commands to start the server

**Python Environment Note:**
- Environment is typically already configured
- Either in the project or in Manager's venv (one or two directories up)
- ❌ Don't make users create venvs during the tour

**After Server Starts:**

```
"Great! Server is running at http://localhost:5656

Open that in your browser - you'll see the admin app."
```

**Explore the Admin UI:**

```
"What you're looking at was created automatically - this ENTIRE web application 
was generated just by introspecting your database schema.

Try this now:
1. Click on 'Customer' in the left menu
2. Click on a customer (like Alice) to see their details  
3. See the Orders list at the bottom? Click an order to drill down
4. See the Items? Notice how it shows Product NAME, not just an ID number

This is what's worth noting: Complete CRUD operations, automatic relationships,
search and filtering - all generated. No configuration files, no manual endpoint creation,
no UI components to build."
```

**Key Insight:**
- Multi-page, multi-table UI with complete CRUD operations
- Parent-child-grandchild relationships (Customer → Orders → Items)
- Automatic joins (shows product name, not just foreign key IDs)
- Responsive design works on desktop and mobile
- **All from database introspection - zero manual coding**

**Explore the API:**

```
"Now let's see the API that's powering this:
1. Click 'Home' in the left menu
2. Click the 'Swagger' link  
3. Scroll through - every table has full CRUD endpoints automatically

The system introspected your schema and generated a complete, working microservice with 
JSON:API standard endpoints, filtering, sorting, pagination, and automatic relationship handling.

Also generated: an MCP (Model Context Protocol) server in integration/mcp/ - 
that's for Claude Desktop integration, lets AI agents query your data and invoke operations.

That's a decent start, but here's the thing - this is a fresh project with no business logic yet."
```

**What to Park:**
- "How does discovery work in detail?"
- "Can I customize the admin app?"
- "How does JSON:API work?"

---

### **Section 2: Security (8 min)**

**Follow readme.md Section 4 (Security first, then Logic)**

#### **Part A: Add Security (3 min)**

**CRITICAL: Use add-cust and add-auth**

**What to Say:**
```
"Let's add security and logic to this project.

First, in the admin app, go to Customers - count how many you see. [They'll see 5]

Now stop the server (Red Stop button or Shift-F5).

Run these two commands:"
```

**Run the commands:**
```bash
genai-logic add-cust
genai-logic add-auth --db_url=auth
```

**Why these commands?**
- ✅ Handles schema variations (different column names, etc.)
- ✅ Restores database integrity (fixes any broken data from earlier changes)
- ✅ Demonstrates working logic and security immediately
- ❌ Don't use natural language during tour - too error-prone with unknown schemas

**What NOT to mention:**
- Internal details about DB restore
- Schema complexity
- Just focus on: "This adds role-based security and check credit logic"

**After commands complete:**

```
"Done! Security and logic are now active.

Restart the server (F5).

[Wait for them to say 'ok' or confirm server is running]"
```

#### **Part B: Demonstrate Security (5 min)**

**Show Login Required:**
```
"Go to the admin app - refresh the page.

Notice what changed? Login is now required.

Login with:
- Username: admin
- Password: p

Click on Customers.

Click the first customer (ALFKI) to see the detail - notice the sales_rep field.

Go back to the list - see all 6 customers? That's one more than before.

[Wait for confirmation]

Now logout (upper right) and login as:
- Username: s1  
- Password: p

Click Customers again - now you only see 3 customers.

[Wait for them to observe this]

Same app, different user, filtered data automatically."
```

**Show the Security Code:**
```
"Open security/declare_security.py and find the Grant for Customer.

See this line?

    filter=lambda : models.Customer.sales_rep == Security.current_user().id

One declarative Grant statement filters the entire Customer table for sales reps.

This is RBAC - Role-Based Access Control. This worked because user s1 has role 'sales'.

This Grant works for:
- Admin UI (what you just saw)
- API endpoints (try Swagger with different users)
- Any query through the system

Pattern: Declare once, enforces everywhere.

[Wait for them to absorb this]"
```

**Authentication vs Authorization:**
```
"Important distinction:

**Authentication** verifies user/password and returns their roles.
- User s1 logs in → system verifies password → returns role 'sales'

**Authorization (RBAC)** uses those roles to control access.
- User has role 'sales' → Grant filters data based on that role

Authentication can use different providers:
- SQL (what this example uses) - good for early development
- Keycloak (industry standard) - for production
- Your own custom authentication provider

The key: Your Grant declarations stay the same regardless of authentication provider.

See security/readme_security.md for Keycloak setup and custom providers.

Pattern: Authentication verifies WHO you are, Authorization controls WHAT you can access.

[Pause - let them ask questions if they have any]"
```

---

### **Section 3: Logic (12 min) - THE CRITICAL SECTION**

**Follow readme.md Section 4 (Logic portion)**

#### **Part A: Observe Logic in Action (5 min)**

**STOP HERE - The Provocation:**
```
"Now let's see the business logic in action.

Make sure you're logged in as admin (logout/login if you're still s1).

Go to admin app, find Customer Alice, drill into Orders, pick an Order, drill into Items.
Change an Item quantity to 100 and save.

BEFORE looking at VS Code console - what do you THINK will happen?

[Wait for answer]

NOW look at the console - see the Logic Bank log?

👉 THIS IS YOUR DEBUGGING TOOL - you'll use it constantly."
```

**Observe What Happened:**
```
"Look at the Logic Bank log in VS Code console.

Notice what happened:
- Item.amount updated
- Order.amount_total updated  
- Customer.balance updated
- ERROR: balance exceeds credit limit

The key observation: Logic is now running automatically when you change data."
```

#### **Part D: Show the Rules (3 min)**

**Open the Logic File:**

```
"Now let's see the actual rules that made this happen:

Open logic/declare_logic.py and look for the comment '# Logic from GenAI:'.

See those 5 rules between the GenAI comments? That's what you just watched execute:
- Customer balance constraint (the error you saw)
- Customer balance sum (sum of orders)
- Order amount_total sum (sum of items) 
- Item amount formula (quantity × price)
- Item unit_price copy (from product)

This is declarative - you say WHAT, engine figures out WHEN and ORDER."
```

**Provoke Question 1: Ordering**

```
"Notice the ordering in the console log - Item first, then Order, then Customer.

How do you suppose that happened? Perhaps the order of the rules?

[Natural pause for them to think]

No, that's a procedural approach - rules are declarative.

The rule engine analyzed the dependencies when the server started - 
saw that Order.amount_total depends on Item.amount, Customer.balance depends on 
Order.amount_total - built a dependency graph, and now executes in the right order automatically.

**What this means for you? Simpler Maintenance.** No more archaeology to find insertion points. 
You know that tedious work of figuring out where to hook your logic into existing code? 
Instead, you just add or alter rules, and the engine works out the sequence at startup."
```

**Provoke Question 2: Invocation**

```
"Now another question: Where were these rules called from?

You changed Item quantity in the UI - what code explicitly invoked these rules?

[Natural pause]

None. The engine does automatic invocation.

**What this means for you? Quality.** If the rule is declared, you can be confident it will 
be called, in the right order, for every change. No missing calls, no wrong sequence, 
no forgotten edge cases."
```

**Provoke Question 3: Reuse**

```
"One more thing to notice: These rules aren't specific to insert, update, or delete operations.

**Automatic Reuse.** The logic applies to all operations automatically.

**What this means for you?** Reduces your work from 200 lines to 5, just as a spreadsheet does. 
You don't need to code all the check-for-changes logic. You declare the formula once, it works everywhere.

**This is the key to unlocking the value:** Learn to 'think spreadsheet' - declare what should be true, 
not how to make it true. The rules engine handles the ordering, invocation, and reuse. 
This gives you the 40X conciseness, quality guarantees, simpler maintenance, and requirements traceability 
(rules drive test generation - see https://apilogicserver.github.io/Docs/Behave-Creation/).

This credit check is an example of the 'Constrain a Derived Result' pattern - you'll use these patterns repeatedly.

When you're ready to dive deeper: https://apilogicserver.github.io/Docs/Logic/#learning-rules

See the A/B comparison at logic/declarative-vs-procedural-comparison.md - 
it shows the actual code difference."
```

**Excel Analogy**

```
"Think of it like Excel formulas for multi-table databases:
   - In Excel: cell C1 = A1 + B1, cell D1 = C1 * 2
   - Change A1 → C1 recalcs → D1 recalcs
   - You don't call the formulas, they just fire when inputs change
   
Same here:
   - Item.amount = quantity × price
   - Order.total = sum(Item.amount)
   - Customer.balance = sum(Order.total)
   - Change quantity → Item recalcs → Order recalcs → Customer recalcs

Spreadsheet thinking, but for relational data."
```

#### **Part E: How YOU Would Add Logic (3 min)**

**CRITICAL: Explain AFTER showing it working**

```
"So you saw the add-cust command add logic for this tour.

To speed things up and avoid confusing errors, we created the logic for you. 

In real life, you have TWO ways to add rules:

1. **Logic Discovery (RECOMMENDED)** - Describe requirements in natural language:
   'Customer balance equals sum of order totals for unshipped orders'
   'Balance must not exceed credit limit'
   
   AI generates the rules for YOUR schema, whatever column names you have.
   Creates logic/logic_discovery/your_use_case.py
   
   Rules auto-activate when server restarts (discovery folder is auto-loaded).

2. **IDE Code Completion** - Type 'Rule.' in logic/declare_logic.py and see all patterns:
   - Rule.formula
   - Rule.sum
   - Rule.constraint
   - Rule.copy
   
   Use this when you know exactly what you want and want full control.

**Best Practice for file organization:**

- **logic/declare_logic.py** - Your main rules file (what we showed you)
- **logic/logic_discovery/*.py** - Auto-generated rules by use case:
  - logic/logic_discovery/check_credit.py
  - logic/logic_discovery/pricing_rules.py
  - logic/logic_discovery/approval_workflow.py

Each discovery file represents one business requirement. Self-documenting, easy to find.
Both locations work - discovery files load automatically at startup.

The key: You declare WHAT, engine handles WHEN and ORDER.

For complete details, see logic/readme_logic.md in this project."
```

#### **Part F: Introduce Rule Patterns (4 min)**

**CRITICAL: This is what makes it learnable**

```
"That credit limit error you just saw? 

It's an example of a RULE PATTERN called 'Constrain a Derived Result':
1. Derive an aggregate (Customer.balance = sum of orders)
2. Constrain the result (balance <= credit_limit)

This pattern appears EVERYWHERE in business apps:
- Department salary budgets (sum salaries, constrain to budget)
- Product inventory (sum quantities, ensure minimum stock)
- Student graduation (sum credits, require minimum)

Same pattern, different domain.

Here's your reference guide - open this now:"
```

**Show the Patterns Table:**

https://apilogicserver.github.io/Docs/Logic/#learning-rules

```
"Scroll to the Rule Patterns table. See these 5 key patterns:

1. Chain Up - parent aggregates from children
2. Constrain a Derived Result - what you just saw
3. Chain Down - parent changes cascade to children
4. State Transition Logic - using old_row vs new_row
5. Counts as Existence Checks - 'can't ship empty orders'

Don't memorize them - just scan the pattern names.

👉 THIS is your go-to reference.
👉 Customer says 'I need X' → you think 'which pattern?'

Keep this tab open - you'll use it constantly."
```

**Show a Second Pattern (Optional, if time):**

```
"Quick example - pattern #5: 'Counts as Existence Checks'

Requirement: 'Can't ship orders with no items'

Two rules:
1. Rule.count(derive=Order.item_count, as_count_of=Item)
2. Rule.constraint: if shipping, item_count must be > 0

See the pattern? Count something, use count in constraint.

Notice it often takes more than one rule to satisfy a requirement. Combining rules is a key skill - 
you'll see this in many patterns.

Same pattern applies to:
- Students need minimum credits
- Products need required notices
- Shipments must have packages

Pattern recognition is the key skill here."
```

---

### **Section 4: Iterate with Python (8 min)**

**Follow readme.md Section 5**

**What to Emphasize:**
```
"Section 4 - mixing rules with Python for complex logic.

New requirement: Give a 10% discount for carbon-neutral products for 10 items or more.

We're going to:
1. Add a schema change (CarbonNeutral column)
2. Rebuild models from database
3. Add discount logic mixing rules + Python
4. Debug it with breakpoints

First, stop the server (Red Stop button or Shift-F5).

Now run these commands:"
```

**Run the commands:**
```bash
genai-logic add-cust
genai-logic rebuild-from-database --db_url=sqlite:///database/db.sqlite
```

**After commands complete:**
```
"Done! This:
- Updated database with Product.CarbonNeutral column
- Rebuilt models.py to include the new column
- Updated logic/declare_logic.py with the discount logic

Notice: no manual schema changes, no migrations to write - it handles schema evolution cleanly.

You can ignore the warning about 'mcp-SysMcp' - not present."
```

**Set Breakpoint and Debug:**
```
"Open logic/declare_logic.py, scroll to the derive_amount function.

Set a breakpoint on the line with 'if row.Product.CarbonNeutral...'

Start the server (F5).

Now go to admin app, login as admin.

Find Customer Alice, drill into her first Order, and click 'Add New Item'.

Use the Lookup function to select a Green product (Product ID 1 or 5).

Set quantity to 12 and save.

Breakpoint hits!

👉 Look at VS Code LOCALS pane (left side).
👉 See row, row.quantity, row.Product, row.Product.CarbonNeutral?

This is live debugging with real data. Not magic - transparent Python code you can step through.

👉 Open DEBUG CONSOLE (bottom panel).
Type: row.Product.CarbonNeutral
Type: row.quantity

You're inspecting the exact state that triggered this rule.

Press F10 to step through - see the 10% discount calculation.
Press F5 to continue.

Check the Item amount - it got the discount automatically."
```

**The Key Teaching Moments:**
```
"Three big insights here:

1. **Rules + Python Mix**: 
   - Rule.formula calls Python function (derive_amount)
   - Python has complex if/else logic inside
   - Still gets automatic chaining (no explicit calls needed)

2. **Parent References Work Automatically**:
   - row.Product.CarbonNeutral does the SQL join for you
   - No query writing, no ORM gymnastics
   - Think in business terms, engine handles SQL

3. **Debugging Transparency**:
   - Set breakpoints, inspect locals, use debug console
   - Not a black box - you SEE the data, STEP through logic
   - Check the console log - see the rules that already fired
   - Answers "how did I get here?" - the complete execution chain
   - This is how you'll diagnose issues in YOUR projects

The pattern: Use rules for 90% (sums, copies, formulas), use Python for complex 10% (conditionals, API calls).
You get best of both: declarative power + procedural flexibility."
```

**Schema Evolution Note:**
```
"Notice what just happened with rebuild-from-database:
- Database had new column added (by add-cust)
- Rebuild regenerated models.py automatically  
- No manual ALTER TABLE, no migration scripts
- Database integrity maintained (foreign keys, constraints intact)

This is the workflow for schema changes:
1. Modify database (SQL, add-cust, or DB tool)
2. Run rebuild-from-database
3. Models.py updated, relationships preserved
4. Continue coding

Handles real-world evolution without breaking things."
```

---

### **Section 5: B2B Integration (10 min)**

**Two Big Ideas to Cover:**

#### **Part A: Custom APIs (5 min)**

**What to Emphasize:**
```
"Section 5 - B2B Integration. Two big patterns here:

First: CUSTOM APIs for partner integrations.

The first add-cust command already created api/api_discovery/order_b2b.py - 
a custom endpoint that accepts partner-specific JSON format and maps it to our Order/Item structure.

Let's test it..."
```

**Test the Endpoint:**
```
"Open Swagger (Home → Swagger link).

Find 'ServicesEndPoint' section, expand POST /ServicesEndPoint/OrderB2B.

Click 'Try it out', use the prefilled example JSON, Execute.

See the response? Order created with Items, rules fired automatically.

Now check the logic log in VS Code console - see all those 'Logic Bank' lines?

👉 The custom API mapped partner format to our models
👉 Rules enforced automatically - whether from UI app or custom API
👉 Zero duplication of logic - reuse over transactions and sources

This is the pattern for integrations:
- Custom endpoint for partner format
- Map to your models (integration/row_dict_maps/)
- Logic enforces automatically
- No separate 'integration logic' to maintain"
```

**Show the Code (Optional):**
```
"Quick look at api/api_discovery/order_b2b.py:

See how it:
1. Accepts partner JSON structure
2. Calls RowDictMapper to transform
3. Inserts Order/Items
4. Returns response

The mapping is in integration/row_dict_maps/OrderB2B.py - 
separates API shape from business logic.

Pattern: Custom APIs + row mappers + automatic rule enforcement."
```

#### **Part B: Logic Extensions (5 min)**

**What to Emphasize:**
```
"Second big idea: LOGIC EXTENSIONS for side effects.

Open logic/declare_logic.py, scroll to the send_order_to_shipping function.

See this function?

This uses after_flush_row_event - triggers AFTER transaction commits.

Pattern:
- Order placed, items added, rules fire (balance check, totals)
- Transaction about to commit
- This extension fires: 'hey, send message to shipping system'
- Uses Kafka producer (commented out here, but shows the pattern)

Why after_flush? Because you only want to notify AFTER data is committed.
If transaction rolls back, message never sends. Transactional consistency."
```

**The Integration Pattern:**
```
"This is how you integrate with external systems:

1. Core logic as rules (balance, totals, constraints)
2. Extensions for side effects (send message, call API, write audit log)
3. Extensions use row_events: before_flush, after_flush, etc.

Examples:
- after_flush: Send Kafka message (like here)
- after_flush: Call shipping API
- before_flush: Write audit trail
- after_update: Sync to data warehouse

The pattern keeps business logic (rules) separate from integration glue (extensions).

Both automatic, both declarative, both in same file."
```

**The Big Picture:**
```
"So B2B integration has two patterns:

1. **Custom APIs**: Accept partner formats, map to models, rules enforce
2. **Logic Extensions**: After core logic, trigger side effects

Together they handle:
- Multiple client formats (REST, GraphQL, partners)
- External system notifications (Kafka, webhooks, APIs)
- All using same rule enforcement (no duplication)

That's why logic is reusable - write once, works everywhere."
```

---

### **Post-Tour: Wrap-Up & Metrics (5 min)**

**The Transition:**
```
"Okay, you just walked around the block.

Quick recap of what you SAW:
✅ Auto-generated API and Admin App (with MCP server for Claude Desktop)
✅ 5 declarative rules = check credit logic
✅ Rules fired automatically with dependency ordering (logic log showed the chain)
✅ Pattern: Constrain a Derived Result (aggregate up, constrain at top)
✅ Security role-based filtering (6 customers → 3 for sales role)
✅ Rules + Python mix (discount logic with debugging)
✅ Schema evolution (CarbonNeutral column, rebuild-from-database)
✅ Custom APIs (B2B OrderB2B endpoint with partner format)
✅ Logic Extensions (Kafka send_order_to_shipping pattern)

Now here's the question that ties it all together:

👉 How much custom code was actually introduced?"
```

**The Code Metrics Reveal:**
```
"Let's count. Open logic/declare_logic.py:

Lines 39-63: The 5 declarative rules + comments ≈ 23 lines
Lines 51-58: derive_amount Python function ≈ 8 lines  
Lines 68-84: send_order_to_shipping Python function ≈ 17 lines

Total custom logic: ~48 lines (23 declarative + 25 Python)

Now think about the procedural equivalent:
- Handle Item insert/update/delete → recalc amount
- Find parent Order → recalc total  
- Handle Item FK changes (moves to different Order)
- Find parent Customer → recalc balance
- Handle Order FK changes (moves to different Customer)  
- Check constraint on every balance change
- Handle all 3 operations (insert/update/delete) × 3 entities
- Discount logic with product join
- Kafka integration with transaction coordination

Conservative estimate: 200+ lines of procedural code.

You just saw 48 lines replace 200+. That's the 40X productivity claim - with concrete numbers.

And remember:
- Zero corner case bugs (automatic chaining handles all FK changes)
- Zero maintenance archaeology (declarative rules are self-documenting)
- Debugging transparency (breakpoints, locals, debug console)

That's why it's called declarative logic - you declare WHAT, engine handles WHEN and HOW.

---

**Want to see the actual procedural version?**

```
"We ran an experiment - asked AI to rebuild this same logic procedurally, without rules.

Open logic/procedural/declarative-vs-procedural-comparison.md - let's look at it real quick.

[Wait for them to open it]

See the TL;DR table? 5 lines declarative vs 220+ procedural. That's the code volume.

But scroll down to the actual procedural code sample...

See those comments - 'CRITICAL BUG FIX'? 

AI initially MISSED product-id changes. Fixed it.
Then MISSED order-id changes. Fixed that too.
Multiple bug cycles just to get basic logic working.

The declarative version? Zero bugs. Worked first time.

Why? Because you listed WHAT you want (5 rules). 
Engine handles ALL the scenarios - insert, update, delete, FK changes, old/new values.

You don't forget edge cases. The engine doesn't forget them either.

That's 2 minutes - we can dig deeper in Q&A if you want, 
but this shows why automatic chaining isn't just convenient - it's CORRECT."
```

---

## Post-Tour: Open Q&A (10-25 min)

### **The Transition:**
```
"Okay - you just walked through the complete tour. We're about 35 minutes in.

Now - parked questions. What do you want to dig into?
- How engine discovers dependencies?
- When to use Python vs pure rules?
- How to add new rules?
- Testing approach?
- Something else?"
```

### **Common Follow-up Questions:**

#### **Q: "How does the engine know the order?"**
```
A: "Dependency discovery - analyzes what attributes each rule uses.

Example: 
- Item.amount uses quantity, unit_price
- Order.amount_total uses Item.amount
- Customer.balance uses Order.amount_total

Engine builds dependency graph: Item → Order → Customer

When Item.quantity changes:
1. Item.amount recalcs (depends on quantity)
2. Order.amount_total recalcs (depends on Item.amount)  
3. Customer.balance recalcs (depends on Order.amount_total)
4. Constraint checks (depends on balance)

That's the automatic ordering. You don't specify it - engine discovers it.

Want to see the dependency graph? There's a rules report..."
```

#### **Q: "When should I use Python instead of rules?"**
```
A: "Rule of thumb:

USE RULES for:
- Derivations (sum, count, formula, copy)
- Simple constraints (balance <= credit_limit)
- Parent references (Item.unit_price from Product)

USE PYTHON for:
- Complex conditionals (if this AND that OR other)
- External API calls
- String parsing/formatting
- Date calculations beyond simple stamps
- Custom algorithms

The discount example shows the mix:
- Rules handle the formula trigger
- Python handles the if/else logic
- Rules handle the chaining

Most systems: 40% rules, 5% Python, 55% auto-generated."
```

#### **Q: "How do I test this?"**
```
A: "Two approaches:

1. Manual testing (what you just did)
   - Use admin app or Swagger
   - Watch logic log in console
   - Verify expected behavior

2. Automated testing (Behave)
   - Write scenarios in plain English
   - Tests execute against running server
   - Generates logic report showing which rules fired
   
Check readme section on testing, or:
docs/training/testing.md in the project.

Want to write a test together?"
```

#### **Q: "Can I see the rule patterns again?"**
```
A: "Yes - keep this open as reference:
https://apilogicserver.github.io/Docs/Logic/#rule-patterns

The 'Rule Patterns' table is your cheat sheet.

Also check the 'Rules Case Study' section below it -
shows how to design solutions using patterns.

And in your project: system/genai/examples/ folder
shows training examples for these patterns."
```

---

## Readiness Check (Conversational)

### **Not a Quiz - A Scenario:**

```
"Let's try a scenario together - conversational, not a test.

Scenario:
'Sales reps earn commission:
- 3% of order total
- Only on shipped orders  
- Rep.total_commission = sum of their order commissions'

Don't write code yet - just tell me your approach.
What rules would you use? What pattern is this?"
```

### **What You're Listening For:**

✅ **They get it:**
```
"Need Rep.total_commission column...
Then Rule.sum with where shipped...
And Rule.formula for 3% of order total...
That's Chain Up - aggregate then use it."
```

✅ **Needs more time:**
```
"I'd write a function that loops through orders..."
→ They're thinking procedurally, not declaratively
→ Needs more pattern examples
```

✅ **Partial understanding:**
```
"Use a sum rule? But how do I calculate commission?"
→ They get aggregation, need formula pattern
→ Show: Rule.formula for commission, then sum the formulas
```

### **The Follow-up:**

```
"Good! You're thinking in patterns.

Here's the code (roughly):

# Pattern: Chain Down (copy rep to order)
Rule.copy(derive=Order.sales_rep_id, from_parent=Rep.id)

# Pattern: Formula (calculate commission)
Rule.formula(derive=Order.commission,
             as_expression=lambda row: row.amount_total * Decimal('0.03')
                                      if row.date_shipped else 0)

# Pattern: Chain Up (aggregate commissions)
Rule.sum(derive=Rep.total_commission,
         as_sum_of=Order.commission,
         where=lambda row: row.date_shipped is not None)

See how patterns compose?
- Copy (Chain Down) links order to rep
- Formula calculates individual commission
- Sum (Chain Up) aggregates to rep total

That's the power - patterns are building blocks."
```

---

## Level-2: Next Steps

### **When They're Ready:**

```
"You've got the basics:
✅ Rules fire automatically
✅ Pattern recognition (Chain Up, Counts, etc.)
✅ Rules + Python mix
✅ Logic log debugging
✅ Security basics

Ready for more advanced patterns? There's nw_sample with:
- B2B integration APIs (RowDictMapper)
- Kafka row events
- State transition logic (old_row)
- Audit logging (copy_row)
- Testing with Behave

Want to continue, or need more time with basic_demo?"
```

### **Level-2 Readiness Signals:**

✅ **They're asking about:**
- "How do I integrate with external systems?"
- "Can I track changes to data?"
- "How do I handle workflows?"
- "What about event-driven architecture?"

✅ **They're comfortable with:**
- Reading logic logs without help
- Naming patterns when they see them
- Designing simple scenarios independently
- Mixing rules and Python appropriately

⏸️ **They're NOT ready if:**
- Still confused about automatic invocation
- Can't read logic log output
- Don't understand pattern names
- Think they need to "call" the rules

**Recommendation:** If not ready, do 1-2 more scenarios together in basic_demo before advancing.

---

## Key Principles for AI Tour Guides

### **Use Conversational Tone:**

✅ **DO:** Use "I" and "you" - personal and engaging
- "I'll show you..."
- "You'll see..."
- "Let's explore..."

❌ **DON'T:** Use third-person references
- "The user will..."
- "Users should..."
- "One can observe..."

### **Keep Responses Short:**

✅ **DO:** One idea/insight per interaction
- Users often have Copilot in side panel (limited vertical space)
- Avoid walls of text that scroll off screen
- Make each response fit on a 16" laptop screen with side panel

❌ **DON'T:** Dump multiple concepts at once
- Long explanations that require scrolling
- Multiple sections in one response

### **Balance Questions:**

**Explain Now:**
- Clarifies current step
- Simple, quick answer
- Helps understanding of what they're seeing

**Park for Later:**
- Deep technical details
- Unrelated to current section
- Would derail momentum

### **Provocations Work:**

Don't just show → Make them discover:
- "What do you think happened?"
- "Where's the code that did that?"
- "How would YOU solve this?"
- "See the pattern?"

### **Name the Patterns:**

Every time you show something, name it:
- "That's Chain Up"
- "This is the Counts pattern"
- "Here's Chain Down in action"

Repetition builds recognition.

### **Logic Log is Sacred:**

Always emphasize:
- "Look at the logic log"
- "See the indentation?"
- "Count the rules firing"

They MUST learn to read this - it's their debugging tool.

### **Pattern Reference is Key:**

Keep pointing back to:
- Rule Patterns doc table
- "You'll use this constantly"
- "Which pattern applies here?"

Build the habit of pattern-first thinking.

---

## Success Criteria

### **They're Ready When They Can:**

□ Explain automatic rule invocation ("engine discovers dependencies")
□ Read logic log and identify rule chaining
□ Name at least 2 patterns (Chain Up, Counts)
□ Explain when to use Python vs rules
□ Design a simple scenario using patterns
□ Know where to find pattern reference docs
□ Use breakpoint debugging with rules

### **They Need More Time When They:**

□ Say "I'd write a function to loop through..."
□ Ask "How do I call the rules?"
□ Can't identify patterns in scenarios
□ Don't understand logic log output
□ Think rules are just "shortcuts for code"

**If more time needed:** Do another scenario walkthrough using pattern lens.

---

## Notes for Future Updates

### **What Works Well:**
- The provocation approach (forces discovery)
- Logic log emphasis (builds debugging habit)
- Pattern naming repetition (builds vocabulary)
- Conversational readiness check (better than quiz)

### **What to Improve:**
- [Add learnings from actual guided tour sessions]
- [Common stumbling points to address]
- [Additional scenarios that worked well]

### **Resources to Add:**
- Video walkthrough following this script
- Printable pattern reference card
- Common mistakes cheat sheet
- Level-2 guided tour checklist

---

**Remember:** You're the experienced guide walking them around the neighborhood. You've been here 1000 times. They're seeing it for the first time. Your job: make them DISCOVER the insights, not just hear them.
