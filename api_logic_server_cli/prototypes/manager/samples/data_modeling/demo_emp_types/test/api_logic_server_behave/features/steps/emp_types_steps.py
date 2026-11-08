"""Steps for the demo_emp_types features (Department Budget, Employee Types, Hourly / Commissioned / Military Employees).

API only (no imports from logic/ or database/). Every scenario creates its own departments, unions and employees
(timestamped names), so the suite is repeatable. The logic log is opened once per scenario, in the first Given.
"""
import json
import re
import shlex
import time
from decimal import Decimal
from pathlib import Path

import requests
from behave import *

import test_utils

BASE = 'http://localhost:5656/api'


def _headers() -> dict:
    headers = {'Content-Type': 'application/vnd.api+json'}
    headers.update(test_utils.login())      # {} when security is disabled
    return headers


def _unique(name: str) -> str:
    return f"{name} {int(time.time() * 1000)}"


def _value(raw: str):
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def _post(resource: str, attributes: dict):
    body = {"data": {"type": resource, "attributes": attributes}}
    return requests.post(f'{BASE}/{resource}/', json=body, headers=_headers())


def _patch(resource: str, row_id: int, attributes: dict):
    body = {"data": {"type": resource, "id": str(row_id), "attributes": attributes}}
    return requests.patch(f'{BASE}/{resource}/{row_id}/', json=body, headers=_headers())


def _get(resource: str, row_id: int) -> dict:
    r = requests.get(f'{BASE}/{resource}/{row_id}/', headers=_headers())
    assert r.status_code == 200, f'GET {resource}/{row_id} failed: {r.status_code} {r.text}'
    return r.json()['data']['attributes']


def _attr_name(name: str) -> str:
    return 'Type' if name == 'type' else name       # SAFRS wire name of the 'type' column


def _parse_attrs(context, attrs: str) -> dict:
    result = {}
    for token in shlex.split(attrs):
        key, raw = token.split('=', 1)
        result[key] = context.union_id if raw == '@union' else _value(raw)
    if 'name' in result:
        result['name'] = _unique(result['name'])
    return result


def _open_log(context):
    scenario_name = re.sub(r'[\s()/\\]', '_', context.scenario.name)[:25]
    context.scenario_name = scenario_name
    test_utils.prt(f'\n\n\n{scenario_name} - starting test\n\n', scenario_name)    # once per scenario


def _create_department(budget: int, name: str) -> int:
    r = _post('Department', {"name": _unique(name), "budget": budget})
    assert r.status_code == 201, f'create Department failed: {r.status_code} {r.text}'
    return int(r.json()['data']['id'])


def _create_employee(context, emp_type: str, attrs: str, dept_id: int):
    attributes = _parse_attrs(context, attrs)
    attributes['Type'] = emp_type
    attributes['dept_id'] = dept_id
    context.response = _post('Employee', attributes)
    return context.response


def _expect(actual, expected: str, what: str):
    assert Decimal(str(actual)) == Decimal(str(expected)), f'{what}: expected {expected}, got {actual}'


# ---- Given / When: setup and actions ------------------------------------------------------------

@given('a department with budget {budget:d}')
def step_department(context, budget):
    _open_log(context)
    context.dept_id = _create_department(budget, "Dept")


@given('another department with budget {budget:d}')
def step_other_department(context, budget):
    context.dept2_id = _create_department(budget, "Other Dept")


@given('a union with dues rate {rate:g}')
def step_union(context, rate):
    r = _post('LaborUnion', {"name": _unique("Union"), "dues_rate": rate})
    assert r.status_code == 201, f'create LaborUnion failed: {r.status_code} {r.text}'
    context.union_id = int(r.json()['data']['id'])


@given('an employee of type {emp_type:w} with {attrs}')
def step_given_employee(context, emp_type, attrs):
    r = _create_employee(context, emp_type, attrs, context.dept_id)
    assert r.status_code == 201, f'create Employee failed: {r.status_code} {r.text}'
    context.emp_id = int(r.json()['data']['id'])


@given('another employee of type {emp_type:w} with {attrs}')
def step_given_other_employee(context, emp_type, attrs):
    r = _create_employee(context, emp_type, attrs, context.dept_id)
    assert r.status_code == 201, f'create other Employee failed: {r.status_code} {r.text}'
    context.emp2_id = int(r.json()['data']['id'])


@when('an employee of type {emp_type:w} is created with {attrs}')
def step_when_employee(context, emp_type, attrs):
    r = _create_employee(context, emp_type, attrs, context.dept_id)
    if r.status_code == 201:
        context.emp_id = int(r.json()['data']['id'])


@given('an order of {amount:d} is added for the employee')
@when('an order of {amount:d} is added for the employee')
def step_order(context, amount):
    context.response = _post('Order', {"employee_id": context.emp_id, "amount": amount,
                                       "customer_name": _unique("Customer")})
    if context.response.status_code == 201:
        context.order_id = int(context.response.json()['data']['id'])


@when('the employee leaves the military')
def step_leave_military(context):
    r = _patch('Employee', context.emp_id, {"military": "no", "branch": None, "rank": None, "service_years": None})
    assert r.status_code == 200, f'PATCH Employee failed: {r.status_code} {r.text}'


@when('the employee {attr:w} is changed to {value}')
def step_change_employee(context, attr, value):
    r = _patch('Employee', context.emp_id, {_attr_name(attr): _value(value)})
    assert r.status_code == 200, f'PATCH Employee failed: {r.status_code} {r.text}'


@when('the union {attr:w} is changed to {value}')
def step_change_union(context, attr, value):
    r = _patch('LaborUnion', context.union_id, {attr: _value(value)})
    assert r.status_code == 200, f'PATCH LaborUnion failed: {r.status_code} {r.text}'


@when('the order amount is changed to {amount:d}')
def step_change_order(context, amount):
    r = _patch('Order', context.order_id, {"amount": amount})
    assert r.status_code == 200, f'PATCH Order failed: {r.status_code} {r.text}'


@when('the employee is moved to the other department')
def step_move_employee(context):
    r = _patch('Employee', context.emp_id, {"dept_id": context.dept2_id})
    assert r.status_code == 200, f'move Employee failed: {r.status_code} {r.text}'


@when('the order is moved to the other employee')
def step_move_order(context):
    r = _patch('Order', context.order_id, {"employee_id": context.emp2_id})
    assert r.status_code == 200, f'move Order failed: {r.status_code} {r.text}'


@when('the employee is deleted')
def step_delete_employee(context):
    r = requests.delete(f'{BASE}/Employee/{context.emp_id}/', headers=_headers())
    assert r.status_code in (200, 204), f'DELETE Employee failed: {r.status_code} {r.text}'


@when('the order is deleted')
def step_delete_order(context):
    r = requests.delete(f'{BASE}/Order/{context.order_id}/', headers=_headers())
    assert r.status_code in (200, 204), f'DELETE Order failed: {r.status_code} {r.text}'


# ---- Then: verification --------------------------------------------------------------------------

@then('the request is accepted')
def step_accepted(context):
    assert context.response.status_code in (200, 201), \
        f'expected the request to be accepted: {context.response.status_code} {context.response.text}'


@then('the request is rejected with "{text}"')
def step_rejected(context, text):
    r = context.response
    assert r.status_code >= 400, f'expected a rejection, got {r.status_code}: {r.text}'
    assert text in r.text, f'expected "{text}" in the error, got: {r.text}'


@then('the other employee {attr:w} is {expected}')
def step_other_employee_attr(context, attr, expected):
    _expect(_get('Employee', context.emp2_id)[attr], expected, f'other employee {attr}')


@then('the employee {attr:w} is {expected}')
def step_employee_attr(context, attr, expected):
    _expect(_get('Employee', context.emp_id)[attr], expected, f'employee {attr}')


@then('the other department total_salary is {expected}')
def step_other_department_total(context, expected):
    _expect(_get('Department', context.dept2_id)['total_salary'], expected, 'other department total_salary')


@then('the department total_salary is {expected}')
def step_department_total(context, expected):
    _expect(_get('Department', context.dept_id)['total_salary'], expected, 'department total_salary')
