import logging
import api.system.api_utils as api_utils
import safrs
from flask import request, jsonify
from safrs import jsonapi_rpc
from database import models

# called by api_logic_server_run.py, to customize api (new end points, services).
# separate from expose_api_models.py, to simplify merge if project recreated

app_logger = logging.getLogger(__name__)

def expose_services(app, api, project_dir, swagger_host: str, PORT: str):
    """ Customize API - new end points for services 
    
        Brief background: see readme_customize_api.md
    
    """
    from api.api_discovery.auto_discovery import discover_services
    discover_services(app, api, project_dir, swagger_host, PORT)

    app_logger.debug("api/customize_api.py - expose custom services")
    api.expose_object(ServicesEndPoint)
    @app.route('/hello_world')
    def hello_world():  # test it with: http://localhost::5656/hello_world?user=ApiLogicServer
        """
        This is inserted to illustrate that APIs not limited to database objects, but are extensible.

        See: https://apilogicserver.github.io/Docs/API-Customize/

        See: https://github.com/thomaxxl/safrs/wiki/Customization
        """
        user = request.args.get('user')
        return jsonify({"result": f'hello, {user}'})


    @app.route('/stop')
    def stop():  # test it with: http://localhost:5656/stop?msg=API stop - Stop API Logic Server
        """
        Use this to stop the server from the Browser.

        See: https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c

        See: https://github.com/thomaxxl/safrs/wiki/Customization
        """

        import os, signal

        msg = request.args.get('msg')
        app_logger.info(f'\nStopped server: {msg}\n')

        os.kill(os.getpid(), signal.SIGINT)
        return jsonify({ "success": True, "message": "Server is shutting down..." })

class ServicesEndPoint(safrs.JABase):
    
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def budget_insert(cls, *args, **kwargs): 
        """ # yaml creates Swagger description
            args :
                year_id: 2023
                qtr_id: 1
                month_id: 1
                user_id: 1
                category_id: 1
                actual_amount: 0
                amount: 100
                is_expense: 1
                description: 'test insert'
        """
        from datetime import datetime
        db = safrs.DB  # valid only after is initialized, above
        session = db.session
        #for category_id in range(5):
        
        budget = models.Budget()
        budget.year_id = 2023
        budget.qtr_id = 1
        budget.month_id = 1
        budget.user_id = 1
        budget.category_id = 1
        budget.actual_amount = 0
        budget.amount = 100
        budget.is_expense = 1
        budget.description = 'test insert'
        api_utils.json_to_entities(kwargs, budget)
        session.add(budget)
        return {"budget insert done"}
        
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def transaction_insert(cls, *args, **kwargs): 
        """ # yaml creates Swagger description
            args :
                budget_id: 1
                amount: 100
                category_id: 1
                is_expense: 0
                description: 'test transaction insert'
        """
        from datetime import datetime
        db = safrs.DB  # valid only after is initialized, above
        session = db.session
        
        trans = models.Transaction()
        trans.budget_id = 1
        trans.amount = 100
        trans.account_id = 1
        trans.is_expense = 0
        trans.category_id = 1 
        trans.description = 'test insert'
        session.add(trans)
        api_utils.json_to_entities(kwargs, trans)
        
        return {"transaction insert done"}
