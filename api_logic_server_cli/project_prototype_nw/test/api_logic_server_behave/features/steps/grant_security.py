from behave import *
import requests, pdb
import test_utils
import sys
import json
from dotmap import DotMap

logic_logs_dir = "logs/scenario_logic_logs"

host = "localhost"
port = "5656"

@given('User u1')
def step_impl(context):
    pass

def get_category_for_user(user):
    get_uri = f'http://{host}:{port}/api/Category'
    header = test_utils.login(user)
    r = requests.get(url=get_uri, headers= header)
    response_text = r.text
    status_code = r.status_code
    if status_code > 300:
        raise requests.ConnectionError(f'get_category failed for user {user} with error: {r.text}')
    save_for_session = True
    if save_for_session:
        s = requests.Session()
        s.headers.update(header)
    result_data = json.loads(response_text)
    #result_map = DotMap(result_data)
    return result_data["data"][0]["attributes"]

@given('Login user u1')
def step_impl(context):
    category_before = get_category_for_user('u1')
    context.category_before = category_before
    
@when('Get Category u1')
def step_impl(context):
    scenario_name = "Test Grant Security u1"
    test_utils.prt(f'\n\n\n{scenario_name} ... category: {context.category_before}')

@then('u1 Category count is 1')
def step_impl(context):
    if len(context.category_before) != 1:
        assert "Category count is not 1"
        
@given('Login user u2')
def step_impl(context):
    category_before = get_category_for_user('u2')
    context.category_before = category_before
    
@when('Get Category u2')
def step_impl(context):
    scenario_name = "Test Grant Security u2"
    test_utils.prt(f'\n\n\n{scenario_name} ... category: {context.category_before}')

@then('u2 Category count > 1')
def step_impl(context):
    if len(context.category_before)  < 2:
        assert "Category count is not > 1"
        

@given('Login User full')
def step_impl(context):
    category_before = get_category_for_user('full')
    context.category_before = category_before

@when('Get Category full')
def step_impl(context):
    scenario_name = "Test Grant Security full"
    test_utils.prt(f'\n\n\n{scenario_name} ... category: {context.category_before}')

@then('full Category count > 1')
def step_impl(context):
    if len(context.category_before)  < 2:
        assert "Category count is not > 1"

@given('Login user ro')
def step_impl(context):
    category_before = get_category_for_user('ro')
    context.category_before = category_before

@when('Get Category ro')
def step_impl(context):
    scenario_name = "Test Grant Security ro"
    test_utils.prt(f'\n\n\n{scenario_name} ... category: {context.category_before}')

@then('User ro count > 1')
def step_impl(context):
    if len(context.category_before)  < 2:
        assert "User ro Category count is not > 1"

@then('Delete ro Category')
def step_impl(context):
    header = test_utils.login('ro')
    get_uri = f'http://{host}:{port}/api/Category/1'
    r = requests.delete(url=get_uri, headers= header)
    context.response_text = r.text
    context.status_code = r.status_code
    #Grant Security Error on User: ro with roles: [[<UserRole ro, readonly>]] does not have delete access on entity: Category
    if 'Grant Security Error' not in r.text:
        assert f"user ro delete category 1 error: {r.text}"
        
@then('Insert ro Category')
def step_impl(context):
    #Grant Security Error on User: ro with roles: [[<UserRole ro, readonly>]] does not have insert access on entity: Category
    post_cat_uri = f'http://{host}:{port}/api/Category'
    post_args = \
        {
            "data": {
                "attributes": {
                    "CategoryName": "Test",
                    "Description": "should fail",
                    "Client_id": 999},
                "type": "Category",
                "id": 999
            }}
    r = requests.post(url=post_cat_uri, json=post_args, headers= test_utils.login('ro'))
    if 'Grant Security Error' not in r.text:
        assert f"user ro insert category 1 error: {r.text}"

@then('Update ro Category')
def step_impl(context):
    #Grant Security Error on User: ro with roles: [[<UserRole ro, readonly>]] does not have update access on entity: Category
    patch_cat_uri = f'http://{host}:{port}/api/Category'
    patch_args = \
        {
            "data": {
                "attributes": {
                    "CategoryName": "Test",
                    "Description": "should fail",
                    "Client_id": 1},
                "type": "Category",
                "id": 1
            }}
    r = requests.patch(url=patch_cat_uri, json=patch_args, headers= test_utils.login('ro'))
    if 'Grant Security Error' not in r.text:
        assert f"user ro update category 1 error: {r.text}"
