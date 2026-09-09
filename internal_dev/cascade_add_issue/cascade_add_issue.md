---
title: Cascade-Add via Plain JSON:API — Spec Limitation, Not a SAFRS Bug
Description: POSTing a parent (with a DB-generated PK) together with a list of new children
  that need that PK as their FK — e.g. an Order plus its Items — cannot be done in a single
  plain JSON:API request. This is a limitation of the JSON:API base spec itself, not a SAFRS
  defect. The spec's own answer (the Atomic Operations extension) is not implemented by SAFRS.
  The project's existing workaround (Row Dict Mapper / custom API endpoint) is the correct
  practical answer.
Source: https://jsonapi.org/format/#crud, https://jsonapi.org/ext/atomic/,
  api_logic_server_cli/prototypes/base/.github/copilot-instructions.md
  ("Creating Advanced B2B Integration APIs" / Row Dict Mapper section)
Usage: Read before telling a user "just POST the order with its items" is supported by plain
  JSON:API CRUD, or before considering whether SAFRS should be patched to support this.
version: 1.0
changelog:
  - 1.0 (Sep 9 2026) - Recorded from a conversational question (Val: "I was never able to
    explain that to the safrs team, so pretty sure it fails. Is this actually an issue with
    the JSON:API spec, or just safrs?"). No live repro built for this one — the conclusion is
    based on the JSON:API spec text and a source check of the installed `safrs` package for
    Atomic Operations / `lid` support (found none). Filed as a companion note to
    `../composite_key_issue/composite_key_issue.md`, a related-but-distinct SAFRS/JSON:API
    friction point found in the same session.
---

# Cascade-Add via Plain JSON:API — Spec Limitation, Not (Just) a SAFRS Bug

## The scenario

`POST` a new `Order` (primary key is DB-generated, e.g. SQLite `AUTOINCREMENT`) together with a
list of new `Item` rows that each need `order_id` set to that not-yet-known generated PK — i.e.
create the parent and its children in one request, with the parent→child FK back-reference
resolved automatically. This is an extremely common real-world shape ("place an order with these
line items") and does not work through plain JSON:API CRUD.

## Verdict: this is a base-spec limitation, with an official but unadopted fix

**JSON:API's core CRUD section is scoped to one resource per write.** `POST` to a collection
creates exactly one resource. Its `relationships` member can *link* that new resource to
resources that already exist (identified by `type`+`id`), but the base spec has no mechanism
for creating several new resources in one request and having them reference each other before
any of them have server-assigned ids. This is a deliberate simplicity/statelessness choice in
the base spec — not an oversight, and not something a client can work around with clever request
shaping.

**The spec's own answer is the [Atomic Operations extension](https://jsonapi.org/ext/atomic/)**
— an official JSON:API extension (opted into via the `ext` parameter on the media type), not
part of the base spec. It defines an `atomic:operations` request containing an ordered array of
add/update/remove operations, where an operation creating a new resource may carry a client-
supplied `lid` (local id) instead of a server `id`. A *later* operation in the same array can
reference that `lid` to link to the not-yet-persisted resource. This is exactly the mechanism
needed for "create Order, then create Items pointing at it" in one atomic request. Some JSON:API
server implementations support this extension; **SAFRS does not**.

**Confirmed by source inspection** (`venv/.../site-packages/safrs/`, installed version as of this
session): no handling of `atomic:operations`, no `lid` resolution, and no request-side use of
the `included` member for compound creates (the `included` member is documented and used only on
the *response* side, to return related resources alongside primary data — `jsonapi.py` comments
confirm this: "included: an array of resource objects that are related to the primary data...").
So the failure Val describes ("I was never able to explain that to the SAFRS team") is real and
expected: plain JSON:API POST, as SAFRS implements it, has no path to this at all — not a bug to
report against a specific SAFRS version, but a feature SAFRS never built (matching the base
spec's own scope, since Atomic Operations is optional).

## The existing, correct workaround: already in the CE

This is precisely why `prototypes/base/.github/.copilot-instructions.md`'s "Creating Advanced
B2B Integration APIs" section (Row Dict Mapper pattern, `OrderB2B` example) exists as a
documented, first-class pattern rather than an edge case: a plain Flask endpoint outside JSON:API
CRUD builds the whole object graph in Python (`RowDictMapper` walks nested dict structures,
including `related=[ItemB2BMapper()]` children), does `session.add()` + `session.flush()` to
obtain the generated parent PK, and sets each child's FK directly before the final commit. This
sidesteps the JSON:API spec gap entirely rather than trying to work around it within JSON:API
semantics.

**Practical guidance:** when a user asks for "create X with a list of Y" in one call, this is the
Request Pattern / B2B API pattern (see `docs/training/logic_bank_api.md` and the CE's B2B
section), not a plain JSON:API POST — do not attempt to construct a plain JSON:API request body
with nested "items" as if the framework would resolve the parent FK automatically. It won't,
and this isn't a bug to chase — it's the spec working as designed, absent the Atomic Operations
extension SAFRS doesn't implement.

## Open question / possible follow-up

Not investigated this session: whether it would be worth adding minimal Atomic-Operations-style
support to SAFRS (or a GenAI-Logic-specific equivalent) for the common "one parent + N children,
one commit" case, as an alternative to hand-writing a `RowDictMapper` per use case. No decision
made either way — flagging only that the Row Dict Mapper pattern, while it works, requires a
bespoke mapper per entity shape; a generic cascade-create endpoint (or genuine Atomic Operations
support) would remove that per-use-case authoring cost. Not pursued further in this session —
no live repro was built (unlike `../composite_key_issue/`), since the conclusion follows directly
from the spec text and a source check, not from an observed runtime failure.
