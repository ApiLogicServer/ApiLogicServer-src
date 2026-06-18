#!/usr/bin/env python3
"""
Recreate the codespaces_mgr checkout from this local-mgr + Codespaces-only overrides.

Usage (from this Manager root):
    python3 .devcontainer-codespaces/create_codespaces_mgr.py /path/to/org_git/codespaces_mgr [--dry-run]

    --dry-run : show what would be copied, apply no changes

What it does:
    1. Copy a scoped subset of local-mgr -> target (see SYNC_PATHS below).
       Excludes basic_demo/, scaffold/, tests/, dockers/, demo_customs/, demo_eai/, venv/.
       (.devcontainer-codespaces/ IS synced — it becomes .devcontainer/ in step 2)
    2. Apply Codespaces-only overrides:
       - rename .devcontainer-codespaces -> .devcontainer
       - CLAUDE.md.append  -> prepended to CLAUDE.md (idempotent)
       - gitignore.append  -> appended to .gitignore (idempotent)
       - README.md         -> strip front matter + <style> block; inject browser/CS notes
       - .vscode/settings.json -> python.defaultInterpreterPath -> /usr/local/bin/python
       - .vscode/launch.json  -> replaced with Codespaces-trimmed 2-config version
       - samples/*/. vscode/settings.json -> same interpreter patch
    3. Leaves target staged for review/commit (does NOT commit or push)
"""

import sys
import re
import shutil
from pathlib import Path

# ── paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
SRC_ROOT   = SCRIPT_DIR.parent          # Manager root
OVERRIDES  = SCRIPT_DIR                 # .devcontainer-codespaces/

SYNC_PATHS = [
    ".claude",
    ".devcontainer-codespaces",
    ".env",
    ".github",
    ".gitignore",
    ".vscode",
    "CLAUDE.md",
    "CodeSpaces.md",
    "README.md",
    "readme_vibe.md",
    "samples",
    "system",
    "webgenai",
]

COPY_EXCLUDES = {
    ".git", "venv", ".venv", "__pycache__", "logs", ".DS_Store", ".devcontainer",
}

# ── helpers ──────────────────────────────────────────────────────────────────

def ignore_fn(dir_, names):
    return {n for n in names if n in COPY_EXCLUDES}


def copy_path(src: Path, dst: Path, dry_run: bool):
    if not src.exists():
        print(f"  (skip, not in local-mgr: {src.name})")
        return
    if dry_run:
        print(f"  [dry-run] would copy {src} -> {dst}")
        return
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=ignore_fn)
        print(f"  ✅ {src.name}/")
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  ✅ {src.name}")


def patch_interpreter(path: Path):
    """Replace any python.defaultInterpreterPath value with /usr/local/bin/python."""
    text = path.read_text()
    new  = re.sub(
        r'"python\.defaultInterpreterPath":\s*"[^"]*"',
        '"python.defaultInterpreterPath": "/usr/local/bin/python"',
        text,
    )
    if new != text:
        path.write_text(new)
        return True
    return False


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: create_codespaces_mgr.py /path/to/org_git/codespaces_mgr [--dry-run]")
        sys.exit(1)

    target  = Path(sys.argv[1]).resolve()
    dry_run = "--dry-run" in sys.argv

    if not (target / ".git").exists():
        print(f"ERROR: {target} does not look like a git checkout (no .git) — refusing.")
        sys.exit(1)

    print(f"Source (local-mgr): {SRC_ROOT}")
    print(f"Target (codespaces_mgr): {target}")
    if dry_run:
        print("Mode: DRY RUN — no changes will be made")
    print()

    # ── Step 1: sync scoped subset ────────────────────────────────────────────
    print("Step 1: Syncing scoped subset...")
    for p in SYNC_PATHS:
        copy_path(SRC_ROOT / p, target / p, dry_run)

    if dry_run:
        print("\nDry run complete — no overrides applied.")
        return

    print()

    # ── Step 2: Codespaces-only overrides ────────────────────────────────────

    # .devcontainer-codespaces/ -> .devcontainer/
    print("Step 2a: Renaming .devcontainer-codespaces -> .devcontainer...")
    dc_src = target / ".devcontainer-codespaces"
    dc_dst = target / ".devcontainer"
    if dc_dst.exists():
        shutil.rmtree(dc_dst)
    dc_src.rename(dc_dst)
    print("  ✅ .devcontainer/")

    # CLAUDE.md — prepend Codespaces venv warning after title line
    print("Step 2b: Applying CLAUDE.md override...")
    claude_path   = target / "CLAUDE.md"
    claude_append = (OVERRIDES / "CLAUDE.md.append").read_text()
    claude_text   = claude_path.read_text()
    if "ApiLogicServer is pre-installed globally" not in claude_text:
        lines      = claude_text.splitlines(keepends=True)
        title_line = lines[0]
        rest       = "".join(lines[1:])
        claude_path.write_text(title_line + "\n" + claude_append + "\n" + rest)
        print("  ✅ CLAUDE.md prepended")
    else:
        print("  (already present, skipped)")

    # .gitignore — append .venv/ if not present
    print("Step 2c: Applying .gitignore override...")
    gi_path   = target / ".gitignore"
    gi_append = (OVERRIDES / "gitignore.append").read_text()
    gi_text   = gi_path.read_text()
    if ".venv/" not in gi_text.splitlines():
        if not gi_text.endswith("\n"):
            gi_path.write_text(gi_text + "\n")
        with gi_path.open("a") as f:
            f.write(gi_append)
        print("  ✅ .gitignore appended")
    else:
        print("  (already present, skipped)")

    # README.md — strip front matter + style block, inject CS/browser notes
    print("Step 2d: Patching README.md...")
    readme_path = target / "README.md"
    readme      = readme_path.read_text()

    # Strip YAML front matter
    readme = re.sub(r"^---\n.*?\n---\n", "", readme, count=1, flags=re.DOTALL)
    # Strip <style>...</style>
    readme = re.sub(r"<style>.*?</style>\n?", "", readme, count=1, flags=re.DOTALL)
    # Strip any leading blank lines left by the above
    readme = readme.lstrip("\n")
    print("  ✅ Front matter and style block stripped")

    # Inject Codespaces + browser notes inside "See it work" (idempotent)
    # Sentinel: "<summary>⚡ See it work — 5 minute first look</summary>" — update if this line ever changes
    if "Use Chrome or Edge" not in readme:
        old_summary = "<summary>⚡ See it work — 5 minute first look</summary>"
        new_summary = "<summary>⚡ See it work — 5 minutes, no install</summary>"
        cs_note = (
            "\n&nbsp;\n\n"
            "You're already running in GitHub Codespaces — a cloud VS Code environment "
            "in your browser. Nothing to install. (Use Chrome or Edge — Safari has known "
            "compatibility issues with VS Code in the browser.)\n"
        )
        if old_summary not in readme:
            raise SystemExit(
                f"ERROR: sentinel line not found in README.md — update this script's "
                f"old_summary string to match: {old_summary!r}"
            )
        readme = readme.replace(old_summary, new_summary + cs_note, 1)
        print("  ✅ Codespaces + browser notes injected")
    else:
        print("  (notes already present, skipped)")

    readme_path.write_text(readme)

    # .vscode/settings.json — global interpreter (Manager root)
    print("Step 2e: Patching .vscode/settings.json (Manager root)...")
    settings = target / ".vscode" / "settings.json"
    if patch_interpreter(settings):
        print("  ✅ Manager root settings.json patched")
    else:
        print("  (already correct, skipped)")

    # .vscode/launch.json — replace with Codespaces-trimmed 2-config version
    print("Step 2f: Replacing .vscode/launch.json with Codespaces-trimmed version...")
    shutil.copy2(OVERRIDES / "launch.json", target / ".vscode" / "launch.json")
    print("  ✅ launch.json replaced")

    # samples/*/. vscode/settings.json — global interpreter for all samples
    print("Step 2g: Patching samples/*/. vscode/settings.json...")
    for f in sorted((target / "samples").glob("*/.vscode/settings.json")):
        if patch_interpreter(f):
            print(f"  ✅ {f.parent.parent.name}")

    print()
    print("Done. Review changes in target, then commit and push:")
    print(f"  cd {target} && git status")


if __name__ == "__main__":
    main()
