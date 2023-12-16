# this is the api_test.py
from behave import *
import requests, pdb
import json
from dotmap import DotMap
from test_utils import login

host = "localhost"
port = "5656"

def getAPI(table_name:str):
	get_uri = f'http://{host}:{port}/api/{table_name}/?'\
	"page%5Boffset%5D=0&page%5Blimit%5D=1"
	r = requests.get(url=get_uri, headers= login())
	result_data = json.loads(r.text)
	return DotMap(result_data)

def patchAPI(table_name:str, payload:dict, key:any):
	get_uri = f'http://{host}:{port}/api/{table_name}/{key}'
	r = requests.patch(url=get_uri, json=payload, headers= login())
	return json.loads(r.text)


@given('GET STRESSTIMESTAMP endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIMESTAMP API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIMESTAMP')

@then('STRESSTIMESTAMP retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSCHARACTERVARYING endpoint')
def step_impl(context):
	assert True

@when('GET STRESSCHARACTERVARYING API')
def step_impl(context):
	context.response_text = getAPI('STRESSCHARACTERVARYING')

@then('STRESSCHARACTERVARYING retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSTIMEWITHTIMEZONE endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIMEWITHTIMEZONE API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIMEWITHTIMEZONE')

@then('STRESSTIMEWITHTIMEZONE retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSREAL endpoint')
def step_impl(context):
	assert True

@when('GET STRESSREAL API')
def step_impl(context):
	context.response_text = getAPI('STRESSREAL')

@then('STRESSREAL retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBITARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBITARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSBITARR')

@then('STRESSBITARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBYTEAARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBYTEAARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSBYTEAARR')

@then('STRESSBYTEAARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSTIMEARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIMEARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIMEARR')

@then('STRESSTIMEARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSCHARACTERVARYINGARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSCHARACTERVARYINGARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSCHARACTERVARYINGARR')

@then('STRESSCHARACTERVARYINGARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL12HOURTOMINUTE endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL12HOURTOMINUTE API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL12HOURTOMINUTE')

@then('STRESSINTERVAL12HOURTOMINUTE retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSTIMESTAMPWITHTIMEZONEARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIMESTAMPWITHTIMEZONEARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIMESTAMPWITHTIMEZONEARR')

@then('STRESSTIMESTAMPWITHTIMEZONEARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSTIMEWITHTIMEZONEARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIMEWITHTIMEZONEARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIMEWITHTIMEZONEARR')

@then('STRESSTIMEWITHTIMEZONEARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSXML endpoint')
def step_impl(context):
	assert True

@when('GET STRESSXML API')
def step_impl(context):
	context.response_text = getAPI('STRESSXML')

@then('STRESSXML retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSREALARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSREALARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSREALARR')

@then('STRESSREALARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBIGINTARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBIGINTARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSBIGINTARR')

@then('STRESSBIGINTARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBIGSERIAL endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBIGSERIAL API')
def step_impl(context):
	context.response_text = getAPI('STRESSBIGSERIAL')

@then('STRESSBIGSERIAL retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBITVARYINGARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBITVARYINGARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSBITVARYINGARR')

@then('STRESSBITVARYINGARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSFLOAT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSFLOAT API')
def step_impl(context):
	context.response_text = getAPI('STRESSFLOAT')

@then('STRESSFLOAT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSArray endpoint')
def step_impl(context):
	assert True

@when('GET STRESSArray API')
def step_impl(context):
	context.response_text = getAPI('STRESSArray')

@then('STRESSArray retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL09DAYTOHOUR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL09DAYTOHOUR API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL09DAYTOHOUR')

@then('STRESSINTERVAL09DAYTOHOUR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSDOUBLEPRECISION endpoint')
def step_impl(context):
	assert True

@when('GET STRESSDOUBLEPRECISION API')
def step_impl(context):
	context.response_text = getAPI('STRESSDOUBLEPRECISION')

@then('STRESSDOUBLEPRECISION retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSUUID endpoint')
def step_impl(context):
	assert True

@when('GET STRESSUUID API')
def step_impl(context):
	context.response_text = getAPI('STRESSUUID')

@then('STRESSUUID retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSDOUBLEPRECISIONARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSDOUBLEPRECISIONARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSDOUBLEPRECISIONARR')

@then('STRESSDOUBLEPRECISIONARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSENUMARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSENUMARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSENUMARR')

@then('STRESSENUMARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSTIMESTAMPWITHTIMEZONE endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIMESTAMPWITHTIMEZONE API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIMESTAMPWITHTIMEZONE')

@then('STRESSTIMESTAMPWITHTIMEZONE retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL02YEAR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL02YEAR API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL02YEAR')

@then('STRESSINTERVAL02YEAR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSSMALLSERIAL endpoint')
def step_impl(context):
	assert True

@when('GET STRESSSMALLSERIAL API')
def step_impl(context):
	context.response_text = getAPI('STRESSSMALLSERIAL')

@then('STRESSSMALLSERIAL retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL14MINUTETOSECOND endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL14MINUTETOSECOND API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL14MINUTETOSECOND')

@then('STRESSINTERVAL14MINUTETOSECOND retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL05HOUR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL05HOUR API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL05HOUR')

@then('STRESSINTERVAL05HOUR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSTEXT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTEXT API')
def step_impl(context):
	context.response_text = getAPI('STRESSTEXT')

@then('STRESSTEXT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSCHARARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSCHARARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSCHARARR')

@then('STRESSCHARARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSCHAR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSCHAR API')
def step_impl(context):
	context.response_text = getAPI('STRESSCHAR')

@then('STRESSCHAR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL04DAY endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL04DAY API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL04DAY')

@then('STRESSINTERVAL04DAY retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL13HOURTOSECOND endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL13HOURTOSECOND API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL13HOURTOSECOND')

@then('STRESSINTERVAL13HOURTOSECOND retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSDATEARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSDATEARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSDATEARR')

@then('STRESSDATEARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL10DAYTOMINUTE endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL10DAYTOMINUTE API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL10DAYTOMINUTE')

@then('STRESSINTERVAL10DAYTOMINUTE retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSTIME endpoint')
def step_impl(context):
	assert True

@when('GET STRESSTIME API')
def step_impl(context):
	context.response_text = getAPI('STRESSTIME')

@then('STRESSTIME retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSStaff endpoint')
def step_impl(context):
	assert True

@when('GET STRESSStaff API')
def step_impl(context):
	context.response_text = getAPI('STRESSStaff')

@then('STRESSStaff retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBIGINT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBIGINT API')
def step_impl(context):
	context.response_text = getAPI('STRESSBIGINT')

@then('STRESSBIGINT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSDATE endpoint')
def step_impl(context):
	assert True

@when('GET STRESSDATE API')
def step_impl(context):
	context.response_text = getAPI('STRESSDATE')

@then('STRESSDATE retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL11DAYTOSECOND endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL11DAYTOSECOND API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL11DAYTOSECOND')

@then('STRESSINTERVAL11DAYTOSECOND retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSJSONB endpoint')
def step_impl(context):
	assert True

@when('GET STRESSJSONB API')
def step_impl(context):
	context.response_text = getAPI('STRESSJSONB')

@then('STRESSJSONB retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSNUMERIC endpoint')
def step_impl(context):
	assert True

@when('GET STRESSNUMERIC API')
def step_impl(context):
	context.response_text = getAPI('STRESSNUMERIC')

@then('STRESSNUMERIC retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSUUIDARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSUUIDARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSUUIDARR')

@then('STRESSUUIDARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSJSON endpoint')
def step_impl(context):
	assert True

@when('GET STRESSJSON API')
def step_impl(context):
	context.response_text = getAPI('STRESSJSON')

@then('STRESSJSON retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL07SECOND endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL07SECOND API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL07SECOND')

@then('STRESSINTERVAL07SECOND retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSVirtualParent endpoint')
def step_impl(context):
	assert True

@when('GET STRESSVirtualParent API')
def step_impl(context):
	context.response_text = getAPI('STRESSVirtualParent')

@then('STRESSVirtualParent retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL06MINUTE endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL06MINUTE API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL06MINUTE')

@then('STRESSINTERVAL06MINUTE retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBITVARYING endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBITVARYING API')
def step_impl(context):
	context.response_text = getAPI('STRESSBITVARYING')

@then('STRESSBITVARYING retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBIT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBIT API')
def step_impl(context):
	context.response_text = getAPI('STRESSBIT')

@then('STRESSBIT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSFLOATARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSFLOATARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSFLOATARR')

@then('STRESSFLOATARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSMONEY endpoint')
def step_impl(context):
	assert True

@when('GET STRESSMONEY API')
def step_impl(context):
	context.response_text = getAPI('STRESSMONEY')

@then('STRESSMONEY retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSSERIAL endpoint')
def step_impl(context):
	assert True

@when('GET STRESSSERIAL API')
def step_impl(context):
	context.response_text = getAPI('STRESSSERIAL')

@then('STRESSSERIAL retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSENUM endpoint')
def step_impl(context):
	assert True

@when('GET STRESSENUM API')
def step_impl(context):
	context.response_text = getAPI('STRESSENUM')

@then('STRESSENUM retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSSMALLINT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSSMALLINT API')
def step_impl(context):
	context.response_text = getAPI('STRESSSMALLINT')

@then('STRESSSMALLINT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSVirtualParentComplex endpoint')
def step_impl(context):
	assert True

@when('GET STRESSVirtualParentComplex API')
def step_impl(context):
	context.response_text = getAPI('STRESSVirtualParentComplex')

@then('STRESSVirtualParentComplex retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSGEOMPOINT endpoint')
def step_impl(context):
	assert True

@when('GET STRESSGEOMPOINT API')
def step_impl(context):
	context.response_text = getAPI('STRESSGEOMPOINT')

@then('STRESSGEOMPOINT retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSMAXCOLUMN endpoint')
def step_impl(context):
	assert True

@when('GET STRESSMAXCOLUMN API')
def step_impl(context):
	context.response_text = getAPI('STRESSMAXCOLUMN')

@then('STRESSMAXCOLUMN retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL01 endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL01 API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL01')

@then('STRESSINTERVAL01 retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSSMALLINTARR endpoint')
def step_impl(context):
	assert True

@when('GET STRESSSMALLINTARR API')
def step_impl(context):
	context.response_text = getAPI('STRESSSMALLINTARR')

@then('STRESSSMALLINTARR retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL08YEARTOMONTH endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL08YEARTOMONTH API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL08YEARTOMONTH')

@then('STRESSINTERVAL08YEARTOMONTH retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSBYTEA endpoint')
def step_impl(context):
	assert True

@when('GET STRESSBYTEA API')
def step_impl(context):
	context.response_text = getAPI('STRESSBYTEA')

@then('STRESSBYTEA retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0

@given('GET STRESSINTERVAL03MONTH endpoint')
def step_impl(context):
	assert True

@when('GET STRESSINTERVAL03MONTH API')
def step_impl(context):
	context.response_text = getAPI('STRESSINTERVAL03MONTH')

@then('STRESSINTERVAL03MONTH retrieved')
def step_impl(context):
	response_text = context.response_text
	assert len(response_text.data) > 0
