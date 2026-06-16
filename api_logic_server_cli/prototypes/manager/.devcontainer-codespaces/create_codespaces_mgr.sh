#!/bin/bash
# Recreate the codespaces_mgr checkout from this local-mgr + Codespaces-only overrides.
#
# Usage (from this Manager root):
#   .devcontainer-codespaces/create_codespaces_mgr.sh /path/to/org_git/codespaces_mgr [--dry-run]
#
#   --dry-run : preview rsync changes only (passes -n to rsync, skips overrides
#               and does not touch the target at all)
#
# What it does:
#   1. rsync a SCOPED SUBSET of this local-mgr -> <target> (see SYNC_PATHS below).
#      codespaces_mgr is a deliberate trimmed-down trial repo, NOT a full mirror -
#      it does not include basic_demo/, scaffold/, tests/, dockers/,
#      demo_customs/, demo_eai/, or venv/.
#      (.devcontainer-codespaces/ IS synced - it becomes .devcontainer/ in step 2)
#   2. Apply Codespaces-only overrides:
#      - rename <target>/.devcontainer-codespaces -> <target>/.devcontainer
#        (overwriting any .devcontainer copied from local-mgr)
#      - CLAUDE.md.append     -> prepended to <target>/CLAUDE.md (if not already present)
#      - gitignore.append     -> appended to <target>/.gitignore (if not already present)
#      - .vscode/settings.json -> python.defaultInterpreterPath rewritten from
#        local-mgr's "${workspaceFolder}/venv/bin/python" to "/usr/local/bin/python"
#        (codespaces-mgr has no venv/ - ApiLogicServer is installed globally)
#   3. Leaves <target> staged for review/commit (does NOT commit or push)

set -euo pipefail

TARGET="${1:?Usage: create_codespaces_mgr.sh /path/to/org_git/codespaces_mgr [--dry-run]}"
DRY_RUN=""
[ "${2:-}" = "--dry-run" ] && DRY_RUN="-n"
SRC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OVERRIDES="$SRC_ROOT/.devcontainer-codespaces"

if [ ! -d "$TARGET/.git" ]; then
    echo "ERROR: $TARGET does not look like a git checkout (no .git) - refusing to overwrite."
    exit 1
fi

echo "Source (local-mgr): $SRC_ROOT"
echo "Target (codespaces_mgr): $TARGET"
[ -n "$DRY_RUN" ] && echo "Mode: DRY RUN (rsync preview only, no overrides applied)"
echo

# 1. Sync only the paths codespaces_mgr actually contains - a curated trial subset
#    of local-mgr, not a full mirror. Excludes basic_demo/, scaffold/, tests/,
#    dockers/, demo_customs/, demo_eai/, venv/ (dev/test infra not relevant to a
#    Codespaces trial repo).
#    (.devcontainer-codespaces/ IS synced - it becomes .devcontainer/ below)
SYNC_PATHS=(
    .claude
    .devcontainer-codespaces
    .env
    .github
    .gitignore
    .vscode
    CLAUDE.md
    CodeSpaces.md
    README.md
    readme_vibe.md
    samples
    system
    webgenai
)

for p in "${SYNC_PATHS[@]}"; do
    src="$SRC_ROOT/$p"
    [ -e "$src" ] || { echo "  (skip, not in local-mgr: $p)"; continue; }
    if [ -d "$src" ]; then
        rsync -av $DRY_RUN --delete \
            --exclude='.git/' \
            --exclude='venv/' \
            --exclude='.venv/' \
            --exclude='__pycache__/' \
            --exclude='logs/' \
            --exclude='.DS_Store' \
            --exclude='.devcontainer/' \
            "$src/" "$TARGET/$p/"
    else
        rsync -av $DRY_RUN "$src" "$TARGET/$p"
    fi
done

if [ -n "$DRY_RUN" ]; then
    echo
    echo "Dry run complete - no changes made, overrides (step 2) skipped."
    exit 0
fi

# 2. Apply Codespaces-only overrides

# .devcontainer-codespaces/ -> .devcontainer/ (rename, like per-project -option convention)
echo
echo "Renaming .devcontainer-codespaces -> .devcontainer..."
rm -rf "$TARGET/.devcontainer"
mv "$TARGET/.devcontainer-codespaces" "$TARGET/.devcontainer"

# CLAUDE.md - prepend Codespaces venv warning (after the title line) if not already present
echo "Applying CLAUDE.md override..."
if ! grep -q "ApiLogicServer is pre-installed globally" "$TARGET/CLAUDE.md"; then
    TITLE_LINE=$(head -1 "$TARGET/CLAUDE.md")
    {
        echo "$TITLE_LINE"
        echo
        cat "$OVERRIDES/CLAUDE.md.append"
        echo
        tail -n +2 "$TARGET/CLAUDE.md"
    } > "$TARGET/CLAUDE.md.tmp"
    mv "$TARGET/CLAUDE.md.tmp" "$TARGET/CLAUDE.md"
else
    echo "  (already present, skipped)"
fi

# .gitignore - append .venv/ if not already present
echo "Applying .gitignore override..."
if ! grep -qx ".venv/" "$TARGET/.gitignore"; then
    # ensure file ends with a newline before appending
    [ -n "$(tail -c1 "$TARGET/.gitignore")" ] && echo >> "$TARGET/.gitignore"
    cat "$OVERRIDES/gitignore.append" >> "$TARGET/.gitignore"
else
    echo "  (already present, skipped)"
fi

# .vscode/settings.json - no venv/ in codespaces-mgr; use the global interpreter
echo "Applying .vscode/settings.json override (Manager root)..."
if grep -q '"python.defaultInterpreterPath"' "$TARGET/.vscode/settings.json"; then
    sed -i.bak 's|"python.defaultInterpreterPath": ".*"|"python.defaultInterpreterPath": "/usr/local/bin/python"|' "$TARGET/.vscode/settings.json"
    rm -f "$TARGET/.vscode/settings.json.bak"
    echo "  ✅ Manager root settings.json patched"
else
    echo "  (no interpreter path found, skipped)"
fi

# README.md - strip front matter (---...---) and <style>...</style> block
# These are mkdocs artifacts; copy_md() strips them for local-mgr but rsync copies them raw.
echo "Stripping README.md front matter and style block..."
python3 - "$TARGET/README.md" <<'PYEOF'
import sys, re
path = sys.argv[1]
text = open(path).read()
# Strip YAML front matter
text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
# Strip <style>...</style> block
text = re.sub(r'<style>.*?</style>\n?', '', text, count=1, flags=re.DOTALL)
open(path, "w").write(text)
PYEOF
echo "  ✅ Front matter and style block stripped"

# README.md - inject Codespaces-only browser note after the OBX heading (idempotent)
# Gold Manager-readme.md is shared; we don't fork it — inject here instead.
# Sentinel: "## 🚀 First Time Here?" — if that heading changes, update this grep too.
echo "Applying README.md Codespaces notes injection..."
if ! grep -q "Use Chrome or Edge" "$TARGET/README.md"; then
    # Insert two-line blockquote block after the OBX heading
    python3 - "$TARGET/README.md" <<'PYEOF'
import sys, re
path = sys.argv[1]
text = open(path).read()
insert = (
    "\n"
    "> **Codespaces:** This workspace runs in GitHub Codespaces — a cloud VS Code environment, "
    "no local install needed. New to Codespaces? See "
    "[GitHub Codespaces docs](https://docs.github.com/en/codespaces).\n"
    ">\n"
    "> **Browser:** Use Chrome or Edge — Safari has known compatibility issues with VS Code in the browser.\n"
)
text = text.replace("## 🚀 First Time Here?\n", "## 🚀 First Time Here?\n" + insert, 1)
open(path, "w").write(text)
PYEOF
    echo "  ✅ Codespaces + browser notes injected"
else
    echo "  (already present, skipped)"
fi

# .vscode/launch.json - replace with Codespaces-trimmed version (2 configs only)
# local-mgr launch.json has 40+ dev/internal configs; rsync would copy all of them
echo "Applying .vscode/launch.json override (Codespaces-trimmed version)..."
cp "$OVERRIDES/launch.json" "$TARGET/.vscode/launch.json"
echo "  ✅ launch.json replaced with Codespaces-trimmed version"

# samples/*/. vscode/settings.json - same fix for all sample projects
# (samples have ../../venv/bin/python or baked local paths - none exist in the container)
echo "Applying .vscode/settings.json override (all samples)..."
find "$TARGET/samples" -name "settings.json" -path "*/.vscode/*" | while read f; do
    if grep -q '"python.defaultInterpreterPath"' "$f"; then
        sed -i.bak 's|"python.defaultInterpreterPath": ".*"|"python.defaultInterpreterPath": "/usr/local/bin/python"|' "$f"
        rm -f "${f}.bak"
        echo "  ✅ $(basename $(dirname $(dirname $f)))"
    fi
done

echo
echo "Done. Review changes in $TARGET, then commit and push:"
echo "  cd $TARGET && git status"
