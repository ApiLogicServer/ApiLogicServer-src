"""
Convenience wrapper — generate the logic diagram for this project.

Usage (from anywhere inside the project):
    python docs/training/logic_diagrams/generate_logic_diagram.py              # full diagram
    python docs/training/logic_diagrams/generate_logic_diagram.py check_credit # scoped
"""
import sys
from pathlib import Path

# Locate the generator relative to this file
# This file: <project>/docs/training/logic_diagrams/generate_logic_diagram.py
this_dir    = Path(__file__).resolve().parent          # project/docs/training/logic_diagrams/
project_dir = this_dir.parent.parent.parent            # project/
manager_dir = project_dir.parent                       # Manager root

gen = manager_dir / "system" / "ApiLogicServer-Internal-Dev" / "logic_diagram_gv.py"
if not gen.exists():
    print(f"ERROR: generator not found at {gen}")
    sys.exit(1)

# Import and run
sys.path.insert(0, str(gen.parent))
from logic_diagram_gv import generate

requirement = sys.argv[1] if len(sys.argv) > 1 else None
generate(project_dir.name, requirement=requirement, manager_root=manager_dir)
