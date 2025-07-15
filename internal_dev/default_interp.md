vcscode 1.102.0

Writing a project generator - I want to create projects that open with a venv setup for run and terminal use.
This venv is shared, and can be at different locations relative to the project (so awkward to use $workspace).

Prior versions, I computed the venv location to set defaultInterpreterPath in vscode/.settings, which worked fine.

FINAL SOLUTION:
- python.defaultInterpreterPath is correct (not python.pythonPath which is deprecated)
- Need additional settings for venv activation:
  - python.terminal.activateEnvironment: true
  - python.terminal.activateEnvInCurrentTerminal: true

EXPLICIT TERMINAL PROFILE APPROACH:
Since VS Code Python extension wasn't reliably activating the shared venv, now:
1. Creates custom terminal profiles that explicitly source the venv activate script
2. Sets these profiles as default for macOS and Linux
3. Creates .env file for additional environment support

This forces VS Code terminals to always activate the venv by:
- Using custom terminal profiles with explicit activation commands
- Setting the profiles as default so new terminals auto-activate
- Providing fallback .env file for environment variables

Updated template and generation code to create:
- .vscode/settings.json with interpreter path, activation settings, and custom terminal profiles
- .env file with VIRTUAL_ENV and PATH variables

Now generates terminal profiles that run:
- macOS: `source /path/to/venv/bin/activate && exec zsh`
- Linux: `source /path/to/venv/bin/activate && exec bash`

This ensures virtual environment is ALWAYS activated in VS Code terminals.

build 46:

    "python.defaultInterpreterPath": "ApiLogicServerPython",
    // "python.terminal.activateEnvironment": true,
    // "python.terminal.activateEnvInCurrentTerminal": true,
