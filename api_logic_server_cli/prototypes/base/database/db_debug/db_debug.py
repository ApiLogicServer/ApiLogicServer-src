import sqlalchemy
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import Session
import os, sys

from pathlib import Path

running_at = Path(__file__)
project_dir = running_at.parent.parent.parent
sys.path.append(str(project_dir))
os.chdir(str(project_dir))  # so admin app can find images, code

import database.models as models

# *******************************************
# Use this to inspect SQLAlchemy2 connection
# *******************************************

def print_meta(meta):
    print("\n\nmeta.sorted_tables (meta = models.metadata.sorted_tables)\n")
    for each_table in meta.sorted_tables:
        print(f'\n{each_table.key}')
        for each_column in each_table.columns:
            print(f'\t{each_column.name}')

db_loc = str(project_dir.joinpath('database/db.sqlite'))
db_url = "sqlite:////Users/val/dev/servers/ApiLogicProject/database/db.sqlite"
db_url = f"sqlite:///{db_loc}"
# db_url = "sqlite:////Users/val/dev/servers/ApiLogicProject/database/nw-gold.sqlite"

e = sqlalchemy.create_engine(db_url)
inspector = inspect(e)
conn = e.connect()

with Session(e) as session:
    print(f'session: {session}')
    # metadata = MetaData(bind=e)
    metadata = MetaData()  # SQLAlchemy2
    meta = models.metadata  # tables should show list of db tables
    print_meta(meta)
    print("\n\n")
