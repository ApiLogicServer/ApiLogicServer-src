"""
Steps for the customs_demo features: ISDC subscribe, importer matching, CLVS eligibility, live Kafka end to end.

Messages are built from a reference XML with unique shipment keys per scenario (repeatable), written to a file the
SERVER can read, and delivered through GET /consume_debug/isdc (live through Kafka when a broker answers, else
simulated).  Then-steps assert on the normalized result, so they hold in both modes.
"""
import json, re, time
from pathlib import Path
import requests
from behave import *
import test_utils

BASE = 'http://localhost:5656'
PROJECT_DIR = Path(__file__).resolve().parents[4]
TEMPLATE = PROJECT_DIR / 'docs/requirements/customs_demo/message_formats/demo-02-match-replace.xml'
MSG_DIR_REL = 'test/api_logic_server_behave/logs/messages'      # relative to the project root, where the server runs
MODE_FILE = PROJECT_DIR / 'test' / 'api_logic_server_behave' / 'logs' / 'delivery_modes.json'
NO_MATCH_ACCOUNT = '999000001'
JSONAPI = {'Content-Type': 'application/vnd.api+json'}
_counter = [0]


def record_mode(context, mode, broker=None):
    """Remember how this scenario's message was delivered, for the traceability report."""
    modes = json.loads(MODE_FILE.read_text()) if MODE_FILE.is_file() else {}
    modes[f'{context.feature.name} / {context.scenario.name}'] = {"mode": mode, **({"broker": broker} if broker else {})}
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODE_FILE.write_text(json.dumps(modes, indent=2))


def unique_oid() -> int:
    _counter[0] += 1
    return 7_000_000_000 + (int(time.time() * 1000) % 1_000_000_000) * 10 + _counter[0] % 10


def build_message(context) -> str:
    """Reference XML with this scenario's key and the scenario's inputs substituted in."""
    xml = TEMPLATE.read_text()
    oid = str(context.oid)
    xml = re.sub(r'(<(?:LOCAL_SHIPMENT_OID_NBR|OID_NBR|LOCAL_PIECE_OID_NBR)>)\d+(</)', r'\g<1>' + oid + r'\2', xml)
    xml = re.sub(r'(<AWB_NBR>)\d+(</)', r'\g<1>' + oid + r'\2', xml)
    xml = re.sub(r'(<TRACKING_ID_NBR>)\d+(</)', r'\g<1>' + oid + r'\2', xml)
    xml = re.sub(r'(<LOCAL_CUSTOMS_VALUE_AMT>)[^<]*(</)', r'\g<1>' + str(context.value) + r'\2', xml)
    xml = re.sub(r'(<SERVICE_TYPE_CD>)[^<]*(</)', r'\g<1>' + context.courier + r'\2', xml)
    xml = re.sub(r'(<FINAL_IMPORT_CLEARANCE_LOC_CD>)[^<]*(</)', r'\g<1>' + context.location + r'\2', xml)
    xml = re.sub(r'(<TRPRT_BILL_TO_ACCT_NBR>)[^<]*(</)', r'\g<1>' + context.account + r'\2', xml)
    xml = re.sub(r'(<HARMONIZED_TARIFF_NBR>)[^<]+(</)', r'\g<1>' + context.tariff + r'\2', xml)
    return xml


def write_message(context, xml: str) -> str:
    folder = PROJECT_DIR / MSG_DIR_REL
    folder.mkdir(parents=True, exist_ok=True)
    name = f'msg_{context.oid}_{int(time.time() * 1000)}.xml'
    (folder / name).write_text(xml)
    return f'{MSG_DIR_REL}/{name}'


def get_json(path, params=None):
    return requests.get(f'{BASE}{path}', params=params).json()


def blobs_for(oid, limit=60):
    """ShipmentXml attributes (newest first) whose payload carries this shipment key."""
    r = get_json('/api/ShipmentXml/', {"sort": "-id", "page[limit]": limit})
    return [each['attributes'] | {'id': int(each['id'])} for each in r.get('data', [])
            if f'>{oid}<' in (each['attributes'].get('payload') or '')]


def wait_for_blob_count(oid, count, timeout=30):
    """Live Kafka is asynchronous: poll until `count` blobs for this key are processed or carry error_text."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        done = [b for b in blobs_for(oid) if b.get('is_processed') or b.get('error_text')]
        if len(done) >= count:
            return done
        time.sleep(0.5)
    return None


def deliver(context, xml: str, mode='auto'):
    """Send the message through the debug endpoint; normalize the outcome for both modes."""
    before = len(blobs_for(context.oid)) if mode != 'simulated' else 0
    path = write_message(context, xml)
    r = requests.get(f'{BASE}/consume_debug/isdc', params={"file": path, "mode": mode})
    body = r.json()
    context.consumed, context.error_text, context.last_body = False, None, body
    if r.status_code == 409:                                  # live required but not available: not verified, not failed
        context.scenario.skip(body.get('error', 'live Kafka is not available'))
        context.skipped = True
        return
    record_mode(context, body['mode'], body.get('broker'))
    context.mode = body['mode']
    context.deliveries = getattr(context, 'deliveries', 0) + 1
    if body['mode'] == 'simulated':
        context.consumed, context.error_text = bool(body.get('success')), body.get('error')
        return
    assert body.get('published'), f'live publish failed: {r.text}'
    done = wait_for_blob_count(context.oid, before + 1)
    assert done, (f'no processed blob for shipment {context.oid} within 30 s - was the server started AFTER Kafka, '
                  'with KAFKA_SERVER and a unique KAFKA_CONSUMER_GROUP?')
    newest = done[0]
    context.error_text = newest.get('error_text')
    context.consumed = bool(newest.get('is_processed')) and not context.error_text


def shipment(context):
    r = requests.get(f'{BASE}/api/Shipment/{context.oid}')
    assert r.status_code == 200, f'shipment {context.oid} not found: {r.status_code} {r.text[:200]}'
    return r.json()['data']['attributes']


def child_count(resource, key, oid):
    r = get_json(f'/api/{resource}/', {f'filter[{key}]': oid, 'page[limit]': 100})
    return len(r.get('data', []))


def party_types(oid):
    r = get_json('/api/ShipmentParty/', {'filter[local_shipment_oid_nbr]': oid, 'page[limit]': 100})
    return [(each['id'], each['attributes']) for each in r.get('data', [])]


def patch(resource, rid, attrs):
    r = requests.patch(f'{BASE}/api/{resource}/{rid}', headers=JSONAPI,
                       data=json.dumps({"data": {"type": resource, "id": str(rid), "attributes": attrs}}))
    assert r.status_code == 200, f'PATCH {resource}/{rid} failed: {r.status_code} {r.text[:300]}'


# ---------------------------------------------------------------- Given

@given('a CIMCorp shipment message from courier "{courier}" released at "{location}" with customs value {value} CAD and tariff "{tariff}"')
def step_impl(context, courier, location, value, tariff):
    test_utils.prt(f'\n{context.scenario.name}\n', context.scenario.name)       # once per scenario: logic log
    context.oid = unique_oid()
    context.courier, context.location, context.value, context.tariff = courier, location, value, tariff
    context.account = NO_MATCH_ACCOUNT
    context.skipped = False


@given('a malformed shipment message')
def step_impl(context):
    test_utils.prt(f'\n{context.scenario.name}\n', context.scenario.name)
    context.oid = unique_oid()
    context.skipped = False
    context.malformed = True
    context.courier, context.location, context.value, context.tariff, context.account = '04', 'YYZ', '1', '1', NO_MATCH_ACCOUNT


@given('the message names the importer account of customer "{name}"')
def step_impl(context, name):
    r = get_json('/api/Customer/', {"filter[name]": name})
    assert r['data'], f'customer {name} not found'
    context.account = str(r['data'][0]['attributes']['duty_bill_to_acct_nbr'])
    context.customer = r['data'][0]['attributes']


@given('the message names an importer account that no customer has')
def step_impl(context):
    context.account = NO_MATCH_ACCOUNT


# ---------------------------------------------------------------- When

def _xml(context):
    if getattr(context, 'malformed', False):
        return f'<notxml shipment="{context.oid}"><LOCAL_SHIPMENT_OID_NBR>{context.oid}</LOCAL_SHIPMENT_OID_NBR>'
    return build_message(context)


@when('the message is delivered to topic isdc')
def step_impl(context):
    context.blobs_before = 0
    deliver(context, _xml(context))


@when('the same message is delivered to topic isdc again')
def step_impl(context):
    deliver(context, _xml(context))


@when('the message is delivered to topic isdc live only')
def step_impl(context):
    deliver(context, _xml(context), mode='live')


@when('the shipment is deleted through the API')
def step_impl(context):
    r = requests.delete(f'{BASE}/api/Shipment/{context.oid}')
    assert r.status_code in (200, 204), f'delete failed: {r.status_code} {r.text[:300]}'


@when('the shipment customs value is changed to {value}')
def step_impl(context, value):
    patch('Shipment', context.oid, {"local_customs_value_amt": float(value)})


@when('the shipment cargo description is changed')
def step_impl(context):
    patch('Shipment', context.oid, {"shipment_desc": f"changed {int(time.time())}"})


@when('the shipment release location is changed to "{location}"')
def step_impl(context, location):
    patch('Shipment', context.oid, {"final_import_clearance_loc_cd": location})


@when('the first commodity tariff is changed to "{tariff}"')
def step_impl(context, tariff):
    patch('ShipmentCommodity', f'{context.oid}_1', {"harmonized_tariff_nbr": tariff})


@when('a second commodity line with tariff "{tariff}" is added')
def step_impl(context, tariff):
    r = requests.post(f'{BASE}/api/ShipmentCommodity/', headers=JSONAPI, data=json.dumps({"data": {
        "type": "ShipmentCommodity",
        "attributes": {"local_shipment_oid_nbr": context.oid, "sequence_nbr": 2, "harmonized_tariff_nbr": tariff}}}))
    assert r.status_code in (200, 201), f'POST commodity failed: {r.status_code} {r.text[:300]}'


@when('the second commodity line is deleted')
def step_impl(context):
    r = requests.delete(f'{BASE}/api/ShipmentCommodity/{context.oid}_2')
    assert r.status_code in (200, 204), f'delete failed: {r.status_code} {r.text[:300]}'


# ---------------------------------------------------------------- Then

@then('the shipment is persisted with {pieces:d} piece, {commodities:d} commodity and {parties:d} parties')
def step_impl(context, pieces, commodities, parties):
    assert context.consumed, f'message not processed: {context.error_text}'
    s = shipment(context)
    assert s['awb_nbr'] == str(context.oid), s['awb_nbr']
    assert child_count('Piece', 'local_shipment_oid_nbr', context.oid) == pieces
    assert child_count('ShipmentCommodity', 'local_shipment_oid_nbr', context.oid) == commodities
    assert len(party_types(context.oid)) == parties, [p[1]['shipment_party_type_cd'] for p in party_types(context.oid)]


@then('the two parties have distinct keys')
def step_impl(context):
    ids = [p[0] for p in party_types(context.oid)]
    assert len(ids) == 2 and len(set(ids)) == 2, ids


@then('the blob count for the shipment went up by one per delivery')
def step_impl(context):
    assert len(blobs_for(context.oid)) == context.deliveries, (len(blobs_for(context.oid)), context.deliveries)


@then('no piece, commodity, party or special handling rows remain for the shipment')
def step_impl(context):
    assert child_count('Piece', 'local_shipment_oid_nbr', context.oid) == 0
    assert child_count('ShipmentCommodity', 'local_shipment_oid_nbr', context.oid) == 0
    assert len(party_types(context.oid)) == 0
    assert child_count('SpecialHandling', 'oid_nbr', context.oid) == 0


@then('the blob stays unprocessed with error text')
def step_impl(context):
    blob = blobs_for(context.oid)[0]
    assert not blob.get('is_processed'), blob
    assert blob.get('error_text'), 'a failed Tx 2 must leave error_text on the blob'


@then('the blob is processed without error text')
def step_impl(context):
    blob = blobs_for(context.oid)[0]
    assert blob.get('is_processed') and not blob.get('error_text'), blob


@then('the shipment has an importer party copied from customer "{name}"')
def step_impl(context, name):
    importers = [p[1] for p in party_types(context.oid) if p[1]['shipment_party_type_cd'] == 'I']
    assert len(importers) == 1, f'{len(importers)} importer parties'
    assert importers[0]['company_nm'] == name, importers[0]['company_nm']
    assert str(importers[0]['customer_acct_nbr']) == context.account


@then('the shipment has no importer party')
def step_impl(context):
    assert not [p for p in party_types(context.oid) if p[1]['shipment_party_type_cd'] == 'I']


@then('the shipment has exactly {n:d} importer party')
def step_impl(context, n):
    assert len([p for p in party_types(context.oid) if p[1]['shipment_party_type_cd'] == 'I']) == n


@then('the shipment is eligible for the CLVS Program')
def step_impl(context):
    s = shipment(context)
    assert s['clvs_eligible'] == 1, f"clvs_eligible={s['clvs_eligible']} reason={s['clvs_reason']!r}"


@then('the shipment is not eligible for the CLVS Program')
def step_impl(context):
    s = shipment(context)
    assert s['clvs_eligible'] == 0, f"clvs_eligible={s['clvs_eligible']} reason={s['clvs_reason']!r}"


@then('the clvs_reason is blank')
def step_impl(context):
    assert (shipment(context)['clvs_reason'] or '') == ''


@then('the clvs_reason is "{reason}"')
def step_impl(context, reason):
    assert shipment(context)['clvs_reason'] == reason, repr(shipment(context)['clvs_reason'])


@then('the shipment has {controlled:d} controlled line and {prohibited:d} prohibited lines')
def step_impl(context, controlled, prohibited):
    s = shipment(context)
    assert (s['controlled_item_count'], s['prohibited_commodity_count']) == (controlled, prohibited), \
        (s['controlled_item_count'], s['prohibited_commodity_count'])


@then('the shipment has {controlled:d} controlled lines and {prohibited:d} prohibited lines')
def step_impl(context, controlled, prohibited):
    s = shipment(context)
    assert (s['controlled_item_count'], s['prohibited_commodity_count']) == (controlled, prohibited), \
        (s['controlled_item_count'], s['prohibited_commodity_count'])
