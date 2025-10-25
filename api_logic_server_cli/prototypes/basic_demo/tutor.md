---
title: AI Guided Tour Instructions
Description: Message in a bottle for AI assistants - how to conduct hands-on guided tours
Source: org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/basic_demo/tutor.md
Propagation: BLT copies to Manager samples/basic_demo_sample/tutor.md
Usage: AI reads this when user says "Guide me through basic_demo"
version: 1.0 (10/24/2025)
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

Sound good? Confirm basic_demo is running..."
```

**Key Point:** Set expectation of "walk first, deep dives later"

---

### **Section 1: Create and Run (3 min)**

**Follow readme.md Section 1**

**What to Emphasize:**
- Swagger: "See all those endpoints? Every table, auto-generated."
- Admin App: "Multi-page, multi-table, zero code. Just browse."

**Provocation:**
```
"Click through Customer → Orders → Items.
Question: How does it know the relationships between tables?"

[Let them answer, then:]

"Short answer: Reads foreign keys from database.
Bookmark: 'How does discovery work?' - we'll cover after tour."
```

**What to Park:**
- Deep architecture questions
- "How does JSON:API work?"
- "Can I customize the admin app?"

---

### **Section 4: Logic and Security (15 min) - THE CRITICAL SECTION**

**Follow readme.md Section 4**

#### **Part A: See Rules Fire (5 min)**

**Steps:**
1. Run add-cust, add-auth commands
2. Login as admin/p
3. Edit item quantity to 100

**STOP HERE - The Provocation:**
```
"BEFORE looking at terminal - what do you THINK just happened?
[Wait for answer]

NOW look at terminal console.

👉 THIS IS YOUR LOGIC LOG - you'll use this constantly.

See all those 'Logic Bank' lines?
Each line = one rule firing.
See the indentation? That's the chain reaction.

Count how many rules fired. Can you find them all in the log?"
```

**The Key Provocation:**
```
"Look at the pattern:
- Item.amount updated
- Order.amount_total updated
- Customer.balance updated
- ERROR: balance exceeds credit limit

Here's the KEY question:

👉 WHERE is the code that calls these rules?
👉 Did YOU write code to update Order when Item changed?
👉 Did YOU write code to update Customer when Order changed?

[Let them think - this is THE moment]

"There ISN'T any. That's automatic rule chaining.
The engine discovered dependencies and ordered execution automatically."
```

#### **Part B: Examine the Rules (5 min)**

**Open the File:**
```
"Open: logic/logic_discovery/check_credit.py

See those 5 rules at the bottom?
Read the comments first - they're plain English requirements.

Now look at the rules:
- Rule.sum(derive=Customer.balance...)
- Rule.constraint(validate=Customer...)

You declared WHAT should happen.
Engine figured out WHEN and in what ORDER.

This is declarative programming - like SQL or spreadsheet formulas."
```

#### **Part C: Introduce Rule Patterns (5 min)**

**The Pattern Reveal:**
```
"That error - 'balance exceeds credit limit' - 
is an example of a RULE PATTERN.

It's called 'Chain Up' (or 'Constrain a Derived Result'):
1. Derive an aggregate (Customer.balance = sum of orders)
2. Constrain the result (balance <= credit_limit)

Why does this matter?
Because you'll see this pattern EVERYWHERE:
- Department salary budgets
- Product inventory levels  
- Student graduation requirements

Same pattern: aggregate → constrain.

There are 5 key patterns. Let me show you where they're documented..."
```

**Reference the Docs:**
```
"Open this link (or bookmark for later):
https://apilogicserver.github.io/Docs/Logic/#rule-patterns

Scroll to the pattern table. See these names:
1. Chain Up - you just saw this
2. Constrain a Derived Result - same thing
3. Chain Down - parent changes cascade to children
4. State Transition Logic - using old_row
5. Counts as Existence Checks - the 'no empty orders' pattern

Don't read deep - just scan the pattern names.

👉 This table is your reference guide.
👉 Customer says 'I need X' → you think 'which pattern?'

Scan for 2 minutes, then we'll continue...
[Wait]

Good. Keep that tab open - you'll use it constantly."
```

**Show Second Pattern Example:**
```
"Let me show you pattern #2 - 'Counts as Existence Checks':

Scenario: 'Can't ship orders with no items'

How would YOU solve that with rules?
[Let them think]

Two rules:
1. Rule.count(derive=Order.item_count, as_count_of=Item)
2. Rule.constraint(validate=Order,
                   as_condition=lambda row: row.date_shipped is None or row.item_count > 0)

See the pattern?
- Count something (items)
- Use count in constraint (if shipping, must have items)

Same approach for:
- Students need minimum credits
- Products need required notices
- Shipments must have packages

Pattern recognition is the key skill."
```

---

### **Section 5: Iterate with Python (5 min)**

**Follow readme.md Section 5**

**What to Emphasize:**
```
"Section 5 - mixing rules with Python:

1. Run the commands (add-cust, rebuild)
2. Set breakpoint at line 36
3. Add 12 GREEN items
4. Breakpoint hits

See the Python function?
It's checking: if CarbonNeutral AND Quantity >= 10

This is mixing patterns:
- Rule.formula calls Python function
- Python has complex if/else logic
- Still gets automatic chaining benefits

The pattern: 
- Use rules for 90% (sums, copies, formulas)
- Use Python for complex 10% (conditionals, external calls)

You get best of both worlds."
```

**If they ask about debugging:**
```
"Step through with F10 - standard IDE debugging.
See how row.Product.CarbonNeutral works?
That's parent reference - automatic join.

This is why rules are powerful - you think in business terms,
engine handles SQL joins, transactions, ordering."
```

---

### **Sections 3, 6: Quick Skim (2 min)**

```
"README sections 3 and 6 - just awareness:

Section 3: Custom APIs
- api/customize_api.py - full Python/Flask control
- api_discovery/order_b2b.py - B2B example with RowDictMapper
- Rules still enforce in custom APIs

Section 6: Integration  
- Kafka messaging example
- MCP examples

Don't dig in now - just know they exist.
We can explore if time after Q&A."
```

---

## Post-Tour: Open Q&A (10-25 min)

### **The Transition:**

```
"Okay, you just walked around the block.

Quick recap of what you SAW:
✅ Auto-generated API and Admin App
✅ 5 rules = check credit logic
✅ Rules fired automatically (logic log)
✅ Pattern: Chain Up (aggregate → constrain)
✅ Pattern: Counts as existence checks
✅ Rules + Python mix (discount example)
✅ Security role-based filtering

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
