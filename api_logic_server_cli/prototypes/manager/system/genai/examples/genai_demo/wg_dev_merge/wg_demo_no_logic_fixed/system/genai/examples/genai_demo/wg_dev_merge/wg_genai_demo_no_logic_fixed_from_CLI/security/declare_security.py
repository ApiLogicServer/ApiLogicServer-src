from security.system.authorization import Grant, Security, Security, DefaultRolePermission, GlobalFilter
import logging
from database import models
import safrs

db = safrs.DB
session = db.session

app_logger = logging.getLogger(__name__)

declare_security_message = "No Grants Yet"  # printed in api_logic_server.py

"""
First, Activate Security: https://apilogicserver.github.io/Docs/Security-Activation/

Then, Declare Security here: https://apilogicserver.github.io/Docs/Security-Authorization/

See documentation: https://apilogicserver.github.io/Docs/Security-Overview/

Security is invoked on server start (api_logic_server_run), per activation in `config.py`

Your Code Goes Here - alter the starter code below to suit your needs
"""

class Roles():
    """ For code completion (auth data is the source of truth) 
    
    Revise these for your app's roles"""
    manager = "manager"
    teller = "teller"
    tenant = "tenant"
    customer = "customer"
    read_only = "readonly"
    admin = "CS_ADMIN"
    public="public"             # p1/p (no roles, but gets public)
    
DefaultRolePermission(to_role=Roles.tenant, can_read=True, can_delete=True)
DefaultRolePermission(to_role=Roles.admin, can_read=True, can_insert=True,can_update=True, can_delete=True)
DefaultRolePermission(to_role=Roles.manager, can_read=True, can_insert=True,can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.teller, can_read=True, can_insert=True,can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.customer, can_read=True, can_insert=True,can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.read_only, can_read=True, can_insert=False,can_update=False, can_delete=False)
DefaultRolePermission(to_role=Roles.public, can_read=True, can_insert=False,can_update=False, can_delete=False)
