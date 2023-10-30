from security.system.authorization import Grant, Security, Security, DefaultRolePermission, GlobalFilter
import logging
from database import models
import safrs

db = safrs.DB
session = db.session

app_logger = logging.getLogger(__name__)

"""

First, Activate Security: https://apilogicserver.github.io/Docs/Security-Activation/

Then, Declare Security here, for example:

class Roles():
    ''' Define Roles here, so can use code completion (Roles.tenant) '''
    tenant = "tenant"
    renter = "renter"
    manager = "manager"


DefaultRolePermission(to_role = Roles.tenant, can_read=True, can_delete=True)

DefaultRolePermission(to_role = Roles.renter, can_read=True, can_delete=False)

DefaultRolePermission(to_role = Roles.manager, can_read=True, can_delete=False)

GlobalFilter(global_filter_attribute_name = "Client_id",
                    roles_not_filtered = ["sa"],
                    filter = '{entity_class}.Client_id == Security.current_user().client_id')


Grant(  on_entity = models.Category,    # illustrate multi-tenant
        to_role = Roles.tenant,
        filter = lambda : models.Category.Client_id == Security.current_user().client_id)  # User table attributes

See [documentation](https://apilogicserver.github.io/Docs/Security-Overview/)

Security is invoked on server start (api_logic_server_run), per activation in `config.py`
"""