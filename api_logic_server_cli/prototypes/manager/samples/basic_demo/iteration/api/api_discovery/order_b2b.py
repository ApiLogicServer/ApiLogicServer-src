from flask import request, jsonify
import logging

from safrs import jsonapi_rpc
import safrs

from integration.row_dict_maps.OrderB2B import OrderB2B

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    pass


    """
    Illustrates #als: custom end point with swagger, RowDictMapper

    * Custom service - visible in swagger
    * Services *not* requiring authentication (contrast to CategoriesEndPoint, below)
    * Use OrderB2B (extends RowDictMapper) to map json to rows with aliasing, joins and lookups
    * Recall business logic is not in service, but encapsulated for reuse in logic/declare_logic.py
    """
    # class B2BSvcs(safrs.JABase):

    api.expose_object(ServicesEndPoint)  # Swagger-visible services

"""
Illustrates #als: custom end point with swagger, RowDictMapper

* Custom service - visible in swagger
* Services *not* requiring authentication (contrast to CategoriesEndPoint, below)
* Use OrderB2B (extends RowDictMapper) to map json to rows with aliasing, joins and lookups
* Recall business logic is not in service, but encapsulated for reuse in logic/declare_logic.py
"""
class ServicesEndPoint(safrs.JABase):


    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def OrderB2B(self, *args, **kwargs):  # yaml comment => swagger description
        """ # yaml creates Swagger description
            args :
                order:
                    Account: "Alice"
                    Notes: "Please Rush"
                    Items :
                    - Name: "Gadget"
                      QuantityOrdered: 1
                    - Name: "Widget"
                      QuantityOrdered: 2
                    - Name: "Green"
                      QuantityOrdered: 3
            ---

        Note attribute alias, Lookup automation in OrderB2B

        See: https://apilogicserver.github.io/Docs/Sample-Integration/
        Test with swagger, or, from command line:

        $(venv) ApiLogicServer login --user=admin --password=p
        $(venv) ApiLogicServer curl "'POST' 'http://localhost:5656/api/ServicesEndPoint/OrderB2B'" --data '
        {"meta": {"args": {"order": {
            "Account": "Customer 1",
            "Notes": "Please Rush",
            "Items": [
                {
                "Name": "Product A",
                "QuantityOrdered": 1
                },
                {
                "Name": "Product B",
                "QuantityOrdered": 2
                },
                {
                "Name": "Product B",
                "QuantityOrdered": 2
                }
                ]
            }
        }}}'

        """

        db = safrs.DB         # Use the safrs.DB, not db!
        session = db.session  # sqlalchemy.orm.scoping.scoped_session

        order_b2b_def = OrderB2B()
        request_dict_data = request.json["meta"]["args"]["order"]
        sql_alchemy_row = order_b2b_def.dict_to_row(row_dict = request_dict_data, session = session)

        session.add(sql_alchemy_row)
        return {"Thankyou For Your OrderB2B"}  # automatic commit, which executes transaction logic
