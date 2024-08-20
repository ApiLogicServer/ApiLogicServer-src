from database import models
from safrs import jsonapi_attr
from sqlalchemy.orm import relationship, remote, foreign
import logging

app_logger = logging.getLogger(__name__)

from database.database_discovery.auto_discovery import discover_models
discover_models()

"""
If you wish to drive models from the database schema,
you can use this file to customize your schema (add relationships, derived attributes),
and preserve customizations over iterations (regenerations of models.py).

Called from models.py (classes describing schema, per introspection).
# add relationship: https://docs.sqlalchemy.org/en/13/orm/join_conditions.html#specifying-alternate-join-conditions

    models.Employee.Manager = relationship('Employee', 
        cascade_backrefs=False, backref='Manages',
        primaryjoin=remote(models.Employee.Id) == foreign(models.Employee.ReportsTo))

        
    # parent relns (access parent) -- on child EmployeeAudit
    Employee : Mapped["Employee"] = relationship(back_populates=("EmployeeAuditList"))

    # child relationships (access children) -- on parent Employee
    EmployeeAuditList : Mapped[List["EmployeeAudit"]] = relationship(back_populates="Employee")

Your Code Goes Here
"""

# parent
# models.ComprasCAB.ManagesList = relationship("ComprasLIN", back_populates=("Manager"))

# child
models.ComprasLIN.Manager = relationship("ComprasCAB",
    cascade_backrefs=False, backref='ManagesList',
    primaryjoin = remote(models.ComprasCAB.SerieNmero) == foreign(models.ComprasLIN.AlbarnCompra))

# sqlalchemy.exc.ArgumentError: Error creating backref
#  'ManagesList' on relationship 'ComprasLIN.Manager': property of that name 
#   exists on mapper 'Mapper[ComprasCAB(Compras_CAB)]'

