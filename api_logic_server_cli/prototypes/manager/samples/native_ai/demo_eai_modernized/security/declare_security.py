"""
Feature: Row-Level Security
  Scenario: Sales role sees limited customers
    Given a user with the sales role
    When querying the Customer list
    Then only return customers where credit_limit >= 3000 or balance > 0
"""

from security.system.authorization import Grant, Security, DefaultRolePermission, GlobalFilter
import logging
from database import models
import safrs

db = safrs.DB
session = db.session

app_logger = logging.getLogger(__name__)

declare_security_message = "Sales role row-level grants active"


class Roles():
    """For code completion (auth data is the source of truth)."""
    manager = "manager"
    sales = "sales"
    teller = "teller"
    tenant = "tenant"
    customer = "customer"
    read_only = "readonly"
    admin = "CS_ADMIN"
    public = "public"
    sa = "sa"
    default_roles_kcals = "default-roles-kcals"
    uma_authorization = "uma_authorization"


DefaultRolePermission(to_role=Roles.sa, can_read=True, can_update=True, can_insert=True, can_delete=True)
DefaultRolePermission(to_role=Roles.tenant, can_read=True, can_delete=True)
DefaultRolePermission(to_role=Roles.admin, can_read=True, can_insert=True, can_update=True, can_delete=True)
DefaultRolePermission(to_role=Roles.manager, can_read=True, can_insert=True, can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.sales, can_read=True, can_insert=False, can_update=False, can_delete=False)
DefaultRolePermission(to_role=Roles.teller, can_read=True, can_insert=True, can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.customer, can_read=True, can_insert=True, can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.read_only, can_read=True, can_insert=False, can_update=False, can_delete=False)
DefaultRolePermission(to_role=Roles.public, can_read=True, can_insert=False, can_update=False, can_delete=False)
DefaultRolePermission(to_role=Roles.default_roles_kcals, can_read=True, can_insert=True, can_update=True, can_delete=False)
DefaultRolePermission(to_role=Roles.uma_authorization, can_read=True, can_insert=True, can_update=True, can_delete=False)

# §5 Security — Row-Level Security on Customer for sales role
Grant(
    on_entity=models.Customer,
    to_role=Roles.sales,
    filter=lambda: models.Customer.credit_limit >= 3000,
    filter_debug="credit_limit >= 3000"
)

# §5 Security — Row-Level Security on Customer for sales role
Grant(
    on_entity=models.Customer,
    to_role=Roles.sales,
    filter=lambda: models.Customer.balance > 0,
    filter_debug="balance > 0"
)
