"""
AI Project Identification — Probabilistic Logic Handler

When a contractor posts a Charge with only a project_description (no project_id),
this handler uses AI (or a keyword/history fallback) to fuzzy-match the description
to an active Project, then sets Charge.project_id.

Request Pattern:
  - Request fields:  contractor_id, project_description
  - Response fields: matched_project_id, confidence, reason, request

The early_row_event on Charge (registered in charge_distribution.py BEFORE Allocate)
calls identify_project_for_charge(), which inserts a SysProjectReq to trigger this
handler and then reads back matched_project_id.

version: 1.0
date: March 12, 2026
"""
from __future__ import annotations

import os
from datetime import datetime
from logic_bank.logic_bank import Rule
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models


# ── SysProjectReq handler ────────────────────────────────────────────────────

def declare_logic():
    """Register early_row_event on SysProjectReq to perform AI project matching."""
    Rule.early_row_event(on_class=models.SysProjectReq, calling=_identify_project)


def _identify_project(row: models.SysProjectReq, old_row, logic_row: LogicRow):
    """
    Fires when a SysProjectReq is inserted.
    Populates matched_project_id, confidence, reason.
    """
    if not logic_row.is_inserted():
        return

    row.created_on = datetime.utcnow().isoformat()
    description = (row.project_description or "").lower()

    # Gather all active projects (those with an active ProjectFundingDefinition)
    session = logic_row.session
    active_projects = (
        session.query(models.Project)
        .join(models.ProjectFundingDefinition,
              models.Project.project_funding_definition_id == models.ProjectFundingDefinition.id)
        .filter(models.ProjectFundingDefinition.is_active == 1)
        .all()
    )

    # ── Build rich context for the request audit field ───────────────────────
    candidate_summary = ", ".join(
        f"id={p.id} '{p.name}'" for p in active_projects
    ) or "(none)"

    # Collect past projects this contractor has billed (for context weighting)
    past_project_ids: list[int] = []
    if row.contractor_id:
        past_charges = (
            session.query(models.Charge.project_id)
            .filter(
                models.Charge.contractor_id == row.contractor_id,
                models.Charge.project_id.isnot(None),
            )
            .distinct()
            .all()
        )
        past_project_ids = [r[0] for r in past_charges]

    past_names = []
    for pid in past_project_ids:
        p = session.query(models.Project).filter(models.Project.id == pid).first()
        if p:
            past_names.append(f"id={p.id} '{p.name}'")
    past_summary = ", ".join(past_names) or "(none)"

    row.request = (
        f"Match description='{description}' | "
        f"active_projects=[{candidate_summary}] | "
        f"contractor_past=[{past_summary}]"
    )

    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key and active_projects:
        matched, confidence, reason = _ai_match(
            description, active_projects, past_project_ids, api_key
        )
    else:
        matched, confidence, reason = _keyword_match(
            description, active_projects, past_project_ids
        )

    if matched:
        row.matched_project_id = matched.id
        row.confidence = confidence
        row.reason = reason
        logic_row.log(
            f"Project identified: id={matched.id} '{matched.name}' "
            f"confidence={confidence:.2f} reason={reason}"
        )
    else:
        row.matched_project_id = None
        row.confidence = 0.0
        row.reason = "No active project matched the description"
        logic_row.log("No project match found for charge description")


# ── Keyword / history fallback ───────────────────────────────────────────────

def _keyword_match(
    description: str,
    active_projects: list,
    past_project_ids: list[int],
) -> tuple:
    """
    Score each active project by keyword overlap + past-billing bonus.
    Returns (project | None, confidence, reason).
    """
    best = None
    best_score = 0
    best_reason = ""

    for project in active_projects:
        name_tokens = set(project.name.lower().split())
        desc_tokens  = set(description.split())
        overlap = name_tokens & desc_tokens
        score = len(overlap) * 10

        # Bonus for past billing by this contractor
        if project.id in past_project_ids:
            score += 20

        if score > best_score:
            best_score = score
            best = project
            best_reason = (
                f"keyword match: {overlap} | "
                f"past_billing={'yes' if project.id in past_project_ids else 'no'}"
            )

    if best and best_score > 0:
        return best, min(best_score / 50.0, 1.0), best_reason
    # No overlap — prefer a past project if any active
    if past_project_ids:
        for project in active_projects:
            if project.id in past_project_ids:
                return project, 0.3, "fallback: contractor's most-used project"
    return None, 0.0, "no match"


# ── OpenAI match ─────────────────────────────────────────────────────────────

def _ai_match(description: str, active_projects: list, past_project_ids: list[int], api_key: str) -> tuple:
    """
    Call OpenAI to select the best matching active project.
    Returns (project | None, confidence, reason).
    """
    try:
        import json
        import openai
        openai.api_key = api_key

        project_list = "\n".join(
            f"  id={p.id}: {p.name}"
            + (" [past contractor]" if p.id in past_project_ids else "")
            for p in active_projects
        )

        prompt = (
            f"A contractor submitted a charge with description: '{description}'.\n"
            f"Active projects:\n{project_list}\n\n"
            f"Select the best matching project. "
            f"Respond with JSON: {{\"project_id\": <int>, \"confidence\": <0-1 float>, \"reason\": <string>}}"
        )

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        pid = int(data["project_id"])
        matched = next((p for p in active_projects if p.id == pid), None)
        return matched, float(data.get("confidence", 0.5)), str(data.get("reason", "AI selection"))
    except Exception as exc:
        # Fallback to keyword on any AI error
        return _keyword_match(description, active_projects, past_project_ids)


# ── Wrapper called from Charge early_row_event ───────────────────────────────

def identify_project_for_charge(row: models.Charge, old_row, logic_row: LogicRow):
    """
    Early event on Charge: if project_id is missing but project_description is set,
    use AI to find the correct project and set row.project_id.

    Registered FIRST in charge_distribution.py so it fires before Allocate.
    """
    if logic_row.is_deleted():
        return
    if not logic_row.is_inserted():
        return
    # Already has a project — nothing to do
    if row.project_id is not None:
        return
    # Need a description to match on
    if not row.project_description:
        return

    logic_row.log(
        f"Charge has no project_id; using AI to match "
        f"description='{row.project_description}'"
    )

    req_lr = logic_row.new_logic_row(models.SysProjectReq)
    req = req_lr.row
    req.contractor_id = row.contractor_id
    req.project_description = row.project_description
    req_lr.insert(reason="AI project identification for charge")

    if req.matched_project_id:
        row.project_id = req.matched_project_id
        logic_row.log(
            f"AI matched project_id={row.project_id} "
            f"confidence={req.confidence:.2f}"
        )
    else:
        logic_row.log("AI could not match a project — charge will have NULL project_id")
