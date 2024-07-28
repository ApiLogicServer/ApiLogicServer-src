import subprocess
import os
from pathlib import Path

# Step 1: Create a virtual environment
venv_dir = 'C:\\Users\\val\\dev\\ApiLogicServer\\ApiLogicServer-dev\\build_and_test\\ApiLogicServer\\venv'
# venv_dir = 'C:\\Users\\val\\dev\\ApiLogicServer\\ApiLogicServer-dev\\org_git\\ApiLogicServer-src\\venv'
venv_path = Path(venv_dir)
venv_path_dir = str(venv_path)
assert venv_path.exists(), f"Bad Path: {venv_dir}"
# subprocess.run(['python', '-m', 'venv', venv_dir])

# Step 2: Activate the virtual environment
activate_script = os.path.join(venv_path_dir, 'Scripts', 'activate')  # or, .bat

# Step 3: Run the desired command within the virtual environment
command = 'python --version'
subprocess.run(f'{activate_script} && {command}', shell=True)