"""
Charge Distribution — Cascade Two-Level Allocation

When a Charge is inserted against a Project:
  Level 1: Allocate charge.amount to each ProjectFundingLine (per percent)
           → creates ChargeDeptAllocation rows
  Level 2: Allocate each ChargeDeptAllocation.amount to the Dept's GL Accounts
           (per DeptChargeDefinitionLine percent) → creates ChargeGlAllocation rows

Constraint: Charge may only be posted if the Project's ProjectFundingDefinition is active.

AI tie-in: identify_project_for_charge is imported here and declared FIRST as an
early_row_event on Charge so it runs before the Allocate extension.  This ensures
project_id is set before the recipients function queries funding lines.

See: docs/training/allocate.md — Variant C (Cascade) for full pattern reference.

version: 1.0
date: March 12, 2026
"""
from __future__ import annotations

from decimal import Decimal
from logic_bank.logic_bank import Rule
from logic_bank.extensions.allocate import Allocate
from logic_bank.exec_row_logic.logic_row import LogicRow
from database import models

# ── Import AI handler so we control registration order ───────────────────────
from logic.logic_discovery.ai_requests.project_identification import (
    identify_project_for_charge,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Recipients
# ═══════════════════════════════════════════════════════════════════════════════

def funding_lines_for_charge(provider: LogicRow):
    """
    Level-1 recipients: all ProjectFundingLines for this charge's project.
    Uses explicit session query (not relationship proxy) because project_id
    may have been set programmatically by the AI early_row_event.
    """
    project_id = provider.row.project_id   # scalar FK — always current
    if not project_id:
        return []
    project = provider.session.query(models.Project).filter(
        models.Project.id == project_id
    ).first()
    if not project or not project.project_funding_definition_id:
        return []
    return provider.session.query(models.ProjectFundingLine).filter(
        models.ProjectFundingLine.project_funding_definition_id
        == project.project_funding_definition_id
    ).all()


def charge_def_lines_for_dept_allocation(provider: LogicRow):
    """
    Level-2 recipients: DeptChargeDefinitionLines for this dept allocation's
    charge definition.
    Reads dept_charge_definition_id directly from the ChargeDeptAllocation row —
    it was pre-set by the Level-1 allocator (allocate_charge_to_dept) before
    insert, so it is always populated regardless of whether the FK column has
    been flushed yet.
    """
    dept_charge_def_id = provider.row.dept_charge_definition_id
    if not dept_charge_def_id:
        return []
    return provider.session.query(models.DeptChargeDefinitionLine).filter(
        models.DeptChargeDefinitionLine.dept_charge_definition_id
        == dept_charge_def_id
    ).all()


# ═══════════════════════════════════════════════════════════════════════════════
# Custom allocators
# ═══════════════════════════════════════════════════════════════════════════════

def allocate_charge_to_dept(allocation_logic_row, provider_logic_row) -> bool:
    """
    Level-1 allocator — percent-based, non-draining.
    Pre-computes percent AND amount BEFORE insert so Level-2 allocator
    (which fires as an EarlyRowEvent before copy/formula) reads correct values.
    """
    allocation = allocation_logic_row.row
    funding_line = allocation_logic_row.row.project_funding_line   # linked by Allocate
    charge = provider_logic_row.row

    allocation.department_id = funding_line.department_id
    allocation.dept_charge_definition_id = funding_line.dept_charge_definition_id
    # Pre-compute — Level-2 reads these before Rule.copy/Rule.formula run
    allocation.percent = funding_line.percent
    allocation.amount = (
        Decimal(str(charge.amount or 0))
        * Decimal(str(funding_line.percent or 0))
        / Decimal(100)
    )

    allocation_logic_row.insert(reason="Allocate charge to dept")
    return True   # always process all funding lines


def allocate_dept_to_gl(allocation_logic_row, provider_logic_row) -> bool:
    """
    Level-2 allocator — percent-based, non-draining.
    Reads dept_alloc.amount (pre-set by Level-1 allocator above) and
    pre-computes percent + amount for the GL allocation row before insert.
    """
    allocation = allocation_logic_row.row
    defn_line = allocation_logic_row.row.dept_charge_definition_line  # linked by Allocate
    dept_alloc = provider_logic_row.row   # amount already pre-set by Level-1

    allocation.gl_account_id = defn_line.gl_account_id
    # Pre-compute percent and amount
    allocation.percent = defn_line.percent
    allocation.amount = (
        Decimal(str(dept_alloc.amount or 0))
        * Decimal(str(defn_line.percent or 0))
        / Decimal(100)
    )

    allocation_logic_row.insert(reason="Allocate dept amount to GL account")
    return True   # always process all definition lines


# ═══════════════════════════════════════════════════════════════════════════════
# Logic declarations
# ═══════════════════════════════════════════════════════════════════════════════

def declare_logic():

    # ── AI project identification ────────────────────────────────────────────
    # Registered FIRST — must fire before Allocate so project_id is set.
    # Do NOT rely on auto_discovery file ordering across files.
    Rule.early_row_event(on_class=models.Charge, calling=identify_project_for_charge)

    # ── Constraint: project must have an active funding definition ────────────
    # Extract row.project_id to a local variable to prevent LogicBank dependency
    # scanner from misreading attribute names inside chained method calls.
    def check_active_funding(row: models.Charge, old_row, logic_row: LogicRow):
        if not logic_row.is_inserted():
            return
        project_id = row.project_id
        if project_id is None:
            raise Exception("Charge must be posted to a project (project_id is required)")
        project = logic_row.session.query(models.Project).filter(
            models.Project.id == project_id
        ).first()
        if project is None:
            raise Exception(f"Project id={project_id} not found")
        pfd_id = project.project_funding_definition_id
        if pfd_id is None:
            raise Exception(
                f"Project '{project.name}' has no ProjectFundingDefinition assigned"
            )
        pfd = logic_row.session.query(models.ProjectFundingDefinition).filter(
            models.ProjectFundingDefinition.id == pfd_id
        ).first()
        if pfd is None or pfd.is_active != 1:
            raise Exception(
                f"Charges may only be posted to projects with an active "
                f"ProjectFundingDefinition (project='{project.name}', "
                f"pfd='{pfd.name if pfd else 'None'}', "
                f"is_active={pfd.is_active if pfd else 'N/A'})"
            )

    # Use early_row_event so it fires AFTER project_id is set by AI handler
    # (registered second — after identify_project_for_charge above)
    Rule.early_row_event(on_class=models.Charge, calling=check_active_funding)

    # ── Level-1 companion rules ───────────────────────────────────────────────

    # Freeze percent from the funding line at charge time
    Rule.copy(
        derive=models.ChargeDeptAllocation.percent,
        from_parent=models.ProjectFundingLine.percent,
    )

    # Compute amount = charge.amount × percent / 100
    Rule.formula(
        derive=models.ChargeDeptAllocation.amount,
        as_expression=lambda row: (
            row.charge.amount * row.percent / Decimal(100)
            if row.charge and row.percent is not None
            else Decimal(0)
        ),
    )

    # Roll up to audit total on Charge
    Rule.sum(
        derive=models.Charge.total_distributed_amount,
        as_sum_of=models.ChargeDeptAllocation.amount,
    )

    # Roll up to Project.total_charges
    Rule.sum(
        derive=models.Project.total_charges,
        as_sum_of=models.Charge.amount,
    )

    # ── Level-2 companion rules ───────────────────────────────────────────────

    Rule.copy(
        derive=models.ChargeGlAllocation.percent,
        from_parent=models.DeptChargeDefinitionLine.percent,
    )

    Rule.formula(
        derive=models.ChargeGlAllocation.amount,
        as_expression=lambda row: (
            row.charge_dept_allocation.amount * row.percent / Decimal(100)
            if row.charge_dept_allocation and row.percent is not None
            else Decimal(0)
        ),
    )

    # Roll up to GlAccount.total_allocated
    Rule.sum(
        derive=models.GlAccount.total_allocated,
        as_sum_of=models.ChargeGlAllocation.amount,
    )

    # ── Level-1 Allocate: Charge → ChargeDeptAllocation ──────────────────────
    Allocate(
        provider=models.Charge,
        recipients=funding_lines_for_charge,
        creating_allocation=models.ChargeDeptAllocation,
        while_calling_allocator=allocate_charge_to_dept,
    )

    # ── Level-2 Allocate: ChargeDeptAllocation → ChargeGlAllocation ──────────
    # Fires automatically as each ChargeDeptAllocation is inserted (cascade)
    Allocate(
        provider=models.ChargeDeptAllocation,
        recipients=charge_def_lines_for_dept_allocation,
        creating_allocation=models.ChargeGlAllocation,
        while_calling_allocator=allocate_dept_to_gl,
    )
