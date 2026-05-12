import re

with open('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/docs/training/subsystem_creation.md', 'r') as f:
    text = f.read()

rule = """
8. **Business Logic Patterns:**
   - NEVER ad-lib business logic or missing conditions that are not explicitly defined in the spec.
   - For derived flags or totals (like `clvs_eligible`), ALWAYS use declarative `Rule.formula` or `Rule.count` derivations instead of imperative `Rule.row_event` loops. `row_event` is for side effects (like sending an email or matching a record), NOT formulas.
"""

if "8. **Business Logic Patterns:**" not in text:
    text += "\n" + rule

with open('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/docs/training/subsystem_creation.md', 'w') as f:
    f.write(text)

print("subsystem_creation.md patched")
