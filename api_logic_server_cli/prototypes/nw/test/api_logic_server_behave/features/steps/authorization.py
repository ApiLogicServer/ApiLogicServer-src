from behave import *
import requests, pdb
import json
import test_utils

host = "localhost"
port = "5656"

@given('NW Test Database')
def step_impl(context):
    pass

@when('u1 GETs Categories')
def step_impl(context):
    get_uri = f'http://localhost:5656/api/Category/?' \
        f'fields%5BCategory%5D=Id%2CCategoryName%2CDescription%2CClient_id%2C_check_sum_%2CS_CheckSum& '\
        f'page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id'
    response = requests.get(url=get_uri, headers= test_utils.login(user='u1'))
    context.response = response
    pass

@then('Only 1 is returned')
def step_impl(context):
    """
    u1 GETs Categories
    """
    scenario_name = 'Grant'
    response = context.response
    response_text = response.text
    result_data = json.loads(response_text)
    assert len(result_data['data']) == 1


@when('sam GETs Customers')
def step_impl(context):
    get_uri = f'http://localhost:5656/api/Customer/?' \
        f'include=OrderList&fields%5BCustomer%5D=Id%2CCompanyName%2CContactName%2CContactTitle%2CAddress%2CCity%2CRegion%2CPostalCode%2CCountry%2CPhone%2CFax%2CBalance%2CCreditLimit%2COrderCount%2CUnpaidOrderCount%2CClient_id%2C_check_sum_%2CS_CheckSum&'\
        f'page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id'
    response = requests.get(url=get_uri, headers= test_utils.login(user='sam'))
    context.response = response
    pass

@then('only 3 are returned')
def step_impl(context):
    """ ALFKI, ANATR, CTWTR 
    """
    scenario_name = 'Multi-tenant'
    response = context.response
    response_text = response.text
    result_data = json.loads(response_text)
    assert len(result_data['data']) == 3
    pass


@when('sam GETs Departments')
def step_impl(context):
    get_uri = f'http://localhost:5656/api/Department/?fields%5BDepartment%5D=Id%2CDepartmentId%2CDepartmentName&' \
        f'page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id'
    response = requests.get(url=get_uri, headers= test_utils.login(user='sam'))
    context.response = response
    pass

@then('only 8 are returned')
def step_impl(context):
    """
    Sam gets depts
    """
    scenario_name = 'Global Filters'
    response = context.response
    response_text = response.text
    result_data = json.loads(response_text)
    assert len(result_data['data']) == 8
    pass


@when('s1 GETs Customers')
def step_impl(context):
    """
    s1 GETs Customers
    """
    scenario_name = 'Global Filters With Grants'
    get_uri = f'http://localhost:5656/api/Customer/?' \
        f'include=OrderList&fields%5BCustomer%5D=Id%2CCompanyName%2CContactName%2CContactTitle%2CAddress%2CCity%2CRegion%2CPostalCode%2CCountry%2CPhone%2CFax%2CBalance%2CCreditLimit%2COrderCount%2CUnpaidOrderCount%2CClient_id%2C_check_sum_%2CS_CheckSum&'\
        f'page%5Boffset%5D=0&page%5Blimit%5D=10&sort=id'
    response = requests.get(url=get_uri, headers= test_utils.login(user='s1'))
    context.response = response
    pass

@then('only 1 customer is returned')
def step_impl(context):
    response = context.response
    response_text = response.text
    result_data = json.loads(response_text)
    assert len(result_data['data']) == 1
    pass


@when('r1 deletes a Shipper')
def step_impl(context):
    delete_uri = f'http://localhost:5656/api/Shipper/1/'
    response = requests.delete(url=delete_uri, headers= test_utils.login(user='r1'))
    context.response = response
    pass

@then('Operation is Refused')
def step_impl(context):
    """
    r1 deletes a Shipper
    """
    scenario_name = 'CRUD Permissions'
    response = context.response
    response_text = response.text
    assert 'does not have delete access' in response_text
    pass
