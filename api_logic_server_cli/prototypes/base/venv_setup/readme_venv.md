# API Logic Project - `venv` Setup

This folder contains scripts to set up your Python environment after cloning a project from git.

> **Tip:** If you cloned this project into the ApiLogicServer Manager folder, you can run it
> directly without any venv setup:
> ```
> als run --project-name=<your-project>
> ```

## Option 1 — Symlink to Manager venv (Mac/Linux, recommended)

If your project is inside the Manager folder (i.e. `../venv` exists), create a symlink:

```bash
sh venv_setup/venv.sh symlink
```

VS Code detects the symlink as a local venv and selects the correct Python interpreter
automatically — no manual interpreter picker needed. Reload the VS Code window after running.

## Option 2 — Create a local venv (all platforms)

```bash
# Mac/Linux
sh venv_setup/venv.sh go

# Linux
sh venv_setup/venv-linux.sh go

# Windows PowerShell
.\venv_setup\venv.ps1 go
```

This creates a `venv/` inside the project and runs `pip install -r requirements.txt`.

## Verify the `venv`

Optionally, check your Python environment by running:
```
python venv_setup/py.py
```
