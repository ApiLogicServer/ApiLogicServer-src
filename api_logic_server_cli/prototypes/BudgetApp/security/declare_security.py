from security.system.authorization import Grant, Security, DefaultRolePermission, GlobalTenant
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

Grant(  on_entity = models.Category,    # illustrate multi-tenant
        to_role = Roles.tenant,
        filter = lambda : models.Category.Client_id == Security.current_user().client_id)  # User table attributes

See [documentation](https://apilogicserver.github.io/Docs/Security-Overview/)

Security is invoked on server start (api_logic_server_run), per activation in `config.py`
"""

class Roles():
    ''' Define Roles here, so can use code completion (Roles.tenant) '''
    tenant = "tenant"
    renter = "renter"
    manager = "manager"
    
GlobalFilter(global_filter_attribute_name="user_id",
                roles_not_filtered = ["sa", "manager"],   
                filter="{entity_class}.user_id == Security.current_user().id")