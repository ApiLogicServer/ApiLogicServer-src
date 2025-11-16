# Training Documentation Structure

This directory contains training materials for ApiLogicServer with GenAI integration.

## Documentation Organization

### Universal Framework Patterns
**File:** `genai_logic_patterns.md`  
**Scope:** Framework-level patterns applicable to ANY ApiLogicServer project using AI  
**Topics:**
- Critical imports (Rule vs RuleBank)
- LogicBank triggered insert pattern
- AI value computation architecture
- Auto-discovery system
- Formula patterns with AI
- Event handler patterns
- Testing patterns
- Error handling
- Best practices

**Use this when:** You need to understand core GenAI-LogicBank integration patterns regardless of project.

---

### Probabilistic Logic Implementation
**File:** `probabilistic_logic_guide.md`  
**Scope:** Implementing probabilistic (AI-powered) business rules  
**Topics:**
- Conditional formulas (deterministic vs AI)
- Request Pattern for audit trails
- Integration with deterministic rules
- Execution flow
- Testing probabilistic rules
- Common implementation patterns
- Troubleshooting AI integration

**Use this when:** You're implementing AI-powered rules in your project.

---

### Code Templates
**File:** `template_probabilistic_rules.py`  
**Scope:** Working code examples for copy/paste  
**Topics:**
- Complete working implementation
- Deterministic rules
- Conditional formula with AI
- Reusable AI handler pattern
- Event handler registration

**Use this when:** You need code to copy and adapt for your project.

---

## Quick Navigation

**I want to...**

- **Understand LogicBank + AI patterns** → `genai_logic_patterns.md`
- **Implement AI rules in my project** → `probabilistic_logic_guide.md`
- **Copy working code** → `template_probabilistic_rules.py`
- **Fix import errors** → `genai_logic_patterns.md` (Section 1)
- **Fix "Session is already flushing"** → `genai_logic_patterns.md` (Section 2)
- **Add audit trails** → `probabilistic_logic_guide.md` (Section 2)
- **Test AI rules** → `probabilistic_logic_guide.md` (Section 4)

---

## Other Training Materials

This directory also contains:

- **API Documentation:**
  - `logic_bank_api.prompt` - LogicBank API reference
  - `logic_bank_api_probabilistic.prompt` - Probabilistic extensions
  - `logic_bank_patterns.prompt` - Pattern library

- **Admin App Documentation:**
  - `admin_app_1_context.prompt.md` - Admin app context
  - `admin_app_2_functionality.prompt.md` - Functionality guide
  - `admin_app_3_architecture.prompt.md` - Architecture overview
  - `react_map.prompt.md` - React component mapping
  - `react_tree.prompt.md` - Component tree structure

- **Integration Guides:**
  - `MCP_Copilot_Integration.md` - Model Context Protocol integration
  - `testing.md` - Testing strategies

- **Refactoring History:**
  - `REFACTORING_SUMMARY.md` - Summary of architecture changes
  - `REFACTORING_v1.5_analysis.md` - v1.5 analysis
  - `UPDATES_v1.4.md` - v1.4 updates

- **Examples:**
  - `logic_example.py` - Example logic implementations

---

## Contributing

When adding new training materials:

1. **Choose the right file:**
   - Universal patterns → `genai_logic_patterns.md`
   - Implementation patterns → `probabilistic_logic_guide.md`
   - Project-specific → Keep outside `docs/training/` folder

2. **Keep separation clear:**
   - Don't mix framework patterns with project specifics
   - Don't duplicate content across files
   - Use cross-references when needed

3. **Update this README:**
   - Add new files to appropriate section
   - Update quick navigation if needed

4. **Provide examples:**
   - Include code examples
   - Show both correct and incorrect patterns
   - Explain why patterns work

---

## Maintenance

**Regular reviews:**
- Check for outdated information
- Consolidate duplicate content
- Update cross-references
- Add new troubleshooting cases

**Version updates:**
- Update examples when LogicBank API changes
- Document breaking changes
- Provide migration guides

**Feedback:**
- Collect common questions
- Add FAQ sections
- Improve unclear explanations
