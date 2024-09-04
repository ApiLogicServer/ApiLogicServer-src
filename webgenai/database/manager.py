#!/usr/bin/env python
# 
# Project manager CLI
#
# example:
# cd /opt/webgenai/
# python database/manager.py --list
#
from models import *
import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import psutil


DB_URL = 'sqlite:////opt/webgenai/database/db.sqlite' # TODO, use env var from config

def get_project(project_id: str) -> Project:
    """
    Get project by ID
    :param project_id: Project ID
    :return: Project object
    """
    project = session.get(Project, project_id)
    return project

engine = create_engine(DB_URL, echo=False) # Set echo=True to see the SQL queries
Session = sessionmaker(bind=engine)
session = Session()

def kill_processes_by_port(port: int) -> None:
    """
    Kill processes using the specified port
    """
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port == port:
                    psutil.Process(proc.info['pid']).terminate()
                    print(f"Terminated process with PID {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        

# CLI
@click.command()
@click.option('--list', '-l', is_flag=True, help="List all projects")
@click.option('--create', '-c', is_flag=True, help="Create database")
@click.option('--kill-all', '-K', is_flag=True, help="Kill all running projects")
@click.option('--run', '-r', is_flag=True, help="Run project")
@click.option('--info', '-i',is_flag=True, help="Print project info")
@click.option('--project-id', '-p', default=None, help="Project ID")
@click.option('--append-log', '-a', default=None, help="Append log to project")
def cli(list, create, run, kill_all, info, project_id, append_log):
    """
    A simple CLI that greets a user or repeats a message.
    """
    if list:
        projects = session.query(Project).all()
        for project in projects:
            click.echo(f"{project.id} - {project.name} - {project.running} - {project.pid}")
        return
    if create:
        Base.metadata.create_all(engine)
        return
    if kill_all:
        projects = session.query(Project).all()
        for project in projects:
            if project.running:
                project.stop_app()
        session.commit()
        return
    if not project_id:
        click.echo("No project ID provided")
        return
    if run:
        project = get_project(project_id)
        if not project.running:
            project.run()
            session.commit()
        
    project = get_project(project_id)
    if info:
        click.echo(f"Name: {project.name}, Running: {project.running}, Log: {project.log}")
    elif append_log:
        project.log += append_log + "\n"
        session.commit()

if __name__ == "__main__":
    cli()