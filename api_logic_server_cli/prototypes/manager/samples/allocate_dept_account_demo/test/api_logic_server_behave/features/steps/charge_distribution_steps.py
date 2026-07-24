from behave import *
import requests, test_utils, time
from decimal import Decimal

BASE_URL = 'http://localhost:5656'


def _post(url, data, headers=None):
    return requests.post(url, json=data, headers=headers or {})

def _patch(url, data, headers=None):
    return requests.patch(url, json=data, headers=headers or {})

def _get(url, headers=None):
    return requests.get(url, headers=headers or {})


# ─── GIVEN ────────────────────────────────────────────────────────────────────

@given('a funding setup with Roads 60% / Construction 40%')
def step_funding_setup_full(context):
    _build_funding_setup(context, roads_pct=60, construction_pct=40, complete=True)


@given('a funding setup with Roads 60% / Construction 40% missing a line')
def step_funding_setup_partial(context):
    _build_funding_setup(context, roads_pct=60, construction_pct=40, complete=False)


@given('Roads splits to Labor 60% / Equipment 40%')
def step_roads_split(context):
    _build_dept_charge_definition(context, dept_key='roads',
                                   lines=[('roads_labor', 60), ('roads_equipment', 40)])


@given('Construction splits to Labor 70% / Materials 30%')
def step_construction_split(context):
    _build_dept_charge_definition(context, dept_key='construction',
                                   lines=[('construction_labor', 70), ('construction_materials', 30)])


# ─── WHEN ─────────────────────────────────────────────────────────────────────

@when('a Charge of {amount:d} is posted to the Project')
def step_post_charge(context, amount):
    scenario_name = context.scenario.name[:25]
    context.scenario_name = scenario_name
    test_utils.prt(f'\n{scenario_name}\n', scenario_name)
    _post_charge(context, amount)


@when('a second Charge of {amount:d} is posted to the same Project')
def step_post_second_charge(context, amount):
    _post_charge(context, amount, is_second=True)


@when('the Roads funding line percent is later changed to {new_percent:d}')
def step_change_funding_line_percent(context, new_percent):
    r = _patch(f'{BASE_URL}/api/ProjectFundingLine/{context.roads_funding_line_id}/', {"data": {
        "type": "ProjectFundingLine", "id": context.roads_funding_line_id,
        "attributes": {"percent": new_percent}
    }})
    assert r.status_code == 200, f"ProjectFundingLine patch failed: {r.text}"


# ─── THEN ─────────────────────────────────────────────────────────────────────

@then('Charge total_distributed_amount is {expected:g}')
def step_check_charge_total_distributed(context, expected):
    r = _get(f'{BASE_URL}/api/Charge/{context.charge_id}/')
    assert r.status_code == 200, f"Charge GET failed: {r.text}"
    actual = float(r.json()['data']['attributes']['total_distributed_amount'])
    assert abs(actual - expected) < 0.01, f"total_distributed_amount: expected {expected}, got {actual}"


@then('ChargeDeptAllocation amounts are {amount1:g} and {amount2:g}')
def step_check_dept_allocation_amounts(context, amount1, amount2):
    r = _get(f'{BASE_URL}/api/Charge/{context.charge_id}/ChargeDeptAllocationList')
    assert r.status_code == 200, f"ChargeDeptAllocationList GET failed: {r.text}"
    amounts = sorted(float(row['attributes']['amount']) for row in r.json()['data'])
    expected = sorted([amount1, amount2])
    assert len(amounts) == 2, f"Expected 2 ChargeDeptAllocation rows, got {len(amounts)}: {amounts}"
    for actual, exp in zip(amounts, expected):
        assert abs(actual - exp) < 0.01, f"ChargeDeptAllocation amounts: expected {expected}, got {amounts}"


@then('ChargeGlAllocation amounts for Roads are {amount1:g} and {amount2:g}')
def step_check_gl_allocation_roads(context, amount1, amount2):
    _check_gl_allocation_amounts(context, context.roads_dept_allocation_id, [amount1, amount2])


@then('ChargeGlAllocation amounts for Construction are {amount1:g} and {amount2:g}')
def step_check_gl_allocation_construction(context, amount1, amount2):
    _check_gl_allocation_amounts(context, context.construction_dept_allocation_id, [amount1, amount2])


@then('Project total_charges is {expected:g}')
def step_check_project_total_charges(context, expected):
    r = _get(f'{BASE_URL}/api/Project/{context.project_id}/')
    assert r.status_code == 200, f"Project GET failed: {r.text}"
    actual = float(r.json()['data']['attributes']['total_charges'])
    assert abs(actual - expected) < 0.01, f"Project total_charges: expected {expected}, got {actual}"


@then('Roads Labor GlAccount total_allocated is {expected:g}')
def step_check_roads_labor_gl_total(context, expected):
    _check_gl_account_total_allocated(context, context.gl_ids['roads_labor'], expected)


@then('Roads Equipment GlAccount total_allocated is {expected:g}')
def step_check_roads_equipment_gl_total(context, expected):
    _check_gl_account_total_allocated(context, context.gl_ids['roads_equipment'], expected)


@then('Charge is rejected with inactive funding error')
def step_check_charge_rejected(context):
    assert context.charge_rejected, "Expected Charge post to be rejected but it was accepted"
    assert 'active' in context.charge_error_text.lower(), \
        f"Expected 'active' funding error, got: {context.charge_error_text}"


@then('the existing ChargeDeptAllocation percent for Roads is still {expected:g}')
def step_check_frozen_percent(context, expected):
    r = _get(f'{BASE_URL}/api/ChargeDeptAllocation/{context.roads_dept_allocation_id}/')
    assert r.status_code == 200, f"ChargeDeptAllocation GET failed: {r.text}"
    actual = float(r.json()['data']['attributes']['percent'])
    assert abs(actual - expected) < 0.01, \
        f"ChargeDeptAllocation.percent: expected frozen value {expected}, got {actual} (Rule.copy not snapshotting)"


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _unique(name):
    return f"{name} {int(time.time() * 1000)}"


def _build_funding_setup(context, roads_pct, construction_pct, complete):
    """
    Creates fresh Departments (Roads, Construction), a ProjectFundingDefinition,
    and a Project pointed at it. If complete=True, adds both funding lines
    (summing to 100 -> is_active=1). If complete=False, adds only the Roads
    line (summing to roads_pct -> is_active stays 0), to exercise the
    "not active" constraint.

    Sets context: roads_dept_id, construction_dept_id, pfd_id, project_id,
                  roads_funding_line_id
    """
    context.dept_ids = {}
    context.gl_ids = {}
    context.def_ids = {}

    # Departments
    r = _post(f'{BASE_URL}/api/Department/', {"data": {
        "type": "Department", "attributes": {"name": _unique("Roads")}}})
    assert r.status_code == 201, f"Department create failed: {r.text}"
    roads_id = int(r.json()['data']['id'])
    context.dept_ids['roads'] = roads_id

    r = _post(f'{BASE_URL}/api/Department/', {"data": {
        "type": "Department", "attributes": {"name": _unique("Construction")}}})
    assert r.status_code == 201, f"Department create failed: {r.text}"
    construction_id = int(r.json()['data']['id'])
    context.dept_ids['construction'] = construction_id

    # DeptChargeDefinitions (empty for now; filled in by the split steps)
    r = _post(f'{BASE_URL}/api/DeptChargeDefinition/', {"data": {
        "type": "DeptChargeDefinition",
        "attributes": {"department_id": roads_id, "name": _unique("Roads Split")}}})
    assert r.status_code == 201, f"DeptChargeDefinition create failed: {r.text}"
    context.def_ids['roads'] = int(r.json()['data']['id'])

    r = _post(f'{BASE_URL}/api/DeptChargeDefinition/', {"data": {
        "type": "DeptChargeDefinition",
        "attributes": {"department_id": construction_id, "name": _unique("Construction Split")}}})
    assert r.status_code == 201, f"DeptChargeDefinition create failed: {r.text}"
    context.def_ids['construction'] = int(r.json()['data']['id'])

    # ProjectFundingDefinition
    r = _post(f'{BASE_URL}/api/ProjectFundingDefinition/', {"data": {
        "type": "ProjectFundingDefinition", "attributes": {"name": _unique("Test PFD")}}})
    assert r.status_code == 201, f"ProjectFundingDefinition create failed: {r.text}"
    pfd_id = int(r.json()['data']['id'])
    context.pfd_id = pfd_id

    # Project, pointed at the (not-yet-active) PFD
    r = _post(f'{BASE_URL}/api/Project/', {"data": {
        "type": "Project",
        "attributes": {"name": _unique("Test Project"), "project_funding_definition_id": pfd_id}}})
    assert r.status_code == 201, f"Project create failed: {r.text}"
    context.project_id = int(r.json()['data']['id'])

    # Roads funding line (always present)
    r = _post(f'{BASE_URL}/api/ProjectFundingLine/', {"data": {
        "type": "ProjectFundingLine",
        "attributes": {
            "project_funding_definition_id": pfd_id,
            "department_id": roads_id,
            "dept_charge_definition_id": context.def_ids['roads'],
            "percent": roads_pct}}})
    assert r.status_code == 201, f"ProjectFundingLine (Roads) create failed: {r.text}"
    context.roads_funding_line_id = int(r.json()['data']['id'])

    if complete:
        # Construction funding line -- brings total to 100, PFD becomes active
        r = _post(f'{BASE_URL}/api/ProjectFundingLine/', {"data": {
            "type": "ProjectFundingLine",
            "attributes": {
                "project_funding_definition_id": pfd_id,
                "department_id": construction_id,
                "dept_charge_definition_id": context.def_ids['construction'],
                "percent": construction_pct}}})
        assert r.status_code == 201, f"ProjectFundingLine (Construction) create failed: {r.text}"
        context.construction_funding_line_id = int(r.json()['data']['id'])
    # else: leave PFD partially funded (total_percent = roads_pct, is_active stays 0)


def _build_dept_charge_definition(context, dept_key, lines):
    """
    Adds DeptChargeDefinitionLine rows (GL account + percent) to the
    DeptChargeDefinition created in _build_funding_setup for dept_key
    ('roads' or 'construction'). lines: list of (gl_key, percent) tuples.
    Once the lines sum to 100, DeptChargeDefinition.is_active becomes 1.
    """
    dept_id = context.dept_ids[dept_key]
    def_id = context.def_ids[dept_key]
    for i, (gl_key, percent) in enumerate(lines):
        r = _post(f'{BASE_URL}/api/GlAccount/', {"data": {
            "type": "GlAccount",
            "attributes": {
                "department_id": dept_id,
                "account_number": f"{int(time.time() * 1000) % 100000}{i}",
                "name": _unique(gl_key)}}})
        assert r.status_code == 201, f"GlAccount create failed: {r.text}"
        gl_id = int(r.json()['data']['id'])
        context.gl_ids[gl_key] = gl_id

        r = _post(f'{BASE_URL}/api/DeptChargeDefinitionLine/', {"data": {
            "type": "DeptChargeDefinitionLine",
            "attributes": {
                "dept_charge_definition_id": def_id,
                "gl_account_id": gl_id,
                "percent": percent}}})
        assert r.status_code == 201, f"DeptChargeDefinitionLine create failed: {r.text}"


def _post_charge(context, amount, is_second=False):
    """
    Posts a Charge against context.project_id.
    Sets context: charge_id (or charge_id_2 if is_second), charge_rejected,
                  charge_error_text, roads_dept_allocation_id,
                  construction_dept_allocation_id (from ChargeDeptAllocationList)
    """
    r = _post(f'{BASE_URL}/api/Charge/', {"data": {
        "type": "Charge",
        "attributes": {
            "project_id": context.project_id,
            "amount": amount,
            "description": "Behave test charge"}}})
    if r.status_code >= 300:
        context.charge_rejected = True
        context.charge_error_text = r.text
        context.charge_id = None
        return
    context.charge_rejected = False
    charge_id = int(r.json()['data']['id'])
    if is_second:
        context.charge_id_2 = charge_id
    else:
        context.charge_id = charge_id

    # Fetch the ChargeDeptAllocation rows created by the cascade, and map
    # them to roads/construction by department_id for later assertions.
    r = _get(f'{BASE_URL}/api/Charge/{charge_id}/ChargeDeptAllocationList')
    assert r.status_code == 200, f"ChargeDeptAllocationList GET failed: {r.text}"
    for row in r.json()['data']:
        dept_alloc_id = int(row['id'])
        dept_id = row['attributes']['department_id']
        if dept_id == context.dept_ids.get('roads'):
            context.roads_dept_allocation_id = dept_alloc_id
        elif dept_id == context.dept_ids.get('construction'):
            context.construction_dept_allocation_id = dept_alloc_id


def _check_gl_allocation_amounts(context, dept_allocation_id, expected_amounts):
    r = _get(f'{BASE_URL}/api/ChargeDeptAllocation/{dept_allocation_id}/ChargeGlAllocationList')
    assert r.status_code == 200, f"ChargeGlAllocationList GET failed: {r.text}"
    amounts = sorted(float(row['attributes']['amount']) for row in r.json()['data'])
    expected = sorted(expected_amounts)
    assert len(amounts) == 2, f"Expected 2 ChargeGlAllocation rows, got {len(amounts)}: {amounts}"
    for actual, exp in zip(amounts, expected):
        assert abs(actual - exp) < 0.01, f"ChargeGlAllocation amounts: expected {expected}, got {amounts}"


def _check_gl_account_total_allocated(context, gl_account_id, expected):
    r = _get(f'{BASE_URL}/api/GlAccount/{gl_account_id}/')
    assert r.status_code == 200, f"GlAccount GET failed: {r.text}"
    actual = float(r.json()['data']['attributes']['total_allocated'])
    assert abs(actual - expected) < 0.01, f"GlAccount.total_allocated: expected {expected}, got {actual}"
