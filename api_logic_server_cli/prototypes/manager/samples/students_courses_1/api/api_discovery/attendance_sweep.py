import hmac
import logging
import os
from datetime import datetime

import safrs
from flask import request, jsonify

from database import models

app_logger = logging.getLogger("api_logic_server_app")

API_KEY_HEADER = "X-Api-Key"
API_KEY_ENV = "ATTENDANCE_SWEEP_API_KEY"


def _authorized() -> bool:
    """Service credential check (separate from user JWT / declare_security.py grants).
    Fails closed: if no key is configured in the environment, every call is refused."""
    expected = os.getenv(API_KEY_ENV, "")
    supplied = request.headers.get(API_KEY_HEADER, "")
    return bool(expected) and hmac.compare_digest(expected, supplied)


def _parse_when(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _session_end(cs: models.ClassSchedule) -> datetime | None:
    """End of a ClassSchedule: end_time if it is a full ISO datetime, else session_date + end_time
    (time-only), else end of session_date."""
    if not cs.session_date:
        return None
    try:
        if cs.end_time:
            try:
                return datetime.fromisoformat(cs.end_time)
            except ValueError:
                return datetime.fromisoformat(f"{cs.session_date}T{cs.end_time}")
        return datetime.fromisoformat(f"{cs.session_date}T23:59:59")
    except ValueError:
        app_logger.warning(f"attendance_sweep: unparseable times on ClassSchedule {cs.id}")
        return None


def sweep_session(session, cs: models.ClassSchedule, now: datetime) -> int:
    """Insert Attendance(status='absent') for each Enrollment of cs's course with no
    Attendance row for (student, cs). A normal domain insert - LogicBank rules fire on commit."""
    present = {sid for (sid,) in session.query(models.Attendance.student_id)
               .filter(models.Attendance.class_schedule_id == cs.id)}
    enrolled = session.query(models.Enrollment).filter(models.Enrollment.course_id == cs.course_id) \
        .order_by(models.Enrollment.student_id).all()
    inserted = 0
    for enrollment in enrolled:
        if enrollment.student_id not in present:
            session.add(models.Attendance(student_id=enrollment.student_id,
                                          class_schedule_id=cs.id, status='absent'))
            inserted += 1
    cs.swept_at = now.isoformat()
    session.commit()
    return inserted


def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators=[]):

    @app.route('/api/attendance_sweep', methods=['POST'])
    def attendance_sweep():
        """
        Insert Attendance(status='absent') for every enrolled student with no Attendance row for
        an ended class session (the write path course_dropoff's streak/alert logic depends on).

        Called by an external scheduler. Requires header X-Api-Key matching env
        ATTENDANCE_SWEEP_API_KEY. Body (all optional):
            {"class_schedule_id": 47, "todays_date": "2026-09-08T11:00:00"}
        class_schedule_id null = every ended, not-yet-swept session; todays_date = test-only "now".
        """
        if not _authorized():
            return jsonify({"error": "invalid or missing service credential"}), 401
        body = request.get_json(silent=True) or {}
        class_schedule_id = body.get("class_schedule_id")
        try:
            now = _parse_when(body["todays_date"]) if body.get("todays_date") else datetime.now()
        except (TypeError, ValueError):
            return jsonify({"error": "todays_date must be an ISO date/datetime"}), 400

        session = safrs.DB.session
        try:
            if class_schedule_id is not None:
                cs = session.get(models.ClassSchedule, class_schedule_id)
                if cs is None:
                    return jsonify({"error": f"ClassSchedule {class_schedule_id} not found"}), 404
                candidates = [cs]
            else:
                candidates = [cs for cs in session.query(models.ClassSchedule)
                              .filter(models.ClassSchedule.swept_at.is_(None)).all()
                              if (end := _session_end(cs)) is not None and end <= now]
            # chronological order: the absence streak depends on insert order
            candidates.sort(key=lambda c: (_session_end(c) or datetime.min, c.id))
            results = [{"class_schedule_id": cs.id, "course_id": cs.course_id,
                        "absent_rows_inserted": sweep_session(session, cs, now)} for cs in candidates]
        except Exception as e:
            session.rollback()
            app_logger.exception("attendance_sweep failed")
            return jsonify({"error": "sweep failed", "details": str(e)}), 400
        app_logger.info(f"attendance_sweep: {results}")
        return jsonify({"as_of": now.isoformat(), "sessions_processed": results})
