from security.system.authorization import Grant, Security
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
        readonly = "readonly"
        fullaccess = "fullaccess"
"""
Data error Generic Error: Can't invoke Python callable current_user() 
inside of lambda expression argument at <code object <lambda> at 0x1074ca600, file
"/Users/tylerband/development/apiLogicServerInstall/northwind/security/declare_security.py", line 31>;
lambda SQL constructs should not invoke functions from closure variables to produce literal values
since the lambda SQL system normally extracts bound values without actually invoking the lambda 
or any functions within it.  Call the function outside of the lambda and assign to a local variable 
that is used in the lambda as a closure variable, or set track_bound_values=False 
if the return value of this function is used in some other way other than a SQL bound value.
"""


Grant(  on_entity = models.Category,    # illustrate multi-tenant - u1 shows only row 1
        to_role = Roles.tenant,
        can_delete=False,
        filter =  lambda: models.Category.Client_id == Security.current_user().client_id)  # User table attributes

Grant(  on_entity = models.Category,    # u2 has both roles - should return client_id 2 (2, 3, 4), and 5
        to_role = Roles.manager,
        can_delete=False,
        filter = lambda: models.Category.Id == 5)

Grant(  on_entity = models.Customer,    # ro has only read only access and should only return 1 Customer Row - override update
        to_role = Roles.readonly,
        can_update=True,
        can_delete=False,
        filter = lambda: models.Customer.Id == 'ALFKI')

Grant(  on_entity = models.Customer,    # full has full access - cannot delete customer
        can_delete=False,
        to_role = Roles.fullaccess)

Grant(on_entity='F', can_delete=False, to_role=Roles.fullaccess)
Grant(on_entity='R',to_role=Roles.readonly)

app_logger.debug("Declare Security complete - security/declare_security.py"
    + f' -- {len(database.authentication_models.metadata.tables)} tables loaded')
