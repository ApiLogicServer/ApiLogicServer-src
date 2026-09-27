# 1-Button Recreation — paste this whole block into Claude Code CLI

Run from the Manager root (the directory containing `samples/`).

```
Create a new project called health_fit from the existing database at
samples/requirements/health_fit/docs/requirements/health_fit/db.sqlite:

genai-logic create --project_name=health_fit --db_url=sqlite:///samples/requirements/health_fit/docs/requirements/health_fit/db.sqlite

Then:
1. Copy samples/requirements/health_fit/docs/requirements/health_fit/ (requirements.md and
   db.sqlite) into health_fit/docs/requirements/health_fit/ (the created project already has
   a docs/requirements/ folder — just add this subfolder).
2. cd into health_fit and say "implement reqs health_fit".
3. After implementation, run the seed/test data step and start the server to confirm it
   comes up cleanly (F5 or `python api_logic_server_run.py`).
```

---

## Evaluator notes (read this AFTER the run — do not feed this to the implementing AI)

`requirements.md` deliberately reuses the original, unfixed wording that produced two real
bugs in a prior build of this app. Nothing in the requirements text hints at either problem —
this checks whether the CE catches them unaided.

**Check 1 — Use Case 2, item 2 (`Patient.consecutive_absences = count(Attendance where
status == 'absent')`)**: this is a lifetime cumulative count as written, but the column name
"consecutive" implies a streak that resets when the patient attends/is excused. Did the
implementation notice the mismatch between the column's own name and its own formula text?
Check `logic/logic_discovery/exertion_dropoff.py` (or wherever it landed) for `Rule.count` vs.
some kind of reset-aware accumulator, and check `ad-libs.md` for whether this was flagged.

**Check 2 — Use Case 2, item 3 (drop-off alert on `Attendance.status = 'absent'`)**: nothing
in the requirement, or anywhere else in the schema, ever explains what writes an `absent` row
when a patient simply doesn't show up. Did the implementation notice that the alert has no
real trigger path in production (only seed/test data would ever produce an `absent` row), or
did it implement the reactive rule and stop there? Check `ad-libs.md` for whether this was
flagged, and check whether any write path for `absent` rows was designed/discussed at all.

**Report back**: for each check, was it caught? If caught, was it recorded in `ad-libs.md`
(not just fixed silently in code)? If not caught, that's the finding — the CE's new STEP 8
behavioral-verification pass didn't catch what it was designed to catch.
