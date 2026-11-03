# Failure to post

Logic about a row that never arrives. A rule only reacts to a row being written; nothing fires when an expected row (an absence record, a payment, a renewal) is never posted.

| Project | What it shows |
|---|---|
| `students_courses` | A CE regression fixture. The course drop-off alert depends on an `Attendance(status='absent')` row that nothing writes. The AI should notice this unaided, leave that clause blocked, and list candidate strategies in `ad-libs.md` |
| `students_courses_sweep` | The same project one phase further: an externally triggered sweep endpoint plus an `Enrollment` table writes the missing row, so the blocked clause can be turned on |

The spec set for the second phase is `samples/requirements/students_courses_attendance_sweep`. The pattern is documented in the CE as "Absence of an Event" (`docs/training/logic_bank_api.md`).
