"""
Feature: Security and Row Level Access

* **Keycloak RS256 Bearer Authentication (`authenticate`)**:
  * Validates `Authorization: Bearer <token>` against the Keycloak realm's JWKS endpoint (`{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs`, defaulting to `http://localhost:8080` and realm `kcals`).
  * Unauthenticated requests receive `401 Unauthorized`, except for open operational/test routes: `/health`, `/kafka_log`, and `/consume_debug/<topic>`.
* **Role Assignment & Row-Level Security (`row_filter`)**:
  * Roles are extracted from JWT `realm_access.roles`, and usernames listed in `SALES_USERS` (default `"u1"`) are automatically granted the `sales` role.
  * When a user has the `sales` role, all queries, single-row lookups, updates, and deletes on `Customer` are restricted to rows satisfying:
    `credit_limit >= 3000 OR balance > 0`
  * Filtered-out customers are omitted from `GET /api/customer` list responses and return `404 Not Found` on `/api/customer/<id>` operations.
"""
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
    sa="sa"
    sales = "sales"
    default_roles_kcals = "default-roles-kcals"
    uma_authorization = "uma_authorization"
    
DefaultRolePermission(to_role=Roles.sa, can_read=True, can_update=True, can_insert=True, can_delete=True)
DefaultRolePermission(to_role=Roles.tenant, can_read=True, can_delete=True)
DefaultRolePermission(to_role=Roles.admin, can_read=True, can_insert=True,can_update=True, can_delete=True)
DefaultRolePermission(to_role=Roles.manager, can_read=True, can_insert=True,can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.teller, can_read=True, can_insert=True,can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.customer, can_read=True, can_insert=True,can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.read_only, can_read=True, can_insert=False,can_update=False, can_delete=False)
DefaultRolePermission(to_role=Roles.public, can_read=True, can_insert=False,can_update=False, can_delete=False)
DefaultRolePermission(to_role=Roles.default_roles_kcals, can_read=True, can_insert=True,can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.uma_authorization, can_read=True, can_insert=True,can_update=True, can_delete=False)

# 5. Role Assignment & Row-Level Security: Keycloak validates the bearer token (RS256, realm kcals); roles come from
#    the token's realm roles.  Users with the sales role see, update and delete only customers with
#    credit_limit >= 3000 OR balance > 0 (two grants for one role are OR'd); others get 404.
DefaultRolePermission(to_role=Roles.sales, can_read=True, can_insert=True, can_update=True, can_delete=True)

Grant(  on_entity    = models.Customer,
        to_role      = Roles.sales,
        filter       = lambda: models.Customer.credit_limit >= 3000,
        filter_debug = "credit_limit >= 3000")

Grant(  on_entity    = models.Customer,
        to_role      = Roles.sales,
        filter       = lambda: models.Customer.balance > 0,
        filter_debug = "balance > 0")
