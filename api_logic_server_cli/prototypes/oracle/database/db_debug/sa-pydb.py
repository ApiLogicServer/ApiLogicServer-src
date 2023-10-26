# sa-pydb.py - for debugging oracle connections
#
# https://oracle.github.io/python-oracledb/
#
# thanks to https://gist.github.com/cjbj/b060bb09adc83f29a1afab1e665d9222
# Using SQLAlchemy 2.0 with python-oracledb
# https://medium.com/oracledevs/using-the-development-branch-of-sqlalchemy-2-0-with-python-oracledb-d6e89090899c

import os

import oracledb
from sqlalchemy import create_engine
from sqlalchemy import text

use_env = False  # else hard-coded

# Database Credentials
username = os.environ.get("PYTHON_USERNAME")
password = os.environ.get("PYTHON_PASSWORD")

# I use Easy Connect strings like "localhost/orclpdb1".  These two lines
# let me access the components individually
cp = oracledb.ConnectParams()
if use_env:
    cp.parse_connect_string(os.environ.get("PYTHON_CONNECTSTRING"))

# For the default, python-oracledb Thin mode that doesn't use Oracle Instant Client
thick_mode = None

# To use python-oracledb Thick mode on macOS (Intel x86).
#thick_mode = {"lib_dir": os.environ.get("HOME")+"/Downloads/instantclient_19_8"}

# To use python-oracledb Thick mode on Windows
#thick_mode = {"lib_dir": r"C:\oracle\instantclient_19_15"}

# For thick mode on Linux use {} ie. no lib_dir parameter.  On Linux you
# must configure the Instant Client directory by setting LD_LIBRARY_PATH or
# running ldconfig before starting Python.
#thick_mode = {}

#engine = create_engine(
#    f'oracle+oracledb://{username}:{password}@{cp.host}:{cp.port}/?service_name={cp.service_name}',
#    thick_mode=thick_mode)

if use_env:
    engine = create_engine(
        f'oracle+oracledb://{username}:{password}@{cp.host}:{cp.port}/?service_name={cp.service_name}',
        thick_mode=thick_mode)
else:
    username = "hr"
    password = "tiger"
    host = "localhost"
    port ="1521"
    service_name ="ORCL"  # might see... Not a socket?  Not registered as listener?
    engine = create_engine(
        f'oracle+oracledb://{username}:{password}@{host}:{port}/?service_name={service_name}',
        thick_mode=thick_mode)
    
conn = oracledb.connect(user=username, password=password, dsn=service_name)  # without SQLAlchemy

with engine.connect() as connection:
    print(connection.scalar(text("""SELECT UNIQUE CLIENT_DRIVER
                                    FROM V$SESSION_CONNECT_INFO
                                    WHERE SID = SYS_CONTEXT('USERENV', 'SID')""")))