#!/bin/bash

# Sync training files from basic_demo_2 to dev source templates
# Run this after updating testing.md or .copilot-instructions.md

echo "Syncing training files to dev source..."
echo ""

# 1. Update the base template (trains all new projects)
echo "1. Updating base template (api_logic_server_cli/prototypes/base)..."
cp basic_demo_2/docs/training/testing.md \
   /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/docs/training/testing.md

cp basic_demo_2/.github/.copilot-instructions.md \
   /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/.github/.copilot-instructions.md

echo "   ✅ Base template updated"
echo ""

# 2. Update the Manager's reference sample (for basic_demo examples)
echo "2. Updating Manager reference sample (prototypes/manager/samples/basic_demo_sample)..."
cp basic_demo_2/docs/training/testing.md \
   /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager/samples/basic_demo_sample/docs/training/testing.md

cp basic_demo_2/.github/.copilot-instructions.md \
   /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/manager/samples/basic_demo_sample/.github/.copilot-instructions.md

echo "   ✅ Manager reference sample updated"
echo ""

echo "✅ Sync complete!"
echo ""
echo "Files synced:"
echo "  - docs/training/testing.md (593 lines)"
echo "  - .github/.copilot-instructions.md (740 lines)"
echo ""
echo "Next steps:"
echo "  1. cd /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src"
echo "  2. git status  # Review changes"
echo "  3. git diff    # Check specific changes"
echo "  4. git commit -am 'Updated training: Rule #0.5 (step ordering) + documentation consolidation'"
echo "  5. git push"
