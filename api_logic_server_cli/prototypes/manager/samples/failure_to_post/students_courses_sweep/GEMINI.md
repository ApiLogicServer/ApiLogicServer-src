# Antigravity Context — ApiLogicServer Project

This project was built with ApiLogicServer / GenAI-Logic and includes extensive Context Engineering (CE) for AI-assisted development.

## Context Engineering References

When implementing rules, APIs, services, or tests:
1. **Project Rules & Workflow**: Read [.github/copilot-instructions.md](.github/copilot-instructions.md)
2. **LogicBank Rule Syntax**: Read [docs/training/logic_bank_api.md](docs/training/logic_bank_api.md)
3. **Design Patterns**: Read [docs/training/logic_bank_patterns.md](docs/training/logic_bank_patterns.md) and [docs/training/RequestObjectPattern.md](docs/training/RequestObjectPattern.md)
4. **Testing Rules**: Read [docs/training/testing.md](docs/training/testing.md)

## Key Rules
- **Rule Engine**: Business logic is declared declaratively via LogicBank. Never write procedural handlers for multi-table derivations/constraints that LogicBank can automate.
- **Logic Files**: Place use-case logic in `logic/logic_discovery/<use_case_name>.py` (not `logic/declare_logic.py`, which is a stub).

