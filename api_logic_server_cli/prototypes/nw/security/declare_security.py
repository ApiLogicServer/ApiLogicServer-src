from security.system.authorization import Grant, Security, DefaultRolePermission, GlobalFilter
from database import models
import database
import safrs
import logging

"""
First, Activate Security: https://apilogicserver.github.io/Docs/Security-Activation/

Then, Declare Security here: https://apilogicserver.github.io/Docs/Security-Authorization/

See documentation: https://apilogicserver.github.io/Docs/Security-Overview/

Security is invoked on server start (api_logic_server_run), per activation in `config.py`

Your Code Goes Here

#als: Illustrates declarative security - role-based authorization to database rows.

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
    customer="customer"         # ALFKI, ANATR
    public="public"             # p1 (no roles, so gets public)

                                # user_id = 1 -- aneu              many customers, 1 category
                                # user_id = 2 -- u2, sam, s1, r1   3    customers, 3 categories

DefaultRolePermission(to_role = Roles.tenant, can_read=True, can_delete=True)
DefaultRolePermission(to_role = Roles.renter, can_read=True, can_delete=False)
DefaultRolePermission(to_role = Roles.manager, can_read=True, can_delete=False)
DefaultRolePermission(to_role = Roles.sales, can_read=True, can_delete=False)
DefaultRolePermission(to_role = Roles.public, can_read=True, can_delete=False)

GlobalFilter(   global_filter_attribute_name = "Client_id",  # try customers & categories for u1 vs u2
                roles_not_filtered = ["sa"],
                filter = '{entity_class}.Client_id == Security.current_user().client_id')
                # user attributes come from sqlalchemy User object, or keycloak user attributes


GlobalFilter(   global_filter_attribute_name = "SecurityLevel",  # filters Department 'Eng Area 54'
                roles_not_filtered = ["sa", "manager"],
                filter = '{entity_class}.SecurityLevel == 0')

#############################################
# Observe: Filters are AND'd, Grants are OR'd 
#############################################
GlobalFilter(   global_filter_attribute_name = "Region",  # sales see only Customers in British Isles (9 rows)
                roles_not_filtered = ["sa", "manager", "tenant", "renter", "public"],  # ie, just sales
                filter = '{entity_class}.Region == Security.current_user().region')
        
GlobalFilter(   global_filter_attribute_name = "Discontinued",  # hide discontinued products
                roles_not_filtered = ["sa", "manager"],         # except for admin and managers
                filter = '{entity_class}.Discontinued == 0')
        
Grant(  on_entity = models.Customer,
        to_role = Roles.customer,
        filter = lambda : models.Customer.Id == Security.current_user().id,
        filter_debug = "Id == Security.current_user().id")     # customers can only see their own account
        
Grant(  on_entity = models.Customer,
        to_role = Roles.sales,
        filter = lambda : models.Customer.CreditLimit > 300,
        filter_debug = "CreditLimit > 300")     # this eliminates all British Isle rows, but...

Grant(  on_entity = models.Customer,
        to_role = Roles.sales,
        filter = lambda : models.Customer.ContactName == "Mike",  # Mike sees his contacts
        filter_debug = "ContactName == Mike (see security/declare_security.py)")

# so user s1 sees the CTWSR customer row, per the resulting where from 2 global filters and 2 Grants:
# where (Client_id=2 and region="British Isles") and (CreditLimit>300 or ContactName="Mike")
#       <---- Filters AND'd ------------------->     <--- Grants OR'd --------------------->



Grant(  on_entity = models.Customer,
        to_role = Roles.public,
        filter = lambda : models.Customer.Id != 'ANATR',
        filter_debug = "Customer.Id != 'ANATR'")     # illustrates public role (user p1)


app_logger.debug("Declare Security complete - security/declare_security.py")
