# Human-AI Collaboration: A Case Study in Automated Test Creation

**What happens when humans provide strategic direction and AI handles exhaustive execution**

*By Val Huber, with Claude (GitHub Copilot)*

---

## Background: Teaching AI Through "Messages in a Bottle"

API Logic Server has been using AI collaboration for years. Each created project contains training material - "messages in a bottle" - that teach future AI assistants how to work with THAT specific project:

- **GenAI creates databases** from natural language
- **GenAI creates logic** using declarative rules (after learning procedural causes bugs)
- **GenAI performs database reorganizations** while preserving logic

**The Pattern**: When Copilot works on a project, it reads the project's documentation first. So we embed training material directly in the project - instructions that teach AI how to work with this codebase.

**The Question**: What if AI could also **create tests from business rules?**

This article isn't really about test automation. It's about **how humans and AI collaborate** - a case study showing what each brings and what becomes possible together.

## The Context: Declarative Business Rules

API Logic Server projects declare business logic as rules. Here's a typical example:

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

**The Insight**: These rules already specify:
- What should be computed (formulas, sums)
- When it should happen (constraints, validations)
- What the dependencies are (Item → Order → Customer → Balance)

If AI can read these rules, why can't it generate tests that validate them?

## Aha Moment #1: "Can AI Create Tests From Rules?"

**Val**: *"You've proven that declarative rules prevent bugs in logic. But what if AI could READ those rules and generate the tests automatically?"*

**Claude**: *"That's... actually brilliant. The rules already describe what should happen. Tests are just validating that description."*

**What Happened Next**: AI went to work. Read the rules. Generated comprehensive test scenarios. Implemented the Behave steps. Hundreds of lines of code.

**The Result**: 
- 6 test scenarios automatically generated
- Tests validated aggregates, constraints, cascading updates
- One problem: Only CRUD tests (create order, create item separately)
- Missing: Business transaction tests (order WITH items together)

**The Collaboration Pattern**: Human provided the "Aha moment" - the strategic insight. AI provided exhaustive implementation - reading rules, generating scenarios, implementing steps, debugging issues.

## Aha Moment #2: "Infer Business Objects From Custom APIs"

**Val**: *"Looking at other projects, they test complete business transactions - Order+Items together. But you're only testing CRUD. Look at `api/api_discovery/order_b2b.py` - it shows the business object structure!"*

**Claude**: *"You're right. I generated individual entity tests, but didn't test complete transactions."*

**Val**: *"Could you have figured this out without me pointing it out?"*

**Claude**: *"Honestly? No. I would have kept generating more sophisticated CRUD tests. I wouldn't have made the connection between custom APIs and business object testing. That required your cross-project pattern recognition."*

**What This Revealed**: The heart of human-AI collaboration. AI couldn't make this intuitive leap - recognizing that custom APIs define business objects. But once pointed out, AI could implement it exhaustively.

**The Result**:
- Hybrid approach: Custom APIs (OrderB2B) for transactions, CRUD for granular testing
- 11 scenarios total, 9 passing
- Comprehensive training material for future AIs

## The Collaboration Model

### What This Is Really About

This isn't about "what AI can't do." It's about **what becomes possible when humans provide strategic direction and AI handles exhaustive execution.**

**Not**: Human OR AI  
**Instead**: Human AND AI

**Evidence from our session**:
- AI couldn't make the intuitive leap to custom APIs
- Human couldn't apply patterns to 50+ locations consistently  
- Together: One-day turnaround on comprehensive system

### The Pattern

1. **Human identifies root cause** - "Tests need fresh data every run"
2. **AI implements comprehensively** - Applies timestamp pattern to 50+ locations
3. **Human directs documentation** - "Update testing.md so future AIs know this"
4. **AI creates training material** - Converts fix into anti-pattern guide
5. **Together: System improves permanently** - Next AI won't make same mistake

### What Humans Brought

**Aha Moments** - Intuitive leaps AI couldn't make:
- "Can you create tests from rules?" (Aha #1)
- "Infer business objects from custom APIs" (Aha #2)

**Strategic Direction**:
- "Fix repeatability first, then worry about edge cases"
- "Create training material for future AIs" (message in a bottle)
- "9/11 passing is success, not failure" (knowing when to stop)

**Domain Expertise** - Critical insights that unblocked AI:
- "Balance is DERIVED (sum), not ADDED (accumulation)"
- "Aggregates self-initialize on insert"
- "Use customer mapping for multi-customer tests"

### What AI Brought

**Exhaustive Implementation**:
- Apply pattern to 50+ code locations simultaneously
- Track 11 scenarios through 5+ test runs
- Never forget to update matching files in samples/
- Compare source trees across hundreds of lines

**Pattern Application at Scale**:
- "All customers need timestamps? Fixed in every step."
- "Found 8 instances of 'Widgets' that should be 'Widget'"
- "Customer mapping needed in 6 different step types"

**Documentation Creation**:
- Converts fixes into anti-patterns (~1700 lines)
- Creates comprehensive training material
- Builds reference implementations

### The Synergy

**Traditional Software Development**:
- Human does everything
- Bottleneck: Human capacity

**AI-Only Approach**:
- AI generates from high-level description
- Misses subtle patterns, can't make intuitive leaps
- Bottleneck: AI lacks human insight

**Human-AI Collaboration (What We Discovered)**:
- Human provides Aha moments and strategic direction
- AI handles exhaustive implementation and documentation
- System learns and improves itself (time machine)
- **Bottleneck eliminated** - each covers the other's gaps

**The Multiplier**: One day of work → Every future project gets this knowledge → Thousands of hours saved

## The "Time Machine" - Programming Future AIs

**Val**: *"Every time we fix something, update the testing.md. You're programming your future self. Or rather, you're programming the NEXT AI that tries to generate tests."*

**The Feedback Loop**:
1. AI reads training material (testing.md)
2. AI generates tests
3. Tests reveal gaps in understanding
4. Human provides insight, AI implements fix
5. AI updates training material
6. Next AI starts smarter

**Example**: Test data contamination (customers reused across runs):

*Before fix*: AI created customers named "Bob", "Alice" - which existed from previous runs, causing balance accumulation bugs.

*Human insight*: "Tests need fresh data every run"

*AI implementation*: Applied timestamp pattern to 50+ locations:
```python
unique_name = f"Bob {int(time.time() * 1000)}"
```

*AI documentation*: Added Rule #0 to testing.md: "ALWAYS create fresh test data with timestamps"

*Result*: Future AIs will never make this mistake.

**The "Message in a Bottle"**: ~1700 lines of training material that teaches future AIs:
- How to discover custom APIs
- When to use business transactions vs CRUD
- Why aggregates can't be set directly
- How to prevent data contamination
- Dozens of other hard-won patterns

One day of collaborative work benefits every future project.

## Key Takeaways

**About Human-AI Collaboration:**

1. **Human OR AI = Limited**. Human AND AI = Breakthrough.

2. **Humans provide**: Aha moments, strategic direction, domain expertise

3. **AI provides**: Exhaustive implementation, perfect recall, tireless iteration

4. **Together**: Each covers the other's gaps. Bottleneck eliminated.

5. **The Multiplier**: One day of work → Every future project benefits → Thousands of hours saved

**About the Approach:**

1. **"Messages in a bottle"**: Embed training material in projects for future AIs

2. **"Time machine pattern"**: Fix bugs → Update docs → Program future AIs

3. **Honesty about limitations**: Builds trust, focuses on complementary strengths

4. **Focus on teaching**: Documentation more valuable than specific fixes

**The Result**: 11 test scenarios (9 passing), comprehensive training system, and a validated model for human-AI collaboration.

---

## What's Next?

With this foundation:
- **Test generation from natural language**: "Test that high-value orders require approval"
- **Coverage analysis**: "Which rules don't have tests yet?"
- **Test maintenance**: "Update tests when I change this rule"

The vision: **Declare your business logic. Get everything else automatically.**

Rules → API → UI → Tests → Documentation

All generated. All consistent. All maintainable.

That's the power of human-AI collaboration applied to declarative business rules.

---

## About This Article

This article was written collaboratively by Val Huber (human) and Claude (AI) working together in VS Code with GitHub Copilot. The testing system described was built in a single day of pair programming, demonstrating the same human-AI collaboration it describes.

**Learn more:**
- API Logic Server: https://apilogicserver.github.io
- GenAI Logic: https://github.com/ApiLogicServer/ApiLogicServer-src
- Try it: `pip install genai-logic`

---

*"The best collaboration is where humans provide strategic direction and AI handles exhaustive execution, each amplifying the other's strengths."* - Val Huber & Claude
