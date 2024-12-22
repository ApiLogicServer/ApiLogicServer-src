import logging
import api.system.api_utils as api_utils
import safrs
from flask import request, jsonify, send_from_directory
from safrs import jsonapi_rpc
from database import models
from database.spa_models.spa_page import SPASection, SPAPage, SPAComponent
from pathlib import Path
import yaml

app_logger = logging.getLogger(__name__)

sap_admin_yaml = """
SPAPage:
    hidden: true
    order: 2000
    attributes:
    - label: ' name*'
      name: name
      required: true
      search: true
      sort: true
    - name: id
      required: true
    - name: contact
    tab_groups:
    - direction: tomany
      fks:
      - page_id
      name: SectionList
      resource: Section
    type: SPAPage
    user_key: name
    
  
SPASection:
    hidden: true
    sort: order
    order: 2001
    attributes:
    - name: order
      type: number
      sort: true
    - label: ' name*'
      name: name
      required: true
      search: true
    - name: page_id
    - name: title
      required: true
    - name: subtitle
    - name: label
    - name: Type
    - name: paragraph
      type: textarea
    - name: content
      type: textarea
    - name: id
    - name: background
    - name: template
    - name: style
      type: json
    - name: hidden
      type: boolean
    tab_groups:
    - direction: toone
      fks:
      - page_id
      name: page
      resource: SPASection
    type: SPASection
    user_key: name
    
SPAComponent:
    hidden: true
    order: 2002
    sort: -created_at
    attributes:
    - name: id
      required: true
      hidden: true
    - name: Type
    - name: prompt
      type: textarea
    - name: user_comments
      type: textarea
    - name: created_at
      type: datetime
    - name: ai_comments
      type: textarea
    - label: 'name'
      name: name
      required: true
      search: true
    - name: code
      type: textarea
    tab_groups:
    - direction: tomany
      fks:
      - id
      name: ChildList
      resource: SPAComponent
    type: SPAComponent
    user_key: name
"""


def add_spa(app, api):
    
    api.expose_object(SPASection)
    api.expose_object(SPAPage)
    api.expose_object(SPAComponent)
    admin_yaml_fn = Path('ui/admin/admin.yaml')
    
    with open (admin_yaml_fn, "r" ) as admin_fp:
        admin_yaml = yaml.safe_load(admin_fp)
    admin_yaml['resources'].update(yaml.safe_load(sap_admin_yaml))
    with open (admin_yaml_fn, "w+" ) as admin_fp:
        yaml.dump(admin_yaml, admin_fp, default_flow_style=False)
    
    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)


def expose_services(app, api, project_dir, swagger_host: str, PORT: str):
    """ Customize API - new end points for services 
    
        Brief background: see readme_customize_api.md

        Your Code Goes Here
    
    """
    
    from api.api_discovery.auto_discovery import discover_services
    discover_services(app, api, project_dir, swagger_host, PORT)
    add_spa(app, api)
    
    
