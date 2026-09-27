This sample revealed:

* AI can infer requirements from db design/naming — must be written back into
  requirements.md, not silently coded
* Two distinct gaps found on `Patient.consecutive_absences`:
    1. **Streak vs. count**: `count(Attendance where status=='absent')` is a lifetime
       total; the column name demands reset-on-attendance streak semantics — no rule
       type expresses that directly (needs a fold/accumulator)
    2. **Absence of an event**: nothing ever writes an `absent` Attendance row in
       production (a no-show is a non-event, not an update) — no LogicBank rule can
       react to a row that never arrives
* Why this matters concretely (`exertion_dropoff` clause 3, Care Team Drop-Off
  Alert): a patient doing high-exertion sessions who then misses 2+ classes **in a
  row** is a real clinical signal (possible injury/health event) and should trigger
  a nurse follow-up alert — but only while the miss streak is current. A patient
  who missed 2 classes months ago and has attended reliably since must NOT still
  read as flagged; the streak has to reset on any attended/excused class. This
  confirms an update event genuinely cannot catch this: there is no Attendance row
  to update when a class is simply missed, so nothing exists for a rule to react to
  in the first place — the gap isn't a modeling oversight, it's structural.
* Fix: block on #2 — don't guess a trigger mechanism, and don't implement/test the
  reactive logic either (a hand-seeded test would pass while proving nothing about
  production). FIXME + ad-libs candidate strategies only, until the user decides.
* One candidate strategy worth keeping: skip synthesizing an absent row at all —
  have the child (Attendance) post its own last-attended date onto the parent
  (Patient.last_attended_date), then derive "periods missed" on demand (in a rule
  or a report) by comparing that date to the current date/expected schedule. No
  event needed for the non-occurrence itself; the gap is computed, not stored.
* Validated twice (blind agent + direct build) against a hint-free fixture — same
  bugs, same correct blocking behavior both times.
* Best-practice shape for strategy (a), absent a "heartbeat transaction":
    1. `Patient.last_attendance_date` — a normal reactive rule (Rule.formula/copy),
       set whenever an Attendance row (attended/excused) is written. No gap here;
       this part is a real event LogicBank can react to.
    2. A daily scheduled job (outside LogicBank — rules only fire on commits, not
       the calendar) that finds patients stale past N *expected* classes (compare
       against ClassSchedule, not raw elapsed days) and with prior high-exertion
       sessions, then does the actual write.
    3. Two sub-choices the job must make, not LogicBank's concern:
       - Backfill `Attendance(status='absent')` rows (preserves honest history,
         existing count/streak rules work unmodified) vs. dispatch the alert
         directly (simpler, but leaves a silent gap in attendance history).
       - Dedup/idempotency — don't re-dispatch the same alert daily for one
         ongoing streak; check for an existing unresolved alert first.
    4. On a clustered/multi-replica deployment, the "who runs the daily job"
       question is an infra concern, not application code:
       - Preferred: a K8s `CronJob` (or cloud equivalent — AWS EventBridge
         Scheduler, GCP Cloud Scheduler) as a separate one-off pod/task, with
         `concurrencyPolicy: Forbid` so an overrunning previous run isn't
         duplicated. This sidesteps multi-replica races entirely — the job runs
         as one pod, not inside every app replica.
       - Only if the timer must live inside the app process itself: a
         distributed lock (DB row lock / `SELECT ... FOR UPDATE SKIP LOCKED`,
         or Redis-based) so only one replica executes per tick.
