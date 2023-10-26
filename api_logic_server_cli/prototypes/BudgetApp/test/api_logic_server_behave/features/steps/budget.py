from behave import *
import requests, pdb
import test_utils
import json
import safrs
import requests
from flask import jsonify

db = safrs.DB  # valid only after is initialized, above
session = db.session
headers = {'Content-Type': 'application/json','accept': 'application/vnd.api+json'}

def getYrTotal(year_id: int) -> any: 
    url = "'http://localhost:5656/api/YrTotal/2023"
    yr = requests.get(url, headers=headers)
    print(yr)
    return jsonify(yr).json

@given('Budget Entry')
def step_impl(context):
    context.yr = getYrTotal(2023)
    assert True

@when('Budget Transactions submitted')
def step_impl(context):
    budget = {
    "meta": {
        "method": "budget_insert",
        "args": {
            "year_id": 2023,
            "qtr_id": 1,
            "month_id": 1,
            "user_id": 1,
            "category_id": 1,
            "actual_amount": 0,
            "amount": 10,
            "is_expense": 1,
            "description": "test insert"
            }
        }
    }
    url = 'http://localhost:5656/api/ServicesEndPoint/budget_insert' 
    ret = requests.post(url=url, headers=headers, data=budget)
    print(ret)
    context.budget = jsonify(ret).json

@then('Year Total reflects budget change')
def step_impl(context):
    scenario = "Budget Transaction Processing"
    #test_utils.prt(f'Rules Report', scenario)
    budget_total = context.yr["budget_total"] 
    assert budget_total == budget_total + 10
    
@given('Transaction Entry')
def step_impl(context):
    #yr = session.query(models.YrTotal).filter(models.YrTotal.year_id == year_id).one()
    url = "'http://localhost:5656/api/YrTotal/2023"
    yr = requests.get(url, headers=headers)
    print(yr)
    return jsonify(yr).json

@when('Transactions submitted')
def step_impl(context):
    trans = {
        "meta": {
            "method": "transaction_insert",
            "args": {
            "budget_id": 1,
            "amount": 10,
            "category_id": 1,
            "is_expense": 0,
            "description": "test transaction insert"
            }
        }
    }
    url = 'http://localhost:5656/api/ServicesEndPoint/transaction_insert' 
    ret = requests.post(url=url, headers=headers, data=trans)
    print(ret)

@then('Year Total reflects actual change')
def step_impl(context):
    scenario = "Transaction Processing"
    total = context.yr["actual_total"] 
    assert total == total + 10