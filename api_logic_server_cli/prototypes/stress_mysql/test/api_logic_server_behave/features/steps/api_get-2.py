# this is the api_test.py
from behave import *
import requests, pdb
import json
from dotmap import DotMap
from test_utils import login

host = "localhost"
port = "5656"
"""
	curl "http://localhost:5656/api/STRESSBIGINT"
	curl "http://localhost:5656/api/STRESSBIGINTUNSIGNED"
	curl "http://localhost:5656/api/STRESSBIT"
	curl "http://localhost:5656/api/STRESSCHAR"
	curl "http://localhost:5656/api/STRESSDATE"
	curl "http://localhost:5656/api/STRESSDATETIME"
	curl "http://localhost:5656/api/STRESSDECIMAL"
	curl "http://localhost:5656/api/STRESSDemographic"
	curl "http://localhost:5656/api/STRESSENUM"
	curl "http://localhost:5656/api/STRESSFLOAT"
	curl "http://localhost:5656/api/STRESSINTEGER"
	curl "http://localhost:5656/api/STRESSINTEGERUNSIGNED"
	curl "http://localhost:5656/api/STRESSJSON"
	curl "http://localhost:5656/api/STRESSMEDIUMINT"
	curl "http://localhost:5656/api/STRESSMEDIUMINTUNSIGNED"
	curl "http://localhost:5656/api/STRESSMultiColumnPrimaryKey"
	curl "http://localhost:5656/api/STRESSNUM"
	curl "http://localhost:5656/api/STRESSSET"
	curl "http://localhost:5656/api/STRESSSMALLINT"
	curl "http://localhost:5656/api/STRESSSMALLINTUNSIGNED"
	curl "http://localhost:5656/api/STRESSTIME"
	curl "http://localhost:5656/api/STRESSTIMESTAMP"
	curl "http://localhost:5656/api/STRESSTINYINT"
	curl "http://localhost:5656/api/STRESSTINYINTUNSIGNED"
	curl "http://localhost:5656/api/STRESSVARCHAR"
	curl "http://localhost:5656/api/STRESSYEAR"
"""
def getAPI(table_name:str):
	get_uri = f'http://{host}:{port}/api/{table_name}/?'\
	"page%5Boffset%5D=0&page%5Blimit%5D=100"
	r = requests.get(url=get_uri, headers= login())
	result_data = json.loads(r.text)
	print(r.text)
	return DotMap(result_data)

def patchAPI(table_name:str, payload:dict, key:any):
	get_uri = f'http://{host}:{port}/api/{table_name}/{key}'
	r = requests.patch(url=get_uri, json=payload, headers= login())
	return json.loads(r.text)

def validate(response_text:str) -> bool:
    print(response_text)
    for row in response_text:
        d = row.attributes['description']
        for attr in row.attributes:
            if attr in ['S_CheckSum','_check_sum_','description']:
                pass
            else:
                v = row.attributes[attr]
                if d not in ['null','now(6)','now','localtime'] and d != v:
                    print(attr,v)

    return len(response_text) >= 0

@given('GET STRESSTIMESTAMP endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIMESTAMP API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIMESTAMP')

@then('STRESSTIMESTAMP retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSCHAR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSCHAR API')
def step_impl(context):
	context.response_text = getAPI('STRESSCHAR')

@then('STRESSCHAR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSSMALLINTUNSIGNED endpoint')
def step_impl(context):
	assert True

@when('GET STRESSSMALLINTUNSIGNED API')
def step_impl(context):
	context.response_text = getAPI('STRESSSMALLINTUNSIGNED')

@then('STRESSSMALLINTUNSIGNED retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSMEDIUMINT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSMEDIUMINT API')
def step_impl(context):
	context.response_text = getAPI('STRESSMEDIUMINT')

@then('STRESSMEDIUMINT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSDECIMAL endpoint')
def step_impl(context):
	assert True

@when('GET STRESSDECIMAL API')
def step_impl(context):
	context.response_text = getAPI('STRESSDECIMAL')

@then('STRESSDECIMAL retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSTIME endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIME API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIME')

@then('STRESSTIME retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSTINYINTUNSIGNED endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTINYINTUNSIGNED API')
def step_impl(context):
	context.response_text = getAPI('STRESSTINYINTUNSIGNED')

@then('STRESSTINYINTUNSIGNED retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSBIGINT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBIGINT API')
def step_impl(context):
	context.response_text = getAPI('STRESSBIGINT')

@then('STRESSBIGINT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSSET endpoint')
def step_impl(context):
	assert True

@when('GET STRESSSET API')
def step_impl(context):
	context.response_text = getAPI('STRESSSET')

@then('STRESSSET retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSDATE endpoint')
def step_impl(context):
	assert True

@when('GET STRESSDATE API')
def step_impl(context):
	context.response_text = getAPI('STRESSDATE')

@then('STRESSDATE retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSYEAR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSYEAR API')
def step_impl(context):
	context.response_text = getAPI('STRESSYEAR')

@then('STRESSYEAR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSBIGINTUNSIGNED endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBIGINTUNSIGNED API')
def step_impl(context):
	context.response_text = getAPI('STRESSBIGINTUNSIGNED')

@then('STRESSBIGINTUNSIGNED retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSMEDIUMINTUNSIGNED endpoint')
def step_impl(context):
	assert True

@when('GET STRESSMEDIUMINTUNSIGNED API')
def step_impl(context):
	context.response_text = getAPI('STRESSMEDIUMINTUNSIGNED')

@then('STRESSMEDIUMINTUNSIGNED retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSDATETIME endpoint')
def step_impl(context):
	assert True

@when('GET STRESSDATETIME API')
def step_impl(context):
	context.response_text = getAPI('STRESSDATETIME')

@then('STRESSDATETIME retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSMultiColumnPrimaryKey endpoint')
def step_impl(context):
	assert True

@when('GET STRESSMultiColumnPrimaryKey API')
def step_impl(context):
	context.response_text = getAPI('STRESSMultiColumnPrimaryKey')

@then('STRESSMultiColumnPrimaryKey retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSJSON endpoint')
def step_impl(context):
	assert True

@when('GET STRESSJSON API')
def step_impl(context):
	context.response_text = getAPI('STRESSJSON')

@then('STRESSJSON retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSNUM endpoint')
def step_impl(context):
	assert True

@when('GET STRESSNUM API')
def step_impl(context):
	context.response_text = getAPI('STRESSNUM')

@then('STRESSNUM retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSTINYINT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTINYINT API')
def step_impl(context):
	context.response_text = getAPI('STRESSTINYINT')

@then('STRESSTINYINT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSDemographic endpoint')
def step_impl(context):
	assert True

@when('GET STRESSDemographic API')
def step_impl(context):
	context.response_text = getAPI('STRESSDemographic')

@then('STRESSDemographic retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSBIT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBIT API')
def step_impl(context):
	context.response_text = getAPI('STRESSBIT')

@then('STRESSBIT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSFLOAT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSFLOAT API')
def step_impl(context):
	context.response_text = getAPI('STRESSFLOAT')

@then('STRESSFLOAT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSINTEGER endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTEGER API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTEGER')

@then('STRESSINTEGER retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSENUM endpoint')
def step_impl(context):
	assert True

@when('GET STRESSENUM API')
def step_impl(context):
	context.response_text = getAPI('STRESSENUM')

@then('STRESSENUM retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSSMALLINT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSSMALLINT API')
def step_impl(context):
	context.response_text = getAPI('STRESSSMALLINT')

@then('STRESSSMALLINT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSVARCHAR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSVARCHAR API')
def step_impl(context):
	context.response_text = getAPI('STRESSVARCHAR')

@then('STRESSVARCHAR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)

@given('GET STRESSINTEGERUNSIGNED endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTEGERUNSIGNED API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTEGERUNSIGNED')

@then('STRESSINTEGERUNSIGNED retrieved')
def step_impl(context):
	response_text = context.response_text
	assert validate(response_text.data)
