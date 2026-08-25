# Executable Requirements — Handling Updates

**Q (Val):** We do store the requirements, but it's really just doc
(`basic_demo/docs/requirements`). How would the user indicate: this
`<string>` updates that reqmt?

**A:**

The index already exists — `project_creation_report.md`'s "## Use Cases"
section, keyed by use-case folder name (`check_credit`, `app_integration`),
each with a one-line description and link. That's the addressable handle.
No new file format needed.

The mechanism: the user names the use case, and the string is applied as an
edit to that folder's `requirements.md`, not appended as a new file.

- **Explicit (fast path):** "Update check_credit: also exclude cancelled
  orders from the balance sum." The AI matches `check_credit` against the
  existing index, opens that `requirements.md`, and merges the change into
  the numbered list in place — same file, same numbering discipline,
  diffable like a code change.

- **Implicit (natural-language path, no name given):** "The credit check
  should also exclude cancelled orders." CE guidance should say: before
  treating input as a new use case, search the Use Cases index in
  `project_creation_report.md` for a content match. If found, propose it
  back — "This updates check_credit (item 2, the balance rollup) —
  confirm?" — same confirm-before-lock pattern RFI already uses. Only
  creates a new folder if there's no match or the user says it's new.

Either way, the actual "update" is just an in-place edit to the existing
numbered list, so requirements stay a literal diffable build script rather
than a pile of loose revision strings. `ad-libs.md` picks up any judgment
call made in resolving ambiguous matches, same as it does today for new use
cases.

Open scope call: whether the match/confirm step (implicit path) is worth
building now, or whether "always name the use case" is good enough as a v1
convention.
