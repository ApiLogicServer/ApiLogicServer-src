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
            "SalesRep": "??",
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
        
        custom_endpoint_child_list = custom_endpoint.children
        if isinstance(custom_endpoint_child_list, list) is False:
            custom_endpoint_child_list = []
            custom_endpoint_child_list.append(custom_endpoint.children)
        for each_child_def in custom_endpoint_child_list:
            child_property_name = each_child_def.role_name
            if child_property_name == '':
                child_property_name = "OrderList"  # FIXME default from class name
            if child_property_name.startswith('Product'):
                debug = 'good breakpoint'
            row_dict_child_list = getattr(row, child_property_name)
            row_as_dict[each_child_def.alias] = []
            if each_child_def.isParent:
                the_parent = getattr(row, child_property_name)
                the_parent_to_dict = self.to_dict(row = the_parent, current_endpoint = each_child_def)
                row_as_dict[each_child_def.alias].append(the_parent_to_dict)
            else:
                for each_child in row_dict_child_list:
                    each_child_to_dict = self.to_dict(row = each_child, current_endpoint = each_child_def)
                    row_as_dict[each_child_def.alias].append(each_child_to_dict)
        return row_as_dict
    

    def to_row(self, row_dict: dict, current_endpoint: 'IntegrationEndpoint' = None) -> object:
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
        
        custom_endpoint_child_list = custom_endpoint.children
        if isinstance(custom_endpoint_child_list, list) is False:
            custom_endpoint_child_list = []
            custom_endpoint_child_list.append(custom_endpoint.children)
        for each_child_def in custom_endpoint_child_list:
            child_property_name = each_child_def.alias
            if child_property_name.startswith('Items'):
                debug = 'good breakpoint'
            if child_property_name in row_dict:
                row_dict_child_list = row_dict[child_property_name]
                # row_as_dict[each_child_def.alias] = []  # set up row_dict child array
                if each_child_def.isParent:  # FIXME not support (but TODO Lookup!)
                    the_parent = getattr(row, child_property_name)
                    the_parent_to_dict = self.to_dict(row = the_parent, current_endpoint = each_child_def)
                    row_as_dict[each_child_def.alias].append(the_parent_to_dict)
                else:
                    for each_row_dict_child in row_dict_child_list:  # recurse for each_child
                        each_child_row = self.to_row(row_dict = each_row_dict_child, current_endpoint = each_child_def)
                        child_list = getattr(sql_alchemy_row, each_child_def.role_name)
                        child_list.append(each_child_row)
        return sql_alchemy_row