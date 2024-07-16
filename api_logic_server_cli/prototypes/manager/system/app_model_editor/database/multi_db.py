from safrs import SAFRSAPI
import logging as logging  # additional per-database imports

from api import authentication_expose_api_models
from database import authentication_models
        
app_logger = logging.getLogger("api_logic_server_app")


def bind_dbs(flask_app):
    """ called by api_logic_server_run to open/bind each additional database"""

    flask_app.config.update(SQLALCHEMY_BINDS = {
		'authentication': flask_app.config['SQLALCHEMY_DATABASE_URI_AUTHENTICATION']
    })  # make multiple databases available to SQLAlchemy

    return


def expose_db_apis(flask_app, session, safrs_api, method_decorators):
    """ called by api_logic_server_run to expose APIs for each additional database """

    # Begin Expose APIs

    authentication_expose_api_models.expose_models(safrs_api, method_decorators= method_decorators)
        
    # End Expose APIs
    return