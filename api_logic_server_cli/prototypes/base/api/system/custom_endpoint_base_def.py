from __future__ import annotations  # enables Resource self reference
import sqlalchemy
from sqlalchemy import update, insert
import logging
import contextlib
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.orm.decl_api import DeclarativeMeta #sqlalchemy.orm.decl_api.DeclarativeMeta
from sqlalchemy.orm import relationships, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import get_referencing_foreign_keys
from sqlalchemy import event, MetaData, and_, or_
from sqlalchemy.inspection import inspect
from sqlalchemy import select
from sqlalchemy.sql import text
from flask import jsonify
from sqlalchemy_utils.query_chain import QueryChain
import flask_sqlalchemy
import safrs
from safrs.errors import JsonapiError, ValidationError
from security.system.authorization import Security
from typing import List, Dict, Tuple
import util
import json 
import requests
from config import Config
from config import Args

resource_logger = logging.getLogger("api.customize_api")

db = safrs.DB 
"""this is a safrs db not DB"""
session = db.session  # type: sqlalchemy.orm.scoping.scoped_session

class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    
class CustomEndpointBaseDef():
    """
    Nested CustomEndpoint Definition

        customer = CustomEndpoint(model_class=models.Customer
            , alias="customers"
            , fields = [(models.Customer.CompanyName, "Customer Name")] 
            , children = 
                CustomEndpoint(model_class=models.Order
                    , alias = "orders"
                    , join_on=models.Order.CustomerId
                    , fields = [(models.Order.AmountTotal, "Total"), (models.Order.ShippedDate, "Ship Date")]
                    , children = CustomEndpoint(model_class=models.OrderDetail, alias="details"
                        , join_on=models.OrderDetail.OrderId
                        , fields = [models.OrderDetail.Quantity, models.OrderDetail.Amount]
                        , children = CustomEndpoint(model_class=models.Product, alias="product"
                            , join_on=models.OrderDetail.ProductId
                            , fields=[models.Product.UnitPrice, models.Product.UnitsInStock]
                            , isParent=True
                            , isCombined=False
                        )
                    )
                )
            )
        result = customer.execute(customer,"", "ALFKI")
        # or
        #result = customer.get(request,"OrderList&OrderList.OrderDetailList&OrderList.OrderDetailList.Product", "ALFKI")
    """

    def __init__(self
            , model_class: DeclarativeMeta | None
            , alias: str = ""
            , role_name: str = ""
            , fields: list[tuple[Column, str] | Column] = []
            , children: list[CustomEndpointBaseDef] | CustomEndpointBaseDef = []
            , join_on: list[tuple[Column] | Column] = None
            , calling: callable = None
            , filter_by: str = None
            , order_by: Column = None
            , isParent: bool = False
            , isCombined: bool = False
            ):
        """

        Declare a custom yser shaped resource.

        Args:
            :model_class (DeclarativeMeta | None): model.TableName
            :alias (str, optional): _description_. Defaults to "".
            :fields (list[tuple[Column, str]  |  Column], optional): model.Table.Column. Defaults to [].
            :children (list[CustomEndpoint] | CustomEndpoint, optional): CustomEndpoint(). Defaults to []. (OneToMany)
            join_on: list[tuple[Column, Column]] - this is a tuple of parent/child multiple field joins 
            :calling - name of function (passing row for virtual attributes or modification)
            :filter_by is string object in SQL format (e.g. '"ShipDate" != null')
            :order_by is Column object used to sort aac result (e.g. order_by=models.Customer.Name)
            :isParent = if True - use parent foreign key to join single lookup (ManyToOne)
            :isCombined =  combine the fields of the isParent = routeTrue with the _parentResource (flatten) 
            
        """
        if not model_class:
            raise ValueError("CustomEndpoint model_class=models.EntityName is required")
        #if join_on is None and children is not None or parent is not None:
        #    raise ValueError("join_on= is required if using children (child column)")

        self._model_class = model_class
        self.alias = alias or model_class._s_type.lower()
        self.role_name = role_name
        if role_name == '':
            self.role_name = model_class._s_class_name
            if not isParent:
                self.role_name = self.role_name + "List"
        self.fields = fields
        self.children = children or []
        self.calling = calling
        self.filter_by = filter_by
        self.order_by = order_by
        self.isCombined = isCombined
        self.join_on = join_on 
        self.isParent= isParent 
    
        if isinstance(join_on, tuple):
            if len(join_on) > 0:
                # get parent or child
                self.foreignKey = join_on[0] # - if we have multiple joins
        else:
            self.foreignKey = join_on

        # Internal Private 
        self.primaryKey: str = inspect(model_class).primary_key[0].name
        self.primaryKeyType: str = inspect(self._model_class).primary_key[0].type
        self._model_class_name: str = self._model_class._s_class_name
        # inspect(model_class).primary_key[0].type = Integer() ...
        self._parentResource: CustomEndpointBaseDef = None  # ROOT
        self._pkeyList: list = [] # primary key list  collect when needed - do not store
        self._fkeyList: list = [] # foreign_key list (used by isParent)  collect when needed - do not store
        self._dictRows: list = [] # temporary holding for query results (Phase 1)
        self._parentRow = Dict[str, any] # keep track of linkage
        self._method = None
        self._href = None
        self._columnNames = [k.key for k in self._model_class._s_columns]

    def __str__(self):
            print(
                f"Alias {self.alias} Model: {self._model_class.__name__} PrimaryKey: {self.primaryKey} FilterBy: {self.filter_by} OrderBy: {self.order_by}")

