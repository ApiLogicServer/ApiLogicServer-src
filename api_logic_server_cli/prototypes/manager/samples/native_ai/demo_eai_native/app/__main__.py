import logging
import os

from .api import create_app

logging.basicConfig(level=logging.INFO)
create_app(os.getenv("DB_PATH", "database/db.sqlite"), os.getenv("KAFKA_SERVER")).run(port=5656)
