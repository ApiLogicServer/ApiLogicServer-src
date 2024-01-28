import io
import os
import re

from setuptools import find_packages, setup

find_version = True
if find_version:
    with io.open("api_logic_server_cli/api_logic_server.py", "rt", encoding="utf8") as f:
        version = re.search(r"__version__ = \"(.*?)\"", f.read()).group(1)
else:
    version = 0.0


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    return read("README.md")


project_urls = {
  'Docs': 'https://apilogicserver.github.io/Docs/'
}

setup(
    name="ApiLogicServer",
    version=version,
    url="https://github.com/ApiLogicServer/ApiLogicServer-src",
    license="BSD",
    author="Val Huber",
    author_email="apilogicserver@gmail.com",
    project_urls=project_urls,
    description=(
        "Create JSON:API and Admin Web App from database, with LogicBank -- "
        "40X more concise, Python for extensibility."
    ),
    long_description=desc(),
    long_description_content_type="text/markdown",
    packages=['api_logic_server_cli',
              'api_logic_server_cli.sqlacodegen_wrapper',
              'api_logic_server_cli.sqlacodegen_wrapper.sqlacodegen',
              'api_logic_server_cli.sqlacodegen_wrapper.sqlacodegen.sqlacodegen',
              'api_logic_server_cli.prototypes.base',
              'api_logic_server_cli.prototypes.base.api',
              'api_logic_server_cli.prototypes.base.database',
              'api_logic_server_cli.prototypes.base.logic',
              'api_logic_server_cli.prototypes.base.test',
              'api_logic_server_cli.prototypes.base.ui',
              'api_logic_server_cli.create_from_model'],
    entry_points={
        "console_scripts": ["ApiLogicServer=api_logic_server_cli.cli:start"]
    },
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=[
        "PyJWT==2.6.0",
        "python-dateutil==2.8.2",
        "SQLAlchemy-Utils==0.38.2",
        "logicbankutils==0.6.0",
        "inflect==5.0.2",

        # from safrs, but stipulate version#s
         "Flask==2.3.2",
         "Flask-Cors==3.0.10",
         "Flask-RESTful>=0.3.9",
         "flask-restful-swagger-2>=0.35",
         "Flask-SQLAlchemy==3.0.3",
         "flask-swagger-ui>=4.11.1",
         "flask_bcrypt==1.0.1",
         "itsdangerous==2.1.2",
         "Jinja2==3.1.2",
         "MarkupSafe==2.1.3",
        #  "pyodbc==4.0.34",
         "six==1.16.0",
         "SQLAlchemy==2.0.15",
         "Werkzeug==2.3.3",

        "safrs>=3.1.3",
        "Flask-Admin==1.5.7",
        "Flask-JWT-Extended==4.4.4",
        "Flask-Login==0.6.2",
        "Flask-OpenID==1.3.0",
        "python-dotenv==0.15.0",
        "email-validator==1.1.1",
        "LogicBank>=1.20.1",
        # https://stackoverflow.com/questions/71354710/cryptography-package-is-required-for-sha256-password-or-caching-sha2-password
        # "PyMySQL==1.0.3[rsa]", 
        # "PyMySQL==1.0.3+rsa",
        "cryptography==36.0.1",
        "rsa",
        "PyMySQL==1.0.3", 
        "oracledb==1.4.1",
        "requests==2.27.1",
        "gunicorn==20.1.0",
        "psycopg2-binary==2.9.5",
        # "psycopg-binary==3.1.17",
        "dotmap==1.3.25",
        "WTForms==2.3.3",
        "behave==1.2.6",
        "alembic==1.7.7",
        "GeoAlchemy2==0.12.5",
        "confluent-kafka==2.3.0"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8, !=3.11.0, !=3.11.1",
    setup_requires=['wheel']
)