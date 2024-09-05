import os
import signal
import time
import subprocess
import datetime
import json
import psutil
import safrs
from sqlalchemy import Column, DECIMAL, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from safrs import jsonapi_attr, jsonapi_rpc
from safrs.errors import JsonapiError
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import func
from typing import List
from http import HTTPStatus
from pathlib import Path
from sqlalchemy.sql import func
from ulid import ULID
from safrs.util import classproperty
from flask import g, has_request_context, abort
from flask_jwt_extended import get_jwt_identity, jwt_required, JWTManager, get_jwt, verify_jwt_in_request
from sqlalchemy import create_engine, text
from werkzeug.utils import secure_filename
from pathlib import Path
from sqlalchemy.dialects.sqlite import *
from .util.xls2sql import create_sqlite
from .util import kill_processes_by_port
from . import BaseModel, apifab_dec, FIRST_PORT, PROJ_ROOT, secure_filename_webgenai, log

# Scripts to manage projects (create, start, etc)
CREATE_WGAI_SCRIPT = Path(__file__).parent / "util" / "create_wgai_project.sh"
CREATE_DB_SCRIPT = Path(__file__).parent / "util" / "create_db_project.sh"
RERUN_SCRIPT = Path(__file__).parent / "util" / "rerun_project.sh"

# Create log messages
PROJECT_RUNNING = "Project Running!"
PROJECT_STARTING = "Starting Project"

# Nginx reverse proxy template
NGINX_TEMPLATE = Path(__file__).parent / "templates"/ "nginx.api.template"

# GPT Prompt content, used to create a prompt file in /opt/projects that will be sent to the GPT model
AI_API_REQUEST_FILE = Path(__file__).parent / "ai_api_requests" / "default.json"


class Project(BaseModel):
    __tablename__ = 'projects'
    _s_collection_name = 'Project'
    custom_decorators = [ apifab_dec ]

    # Project attributes - user defined
    name = Column(Text, nullable=False)
    description = Column(Text)
    
    # webgenai attributes
    complexity = Column(Integer)
    prompt = Column(Text)
    
    # db attributes
    connection_string = Column(Text)
    
    # Project attributes - internal, should not be set by the user
    id = Column(String, primary_key=True)
    port = Column(Integer)
    pid = Column(Integer, default=-1)
    directory = Column(Text)
    #link = Column(Text)
    status = Column(Text)
    download = Column(Text)
    response = Column(Text)
    log = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    cost : DECIMAL = Column(DECIMAL(10, 2))
    user_id = Column(ForeignKey('users.id'))

    # parent relationships (access parent)
    user : Mapped["User"] = relationship(back_populates=("ProjectList"))
    FileList : Mapped[List["File"]] = relationship(back_populates="project")

    def __init__(self, *args, **kwargs):
        """
        Invoked by the API POST method
        """
        kwargs['id'] = self.id = str(ULID())
        kwargs['port'] = self.port = (safrs.DB.session.query(func.max(Project.port)).scalar() or FIRST_PORT) + 1
        kwargs['name'] = self.name = self.gen_name(kwargs.get('name', f"genai_{self.id}"))
        if self.name in ["wgadmin", "wgupload"]: # names that are reserved
            abort(400, f"Invalid project name: {self.name}")
        proj_dir = self.path
        kwargs['directory'] = str(proj_dir)
        
        log.info(f"Creating project {self.name} in {proj_dir}, port {self.port}")
        if kwargs.get('connection_string'):
            proj_process = self.create_project_from_db(kwargs)
        elif kwargs.get('prompt'):
            proj_process = self.create_project_from_prompt(kwargs)
        else:
            proj_process = None
            abort(400, f"Failed to create project {self.name}")
        
        self.configure_nginx()
        
        kwargs['pid'] = proj_process.pid
        kwargs['created_at'] = datetime.datetime.now()
        
        return BaseModel.__init__(self, *args, **kwargs)
    
    def gen_name(self, name):
        """
        Method to generate a project name
        """
        sec_name = secure_filename_webgenai(name)
        existing = self.query.filter_by(name=sec_name).all()
        i = 0
        while existing:
            i += 1
            sec_name = f"{secure_filename_webgenai(name)}_{i}" 
            existing = self.query.filter_by(name=sec_name).all()
        
        return sec_name
        
    def create_project_from_db(self, kwargs):
        """
        Create a project from a database connection string
        :param kwargs: dict with project attributes, these are passed from the API POST method
        :return: subprocess.Popen object
        """
        name = kwargs['name']
        connnection_string = kwargs.get('connection_string')
        if connnection_string.startswith("excel://"):
            xls_path = connnection_string.replace("excel://", "")
            connnection_string = create_sqlite(xls_path)
            
        conn_test_result = self.test_conn(connection_string=connnection_string)
        if not conn_test_result.get('success'):
            abort(400, f"Failed to create project {name}: {conn_test_result.get('msg')}")
        log.info(f"Creating project {name} from database {connnection_string}")
        command = [str(CREATE_DB_SCRIPT), name, kwargs['id'], connnection_string, str(kwargs['port'])]
        log.info(f"Executing command {" ".join(command)}")
        cmd_result = subprocess.Popen(command, cwd=PROJ_ROOT, env=self.env)

        return cmd_result
    
    def create_project_from_prompt(self, kwargs):
        """
        Method to create a project using GPT, creates a prompt file and info file in /opt/projects
        :param kwargs: dict with project attributes, these are passed from the API POST method
        :return: subprocess.Popen object
        """
        proj_dir = Path(kwargs['directory'])
        name = kwargs['name']
        prompt_path = proj_dir / f"{name}.prompt"
        info_path = proj_dir / f"{name}_info.txt"
        prompt = kwargs.get('prompt')
        complexity = int(kwargs.get('complexity',4))
        log.info(f"Creating project {name} with complexity {complexity}, prompt file: {prompt_path}")
        with open(AI_API_REQUEST_FILE) as f:
            content = json.load(f)["messages"][1]["content"]
        prompt_path.write_text(content.format(INPUT=prompt, COMPLEXITY=complexity, DATA_COMPLEXITY=complexity*4))
        info_path.write_text(prompt)
        log.info(f"Executing command {CREATE_WGAI_SCRIPT} {name} {kwargs['id']} {kwargs['port']}")
        command = [CREATE_WGAI_SCRIPT, name, kwargs['id'], str(kwargs['port'])]
        cmd_result = subprocess.Popen(command, cwd=PROJ_ROOT, env=self.env)

        return cmd_result
    
    def configure_nginx(self):
        """
        Create an nginx configuration file for the project and reload nginx
        """
        try:
            nginx_conf = open(NGINX_TEMPLATE).read().replace('{port}', str(self.port)).replace('{id}',self.id) # .format isn't convenient here because of nginx syntax
            with open(f"{PROJ_ROOT}/wgadmin/nginx/{self.id}.conf", "w") as f: # cfr /etc/nginx/site.conf
                f.write(nginx_conf)
            subprocess.Popen(["nginx", "-s", "reload"])
        except Exception as e:
            log.error(f"Failed to configure nginx: {e}")
            log.exception(e)
        
    @classmethod
    def kill_all(cls):
        """
        Kill all projects that are still running
        """
        for proj in safrs.DB.session.query(Project).filter(Project.pid < 0).all():
            proj.stop_app()
            
    @classmethod
    @jsonapi_rpc(http_methods=["POST"], valid_jsonapi=False)
    def test_conn(cls, *args, **kwargs):
        """
        Method to test a database connection string
        """
        log.debug(f"Testing connection: {kwargs.get('connection_string')}")
        connection_string = kwargs.get("connection_string")
        result = { "msg" : f"Invalid connection string", "success": False}
        if connection_string and not connection_string.endswith("/"):    
            try:
                engine = create_engine(connection_string)
                with engine.connect() as connection:
                    result = connection.execute(text("SELECT 1"))
                    result.fetchone()
                result = { "msg" : "Connection successful!", "success": True}
            except Exception as e:
                log.warning(f"Connection failed: {e}")
                log.exception(e)
                result = { "msg" : f"Connection failed: {e}", "success": False}
            
        return result
    
    def _s_patch(self, *args, **kwargs):
        """
        Method to patch a project, starts or stops the container based on the "running" attribute
        """
        if 'user_id' in kwargs: del kwargs['user_id']
        if kwargs.get('running') is True:
            log.info(f"Starting..{self}")
            kwargs['pid'] = self.run()
        else:
            self.stop_app()

        return BaseModel._s_patch(self, *args, **kwargs)

    def _s_delete(self):
        """
        Method to delete a project, stops the container before deleting
        Invoked by the API DELETE method
        """
        self.stop_app()
        return BaseModel._s_delete(self)   
 
    def run(self):
        
        if not (self.path / "grun.sh").exists():
            error = f"Failed to start project {self.name}({self.id}): grun.sh not found"
            log.error(error)
            raise WGError(error)
        try:
            process = subprocess.Popen([self.path / "grun.sh"], cwd=self.path, env=self.env, shell=True)
            self.pid = process.pid
            log.info(f"Started project {self.id}, pid {self.pid}")
        except Exception as e:
            raise WGError(f"Failed to start project: {self.name}({self.id}): {e}")

        return self.pid
    
    @property
    def env(self):
        """
        Method to return the environment variables for the project
        """
        env = os.environ.copy()
        # there are secrets in the env, don't just pass it
        return {
            "APILOGICPROJECT_SWAGGER_PORT": env.get("APILOGICPROJECT_SWAGGER_PORT", "8080"),
            "APILOGICPROJECT_EXTERNAL_PORT": env.get("APILOGICPROJECT_EXTERNAL_PORT", "8080"),
            "APILOGICPROJECT_EXTERNAL_HOST": env.get("APILOGICPROJECT_EXTERNAL_HOST", "localhost"),
            "APILOGICPROJECT_SWAGGER_HOST": env.get("APILOGICPROJECT_SWAGGER_HOST", "localhost"),
            "WG_SQLALCHEMY_DATABASE_URI": env.get("WG_SQLALCHEMY_DATABASE_URI", "sqlite:////opt/webgenai/database/db.sqlite"),
            "APILOGICSERVER_CHATGPT_APIKEY" : env.get("APILOGICSERVER_CHATGPT_APIKEY",""),
            "PROJ_ROOT": str(PROJ_ROOT),
            "PATH": env.get("PATH"),
            "APILOGICPROJECT_PORT": str(self.port),
            "SECURITY_ENABLED": "false",
            "APILOGICPROJECT_API_PREFIX": f"/{self.id}",
            
        }

    @jsonapi_attr
    def running(self):
        """
        ---
        Method to check if the app process with pid exists
        :return: bool
        """
        if not isinstance(self.pid, int) or self.pid <= 0:
            return False
        try:
            process = psutil.Process(self.pid)
            log.debug(f"Process {self.pid} exists: {process.cmdline()}")
        except psutil.NoSuchProcess:
            self.pid = -1
            return False
        
        return self.pid
        
    def stop_app(self):
        """
        Method to stop the container associated with the project
        """
        
        if self.running:
            log.info(f"Stopping project {self.id}, pid {self.pid}, port {self.port}")
            try:
                kill_processes_by_port(self.port) # kill gunicorn processes
                os.kill(self.pid, signal.SIGKILL)
            except:
                pass
            
        self.pid = -1

    @jsonapi_rpc(http_methods=["POST"], valid_jsonapi=False)
    def get_log(self, *args, **kwargs):
        """
        This request comes from the "Create" page. We compare the sent log vs the current log
        If they are different, we return the current object
        otherwise we wait for a new log entry. This avoids multiple requests to the server.
        """ 
        if "log" in kwargs:
            for _ in range(30):
                safrs.DB.session.refresh(self)
                if PROJECT_RUNNING in self.log or PROJECT_STARTING in self.log:
                    break
                if kwargs.get("log") != self.log:
                    # Log has changed, return
                    break
                time.sleep(1)
        
        return self

    @property
    def app_origin(self):
        return
    
    @jsonapi_attr
    def link(self):
        """
        
        """
        return f"/{self.id}/admin-app/index.html"
    
    @jsonapi_attr
    def download(self):
        """
        
        """
        return f"/download_project/{self.id}"
    
    @jsonapi_attr
    def response(self):
        """
        
        """
        return f"/download_project/{self.id}"
    
    @property
    def path(self):
        """
        Method to return the project path
        """
        path = PROJ_ROOT / self.name
        path.mkdir(exist_ok=True)
        return path
    
    # @classproperty
    # def _s_query(cls_or_self):
    #     """
    #     :return: sqla query object
    #     """
    #     result = safrs.DB.session.query(cls_or_self).filter_by(user_id = self.user_id)
    #     return result

    # query = _s_query

class WGError(JsonapiError):
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code