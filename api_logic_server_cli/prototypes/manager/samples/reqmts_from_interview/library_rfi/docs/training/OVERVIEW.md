# Training Documentation Overview

## Purpose

This folder contains **generic, reusable training materials** for ApiLogicServer projects with GenAI integration.

## Critical Principle

**⚠️ ALL FILES IN THIS FOLDER MUST BE PROJECT-AGNOSTIC**

- ✅ Generic patterns that apply to ANY ApiLogicServer project
- ✅ Universal LogicBank API documentation
- ✅ Framework-level integration patterns
- ❌ **NEVER include project-specific details** (file names, use cases, workflows)
- ❌ **NEVER reference project-specific files** (like readme_probabilistic.md)

## Intended Use

These training files are:
1. **Read by AI assistants** (GitHub Copilot, ChatGPT) via `.github/.copilot-instructions.md`
2. **Copied to new projects** when creating similar systems
3. **Maintained centrally** and propagated across projects

## File Organization

- **`*.prompt`** - API documentation and pattern libraries for AI consumption
- **`*_guide.md`** - Human-readable implementation guides
- **`template_*.py`** - Working code examples (generic patterns only)
- **`testing.md`** - Universal testing patterns and conventions
- **`README.md`** - Navigation and file descriptions

## Adding New Content

When adding training materials:

1. **Ask: "Does this apply to ALL projects?"**
   - If YES → Add here
   - If NO → Keep in project root (e.g., `readme_*.md`)

2. **Use generic examples:**
   - ✅ "Customer/Order/Item" domain
   - ✅ "SysXxxReq" audit table pattern
   - ❌ Specific product names, table names, or use cases

3. **Remove project context:**
   - No mentions of "PDL project"
   - No references to project-specific scripts
   - No project-specific file paths

## Maintenance

This folder should be **stable and rarely changed**. Updates typically come from:
- LogicBank API changes
- New universal patterns discovered
- Framework architecture improvements

**NOT from:**
- Project-specific implementations
- One-off use cases
- Debugging specific projects

---

**Remember:** If you're describing how YOUR project works, it doesn't belong here.
