from database import models
from flask import request, jsonify
from sqlalchemy import Column
from api.system.custom_endpoint_base_def import CustomEndpointBaseDef

class IntegrationEndpoint(CustomEndpointBaseDef):
    """Services to support App Integration as described in api.custom_resources.readme

    Args:
        CustomEndpointBaseDef (_type_): _description_
    """

    '''
ApiLogicServer curl "'POST' 'http://localhost:5656/api/ServicesEndPoint/add_order_by_id'" --data '
{"order": {
            "AccountId": "ALFKI",
            "SalesRepId": 1,
            "Items": [
                {
                "ProductId": 1,
                "QuantityOrdered": 1
                },
                {
                "ProductId": 2,
                "QuantityOrdered": 2
                }
                ]
            }
}'

ApiLogicServer curl "'POST' 'http://localhost:5656/api/ServicesEndPoint/add_b2b_order'" --data '
{"order": {
            "AccountId": "ALFKI",
            "Surname": "Buchanan",
            "Given": "Steven",
            "Items": [
                {
                "ProductName": "Chai",
                "QuantityOrdered": 1
                },
                {
                "ProductName": "Chang",
                "QuantityOrdered": 2
                }
                ]
            }
}'

    '''
    
    def to_dict(self, row: object, current_endpoint: 'IntegrationEndpoint' = None) -> dict:
        """returns row as dict per custom resource definition, with subobjects

        Args:
            row (_type_): a SQLAlchemy row

        Returns:
            dict: row formatted as dict
        """
        custom_endpoint = self
        if current_endpoint is not None:
            custom_endpoint = current_endpoint
        # row_as_dict = self.row_to_dict(row)
        row_as_dict = {}
        for each_field in custom_endpoint.fields:
            if isinstance(each_field, tuple):
                row_as_dict[each_field[1]] = getattr(row, each_field[0].name)
            else:
                if isinstance(each_field, str):
                    print("Coding error - you need to use TUPLE for attr/alias")
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
                the_parent_to_dict = self.to_dict(row = the_parent, current_endpoint = each_related)
                if each_related.isCombined:
                    for each_attr_name, each_attr_value in the_parent_to_dict.items():
                        row_as_dict[each_attr_name] = each_attr_value
                else:
                    row_as_dict[each_related.alias] = the_parent_to_dict
            else:
                row_as_dict[each_related.alias] = []
                for each_child in row_dict_child_list:
                    each_child_to_dict = self.to_dict(row = each_child, current_endpoint = each_related)
                    row_as_dict[each_related.alias].append(each_child_to_dict)
        return row_as_dict
    

    def to_row(self, row_dict: dict, session: object, current_endpoint: 'IntegrationEndpoint' = None) -> object:
        """Returns SQLAlchemy row(s), converted from safrs-request per subclass custom resource

        Args:
            safrs_request: a 
            current_endpoint (IntegrationEndpoint, optional): _description_. Defaults to None.

        Returns:
            object: SQLAlchemy row / sub-rows, ready to insert
        """

        print( f"to_row receives row_dict: {row_dict}" )

        custom_endpoint = self
        if current_endpoint is not None:
            custom_endpoint = current_endpoint
        sql_alchemy_row = custom_endpoint._model_class()     # new instance
        for each_field in custom_endpoint.fields:           # attr mapping  FIXME 1 field, not array
            if isinstance(each_field, tuple):
                setattr(sql_alchemy_row, each_field[0].name, row_dict[each_field[1]])
            else:
                if isinstance(each_field, str):
                    print("Coding error - you need to use TUPLE for attr/alias")
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
                    self.lookup_parent(child_row_dict = row_dict, 
                            lookup_parent_endpoint = each_related, 
                            child_row = sql_alchemy_row,
                            session = session)
            else:
                if child_property_name in row_dict:
                    row_dict_child_list = row_dict[child_property_name]
                    # row_as_dict[each_related.alias] = []  # set up row_dict child array
                    for each_row_dict_child in row_dict_child_list:  # recurse for each_child
                        each_child_row = self.to_row(row_dict = each_row_dict_child, 
                                                        session = session,
                                                        current_endpoint = each_related)
                        child_list = getattr(sql_alchemy_row, each_related.role_name)
                        child_list.append(each_child_row)
        return sql_alchemy_row
    

    def lookup_parent(self, child_row_dict: dict, child_row: object,
                session: object, lookup_parent_endpoint: 'IntegrationEndpoint' = None):
        parent_class = lookup_parent_endpoint._model_class
        # parent_dict = getattr(row_dict, child_property_name)
        # filter = []
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
                parent_row = parent_rows[0]
                setattr(child_row, lookup_parent_endpoint.role_name, parent_row)
        return
