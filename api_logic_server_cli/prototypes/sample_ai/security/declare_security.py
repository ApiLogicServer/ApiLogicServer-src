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

declare_security_message = "Sample Grants Loaded"

db = safrs.DB
session = db.session


class Roles():
    """ Define Roles here, so can use code completion (Roles.tenant) """
    tenant = "tenant"           # aneu, u1, u2
    renter = "renter"           # r1
    manager = "manager"         # u2, sam
    sales="sales"               # s1

                                # user_id = 1 -- aneu              many customers, 1 category
                                # user_id = 2 -- u2, sam, s1, r1   3    customers, 3 categories

DefaultRolePermission(to_role = Roles.tenant, can_read=True, can_delete=True)
DefaultRolePermission(to_role = Roles.renter, can_read=True, can_delete=False)
DefaultRolePermission(to_role = Roles.manager, can_read=True, can_delete=False)
DefaultRolePermission(to_role = Roles.sales, can_read=True, can_delete=False)

#############################################
# Observe: Filters are AND'd, Grants are OR'd 
#############################################
GlobalFilter(   global_filter_attribute_name = "Region",  # sales see only Customers in British Isles (9 rows)
                roles_not_filtered = ["sa", "manager", "tenant", "renter"],  # ie, just sales
                filter = '{entity_class}.Region == Security.current_user().region')
        
Grant(  on_entity = models.Customer,
        to_role = Roles.sales,
        filter = lambda : models.Customer.CreditLimit > 300,
        filter_debug = "CreditLimit > 0")     # this eliminates all rows, but...

Grant(  on_entity = models.Customer,
        to_role = Roles.sales,
        filter = lambda : models.Customer.ContactName == "Mike",
        filter_debug = "ContactName == Mike (see security/declare_security.py)")

# so user s1 sees the CTWSR customer row, per the resulting where from 2 global filters and 2 Grants:
# where (Client_id=2 and region="British Isles") and (CreditLimit>300 or ContactName="Mike")
#       <---- Filters AND'd ------------------->     <--- Grants OR'd --------------------->


app_logger.debug("Declare Security complete - security/declare_security.py"
    + f' -- {len(database.authentication_models.metadata.tables)} tables loaded')
