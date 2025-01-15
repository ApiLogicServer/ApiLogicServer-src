#!/usr/bin/env python
"""
Minimal run script for the API Logic Project

PROJECT_DIR=../01JH5RZ8PF8KZ379JPQ6AGK1HJ/
cp ${PROJECT_DIR}/database/{models.py,db.sqlite} database/
cp ${PROJECT_DIR}/ui/admin/admin.yaml ui/admin/admin.yaml
"""
import api_logic_server_cli
import click
import sys
import os
from pathlib import Path


@click.command()
@click.option('--spec', '-s', default=f"./docs/export/export.json", help='Path specifying the export json file')
@click.option('--directory', '-d', default=None, help='Project directory')
def main(spec, directory):
    
    if not directory:
        directory = os.getcwd()

    port = os.environ.get("APILOGICPROJECT_EXTERNAL_PORT",5656)
    from api_logic_server_cli.prototypes.base.api_logic_server_run import flask_app
    
    os.chdir(directory) # change to the project directory - may have changed during initialization

    with flask_app.app_context():
        flask_app.run("0.0.0.0", threaded=True, port=int(port))

if __name__ == "__main__":
    
    env_vars = {
        "APILOGICPROJECT_PORT": "5656",
        "APILOGICPROJECT_EXTERNAL_PORT": "5656",
        "APILOGICPROJECT_SWAGGER_HOST": "localhost",
        "APILOGICPROJECT_EXTERNAL_HOST": "localhost",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{os.getcwd()}/database/db.sqlite",
        "APILOGICPROJECT_SRA": str(Path(api_logic_server_cli.__file__).parent / "create_from_model"),
    }

    for var, default in env_vars.items():
        os.environ[var] = os.environ.get(var, default)

    base_path = Path(api_logic_server_cli.__file__).parent / "prototypes/base"
    sys.path = ['.', str(base_path), *sys.path]
    main()
