from database import models
from flask import request, jsonify
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy.model import DefaultMeta
from typing import Self
import logging

logger = logging.getLogger(__name__)

class IntegrationService():
    """Services to support App Integration as described in api.custom_resources.readme

    See: https://apilogicserver.github.io/Docs/Sample-Integration/

    """

    def __init__(self
            , model_class: type[DefaultMeta] | None
            , alias: str = ""
            , role_name: str = ""
            , fields: list[tuple[Column, str] | Column] = []
            , lookup: list[tuple[Column, str] | Column] = None
            , related: list[Self] | Self = []
            , isParent: bool = False
            , isCombined: bool = True
            ):
        """

        Declare a user shaped dict based on a SQLAlchemy model class.

        See: https://apilogicserver.github.io/Docs/Sample-Integration/

        Args:
            :model_class (DeclarativeMeta | None): model.Class
            :alias (str, optional): name of this level in dict
            :role_name (str, optional): disambiguate multiple relationships between 2 tables
            :fields (list[tuple[Column, str]  |  Column], optional): fields, use tuple for alias
            :lookup (list[tuple[Column, str]  |  Column], optional): Foreign Key Lookups
            :related (list[IntegrationService] | IntegrationService): Nested objects in multi-table dict
            :isParent (bool): is ManyToOne
            :isCombined (bool):  combine the fields of the containing parent 
        """
        if not model_class:
            raise ValueError("CustomEndpoint model_class=models.EntityName is required")

        self._model_class = model_class
        self.role_name = role_name
        """ class_name || 'List' """
        if role_name == '':
            self.role_name = model_class._s_class_name
            if not isParent:
                self.role_name = self.role_name + "List"
        self.alias = alias or self.role_name
        self.fields = fields
        self.lookup = lookup
        self.related = related or []
        self.isCombined = isCombined
        self.isParent= isParent 
    

    def __str__(self):
            return f"Alias {self.alias} -- Model: {self._model_class.__name__}"


    def row_to_dict(self, row: object, current_endpoint: 'IntegrationService' = None) -> dict:
        """returns row as dict per IntegrationService definition, with subobjects

        Args:
            row (_type_): a SQLAlchemy row
            current_endpoint(Self): omit (internal recursion use)

        Returns:
            dict: row formatted as dict
        """
        custom_endpoint = self
        if current_endpoint is not None:
            custom_endpoint = current_endpoint
        row_as_dict = {}
        for each_field in custom_endpoint.fields:
            if isinstance(each_field, tuple):
                row_as_dict[each_field[1]] = getattr(row, each_field[0].name)
            else:
                if isinstance(each_field, str):
                    logger.info("Coding error - you need to use TUPLE for attr/alias")
                row_as_dict[each_field.name] = getattr(row, each_field.name)
        
        custom_endpoint_related_list = custom_endpoint.related
        if isinstance(custom_endpoint_related_list, list) is False:
            custom_endpoint_related_list = []
            custom_endpoint_related_list.append(custom_endpoint.related)
        for each_related in custom_endpoint_related_list:
            child_property_name = each_related.role_name
            if child_property_name == '':
                child_property_name = "OrderList"  # FIXME default from class name
            if child_property_name.startswith('Product'):
                debug = 'good breakpoint'
            row_dict_child_list = getattr(row, child_property_name)
            if each_related.isParent:
                the_parent = getattr(row, child_property_name)
                the_parent_to_dict = self.row_to_dict(row = the_parent, current_endpoint = each_related)
                if each_related.isCombined:
                    for each_attr_name, each_attr_value in the_parent_to_dict.items():
                        row_as_dict[each_attr_name] = each_attr_value
                else:
                    row_as_dict[each_related.alias] = the_parent_to_dict
            else:
                row_as_dict[each_related.alias] = []
                for each_child in row_dict_child_list:
                    each_child_to_dict = self.row_to_dict(row = each_child, current_endpoint = each_related)
                    row_as_dict[each_related.alias].append(each_child_to_dict)
        return row_as_dict
    

    def dict_to_row(self, row_dict: dict, session: object, current_endpoint: 'IntegrationService' = None) -> object:
        """Returns SQLAlchemy row(s), converted from dict per IntegrationService definition

        Args:
            row_dict (dict): multi-object dict, typically from request data
            session (session): FlaskSQLAlchemy session
            current_endpoint (IntegrationService, optional): omit (internal recursion use)

        Returns:
            object: SQLAlchemy row / sub-rows, ready to insert
        """

        logger.debug( f"to_row receives row_dict: {row_dict}" )

        custom_endpoint = self
        if current_endpoint is not None:
            custom_endpoint = current_endpoint
        sql_alchemy_row = custom_endpoint._model_class()     # new instance
        for each_field in custom_endpoint.fields:           # attr mapping  FIXME 1 field, not array
            if isinstance(each_field, tuple):
                setattr(sql_alchemy_row, each_field[0].name, row_dict[each_field[1]])
            else:
                if isinstance(each_field, str):
                    logger.info("Coding error - you need to use TUPLE for attr/alias")
                setattr(sql_alchemy_row, each_field.name, row_dict[each_field.name])
        
        custom_endpoint_related_list = custom_endpoint.related
        if isinstance(custom_endpoint_related_list, list) is False:
            custom_endpoint_related_list = []
            custom_endpoint_related_list.append(custom_endpoint.related)
        for each_related in custom_endpoint_related_list:
            child_property_name = each_related.alias
            if child_property_name.startswith('SalesRep'):
                debug = 'good breakpoint'
            if each_related.isParent:  # lookup
                    self._lookup_parent(child_row_dict = row_dict, 
                                       lookup_parent_endpoint = each_related, 
                                       child_row = sql_alchemy_row,
                                       session = session)
            else:
                if child_property_name in row_dict:
                    row_dict_child_list = row_dict[child_property_name]
                    # row_as_dict[each_related.alias] = []  # set up row_dict child array
                    for each_row_dict_child in row_dict_child_list:  # recurse for each_child
                        each_child_row = self.dict_to_row(row_dict = each_row_dict_child, 
                                                        session = session,
                                                        current_endpoint = each_related)
                        child_list = getattr(sql_alchemy_row, each_related.role_name)
                        child_list.append(each_child_row)
        return sql_alchemy_row
    

    def _lookup_parent(self, child_row_dict: dict, child_row: object,
                      session: object, lookup_parent_endpoint: 'IntegrationService' = None):
        parent_class = lookup_parent_endpoint._model_class
        query = session.query(parent_class)
        if lookup_parent_endpoint.lookup is not None:
            lookup_param_fields = lookup_parent_endpoint.lookup
            if isinstance(lookup_param_fields, str):
                lookup_param_fields = lookup_parent_endpoint.fields
            for each_lookup_param_field in lookup_param_fields:
                attr_name = each_lookup_param_field
                if isinstance(each_lookup_param_field, tuple):
                    col_def = each_lookup_param_field[0]
                    attr_name = each_lookup_param_field[1]
                else:
                    col_def = each_lookup_param_field
                    attr_name = each_lookup_param_field.name
                filter_parm = child_row_dict[attr_name]
                filter_val = child_row_dict[attr_name]
                query = query.filter(col_def == filter_val)
                pass
            parent_rows = query.all()
            if parent_rows is not None:
                if len(parent_rows) > 1:
                    raise ValueError('Lookup failed: multiple parents', child_row, str(lookup_parent_endpoint)) 
                if len(parent_rows) == 0:
                    raise ValueError('Lookup failed: missing parent', child_row, str(lookup_parent_endpoint)) 
                parent_row = parent_rows[0]
                setattr(child_row, lookup_parent_endpoint.role_name, parent_row)
        return
