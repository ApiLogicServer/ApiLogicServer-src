#!/usr/bin/env python
import os, logging, logging.config, sys
from config import server_setup
import api.system.api_utils as api_utils
from flask import Flask
import logging
import config.config as config

os.environ["PROJECT_DIR"] = os.environ.get("PROJECT_DIR", os.path.abspath(os.path.dirname(__file__)))

app_logger = server_setup.logging_setup()
app_logger.setLevel(logging.INFO) 

current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.extend([current_path, '.'])

flask_app = Flask("API Logic Server", template_folder='ui/templates')
flask_app.config.from_object(config.Config)
flask_app.config.from_prefixed_env(prefix="APILOGICPROJECT")

args = server_setup.get_args(flask_app)

server_setup.api_logic_server_setup(flask_app, args)

from database.models import *
import safrs
from datetime import date
import os
os.environ['AGGREGATE_DEFAULTS'] = 'True'

with flask_app.app_context():
    safrs.DB.create_all()

    session = safrs.DB.session

    # ── Departments ───────────────────────────────────────────────────────────
    roads = Department(name="Roads & Bridges")
    construction = Department(name="Construction")
    session.add_all([roads, construction])
    session.flush()

    # ── GL Accounts ───────────────────────────────────────────────────────────
    roads_labor    = GlAccount(department_id=roads.id,        account_number="5001", name="Roads Labor")
    roads_equip    = GlAccount(department_id=roads.id,        account_number="5002", name="Roads Equipment")
    const_labor    = GlAccount(department_id=construction.id, account_number="6001", name="Construction Labor")
    const_material = GlAccount(department_id=construction.id, account_number="6002", name="Construction Materials")
    session.add_all([roads_labor, roads_equip, const_labor, const_material])
    session.flush()

    # ── Dept Charge Definitions ───────────────────────────────────────────────
    roads_def = DeptChargeDefinition(department_id=roads.id, name="Roads Standard Split")
    const_def = DeptChargeDefinition(department_id=construction.id, name="Construction Standard Split")
    session.add_all([roads_def, const_def])
    session.flush()

    # Lines — must sum to 100 each for is_active=1
    session.add_all([
        DeptChargeDefinitionLine(dept_charge_definition_id=roads_def.id, gl_account_id=roads_labor.id, percent=60),
        DeptChargeDefinitionLine(dept_charge_definition_id=roads_def.id, gl_account_id=roads_equip.id, percent=40),
        DeptChargeDefinitionLine(dept_charge_definition_id=const_def.id, gl_account_id=const_labor.id, percent=70),
        DeptChargeDefinitionLine(dept_charge_definition_id=const_def.id, gl_account_id=const_material.id, percent=30),
    ])
    session.commit()  # triggers is_active derivations

    # ── Project Funding Definition ────────────────────────────────────────────
    joint_pfd = ProjectFundingDefinition(name="Joint Roads+Construction Funding")
    session.add(joint_pfd)
    session.flush()

    session.add_all([
        ProjectFundingLine(
            project_funding_definition_id=joint_pfd.id,
            department_id=roads.id,
            dept_charge_definition_id=roads_def.id,
            percent=60,
        ),
        ProjectFundingLine(
            project_funding_definition_id=joint_pfd.id,
            department_id=construction.id,
            dept_charge_definition_id=const_def.id,
            percent=40,
        ),
    ])
    session.commit()  # triggers is_active derivation on joint_pfd

    # ── Projects ──────────────────────────────────────────────────────────────
    highway_project = Project(name="Highway 1 Expansion", project_funding_definition_id=joint_pfd.id)
    bridge_project  = Project(name="Bridge Restoration",  project_funding_definition_id=joint_pfd.id)
    session.add_all([highway_project, bridge_project])
    session.commit()

    # ── Contractors ───────────────────────────────────────────────────────────
    acme   = Contractor(name="ACME Road Builders")
    summit = Contractor(name="Summit Construction Inc")
    session.add_all([acme, summit])
    session.commit()

    # ── Sample Charge (explicit project_id — no AI needed) ───────────────────
    # This charge triggers the cascade allocation automatically.
    charge1 = Charge(
        project_id=highway_project.id,
        contractor_id=acme.id,
        amount=100000,
        description="Asphalt resurfacing — Phase 1",
        charge_date="2026-03-12",
    )
    session.add(charge1)
    session.commit()

    # ── Sample Charge with fuzzy description (AI project matching) ───────────
    charge2 = Charge(
        contractor_id=acme.id,
        project_description="highway expansion road work",   # no project_id — AI will identify
        amount=50000,
        description="Line markings and signage",
        charge_date="2026-03-12",
    )
    session.add(charge2)
    session.commit()

    print("Seed data loaded successfully.")
    print(f"  Roads Def is_active={roads_def.is_active}  total_percent={roads_def.total_percent}")
    print(f"  Const Def is_active={const_def.is_active}  total_percent={const_def.total_percent}")
    print(f"  PFD is_active={joint_pfd.is_active}  total_percent={joint_pfd.total_percent}")
    print(f"  Charge1 total_distributed={charge1.total_distributed_amount}")
    print(f"  Charge2 project_id={charge2.project_id}  total_distributed={charge2.total_distributed_amount}")
    print(f"  Roads Labor GL total_allocated={roads_labor.total_allocated}")
    print(f"  Roads Equip GL total_allocated={roads_equip.total_allocated}")
    print(f"  Const Labor GL total_allocated={const_labor.total_allocated}")
    print(f"  Const Material GL total_allocated={const_material.total_allocated}")

