# Antigravity Context — ApiLogicServer Project

This project was built with ApiLogicServer / GenAI-Logic and includes extensive Context Engineering (CE) for AI-assisted development.

## Mandatory Session Bootstrap & Context Engineering References

**UNCONDITIONAL BOOTSTRAP RULE**: On the very first turn of every session — before answering ANY question or running any workflow — silently read [.github/copilot-instructions.md](.github/copilot-instructions.md) in full and adhere to all of its protocols.

When implementing rules, APIs, services, or tests, also consult:
1. **Project Rules & Workflow**: [.github/copilot-instructions.md](.github/copilot-instructions.md) (read at session start)
2. **LogicBank Rule Syntax**: [docs/training/logic_bank_api.md](docs/training/logic_bank_api.md)
3. **Design Patterns**: [docs/training/logic_bank_patterns.md](docs/training/logic_bank_patterns.md) and [docs/training/RequestObjectPattern.md](docs/training/RequestObjectPattern.md)
4. **Testing Rules**: [docs/training/testing.md](docs/training/testing.md)

## Key Rules
- **Rule Engine**: Business logic is declared declaratively via LogicBank. Never write procedural handlers for multi-table derivations/constraints that LogicBank can automate.
- **Logic Files**: Place use-case logic in `logic/logic_discovery/<use_case_name>.py` (not `logic/declare_logic.py`, which is a stub).

