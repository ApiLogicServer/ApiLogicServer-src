from security.system.authorization import Grant, Security, DefaultRolePermission, GlobalTenantFilter
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
    tenant = "tenant"
    renter = "renter"
    manager = "manager"

DefaultRolePermission(to_role = Roles.tenant, can_read=True, can_delete=True)

DefaultRolePermission(to_role = Roles.renter, can_read=True, can_delete=False)

DefaultRolePermission(to_role = Roles.manager, can_read=True, can_delete=False)


use_global_tenant_filter = True
if use_global_tenant_filter:
        GlobalTenantFilter(multi_tenant_attribute_name = "Client_id",
                           roles_non_multi_tenant = ["sa"],
                           filter = '{entity_class}.Client_id == Security.current_user().client_id')

use_normal_grant = False
if use_normal_grant:
        # prove same filter works   1) as a normal Grant, and   2) using lambda variable
        filter_lambda = lambda :  models.Customer.Client_id == 1  #n SQLAlchemy "binary expression"
        Grant(  on_entity = models.Customer, 
                to_role = Roles.tenant,
                filter = filter_lambda) # lambda : models.Customer.Client_id == 1)

Grant(  on_entity = models.Category,    # illustrate multi-tenant - u1 shows only row 1
        to_role = Roles.tenant,
        filter = lambda : models.Category.Client_id == Security.current_user().client_id)  # User table attributes

Grant(  on_entity = models.Category,    # u2 has both roles - should return client_id 2 (2, 3, 4), and 5
        to_role = Roles.manager,
        filter = lambda : models.Category.Id == 5)

GlobalTenantFilter(multi_tenant_attribute_name = "SecurityLevel",  # filters Department 'Eng Area 54'
                        roles_non_multi_tenant = ["sa", "manager"],
                        filter = '{entity_class}.SecurityLevel == 0')

app_logger.debug("Declare Security complete - security/declare_security.py"
    + f' -- {len(database.authentication_models.metadata.tables)} tables loaded')
