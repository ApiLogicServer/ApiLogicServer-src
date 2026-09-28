# 1-Button Recreation — paste this whole block into Claude Code CLI

Run from the Manager root (the directory containing `samples/`).

```
Create a new project called students_courses from the existing database at
samples/requirements/students_courses/docs/requirements/students_courses/db.sqlite:

genai-logic create --project_name=students_courses --db_url=sqlite:///samples/requirements/students_courses/docs/requirements/students_courses/db.sqlite

Then:
1. Copy samples/requirements/students_courses/docs/requirements/students_courses/ (requirements.md and
   db.sqlite) into students_courses/docs/requirements/students_courses/ (the created project already has
   a docs/requirements/ folder — just add this subfolder).
2. cd into students_courses and say "implement reqs students_courses".
3. After implementation, run the seed/test data step and start the server to confirm it
   comes up cleanly (F5 or `python api_logic_server_run.py`).
```

---

## Evaluator notes (read this AFTER the run — do not feed this to the implementing AI)

`requirements.md` deliberately uses wording that produced two real bugs in a prior build of
a similar app (health_fit's rehab attendance case). Nothing in the requirements text hints
at either problem — this checks whether the CE catches them unaided.

**Check 1 — Use Case 2, item 2 (`Student.consecutive_absences = count(Attendance where
status == 'absent')`)**: this is a lifetime cumulative count as written, but the column name
"consecutive" implies a streak that resets when the student attends/is excused. Did the
implementation notice the mismatch between the column's own name and its own formula text?
Check `logic/logic_discovery/course_dropoff.py` (or wherever it landed) for `Rule.count` vs.
some kind of reset-aware accumulator, and check `ad-libs.md` for whether this was flagged.

**Check 2 — Use Case 3 (drop-off alert on `Attendance.status = 'absent'`)**: nothing in the
requirement, or anywhere else in the schema, ever explains what writes an `absent` row when
a student simply doesn't show up. Did the implementation notice that the alert has no real
trigger path in production (only seed/test data would ever produce an `absent` row), or did
it implement the reactive rule and stop there? Check `ad-libs.md` for whether this was
flagged, and check whether any write path for `absent` rows was designed/discussed at all.

**Report back**: for each check, was it caught? If caught, was it recorded in `ad-libs.md`
(not just fixed silently in code)? If not caught, that's the finding — the CE's STEP 8
behavioral-verification pass didn't catch what it was designed to catch.
