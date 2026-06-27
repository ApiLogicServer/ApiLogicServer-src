#!/usr/bin/env python3
"""
Recreate the codespaces_mgr checkout from this local-mgr + Codespaces-only overrides.

Usage (from this Manager root):
    python3 .devcontainer-codespaces/create_codespaces_mgr.py /path/to/org_git/codespaces_mgr [--dry-run|--push|--release]

    (no flag) : sync files into target, leave staged for manual review (does NOT commit/push)
    --dry-run : show what would be copied, apply no changes
    --push    : sync + commit + push to the target repo's `dev` branch (day-to-day update)
    --release : sync + commit + push to `dev`, then merge dev->main, tag main with the
                gold-source product version, bump .devcontainer/devcontainer.json (triggers
                the repo's "Configuration change" prebuild refresh), push main + tag,
                and leave the target checked out on `dev`.

What the sync does:
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
       - broken-link check: every [text](link) in synced *.md is verified against the
         just-synced target tree (i.e. what a Codespaces user actually has, not
         local-mgr's own samples/, which may differ — see local-mgr-is-user-truth).
         A bare https://apilogicserver.github.io/Docs/... link is the accepted fallback
         for samples not pre-built into cs-mgr, and is checked live (HEAD request).
         Anything resolving to neither aborts the push (--push/--release only; plain
         sync-no-flag mode does not check, since nothing is being published).

--release reads the product version from this sibling file (under org_git/, alongside
codespaces_mgr) rather than from any README front matter, since that's the file Val
actually bumps for a real release:
    org_git/ApiLogicServer-src/api_logic_server_cli/api_logic_server.py  (__version__ = "...")

CAUTION — this script does NOT cover the whole CE delivery path into a live Codespace:
    .devcontainer/For_VSCode.dockerfile -> FROM apilogicserver/api_logic_server (Docker Hub)
This base image bakes in api_logic_server_cli/prototypes/ via `COPY . .` straight from
org_git/ApiLogicServer-src at image-build time (see docker/api_logic_server.Dockerfile),
built/pushed manually with `docker buildx build --push ...` — NOT by BLT, NOT by this
script. So a Codespace gets CE from two independent places that can disagree:
  - committed samples/*/.github/.copilot-instructions.md in this repo  -> refreshed by --release/--push
  - CE baked into the apilogicserver/api_logic_server image (used if the user runs
    `genai-logic create` live inside the Codespace) -> stale until that image is rebuilt+pushed
A gold-source CE edit (prototypes/base or prototypes/manager) needs: BLT (refresh local
venv + regenerate samples) AND a manual docker buildx rebuild+push of the base image,
before a fresh Codespace is guaranteed to see it everywhere.
"""

import sys
import re
import shutil
import subprocess
import urllib.request
import urllib.error
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
    ".git", "venv", ".venv", "__pycache__", "logs", ".DS_Store", ".devcontainer", ".obsidian",
}

# Curated files that live inside an otherwise-excluded directory (e.g. logs/) — copied
# individually after the main sync since COPY_EXCLUDES skips their parent wholesale.
EXTRA_FILES = [
    "samples/basic_demo_logic_gov/logs/als-sample.log",
]

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


def find_gold_version(target: Path) -> str:
    """Read __version__ from ApiLogicServer-src/api_logic_server_cli/api_logic_server.py.

    Located via target's own org_git/ ancestor — target (codespaces_mgr) is always a
    sibling of ApiLogicServer-src under org_git/, regardless of where local-mgr lives.
    """
    org_git = None
    for ancestor in [target] + list(target.parents):
        if ancestor.name == "org_git":
            org_git = ancestor
            break
    if org_git is None:
        raise SystemExit(
            f"ERROR: {target} is not under an org_git/ directory — "
            "can't locate ApiLogicServer-src as a sibling."
        )
    candidate = org_git / "ApiLogicServer-src" / "api_logic_server_cli" / "api_logic_server.py"
    if not candidate.exists():
        raise SystemExit(f"ERROR: expected gold-source version file not found: {candidate}")
    text = candidate.read_text()
    m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not m:
        raise SystemExit(f"ERROR: no __version__ line found in {candidate}")
    return m.group(1)


def run_git(args, cwd: Path, check=True):
    print(f"  $ git {' '.join(args)}")
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.stdout.strip():
        print("    " + result.stdout.strip().replace("\n", "\n    "))
    if check and result.returncode != 0:
        print("    " + result.stderr.strip().replace("\n", "\n    "))
        raise SystemExit(f"ERROR: git {' '.join(args)} failed (exit {result.returncode})")
    return result


MD_LINK_RE = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
DOCS_URL_PREFIX = "https://apilogicserver.github.io/Docs/"


def _url_exists(url: str) -> bool:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "create_codespaces_mgr.py"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status < 400
    except urllib.error.HTTPError as e:
        return e.code < 400
    except Exception:
        return False


def check_broken_links(target: Path) -> list:
    """Scan target/README.md for [text](link) targets and verify each one actually
    resolves - against the filesystem for local/relative links, or live (HEAD
    request) for https://apilogicserver.github.io/Docs/... links.

    `target` is the just-synced codespaces_mgr checkout - i.e. what a Codespaces user
    actually has (see local-mgr-is-user-truth memory: this is NOT the same tree as
    local-mgr's own samples/, which can differ - that mismatch is exactly what caused
    the bug this check exists to catch).

    Excluded as out of scope (a separate, pre-existing convention, not a same-repo
    relative link at all - resolved by the mkdocs site at build time, never meant to
    resolve on a filesystem): bare page references with no file extension, e.g.
    "Logic#declaring-rules" or "../Integration-MCP/".

    Returns a list of (file, link) tuples for anything that fails to resolve.
    """
    broken = []
    readme = target / "README.md"
    if not readme.exists():
        return broken
    text = readme.read_text(errors="ignore")
    for link in MD_LINK_RE.findall(text):
        if link.startswith(("#", "mailto:")):
            continue
        if link.startswith(DOCS_URL_PREFIX):
            if not _url_exists(link):
                broken.append((readme, link))
            continue
        if link.startswith(("http://", "https://")):
            continue  # other external links (GitHub images, raw URLs, etc.) - not this check's job
        link_path = link.split("#")[0]
        if not link_path:
            continue  # pure same-page anchor, e.g. "#section"
        if "." not in Path(link_path).name and not link_path.endswith("/"):
            continue  # bare mkdocs page reference (no extension) - resolved by the site, not the filesystem
        local_target = (readme.parent / link_path).resolve()
        if not local_target.exists():
            broken.append((readme, link))
    return broken


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
        print("Usage: create_codespaces_mgr.py /path/to/org_git/codespaces_mgr [--dry-run|--push|--release]")
        sys.exit(1)

    target  = Path(sys.argv[1]).resolve()
    dry_run = "--dry-run" in sys.argv
    push    = "--push" in sys.argv
    release = "--release" in sys.argv

    if not (target / ".git").exists():
        print(f"ERROR: {target} does not look like a git checkout (no .git) — refusing.")
        sys.exit(1)

    if push or release:
        status = run_git(["status", "--porcelain"], cwd=target).stdout
        if status.strip():
            raise SystemExit(
                f"ERROR: {target} has uncommitted changes before the sync even starts — "
                "commit, stash, or discard them first, then re-run."
            )
        run_git(["checkout", "dev"], cwd=target)
        run_git(["pull", "--ff-only", "origin", "dev"], cwd=target)

    print(f"Source (local-mgr): {SRC_ROOT}")
    print(f"Target (codespaces_mgr): {target}")
    if dry_run:
        print("Mode: DRY RUN — no changes will be made")
    print()

    # ── Step 1: sync scoped subset ────────────────────────────────────────────
    print("Step 1: Syncing scoped subset...")
    for p in SYNC_PATHS:
        copy_path(SRC_ROOT / p, target / p, dry_run)
    for f in EXTRA_FILES:
        copy_path(SRC_ROOT / f, target / f, dry_run)

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

    # Inject Codespaces + browser notes inside the first "see it work" collapsible
    # section (idempotent). Match on the lightning-bolt-prefixed <summary> — the
    # exact wording after ⚡ is gold-source copy (org_git/Docs) and changes
    # independently of this script, so anchor on the emoji prefix, not the wording.
    summary_re = re.compile(r"<summary>⚡[^<]*</summary>")
    if "Use Chrome or Edge" not in readme:
        cs_note = (
            "\n&nbsp;\n\n"
            "You're already running in GitHub Codespaces — a cloud VS Code environment "
            "in your browser. Nothing to install. (Use Chrome or Edge — Safari has known "
            "compatibility issues with VS Code in the browser.)\n"
        )
        match = summary_re.search(readme)
        if not match:
            raise SystemExit(
                "ERROR: no '<summary>⚡...</summary>' line found in README.md — "
                "update this script's summary_re pattern to match the current heading."
            )
        readme = readme[:match.end()] + cs_note + readme[match.end():]
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

    if not push and not release:
        print()
        print("Done. Review changes in target, then commit and push:")
        print(f"  cd {target} && git status")
        return

    # ── Step 2h: broken-link check (local first, Docs URL fallback) ──────────
    print()
    print("Step 2h: Checking for broken links (local samples/, else apilogicserver.github.io/Docs/)...")
    broken = check_broken_links(target)
    if broken:
        print(f"  ❌ {len(broken)} broken link(s) found:")
        for md_file, link in broken:
            print(f"     {md_file.relative_to(target)}: {link}")
        raise SystemExit(
            "ERROR: broken links found in synced markdown - fix in local-mgr (or its "
            "gold Docs source) before pushing to cs-mgr. See list above."
        )
    print("  ✅ no broken links")

    # ── Step 3: commit + push to dev ─────────────────────────────────────────
    print()
    print("Step 3: Committing + pushing to dev...")
    run_git(["add", "-A"], cwd=target)
    status = run_git(["status", "--porcelain"], cwd=target).stdout
    if not status.strip():
        print("  (nothing changed — dev already up to date with local-mgr)")
    else:
        gold_version = find_gold_version(target)
        run_git(["commit", "-m", f"Sync from local-mgr (gold v{gold_version})"], cwd=target)
        run_git(["push", "origin", "dev"], cwd=target)
        print("  ✅ pushed to dev")

    if not release:
        print()
        print(f"Done — {target} is on dev, pushed. Re-run with --release to publish to main.")
        return

    # ── Step 4: release — merge to main, tag, bump prebuild trigger ─────────
    print()
    print("Step 4: Releasing — merging dev -> main...")
    gold_version = find_gold_version(target)
    existing_tags = run_git(["tag", "-l"], cwd=target).stdout.split()
    tag_already_exists = gold_version in existing_tags
    if tag_already_exists:
        print(
            f"  (gold version '{gold_version}' already tagged — releasing content-only "
            f"changes without a new version tag)"
        )

    run_git(["checkout", "main"], cwd=target)
    run_git(["pull", "--ff-only", "origin", "main"], cwd=target)
    merge = run_git(["merge", "dev", "--no-edit"], cwd=target, check=False)
    if merge.returncode != 0:
        raise SystemExit(
            "ERROR: merge dev -> main failed (likely a conflict). Repo is left mid-merge on "
            "main — resolve manually, or `git merge --abort` and re-run --release.\n"
            + merge.stderr
        )

    # Touch devcontainer.json to fire the prebuild trigger. This line is disposable —
    # it's NOT the version record (the git tag is); the next ordinary --push overwrites
    # this file wholesale from local-mgr's untouched copy, which is fine, since this
    # comment's only job is to differ from main's current content at release time.
    devcontainer_json = target / ".devcontainer" / "devcontainer.json"
    text = devcontainer_json.read_text()
    bump_re = re.compile(r'^// prebuild trigger bump: .*\n', re.MULTILINE)
    text = bump_re.sub("", text)
    text = f"// prebuild trigger bump: release {gold_version}\n" + text
    devcontainer_json.write_text(text)
    run_git(["add", ".devcontainer/devcontainer.json"], cwd=target)
    run_git(["commit", "-m", f"Release {gold_version}: bump devcontainer.json to refresh prebuild"], cwd=target)

    run_git(["push", "origin", "main"], cwd=target)
    if not tag_already_exists:
        run_git(["tag", gold_version], cwd=target)
        run_git(["push", "origin", gold_version], cwd=target)

    run_git(["checkout", "dev"], cwd=target)
    run_git(["merge", "main", "--no-edit"], cwd=target)
    run_git(["push", "origin", "dev"], cwd=target)

    print()
    print(f"✅ Released {gold_version}: dev -> main merged, tagged, pushed.")
    print(f"   {target} is left on dev.")
    print("   Prebuild refresh should start automatically (devcontainer.json changed on main).")


if __name__ == "__main__":
    main()
