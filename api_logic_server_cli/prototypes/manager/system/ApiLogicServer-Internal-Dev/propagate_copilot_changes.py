#!/usr/bin/env python3
"""
Propagate Copilot Instructions Changes from BLT Test Projects to Source Prototypes

Usage:
    cd /Users/val/dev/ApiLogicServer/ApiLogicServer-dev
    python3 build_and_test/ApiLogicServer/system/ApiLogicServer-Internal-Dev/propagate_copilot_changes.py

Purpose:
    When you edit .copilot-instructions.md in test projects (tests/ApiLogicProject),
    this script copies those changes back to the source prototype 
    (org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/).
    
    This ensures changes propagate to future project creations.
"""

import re
import sys
from pathlib import Path

def propagate_copilot_instructions():
    """Copy changes from BLT test project to source prototype"""
    
    base_dir = Path('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev')
    
    # Source files
    test_file = base_dir / 'build_and_test/ApiLogicServer/tests/ApiLogicProject/.github/.copilot-instructions.md'
    source_file = base_dir / 'org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/.github/.copilot-instructions.md'
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
        
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        return False
    
    # Read test file
    with open(test_file, 'r') as f:
        test_content = f.read()
    
    # Read source file
    with open(source_file, 'r') as f:
        source_content = f.read()
    
    # Extract sections to copy (between title and "Key Technical Points")
    # This captures additions like "What You Get" and "What You Do"
    match = re.search(
        r'(# GitHub Copilot Instructions.*?\n---\n)(.*?)(---\n\n## 🔑 Key Technical Points)',
        test_content,
        re.DOTALL
    )
    
    if not match:
        print("❌ Could not find sections to copy in test file")
        return False
    
    new_sections = match.group(2)
    
    # Replace in source file
    updated_content = re.sub(
        r'(# GitHub Copilot Instructions.*?\n---\n).*?(---\n\n## 🔑 Key Technical Points)',
        r'\1' + new_sections + r'\2',
        source_content,
        flags=re.DOTALL
    )
    
    if updated_content == source_content:
        print("ℹ️  No changes needed - source already up to date")
        return True
    
    # Write back to source
    with open(source_file, 'w') as f:
        f.write(updated_content)
    
    print("✅ Successfully updated source prototype:")
    print(f"   {source_file.relative_to(base_dir)}")
    print("   Changes will propagate to newly created projects after next BLT run")
    
    return True

def propagate_readme_changes():
    """
    Reminder: README files have gold source in Docs repo, not prototypes.
    
    Changes to readme.md and readme_ai_mcp.md in test projects need to be
    manually copied to:
        /org_git/Docs/docs/Sample-Basic-Demo.md
        /org_git/Docs/docs/Integration-MCP-AI-Example.md
    """
    print("\n📝 Reminder: README changes need manual update in Docs repo:")
    print("   /org_git/Docs/docs/Sample-Basic-Demo.md")
    print("   /org_git/Docs/docs/Integration-MCP-AI-Example.md")

if __name__ == '__main__':
    print("Propagating Copilot Instructions Changes...")
    print("-" * 60)
    
    success = propagate_copilot_instructions()
    propagate_readme_changes()
    
    sys.exit(0 if success else 1)
