from safrs import SAFRSAPI
import logging as logging  # additional per-database imports

app_logger = logging.getLogger("api_logic_server_app")

'''
For multi-database support, this is called by Config/server_setup to
* create the SQLAlchemy binds for each database
  * NB: must do all binds in 1 call (not 1 call per db): https://www.youtube.com/watch?v=SB5BfYYpXjE
'''


def bind_dbs(flask_app):
    """ called by api_logic_server_run to open/bind each additional database"""

    flask_app.config.update(SQLALCHEMY_BINDS = {
      'authentication': flask_app.config['SQLALCHEMY_DATABASE_URI_AUTHENTICATION'],
      'landing_page' : flask_app.config['SQLALCHEMY_DATABASE_URI_LANDING']
    })  # make multiple databases available to SQLAlchemy

    return
