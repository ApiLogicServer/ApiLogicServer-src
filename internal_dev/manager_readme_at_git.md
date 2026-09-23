# Pointing evaluators at prototypes/manager/README.md on GitHub

Date: 2026-09-22

## The idea

Instead of (or in addition to) cs-mgr (~1 min to load), point evaluators straight at:

https://github.com/ApiLogicServer/ApiLogicServer-src/blob/main/api_logic_server_cli/prototypes/manager/README.md

Zero install, zero wait — GitHub renders the `<details>` collapsibles and images fine.

## Verified mechanism (was Val's recollection, confirmed against code)

- `ApiLogicServer start` → `manager.py: create_manager()`:
  1. `shutil.copytree` copies the whole `prototypes/manager/` dir (incl. `README.md`) into the target dir as a seed/placeholder.
  2. `copy_md(from_doc_file='Manager-readme.md', ...)` immediately overwrites that seeded file — comment in code: `# override api_logic_server_cli/prototypes/manager/README.md from git`. This fetches **`org_git/Docs/docs/Manager-readme.md`** (the real gold source), converts it from mkdocs syntax to plain markdown (strips `!!!` admonitions, absolutizes image/doc links to GitHub raw URLs, etc.), and writes the result over the seeded copy.
- So on every normal (online) `start`, `prototypes/manager/README.md`'s own content is irrelevant — it's clobbered immediately. Its content only matters in two cases:
  1. **Offline fallback** — if the GitHub fetch fails and there's no local `Docs/` checkout, the copytree'd version survives as the actual README the user sees.
  2. **Direct GitHub browsing of `ApiLogicServer-src`** — this proposal's exact use case.
- As of this session: `prototypes/manager/README.md` was regenerated and committed today (`4a114d81`, "samples, readme") — it's a real, recent revision of the gold doc, not stale filler. Brought fully current in this session (see "Actions taken" below).

## Value

Real. This is a legitimate zero-install eval path, strictly faster than cs-mgr, and GitHub's renderer handles the doc's structure fine.

## Risks (neither is a blocker, both actionable)

1. **Drift, not one-time staleness.** Because the live default is normally overwritten by every `start` run, "make this the default" is not a one-time edit — it only stays current if gold edits are followed by a regen+commit of `prototypes/manager/README.md`. If someone edits `Docs/docs/Manager-readme.md` and an evaluator clicks the GitHub link before the next regen, they see stale content with no warning. Recommend: treat "sync prototypes/manager/README.md" as a standing step in the gold-update workflow once this link is actively promoted, not an occasional cleanup.

2. **The doc is written for an active Manager session, not a cold read.** The `## 🚀 First Time Here?` section (and its "The Ideal" subsection) is fundamentally a *guided-tour script*:
   - "Say this to your AI assistant" (lines ~84-98) — inert with no chat session open.
   - "Press F5 using 'API Logic Server Run...'" (~line 127) — meaningless outside VS Code/Codespaces.
   - "Now trigger it: open an unshipped Order... Change the quantity... Save" (~129-133) — the single strongest piece of evidence in the whole doc (a governed save failing live) is something a cold GitHub reader can only read about, never experience.
   - Codespaces/local-mgr conditional blocks (`CODESPACES-ONLY-START`/`LOCAL-MGR-ONLY-START`) are HTML comments — invisible on a raw GitHub render, so a cold reader sees neither variant's guidance (degrades to nothing, not to something written for them).

   This is **not new risk** — it's true today, for any Manager user, and already true of whatever revision sits in `prototypes/manager/README.md` on GitHub right now. It only becomes higher-stakes once evaluators are *deliberately* routed at that URL as their first impression, rather than stumbling into it while browsing source.

   Later sections ("AI Alone Writes Code You Can't Trust", "Easy to Read, Trust, and Maintain", "Pre-Built Enterprise Architecture", etc.) are self-contained narrative + evidence links and read fine cold — the gap is specifically the top "First Time Here?" tour section.

## Real bug found and fixed (unrelated to the risk assessment, fixed regardless)

`![credit-check](...credit-check.png?raw=true?raw=true)` — doubled `?raw=true` query string, likely broken image render. Found in:
- `org_git/Docs/docs/Manager-readme.md` (gold)
- `build_and_test/genai-logic/README.md` (local mirror)
- `api_logic_server_cli/prototypes/manager/README.md` (default manager)

Fixed in all three as part of this session.

## Actions taken this session

1. Fixed the doubled `?raw=true` bug in gold, local mirror, and prototypes/manager/README.md.
2. Synced `prototypes/manager/README.md` to the current mkdocs-converted content (matching `build_and_test/genai-logic/README.md`, which reflects the current state of gold `Docs/docs/Manager-readme.md` plus this session's edits — see below).
3. Gold-source edits made this session, now reflected in all three copies:
   - Added `images/architecture/proc-decl-simple.png` to the "Scales Past One Project" section, positioned after the architecture-difference sentence, before `proc-to-decl.png`.
   - Moved `proc-to-decl.png` to after "...not just the one the prompt described."
   - Reworded the "What can you do for me?" sub-section → "No Proprietary Interface, No Rigid Structure — just ask the AI when you need guidance."
   - Reordered "Business Users, Empowered" sub-sections: BU IDE → No Prop Interface → RFI (was RFI → No Prop Interface → BU IDE).
   - Reworded RFI sub-section summary/body to read as a continuation ("And When You Need Even More Guidance...").
   - Reworded top-level "AI-driven rules are easy to Read, Trust, and Maintain" summary → "Easy to Read, Trust, and Maintain — Augment AI with Rules" (value-first framing, addresses risk that GenAI-Logic reads as "just AI, made friendlier").
   - Added "Rules" to the "Pre-Built Enterprise Architecture — API, MCP, Messages, Rules, RBAC" summary (was missing from the list of things it's pre-built with).
   - Bolded the lead phrase (before the em dash) in every sub-`<details>` summary from "AI Alone Writes Code" through "Go deeper" — matching the existing bold-lead-phrase pattern already used in "AI Alone..." and "Pre-Built Enterprise Architecture," to draw the eye to the specific sub-topic per section (per diagram/screenshot Val referenced).

## Pre-existing, unrelated issues noticed (not touched — out of scope for this pass)

- `build_and_test/genai-logic/README.md` (and now `prototypes/manager/README.md`, since it was resynced from the same converted content) has several malformed nested-link artifacts from the mkdocs→markdown link-rewrite, e.g.:
  `(https://apilogicserver.github.io/Docs/[↗](https://github.com/.../prompt))` — the rewrite appears to have double-wrapped a link. Visible around the "Budget allocation system" / "Canadian CBSA" bullets (~lines 416-427 in the mirror).
- Same conversion also strips `.md` from some but not all GitHub blob-URL links (e.g. `.../prompt.md` → `.../prompt`), inconsistently, in a handful of places. Pre-existing, not introduced this session.

## Open question for Val

Whether/how to add a distinct cold-read entry point before recommending this link to evaluators — e.g., a short note after the intro paragraph (before "## 🚀 First Time Here?") framed as "Browsing on GitHub? Skip to [Evidence section] — or clone and run it yourself" — versus leaving the tour section as tour-only and judging whether the later sections alone carry enough weight for a GitHub-only reader.
