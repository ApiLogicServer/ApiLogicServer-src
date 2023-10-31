from behave import *
import requests
import test_utils
import json
import requests
from flask import jsonify

headers = {'Content-Type': 'application/json','accept': 'application/vnd.api+json'}

def getYrTotal(year_id: str) -> any: 
    url = f"http://localhost:5656/api/YrTotal/{year_id}/"
    r = requests.get(url, headers=headers)
    response_text = r.text
    status_code = r.status_code
    print(response_text)
    if status_code > 300:
        raise requests.HTTPError(f'GET YrTotal failed with {response_text}')
    #j = jsonify(response_text).json
    result_data = json.loads(response_text)
    return result_data["data"]["attributes"]

def insert_budget(amount:int, category_id: int) -> any:
    budget = {
        "data": {
            "attributes": {
                "year_id": 2023,
                "month_id": 1,
                "user_id": 1,
                "category_id": category_id,
                "description": "Budget Test",
                "amount": amount,
            },
            "type": "Budget"
        }
    }
    url = 'http://localhost:5656/api/Budget' 
    r = requests.post(url=url, headers=headers, json=budget)
    response_text = r.text
    status_code = r.status_code
    print(response_text)
    if status_code > 300:
        raise requests.HTTPError(f'POST budget failed with {response_text}')
    return response_text

@given('Budget Entry')
def step_impl(context):
    insert_budget(0,1)
    context.yr = getYrTotal('2023_1')
    print(context.yr)

@when('Budget Transactions submitted')
def step_impl(context):
    context.budget = insert_budget(100, 1)

@then('Year Total reflects budget change')
def step_impl(context):
    scenario = "Budget Processing"
    #test_utils.prt(f'Rules Report', scenario)
    budget_total = context.yr["budget_total"] 
    after = getYrTotal('2023_1')
    assert after["budget_total"] - budget_total ==  100
    
@given('Transaction Entry')
def step_impl(context):
    insert_budget(0,1)
    context.yr = getYrTotal('2023_1')
    print(context.yr)

@when('Transactions submitted')
def step_impl(context):
    trans = {
        "data": {
            "attributes": {
                "budget_id": 1,
                "account_id": 1,
                "description": "Behave Transaction",
                "amount": 100
            },
            "type": "Transaction"
        }
    }
    url = 'http://localhost:5656/api/Transaction' 
    r = requests.post(url=url, headers=headers, json=trans)
    response_text = r.text
    status_code = r.status_code
    print(response_text)
    if status_code > 300:
        raise requests.HTTPError(f'POST transaction failed with {response_text}')
    context.transaction = response_text

@then('Year Total reflects actual change')
def step_impl(context):
    scenario = "Transaction Processing"
    total = context.yr["actual_amount"] 
    after = getYrTotal('2023_1')
    assert after["actual_amount"] - total == 100