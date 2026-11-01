"""
Steps for the customs_demo features: Subscribe to Kafka and persist shipments, Importer matching, CVLS Eligibility.

Messages are built from a reference XML (unique shipment key per scenario), written where the server can read them,
and delivered through the pipeline's debug endpoint: live through Kafka when a broker answers, else simulated.
"""
import json
import re
import time
from pathlib import Path

import requests
from behave import *
import test_utils

BASE = 'http://localhost:5656'
STEPS_DIR = Path(__file__).resolve().parent
BEHAVE_DIR = STEPS_DIR.parent.parent
PROJECT_DIR = BEHAVE_DIR.parent.parent
TEMPLATE = PROJECT_DIR / 'docs/requirements/customs_demo/message_formats/MDE-CDV-LVS-2.xml'
MESSAGE_DIR = BEHAVE_DIR / 'logs' / 'messages'
MODE_FILE = BEHAVE_DIR / 'logs' / 'delivery_modes.json'
_sequence = [0]


def headers() -> dict:
    """Auth headers (empty when security is disabled)."""
    return test_utils.login()


def record_mode(context, mode, broker=None):
    """Remember how this scenario's message was delivered, for the traceability report."""
    modes = json.loads(MODE_FILE.read_text()) if MODE_FILE.is_file() else {}
    modes[f'{context.feature.name} / {context.scenario.name}'] = {"mode": mode, **({"broker": broker} if broker else {})}
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODE_FILE.write_text(json.dumps(modes, indent=2))


def new_key() -> int:
    """A shipment key that is unique per scenario and per run."""
    _sequence[0] += 1
    return 7_000_000_000 + (int(time.time() * 10) % 100_000_000) * 10 + _sequence[0] % 10


def build_message(oid: int, account='451000010', value='3000', courier='04', office='0504', tariff='4901.99.00.91') -> str:
    """Reference message with the shipment key and the fields the scenarios vary substituted."""
    text = TEMPLATE.read_text()
    text = re.sub(r'(<LOCAL_SHIPMENT_OID_NBR>)\d+(<)', rf'\g<1>{oid}\g<2>', text)
    text = re.sub(r'(<LOCAL_PIECE_OID_NBR>)\d+(<)', rf'\g<1>{oid}\g<2>', text)
    for tag, val in (('LOCAL_CUSTOMS_VALUE_AMT', value), ('SERVICE_TYPE_CD', courier),
                     ('PLANNED_CLEARANCE_LOCATION_CD', office), ('TRPRT_BILL_TO_ACCT_NBR', account),
                     ('HARMONIZED_TARIFF_NBR', tariff)):
        text, n = re.subn(rf'(<{tag}>)[^<]*(<)', rf'\g<1>{val}\g<2>', text)
        assert n >= 1, f'template has no <{tag}>'
    return text


def write_message(oid: int, text: str, suffix='') -> str:
    """Write the message where the server can read it; returns the path relative to the project root."""
    MESSAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = MESSAGE_DIR / f'm_{oid}{suffix}.xml'
    path.write_text(text)
    return str(path.relative_to(PROJECT_DIR))


def find_blobs(oid: int) -> list:
    """The message blobs whose payload carries this shipment key."""
    r = requests.get(f'{BASE}/api/ShipmentXml/', params={"sort": "-id", "page[limit]": 60}, headers=headers())
    return [each for each in r.json()['data'] if str(oid) in (each['attributes'].get('payload') or '')]


def wait_for_blob(oid: int, count: int = 1, timeout=25):
    """Live Kafka is asynchronous: poll until `count` blobs for this shipment key are processed or have error_text."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        done = [b for b in find_blobs(oid) if b['attributes'].get('is_processed') or b['attributes'].get('error_text')]
        if len(done) >= count:
            return done
        time.sleep(0.5)
    return []


def deliver(context, text: str, mode='auto', suffix=''):
    """Send the message through the debug endpoint; sets context.consumed / error_text the same way for both modes."""
    path = write_message(context.oid, text, suffix)
    r = requests.get(f'{BASE}/consume_debug/isdc', params={"file": path, "mode": mode})
    body = r.json()
    context.consumed, context.error_text = False, None
    if r.status_code == 409:
        context.scenario.skip(body.get('error', 'live Kafka is not available'))
        return False
    record_mode(context, body.get('mode', mode), body.get('broker'))
    if body.get('mode') == 'simulated':
        context.consumed, context.error_text = bool(body.get('success')), body.get('error')
        return True
    assert body.get('published'), f'live publish failed: {r.text}'
    done = wait_for_blob(context.oid, count=context.deliveries + 1)
    assert done, f'no processed blob for shipment {context.oid} within 25 s - was the server started AFTER Kafka?'
    context.deliveries += 1
    last = done[0]['attributes']
    context.error_text = last.get('error_text')
    context.consumed = bool(last.get('is_processed')) and not context.error_text
    return True


def open_log(context):
    """Open the per-scenario logic log: ONCE per scenario, before the first API call."""
    context.scenario_name = re.sub(r'[\s()/\\]', '_', context.scenario.name)[:25]
    test_utils.prt(f'\n\n{context.scenario_name} - starting test\n\n', context.scenario_name)


def get_shipment(context) -> dict:
    """The shipment's attributes, read back through the API."""
    r = requests.get(f'{BASE}/api/Shipment/{context.oid}/', headers=headers())
    assert r.status_code == 200, f'shipment {context.oid} not found: {r.status_code} {r.text[:200]}'
    return r.json()['data']['attributes']


def children(table: str, oid: int) -> list:
    """Rows of a child table for a shipment."""
    r = requests.get(f'{BASE}/api/{table}/', params={"filter[local_shipment_oid_nbr]": oid, "page[limit]": 50}, headers=headers())
    return r.json()['data']


def patch(table: str, row_id: str, attributes: dict):
    """PATCH one row; asserts success."""
    body = {"data": {"type": table, "id": row_id, "attributes": attributes}}
    r = requests.patch(f'{BASE}/api/{table}/{row_id}/', json=body, headers=headers())
    assert r.status_code in (200, 204), f'PATCH {table}/{row_id} failed: {r.status_code} {r.text[:300]}'


# ---------------------------------------------------------------------------------------------------- Given

@given('a shipment imported by courier "{courier}" with value {value} at office "{office}" with tariff "{tariff}"')
def step_given_shipment(context, courier, value, office, tariff):
    open_log(context)
    context.oid, context.deliveries = new_key(), 0
    context.message = build_message(context.oid, value=value, courier=courier, office=office, tariff=tariff)
    deliver(context, context.message)
    assert context.consumed, f'shipment message was not persisted: {context.error_text}'


@given('a shipment message for account {account} with value {value}')
def step_given_message(context, account, value):
    open_log(context)
    context.oid, context.deliveries = new_key(), 0
    context.message = build_message(context.oid, account=account, value=value)


@given('a malformed shipment message')
def step_given_malformed(context):
    open_log(context)
    context.oid, context.deliveries = new_key(), 0
    context.message = f'<broken shipment {context.oid}'


# ---------------------------------------------------------------------------------------------------- When

@when('the message is delivered to topic isdc')
def step_when_delivered(context):
    deliver(context, context.message)


@when('the same message is delivered to topic isdc again')
def step_when_delivered_again(context):
    deliver(context, context.message, suffix='_again')
    assert context.consumed, f'replayed message was not persisted: {context.error_text}'


@when('the message is delivered again with value {value}')
def step_when_delivered_changed(context, value):
    text = build_message(context.oid, account='451000001', value=value)
    deliver(context, text, suffix='_changed')
    assert context.consumed, f'replayed message was not persisted: {context.error_text}'


@when('the malformed message is delivered live to topic isdc')
def step_when_malformed(context):
    deliver(context, context.message, mode='live')


@when('the shipment is deleted')
def step_when_shipment_deleted(context):
    r = requests.delete(f'{BASE}/api/Shipment/{context.oid}/', headers=headers())
    assert r.status_code in (200, 204), f'delete failed: {r.status_code} {r.text[:300]}'


@when('the shipment eligibility is evaluated')
def step_when_evaluated(context):
    context.shipment = get_shipment(context)


@when('the commodity line is flagged prohibited')
@given('the commodity line is flagged prohibited')
def step_when_flagged(context):
    line = children('ShipmentCommodity', context.oid)[0]
    patch('ShipmentCommodity', line['id'], {"is_prohibited": 1})


@when('the prohibited flag is cleared')
def step_when_cleared(context):
    line = children('ShipmentCommodity', context.oid)[0]
    patch('ShipmentCommodity', line['id'], {"is_prohibited": 0})


@when('the commodity line is deleted')
def step_when_line_deleted(context):
    line = children('ShipmentCommodity', context.oid)[0]
    r = requests.delete(f'{BASE}/api/ShipmentCommodity/{line["id"]}/', headers=headers())
    assert r.status_code in (200, 204), f'delete failed: {r.status_code} {r.text[:300]}'


@when('the shipment value is changed to {value}')
def step_when_value(context, value):
    patch('Shipment', str(context.oid), {"local_customs_value_amt": value})


@when('the planned clearance office is changed to "{office}"')
def step_when_office(context, office):
    patch('Shipment', str(context.oid), {"planned_clearance_location_cd": office})


@when('the courier service type is changed to "{courier}"')
def step_when_courier(context, courier):
    patch('Shipment', str(context.oid), {"service_type_cd": courier})


# ---------------------------------------------------------------------------------------------------- Then

@then('the shipment is persisted with {pieces:d} piece, {parties:d} parties and {commodities:d} commodity')
def step_then_graph(context, pieces, parties, commodities):
    assert context.consumed, f'message not persisted: {context.error_text}'
    got = (len(children('Piece', context.oid)), len(children('ShipmentParty', context.oid)),
           len(children('ShipmentCommodity', context.oid)))
    assert got == (pieces, parties, commodities), f'expected {(pieces, parties, commodities)}, got {got}'
    ships = requests.get(f'{BASE}/api/Shipment/', params={"filter[local_shipment_oid_nbr]": context.oid}, headers=headers()).json()['data']
    assert len(ships) == 1, f'expected 1 shipment, got {len(ships)}'


@then('the message blob is marked processed')
def step_then_blob(context):
    blobs = find_blobs(context.oid)
    assert blobs and all(b['attributes']['is_processed'] for b in blobs), f'blobs not processed: {blobs}'


@then('there are {count:d} message blobs for the shipment')
def step_then_blob_count(context, count):
    got = len(find_blobs(context.oid))
    assert got == count, f'expected {count} blobs, got {got}'


@then('the stored shipment value is {value}')
def step_then_value(context, value):
    got = float(get_shipment(context)['local_customs_value_amt'])
    assert abs(got - float(value)) < 0.005, f'expected {value}, got {got}'


@then('no pieces, parties or commodities remain for the shipment')
def step_then_no_orphans(context):
    left = {t: len(children(t, context.oid)) for t in ('Piece', 'ShipmentParty', 'ShipmentCommodity')}
    assert not any(left.values()), f'orphans remain: {left}'


@then('the message blob is not processed and has error text')
def step_then_blob_error(context):
    blobs = find_blobs(context.oid)
    assert blobs, 'no blob saved for the malformed message'
    attrs = blobs[0]['attributes']
    assert not attrs['is_processed'] and attrs.get('error_text'), f'expected unprocessed blob with error_text: {attrs}'


@then('the shipment has an importer party for "{name}"')
def step_then_importer(context, name):
    parties = [p['attributes'] for p in children('ShipmentParty', context.oid)]
    importer = [p for p in parties if p['shipment_party_type_cd'] == 'I']
    assert len(importer) == 1 and importer[0]['company_nm'] == name, f'importer parties: {importer}'


@then('the shipment has no importer party')
def step_then_no_importer(context):
    parties = [p['attributes'] for p in children('ShipmentParty', context.oid)]
    assert not [p for p in parties if p['shipment_party_type_cd'] == 'I'], f'unexpected importer: {parties}'


@then('the shipment is eligible for the CLVS Program')
def step_then_eligible(context):
    ship = get_shipment(context)
    assert ship['clvs_eligible'] == 1, f"expected eligible; clvs_reason={ship['clvs_reason']!r}"


@then('the shipment is not eligible for the CLVS Program')
def step_then_not_eligible(context):
    ship = get_shipment(context)
    assert ship['clvs_eligible'] == 0, 'expected not eligible, but clvs_eligible = 1'


@then('clvs_reason is blank')
def step_then_reason_blank(context):
    reason = get_shipment(context)['clvs_reason']
    assert reason in ('', None), f'expected blank clvs_reason, got {reason!r}'


@then('clvs_reason is "{reason}"')
def step_then_reason(context, reason):
    got = get_shipment(context)['clvs_reason']
    assert got == reason, f'expected clvs_reason {reason!r}, got {got!r}'


@then('the shipment has {count:d} controlled commodity line')
@then('the shipment has {count:d} controlled commodity lines')
def step_then_controlled(context, count):
    got = get_shipment(context)['controlled_commodity_count']
    assert got == count, f'expected controlled_commodity_count {count}, got {got}'


@then('the shipment has {count:d} prohibited commodity line')
@then('the shipment has {count:d} prohibited commodity lines')
def step_then_prohibited(context, count):
    got = get_shipment(context)['prohibited_commodity_count']
    assert got == count, f'expected prohibited_commodity_count {count}, got {got}'
