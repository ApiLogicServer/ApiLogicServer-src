from functools import wraps
import logging
from flask_jwt_extended import get_jwt, jwt_required, verify_jwt_in_request
from config.config import Config, Args
from security.system.authorization import Security
import api.system.api_utils as api_utils
from typing import List
import safrs
import sqlalchemy
from flask import request, jsonify
from safrs import jsonapi_rpc, SAFRSAPI
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_mapper
from database import models
from flask_cors import cross_origin
from logic_bank.rule_bank.rule_bank import RuleBank
import integration.system.RowDictMapper as row_dict_mapper
from integration.row_dict_maps.OrderById import OrderById
from integration.row_dict_maps.OrderShipping import OrderShipping
from integration.row_dict_maps.OrderB2B import OrderB2B

# Customize this file to add endpoints/services, using SQLAlchemy as required
#     Separate from expose_api_models.py, to simplify merge if project rebuilt
# Called by api_logic_server_run.py

app_logger = logging.getLogger("api_logic_server_app")

# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated

def expose_services(app, api, project_dir, swagger_host: str, PORT: str):
    """ #als: Customize API - new end points for services 
    
    Brief background: see readme_customize_api.md

    Your Code Goes Here
    
    Illustrates Customized APIs and Data Access.

    1. Observe that APIs not limited to database objects, but are extensible.
    2. See: https://apilogicserver.github.io/Docs/Sample-Integration/
    3. See: https://apilogicserver.github.io/Docs/API-Customize/
    4. See: https://github.com/thomaxxl/safrs/wiki/Customization

    
    #### Illustrate Reusable Integration Services

    1. ServicesEndPoint OrderB2B() - 
            * Illustrates: Reusable IntegrationServices to POST order

    2. OrderShipping_Test() - 
            * Illustrates: SQLAlchemy related row retrieval, reformat as multi-table dict and convert to json

    #### Illustrate Using Flask and SQLAlchemy

    1. join_order() - 
            * Illustrates: SQLAlchemy parent join fields

    2. CategoriesEndPoint get_cats() - swagger, row security
            * Uses row_dict_mapper.rows_to_dict

    3. filters_cats() - model query with filters
            * Uses manual result creation (not util)

    4. raw_sql_cats() - raw sql (non-modeled objects)
            * Uses row_dict_mapper.rows_to_dict
    
    """

    app_logger.debug("api/customize_api.py - expose custom services")

    from api.api_discovery.auto_discovery import discover_services
    discover_services(app, api, project_dir, swagger_host, PORT)

    api.expose_object(ServicesEndPoint)  # Swagger-visible services
    api.expose_object(CategoriesEndPoint)

    @app.route('/hello_world')
    def hello_world():
        """        
        Illustrates:
        * Use standard Flask, here for non-database endpoints.

        Test it with:
        
                http://localhost:5656/hello_world?user=ApiLogicServer
        """
        user = request.args.get('user')
        # app_logger.info(f'hello_world returning:  hello, {user}')
        app_logger.info(f'{user}')
        return jsonify({"result": f'hello, {user}'})


    def bypass_security():
        """
        Support option to bypass security (see cats, below).

        See: https://flask-jwt-extended.readthedocs.io/en/stable/custom_decorators/
        """
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                if Config.SECURITY_ENABLED == False:
                    return fn(*args, **kwargs)
                verify_jwt_in_request(True)  # must be issued if security enabled
                return fn(*args, **kwargs)
            return decorator
        return wrapper

  
    def admin_required():
        """
        Support option to bypass security (see cats, below).
        """
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                if Args.instance.security_enabled == False:
                    return fn(*args, **kwargs)
                verify_jwt_in_request(True)  # must be issued if security enabled
                return fn(*args, **kwargs)
            return decorator
        return wrapper


    @app.route('/OrderShipping_Test', methods=['GET','OPTIONS'])
    @admin_required()
    @jwt_required()
    @cross_origin(supports_credentials=True)
    def OrderShipping_Test():
        """ 
        Illustrates  redundant (declare_logic)
        
        1. SQLAlchemy row retrieval
        
        2. RowDictMapper to reformat row as multi-table dict, and then json

        $(venv) ApiLogicServer login --user=admin --password=p
        $(venv) ApiLogicServer curl "http://localhost:5656/OrderShipping_Test?id=10643"

        """
        request_id = request.args.get('id')
        if request_id is None:
            request_id = 10643
        db = safrs.DB           # #als: SQLAlchemy retrieval
        session = db.session    # sqlalchemy.orm.scoping.scoped_session
        Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)
        the_order : models.Order = session.query(models.Order) \
                .filter(models.Order.Id == request_id).one()
        
        order_def = OrderShipping()
        dict_row = order_def.row_to_dict(row = the_order)
        return jsonify({"OrderShipping_Test with Items and Product":  dict_row})


    #########################################################
    # Illustrate using SQLAlchemy for views
    #########################################################

    @app.route('/ProductDetails_View', methods=['GET','OPTIONS'])
    @bypass_security()
    def ProductDetails_View():
        """
        Illustrates: 
        
        * #als: "Raw" SQLAlchemy table queries (non-mapped objects), by manual code

        $(venv) ApiLogicServer curl "http://localhost:5656/ProductDetails_View?id=1"

        Returns:
            json: response
        """

        request_id = request.args.get('id')
        db = safrs.DB
        session = db.session
        Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)
        if request_id is None:
            results = session.query(models.t_ProductDetails_View) 
        else:                   # observe filter requires view_name.c
            results = session.query(models.t_ProductDetails_View) \
                    .filter(models.t_ProductDetails_View.c.Id == request_id)
        return_result = []
        for each_result in results:
            row = { 'id': each_result.Id, 'name': each_result.ProductName}
            return_result.append(row)
        return jsonify({ "success": True, "result":  return_result})


    #########################################################
    # Illustrate using SQLAlchemy in standard Flask endpoints
    # #als: ORM database access
    #########################################################

    @app.route('/join_order')
    @bypass_security()
    def join_order():
        """
        Illustrates: SQLAlchemy join fields, by manual code

        Better: use RowDictMapper (see OrderB2B, below)

        If you've not used ORMs like SQLAlchemy, this example illustrates a few key features:
        * They return objects (not dicts), which enable code completion and type checking
        * They provide accessors to related data (parent join fields, child data)

        $(venv) ApiLogicServer curl "http://localhost:5656/join_order?id=11077"

        Returns:
            _type_: _description_
        """

        request_id = request.args.get('id')
        if request_id is None:
            request_id = 11078
        db = safrs.DB           # Use the safrs.DB, not db!
        session = db.session    # sqlalchemy.orm.scoping.scoped_session
        Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)
        the_order : models.Order = session.query(models.Order) \
                .filter(models.Order.Id == request_id).one()
        
        dict_row = {}
        dict_row["id"] = the_order.Id
        dict_row["AmountTotal"] = the_order.AmountTotal
        dict_row["SalesRepLastName"] = the_order.Employee.LastName  # access join field
        return jsonify({"order_with_join_attr":  dict_row})


    @app.route('/filters_cats')
    @bypass_security()
    def filters_cats():
        """
        Illustrates:
        * Explore SQLAlchemy and/or filters.
        
        Test (returns rows 2-5) (no auth):
            curl -X GET "http://localhost:5656/filters_cats" [no-filter | simple-filter]"
        """

        from sqlalchemy import and_, or_
        filter_type = request.args.get('filter')
        if filter_type is None:
            filter_type = "multiple filters"
        db = safrs.DB           # Use the safrs.DB, not db!
        session = db.session    # sqlalchemy.orm.scoping.scoped_session
        Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)

        if filter_type.startswith("n"):
            results = session.query(models.Category)    # .filter(models.Category.Id > 1)
        elif filter_type.startswith("s"):               # normally coded like this
            results = session.query(models.Category) \
                .filter(models.Category.Id > 1) \
                .filter(or_((models.Category.Client_id == 2), (models.Category.Id == 5)))
        else:                                           # simulate grant logic (multiple filters)
            client_grant = models.Category.Client_id == 2
            id_grant = models.Category.Id == 5
            grant_filter = or_( client_grant, id_grant)
            results = session.query(models.Category) \
                .filter(models.Category.Id > 1)  \
                .filter(grant_filter)
        return_result = []
        for each_result in results:
            row = { 'id': each_result.Id, 'name': each_result.CategoryName}
            return_result.append(row)
        return jsonify({ "success": True, "result":  return_result})


    @app.route('/raw_sql_cats')
    @bypass_security()
    def raw_sql_cats():
        """
        Illustrates:
        * #als: "Raw" SQLAlchemy table queries (non-mapped objects)
        * Observe phyical column name: CategoryName_ColumnName
              * Contrast to models.py, get_cats()
        
        Test (auth optional):
            curl -X GET "http://localhost:5656/raw_sql_cats"

        """
        DB = safrs.DB 
        sql_query = DB.text("SELECT * FROM CategoryTableNameTest")
        with DB.engine.begin() as connection:
            query_result = connection.execute(sql_query).all()
            rows_to_dict_rows = row_dict_mapper.rows_to_dict(query_result)
        response = {"result": rows_to_dict_rows} 
        return response


    @app.route('/stop')
    def stop():
        """
        Use this to stop the server from the Browser.
        * See: https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c
        * See: https://github.com/thomaxxl/safrs/wiki/Customization

        Usage:

                http://localhost:5656/stop?msg=API stop - Stop API Logic Server
        """

        import os, signal

        msg = request.args.get('msg')
        app_logger.info(f'\nStopped server: {msg}\n')

        os.kill(os.getpid(), signal.SIGINT)
        return jsonify({ "success": True, "message": "Server is shutting down..." })


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
                    AccountId: "ALFKI"
                    Given: "Steven"
                    Surname: "Buchanan"
                    Items :
                    - ProductName: "Chai"
                      QuantityOrdered: 1
                    - ProductName: "Chang"
                      QuantityOrdered: 2
            ---

        Note attribute alias, Lookup automation in OrderB2B

        See: https://apilogicserver.github.io/Docs/Sample-Integration/
        Test with swagger, or, from command line:

        $(venv) ApiLogicServer login --user=admin --password=p
        $(venv) ApiLogicServer curl "'POST' 'http://localhost:5656/api/ServicesEndPoint/OrderB2B'" --data '
        {"meta": {"args": {"order": {
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
        }}}'

        """

        db = safrs.DB         # Use the safrs.DB, not db!
        session = db.session  # sqlalchemy.orm.scoping.scoped_session

        order_b2b_def = OrderB2B()  # a RowDictMapper
        request_dict_data = request.json["meta"]["args"]["order"]
        sql_alchemy_row = order_b2b_def.dict_to_row(row_dict = request_dict_data, session = session)
        sql_alchemy_row.Ready = True

        session.add(sql_alchemy_row)
        return {"Thankyou For Your OrderB2B"}  # automatic commit, which executes transaction logic
    

    #################################################################################
    # The example above is a best practice,
    #   using the OrderB2B object for mapping, alias, and lookup IntegrationServices.
    #
    # Contrast to the discouraged examples below
    #################################################################################
    
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def add_order_by_id(self, *args, **kwargs):  # yaml comment => swagger description
        """ # yaml creates Swagger description
            args:
                order :
                    AccountId: ALFKI
                    SalesRepId: 1
                    Items :
                    - ProductId: 1
                      QuantityOrdered: 1
                    - ProductId: 2
                      QuantityOrdered: 2
            ---

            Best Practice: use OrderB2B for automated map/alias, Lookups etc.
              eg, how would a B2B partner determine a SalesRepId or a ProductId?
            Test using swagger -> try it out (includes sample data, above)
        """

        db = safrs.DB         # Use the safrs.DB, not db!
        session = db.session  # sqlalchemy.orm.scoping.scoped_session

        order_id_def = OrderById()  # a RowDictMapper, but without joins, lookups
        request_dict_data = request.json["meta"]["args"]["order"]
        sql_alchemy_row = order_id_def.dict_to_row(row_dict = request_dict_data, session = session)

        session.add(sql_alchemy_row)
        return {"Thankyou For Your OrderById"}  # automatic commit, which executes transaction logic

    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def add_order(self, *args, **kwargs):  # yaml comment => swagger description
        """ # yaml creates Swagger description
            args :
                CustomerId: ALFKI
                EmployeeId: 1
                Freight: 10
                OrderDetailList :
                  - ProductId: 1
                    Quantity: 1
                    Discount: 0
                  - ProductId: 2
                    Quantity: 2
                    Discount: 0
            ---

            Best Practice: use OrderB2B for automated map/alias, Lookups etc.
            Test using swagger -> try it out (includes sample data, above)
        """

        db = safrs.DB         # Use the safrs.DB, not db!
        session = db.session  # sqlalchemy.orm.scoping.scoped_session
        new_order = models.Order()
        new_order.Ready = True
        session.add(new_order)

        row_dict_mapper.json_to_entities(kwargs, new_order)  # generic function - any db object
        return {"Thankyou For Your Order"}  # automatic commit, which executes transaction logic



"""
Illustrates #als: auth required
* Swagger-visible RPC that requires authentication (@jwt_required()).
* Row Security

Test in swagger (auth required)
* Post to endpoint auth to obtain <access_token> value - copy to clipboard
        * Row Security - Users determines results
        * u1 - 1 row, u2 - 4 rows, admin - 9 rows
* Authorize (top of swagger), using Bearer <access_token>
* Post to CategoriesEndPoint/get_cats, observe results depend on login

"""
class CategoriesEndPoint(safrs.JABase):

    @staticmethod
    @jwt_required()
    @jsonapi_rpc(http_methods=['POST'], valid_jsonapi=False)
    def get_cats():
        db = safrs.DB
        session = db.session

        result = session.query(models.Category)
        for each_row in result:
            app_logger.debug(f'each_row: {each_row}')
        rows = row_dict_mapper.rows_to_dict(result)
        response = {"result": rows}
        return response
