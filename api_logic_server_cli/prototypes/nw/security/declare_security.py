from security.system.authorization import Grant, Security, DefaultRolePermission, GlobalFilter
from database import models
import database
import safrs
import logging

"""
Illustrates declarative security - role-based authorization to database rows.

* See [documentation](https://apilogicserver.github.io/Docs/Security-Overview/)

* Security is invoked on server start (api_logic_server_run), per activation in `config.py`
"""

app_logger = logging.getLogger(__name__)

db = safrs.DB
session = db.session


class Roles():
    """ Define Roles here, so can use code completion (Roles.tenant) """
    tenant = "tenant"           # aneu, u1, u2
    renter = "renter"           # r1
    manager = "manager"         # u2, sam
    sales="sales"               # s1

DefaultRolePermission(to_role = Roles.tenant, can_read=True, can_delete=True)

DefaultRolePermission(to_role = Roles.renter, can_read=True, can_delete=False)

DefaultRolePermission(to_role = Roles.manager, can_read=True, can_delete=False)

DefaultRolePermission(to_role = Roles.sales, can_read=True, can_delete=False)


use_global_tenant_filter = True
if use_global_tenant_filter:
        GlobalFilter(   global_filter_attribute_name = "Client_id",
                        roles_not_filtered = ["sa"],
                        filter = '{entity_class}.Client_id == Security.current_user().client_id')


GlobalFilter(   global_filter_attribute_name = "SecurityLevel",  # filters Department 'Eng Area 54'
                roles_not_filtered = ["sa", "manager"],
                filter = '{entity_class}.SecurityLevel == 0')

by_region = True
if by_region:
        GlobalFilter(   global_filter_attribute_name = "Region",
                        roles_not_filtered = ["sa", "manager", "tenant", "renter"],  # for sales
                        filter = '{entity_class}.Region == Security.current_user().region')

############################
# Observer Grants are OR'd
############################
Grant(  on_entity = models.Customer,
        to_role = Roles.sales,
        filter = lambda : models.Customer.CreditLimit > 300,
        filter_debug = "Credit > 300... filters out CTWTR, but *passes* ContactName")

Grant(  on_entity = models.Customer,
        to_role = Roles.sales,
        filter = lambda : models.Customer.ContactName == "Mike",
        filter_debug = "ContactName Mike granted (grants are OR'd)")


app_logger.debug("Declare Security complete - security/declare_security.py"
    + f' -- {len(database.authentication_models.metadata.tables)} tables loaded')
