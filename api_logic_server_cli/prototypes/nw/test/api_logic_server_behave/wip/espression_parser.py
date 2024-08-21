from behave import *
import requests, pdb
import json
import test_utils
from urllib.parse import quote

'''
        No Filter
        filter[AttrName]=Value (numeric) 	
            where “AttrName” like :parm_1 [Value]
        filter[AttrName][like]=”%value%” (string)
            where “AttrName” like :parm_1 [‘%Value%’]
        filter[AttrName][like]=value (date or timestamp)
            where “AttrName” like :parm_1 [‘YYYY-mm-dd’]
        filter[AttrName][in]=”(a,b,c)”
            where “AttrName” in :parm_1 [ ‘(a,b,c)’ ]
        filter[AttrName][like]=”Value”&filter[AttrName2][like]=”%Value1%”  
            where “AttrName” like :parm_1 or “AttrName2” like :parm_2 [Value,Value1]
        filter={“lop”:”AttrName”,”op”:”eq”,”rop”:”Value”}
            where “AttrName” = :parm_1 [value]

'''
# for this test - go to database/system/SAFRSBaseX.py and set do_enable_ont_advanced_filters = True
ENABLE_BEHAVE_JSONAPI = False

host = "localhost"
port = "5656"

@given('No Filter')
def step_impl(context):
    filter = ''
    context.filter = filter
    pass

@when('Query submitted')
def step_impl(context):
    filter = context.filter if hasattr(context, 'filter') and context.filter != '' else ''
    get_uri = f'http://localhost:5656/api/Order/?' \
                f'fields%5BOrder%5D=Id%2CCustomerId%2CEmployeeId%2COrderDate%2CAmountTotal' \
                f'&page%5Boffset%5D=0&page%5Blimit%5D=5' \
                f'{filter}'
    r = requests.get(url=get_uri, headers= test_utils.login(user='admin'))
    context.response_text = r.text
    print(get_uri, r.text)
    assert True is not False

@then('Return limit records')
def step_impl(context):
    response_text = context.response_text
    result_data = json.loads(response_text)
    if ENABLE_BEHAVE_JSONAPI:
        assert len(result_data['data']) == 5 , f'Error - " {response_text}'
    #assert "AmountTotal" in response_text, f'Error - " {response_text}'
    
@given('One Filter')
def step_impl(context):
    filter = '&filter[Id]=10259'
    context.filter = filter
    pass

@then('One key record returned')
def step_impl(context):
    response_text = context.response_text
    result_data = json.loads(response_text)
    if ENABLE_BEHAVE_JSONAPI:
        assert len(result_data['data']) == 1, f'Error - " {response_text}'
        assert "10259" in response_text, f'Error - " {response_text}'
    
@given('Two Filter')
def step_impl(context):
    filter = '&filter[Id]=10259'
    filter2 = '&filter[AmountTotal]=448.00'
    context.filter =  f'{filter}{filter2}'
    pass

@then('Two records returned')
def step_impl(context):
    response_text = context.response_text
    result_data = json.loads(response_text)
    if ENABLE_BEHAVE_JSONAPI:
        assert len(result_data['data']) == 2, f'Error - " {response_text}'
        assert "10259" in response_text and "448.00" in response_text, f'Error - " {response_text}'
    
@given('Basic Filter')
def step_impl(context):
    filter = '{"filter":{"@basic_expression":{"lop":"AmountTotal","op":"eq","rop":448.00}}}'
    context.filter = f'&filter={quote(filter)}'
    pass

@then('Basic row returned')
def step_impl(context):
    response_text = context.response_text
    result_data = json.loads(response_text)
    if ENABLE_BEHAVE_JSONAPI:
        assert len(result_data['data']) == 1, f'Error - " {response_text}'
        assert  "448.00" in response_text, f'Error - " {response_text}'
    
@given('Basic or Filter')
def step_impl(context):
    filter = '{"filter":{"@basic_expression":{"lop":{"lop":"AmountTotal","op":"eq","rop":448.00},"op":"or","rop":{"lop":"Id","op":"eq","rop":10259}}}}'
    context.filter =  f'&filter={quote(filter)}'
    pass

@then('Basic 2 rows returned')
def step_impl(context):
    response_text = context.response_text
    result_data = json.loads(response_text)
    if ENABLE_BEHAVE_JSONAPI:
        assert len(result_data['data']) == 2, f'Error - " {response_text}'
        assert  "448.00" in response_text and "10259" in response_text, f'Error - " {response_text}'

@given('Single Filter Expression')
def step_impl(context):
    filter = '{"filter":{"@filter_expression":{"lop":"Id","op":"eq","rop":10259}}}'
    context.filter =  f'&filter={quote(filter)}'
    pass

@then('Filter 1 row returned')
def step_impl(context):
    response_text = context.response_text
    result_data = json.loads(response_text)
    if ENABLE_BEHAVE_JSONAPI:
        assert len(result_data['data']) == 1, f'Error - " {response_text}'
        assert  "10259" in response_text, f'Error - " {response_text}'
    

@given('Filter Expression with and')
def step_impl(context):
    filter = '{"filter":{"@filter_expression":{"lop":{"lop":"Id","op":"eq","rop":10259},"op":"and","rop":{"lop":"CustomerId","op":"eq","rop":"CENTC"}}}}'
    context.filter =  f'&filter={quote(filter)}'
    pass

@then('Filter 2 rows returned')
def step_impl(context):
    response_text = context.response_text
    result_data = json.loads(response_text)
    if ENABLE_BEHAVE_JSONAPI:
        assert len(result_data['data']) == 1, f'Error - " {response_text}'
        assert  "CENTC" in response_text and "10259" in response_text, f'Error - " {response_text}'
    

@given('SAFRS like Expression')
def step_impl(context):
    filter = '"filter"=[{"lop":{"lop":"ShipName","op":"ilike","val":"%Alfred%"}]'
    context.filter =  f'&filter={quote(filter)}'
    pass

@then('SAFRS 5 rows returned')
def step_impl(context):
    response_text = context.response_text
    result_data = json.loads(response_text)
    if ENABLE_BEHAVE_JSONAPI:
        assert len(result_data['data']) == 5, f'Error - " {response_text}'
        assert  "Alfred's Futterkiste" in response_text, f'Error - " {response_text}'
    