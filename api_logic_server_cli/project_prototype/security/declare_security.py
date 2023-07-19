from security.system.authorization import Grant, Security
from database import models
import database
import safrs
import logging

"""
Illustrates declarative security - role-based authorization to database rows..

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

# Configure each Role for default global permission using CRUD, All, or None
Grant(on_entity="ALL",to_role=Roles.manager)
Grant(on_entity="A",to_role=Roles.fullaccess)
Grant(on_entity="R",to_role=Roles.readonly)
Grant(on_entity="RU",to_role=Roles.tenant)
Grant(on_entity="N",to_role=Roles.renter)

Grant(  on_entity = models.Category    # illustrate multi-tenant - u1 shows only row 1
        , to_role = Roles.tenant
        , can_delete=False
        , filter = lambda :  models.Category.Client_id == Security.current_user().client_id)  # User table attributes

Grant(  on_entity = models.Category,    # u2 has both roles - should return client_id 2 (2, 3, 4), and 5
        to_role = Roles.manager,
        can_delete=False,
        filter = lambda : models.Category.Id == 5)

Grant(  on_entity = models.Customer,    # user full has full access - cannot delete customer
        can_delete=False,
        to_role = Roles.fullaccess)

Grant(  on_entity = models.Customer,    # user full has full access - cannot insert,update, or delete customer
        can_read=True,
        can_delete=False,
        can_update=False,
        can_insert=False,
        to_role = Roles.renter)

app_logger.debug("Declare Security complete - security/declare_security.py"
        + f' -- {len(Grant.grants_by_table)} Grants by tables loaded and {len(Grant.grants_by_role)} Grants by role loaded.')
