#!/bin/bash
#
# pull_source.sh - pull gold source, Docs, and cs-mgr; optionally run BLT
#
# Pulls (git pull) the org_git sibling repos this Manager workspace is built from:
#   - ApiLogicServer-src   gold source: prototypes, CE, CLI
#   - Docs                 gold source for README files (copy_md())
#   - codespaces_mgr       cs-mgr trial repo (tracks branch: dev)
#
# Usage:
#   sh system/ApiLogicServer-Internal-Dev/pull_source.sh pull
#       Just git-pull the three repos above. Confined to org_git/ - does not
#       touch this workspace (build_and_test/genai-logic).
#
#   sh system/ApiLogicServer-Internal-Dev/pull_source.sh blt
#       Pulls, then runs a full Build-Load-Test from the freshly-pulled
#       ApiLogicServer-src (org_git/ApiLogicServer-src/tests/build_and_test/blt.sh).
#
#       WARNING - self-modifying: BLT regenerates THIS ENTIRE WORKSPACE
#       (build_and_test/genai-logic) from org_git/ApiLogicServer-src gold
#       source - including this very script (system/ApiLogicServer-Internal-Dev/
#       is itself a BLT-propagated directory, see dev-architecture.md). Any
#       local edits under this workspace not yet copied back to gold source
#       will be overwritten. It is also untested whether a running bash script
#       tolerates its own file being rewritten out from under it mid-execution -
#       the BLT invocation is deliberately the last thing this script does, but
#       that is not a guarantee. You'll be asked to confirm before BLT runs.
#
# No arg (or an unrecognized one) prints this message and exits.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANAGER_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"      # build_and_test/genai-logic
DEV_ROOT="$(cd "$MANAGER_ROOT/../.." && pwd)"        # ApiLogicServer-dev
ORG_GIT="$DEV_ROOT/org_git"

REPOS=(ApiLogicServer-src Docs codespaces_mgr)

usage() {
    echo ""
    echo "pull_source.sh - pull gold source, Docs, and cs-mgr; optionally run BLT"
    echo ""
    echo "  Pulls (git pull) these repos:"
    echo "    $ORG_GIT/ApiLogicServer-src   (gold source: prototypes, CE, CLI)"
    echo "    $ORG_GIT/Docs                 (gold source for README files)"
    echo "    $ORG_GIT/codespaces_mgr       (cs-mgr trial repo, branch: dev)"
    echo ""
    echo "  Usage:"
    echo "    sh system/ApiLogicServer-Internal-Dev/pull_source.sh pull"
    echo "        just pulls the 3 repos above - confined to org_git/"
    echo ""
    echo "    sh system/ApiLogicServer-Internal-Dev/pull_source.sh blt"
    echo "        pulls, then runs a full Build-Load-Test"
    echo ""
    echo "  WARNING: 'blt' regenerates THIS Manager workspace"
    echo "    ($MANAGER_ROOT)"
    echo "    from gold source - including this script. Any local edits here"
    echo "    not yet propagated to gold source will be overwritten. You'll"
    echo "    be prompted to confirm before it runs."
    echo ""
    exit 0
}

pull_repo() {
    local repo="$1"
    local dir="$ORG_GIT/$repo"
    if [ ! -d "$dir/.git" ]; then
        echo "  x $repo - not a git repo at $dir, skipping"
        return 1
    fi
    local dirty
    dirty="$(git -C "$dir" status --porcelain)"
    if [ -n "$dirty" ]; then
        echo "  ! $repo has local changes - pulling anyway (git will refuse to clobber them):"
        echo "$dirty" | sed 's/^/        /'
    fi
    local branch
    branch="$(git -C "$dir" rev-parse --abbrev-ref HEAD)"
    echo "  > $repo (branch $branch)"
    if git -C "$dir" pull; then
        echo "  + $repo up to date"
        return 0
    else
        echo "  x $repo pull failed"
        return 1
    fi
}

do_pull() {
    echo ""
    echo "Pulling gold source repos into $ORG_GIT ..."
    local failed=()
    local repo
    for repo in "${REPOS[@]}"; do
        pull_repo "$repo" || failed+=("$repo")
    done
    echo ""
    if [ "${#failed[@]}" -gt 0 ]; then
        echo "Done, with failures: ${failed[*]}"
        return 1
    fi
    echo "Done - all repos up to date."
    return 0
}

do_blt() {
    echo ""
    echo "WARNING: BLT will regenerate this Manager workspace:"
    echo "    $MANAGER_ROOT"
    echo "  from $ORG_GIT/ApiLogicServer-src, including this script"
    echo "  (system/ApiLogicServer-Internal-Dev/pull_source.sh). Any local"
    echo "  edits under this workspace not yet propagated to gold source"
    echo "  will be lost."
    echo ""
    read -r -p "Continue with BLT? [y/N] " confirm
    case "$confirm" in
        y|Y|yes|YES) ;;
        *) echo "Aborted - BLT not run."; exit 1 ;;
    esac

    local blt_script="$ORG_GIT/ApiLogicServer-src/tests/build_and_test/blt.sh"
    if [ ! -f "$blt_script" ]; then
        echo "x BLT script not found: $blt_script"
        exit 1
    fi
    local blt_venv_activate="$ORG_GIT/ApiLogicServer-src/venv/bin/activate"
    if [ ! -f "$blt_venv_activate" ]; then
        echo "x BLT venv not found: $blt_venv_activate"
        exit 1
    fi
    echo ""
    echo "Running BLT from $ORG_GIT/ApiLogicServer-src ..."
    # blt.sh calls bare 'python3' - it expects this venv (which has requests, etc.
    # installed) to already be active, not system python3.
    ( cd "$ORG_GIT/ApiLogicServer-src" && . "$blt_venv_activate" && sh tests/build_and_test/blt.sh s )
}

case "${1:-}" in
    pull)
        do_pull
        ;;
    blt)
        do_pull && do_blt
        ;;
    *)
        usage
        ;;
esac
