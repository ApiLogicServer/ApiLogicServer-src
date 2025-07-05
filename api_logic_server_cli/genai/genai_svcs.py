''' shared functions for genai '''

import shutil
import subprocess
from typing import Dict, List, Tuple
from api_logic_server_cli.cli_args_project import Project
import create_from_model.api_logic_server_utils as create_utils
import logging
from pathlib import Path
import os
import sys
import create_from_model.api_logic_server_utils as utils
from api_logic_server_cli.genai.genai_fatal_excp import GenAIException
import time
from openai import OpenAI
import json
from typing import List, Dict
from pydantic import BaseModel
from dotmap import DotMap
import ast
import astor
import yaml

from genai.client import get_ai_client

K_LogicBankOff = "LBX"
''' LBX Disable Logic (for demos) '''
K_LogicBankTraining = "Here is the simplified API for LogicBank"
''' Identify whether conversation contains LB training '''


class Rule(BaseModel):
    name: str
    description: str
    use_case: str # specified use case or requirement name (use 'General' if missing)
    entity: str # the entity being constrained or derived
    code: str # logicbank rule code
    
class Model(BaseModel):
    classname: str
    code: str # sqlalchemy model code
    description: str
    name: str

class Graphic(BaseModel):
    sqlalchemy_query: str  # sqlalchemy query using group by, returns result = { "result": [ ("name", "value")  ] }
    sql_query: str  # sql query using group by, returns result = { "result": [ ("name", "value")  ] }
    classes_used: str # comma-delimited list of classes used in sqlalchemy_query
    class_x_axis: str # name of class for x axis
    name: str  # suggested Python name for sqlalchemy_query - unique
    prompt: str  # prompt used to create the graphic
    title: str # expanded name
    xAxis: str # caption for x axis
    yAxis: str # caption for y axis
    dashboard: bool  # whether appears on home page
    graph_type: str  # Bar, Line, Pie
    html_code: str # create a java script app to show a bar chart from sqlalchemy_query result

class TestDataRow(BaseModel):
    test_data_row_variable: str  # the Python test data row variable
    code: str  # Python code to create a test data row instance

class WGResult(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    # response: str # result
    models : List[Model] # list of sqlalchemy classes in the response
    rules : List[Rule] # list rule declarations
    graphics: List[Graphic] # list of graphs
    test_data: str
    test_data_rows: List[TestDataRow]  # list of test data rows
    test_data_sqlite: str # test data as sqlite INSERT statements
    name: str  # suggest a short name for the project

log = logging.getLogger(__name__)
try:  # this is just for WebGenAI
    file_handler = logging.FileHandler('/tmp/genai_svcs.log', mode='a')
    file_handler.setLevel(logging.DEBUG)

    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    log.addHandler(file_handler)
    # log.setLevel(logging.DEBUG)
    
except Exception as exc:
    pass # this is just for WebGenAI, ok to ignore error

def get_code_update_logic_file(rule_list: List[DotMap], logic_file_path: Path = None) -> str:
    """returns code snippet for rules from rule, updates rules if logic_file_path provided

        * see avoid_collisions_on_rule

    Args:
        rule_list (List[DotMap]): list of rules from ChatGPT in DotMap format
        logic_file_path (Path): if provided, update default rule file, with provisions for model named `Rule`

    Returns:
        str: the rule code
    """    

    import re

    patterns = [ re.compile(r"derive=(\w+).*$"),
                 re.compile(r"from_parent=(\w+).*$"),
                 re.compile(r"Rule\.constraint\(validate=(\w+).*$"),
                 re.compile(r"as_sum_of=(\w+).*$"),
                 re.compile(r"as_count_of=(\w+).*$")
               ]

    def get_imports(each_line: str, imports: set):
        """updates imports by extracting the class names to import
        
        eg, Rule.constraint(validate=Customer) -> Customer

        Args:
            each_line (str): the ChatGPT code
            imports (set): the set of imported classes (updated in place)
        """

        for each_pattern in patterns:
            match = each_pattern.search(each_line)
            if match:
                the_class_name = match.group(1)
                log.debug(f'.. found class: {the_class_name} in: {each_line}')
                imports.add(the_class_name)
            else:
                pass
                # log.debug(f'.. no classes found in: {each_line}')
        return

    def insert_logic_into_file_and_avoid_collisions_on_rule(translated_logic: str, imports: set, logic_file_path: Path = None) -> None:
        """ Update logic file with rule code (if provided), with collision avoidance on models named Rule
        
        If there's a model named `Rule`, that collides with LogicBank.Rule.  So, change LogicBank.Rule refs:

        1. `from logic_bank.logic_bank import Rule`
                * to: from logic_bank.logic_bank import Rule as LogicBankRule
        2. `Rule.early_row_event_all_classes(early_row_event_all_classes=handle_all)`
                * to: LogicBankRule.early_row_event_all_classes
                * not used in logic_files, so project is None
        3. Users' logic (e.g, Rule.constraint) --> LogicBank.Rule.constraint

        Beware of these cases:
        1. als create - this is not used (but logic/declare_logic.py must exist)
        2. als genai - uses this, with discovery stuff & Rule.early_event at the end
        3. als genai-logic - logic/logic_discovery files, no discovery stuff at end
        4. webG logic - operates differently, to create logic/wg_rules files (for diagnostics)

        Args:
            rule_list (List[DotMap]): list of rules from ChatGPT in DotMap format
            project (Project): a Project object (unless creating a logic file)
            imports (set): the set of imported classes
        """        
        insert_logic = "\n    # Logic from GenAI: (or, use your IDE with code completion)\n"
        insert_import = translated_logic
        if 'import \n' in translated_logic:
            insert_import = "    # no rules"
        insert_logic += insert_import
        insert_logic += "\n    # End Logic from GenAI\n\n"

        insert_point = 'discover_logic()'  # default for als`
        if utils.does_file_contain(in_file=logic_file_path, search_for='# Logic from GenAI'):
            insert_point = '# Logic from GenAI'

        utils.insert_lines_at(lines=insert_logic, 
                            file_name=logic_file_path, 
                            at=insert_point, 
                            after=True)
        
        if 'Rule' not in imports:
            return
        if logic_file_path is None:  # this needs review for WebGenAI
            log.debug(f'.. .. WebGenAI - avoid_collisions_on_rule: {logic_file_path}')
            return
        # find and replace `Rule` in declare_logic.py:
        utils.replace_string_in_file(search_for='from logic_bank.logic_bank import Rule', 
                                     replace_with='from logic_bank.logic_bank import Rule as LogicBankRule', 
                                     in_file=logic_file_path)
        utils.replace_string_in_file(search_for='Rule.early_row_event_all_classes', 
                                     replace_with='LogicBankRule.early_row_event_all_classes', 
                                     in_file=logic_file_path)
        utils.replace_string_in_file(search_for='    Rule.', 
                                     replace_with='    LogicBankRule.', 
                                     in_file=logic_file_path)



    def remove_logic_halluncinations(each_line: str) -> str:
        """remove hallucinations from logic

        eg: Rule.setup()

        Args:
            each_line (str): _description_

        Returns:
            str: _description_
        """
        return_line = each_line
        if each_line.startswith('Rule.'):
            # Sometimes indents left out (EmpDepts) - "code": "Rule.sum(derive=Department.salary_total, as_sum_of=Employee.salary)\nRule.constraint(validate=Department,\n                as_condition=lambda row: row.salary_total <= row.budget,\n                error_msg=\"Department salary total ({row.salary_total}) exceeds budget ({row.budget})\")"
            each_line = "    " + each_line  # add missing indent
            log.debug(f'.. fixed hallucination/indent: {each_line}')
        if 'No rule generated' in each_line:
            each_line = '#' + each_line
        if each_line.startswith('    Rule.') or each_line.startswith('    DeclareRule.'):
            if 'Rule.sum' in each_line:
                pass
            elif 'Rule.count' in each_line:
                pass
            elif 'Rule.formula' in each_line:
                pass
            elif 'Rule.copy' in each_line:
                pass
            elif 'Rule.constraint' in each_line:
                pass
            elif 'Rule.after_flush_row_event' in each_line:
                pass
            elif 'Rule.allocate' in each_line:
                pass
            elif 'Rule.calculate' in each_line:
                return_line = each_line.replace('Rule.calculate', 'Rule.copy')
            else:
                return_line = each_line.replace('    ', '    # ')
                log.debug(f'.. removed hallucination: {each_line}')
        return return_line


    translated_logic = ""
    imports = set()
    for each_rule in rule_list:
        comment_line = each_rule.description
        translated_logic += f'\n    # {comment_line}\n'
        code_lines = each_rule.code.split('\n')
        if '\n' in each_rule.code:
            debug_string = "good breakpoint - multi-line rule"
        for each_line in code_lines:
            if 'declare_logic.py' not in each_line:
                each_repaired_line = remove_logic_halluncinations(each_line=each_line)
                get_imports(each_line = each_repaired_line, imports=imports)
                if not each_repaired_line.startswith('    '):  # sometimes in indents, sometimes not
                    each_repaired_line = '    ' + each_repaired_line
                if 'def declare_logic' not in each_repaired_line:
                    translated_logic += each_repaired_line + '\n' 

    # from database.models import Customer, Order, Item, Product 
    return_translated_logic = '    from database.models import ' + ', '.join(imports) + '\n' + translated_logic
    insert_logic_into_file_and_avoid_collisions_on_rule(
        imports=imports, 
        translated_logic=return_translated_logic, 
        logic_file_path=logic_file_path)
    return return_translated_logic

def rebuild_test_data_for_project(response: str = 'docs/response.json',
                                  project: Project = None,
                                  use_existing_response: bool = False,
                                  use_project_path: Path = None) -> None:
    """
    1. Rebuild the test data - updates existing docs/response.json
    2. Builds database/test_data/test_data.py from updated docs/response.json
    3. Runs it to create database/test_data/db.sqlite
    4. Copies database/test_data/db.sqlite to database/db.sqlite

    Args:
        response (str, optional): _description_. Defaults to 'docs/response.json'.
        use_project_path (Path, optional): _description_. Defaults to None.
    """    

    pass  # basic test: Rebuild test data -  blt/ApiLogicServer/genai_demo_informal
    project_path = Path(os.getcwd())
    if use_project_path is not None:
        project_path = use_project_path
    assert project_path.is_dir(), f"rebuild_test_data_for_project - missing project directory: {project_path}"
    assert project_path.joinpath('database').is_dir(), f"rebuild_test_data_for_project - missing project database directory: {project_path}"
    assert project_path.joinpath(response).is_file(), f"rebuild_test_data_for_project - missing Response File: {response}"

    if use_existing_response:
        use_response = response
    else:
        rebuild_request : List[ Dict[str, str] ] = []
        rebuild_request.append(get_prompt_you_are())
        with open(project_path.joinpath(response), 'r') as file:
            rebuild_project = json.load(file)
        existing_models = rebuild_project
        del existing_models['rules']
        del existing_models['test_data']
        del existing_models['test_data_sqlite']
        rebuild_request.append({"role": "user", "content": json.dumps(existing_models)})
        with open(get_manager_path().joinpath('system/genai/prompt_inserts/rebuild_test_data.prompt'), 'r') as file:
            rebuild_prompt = file.read()
        rebuild_request.append({"role": "user", "content": rebuild_prompt})
        rebuild_response = call_chatgpt(  messages=rebuild_request
                                        , api_version = ''
                                        , using=project_path.joinpath('database/test_data'))
        use_response = project_path.joinpath('database/test_data/response.json')

    python_loc = sys.executable  # eg, /Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/venv/bin/python

    run_file = project_path.joinpath('database/test_data/response2code.py')
    # run_file = '"' + str(run_file) + '"'  # spaces in file names - with windows  FIXME
    run_file = str(Path(run_file).resolve()) 
    run_args = f'--test-data --response={use_response}'

    cwd = project_path.resolve()
    result = create_utils.run_command(f'{python_loc} {run_file} {run_args}', 
                                      msg="\nCreating Test Data Builder...",
                                      cwd = cwd)

    run_file = project_path.joinpath('database/test_data/test_data_code.py')
    run_file = str(Path(run_file).resolve()) 

    subprocess.check_output([python_loc,run_file,'--test-data','--response=docs/response.json'] , 
                            cwd=cwd,shell=False, env=os.environ.copy())
    # subprocess.check_output([python_loc,run_file,'--test-data','--response', 'docs/response.json'] , cwd=cwd,shell=True)
    # result = create_utils.run_commiand(f'{python_loc} {run_file}', 
    #                                  msg="\Running Test Data Builder...",
    #                                  cwd=cwd)

    shutil.copyfile(project_path.joinpath('database/test_data/db.sqlite'), 
                    project_path.joinpath('database/db.sqlite')) # db with corrected test data

    pass


def model2code(model: DotMap) -> str:
    """Add a description to the model
    Args:
        model (DotMap): the model

    Returns:
        str: model_code with the description
    """
    description = model.description
    model_code = model.code
    log.info(f"add description to {model.name}: {description}")
    # Parse the code string into an AST
    try:
        tree = ast.parse(model_code)
    except Exception as exc:
        log.error(f"Failed to parse model code ({model_code}): {exc}")
        try:
            # common error in models generated by chatgpt
            tree = ast.parse(model_code.replace('\\n', '\n'))
        except Exception as exc:
            raise exc
    # check for reserved words... these can fail before sqlacodegen can fix, and might inter-relate, so quit
    if model.name in ['column', 'Column', 'table', 'Table', 'session', 'Session', 'base', 'Base']:
        log.error(f"Reserved word in model name: {model.name}")
        raise GenAIException(f"Reserved word in model name: {model.name}")


    # Function to add a docstring to a class node
    def add_docstring_to_class(node, docstring):
        if isinstance(node, ast.ClassDef):
            node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))

    # Walk through the AST and add the docstring to the class
    class DocstringAdder(ast.NodeTransformer):
        def visit_ClassDef(self, node):
            add_docstring_to_class(node, f"description: {description}")
            return self.generic_visit(node)

    # Transform the AST
    tree = DocstringAdder().visit(tree)

    # Convert the AST back to a code string
    updated_model_str = astor.to_source(tree)
    return updated_model_str


def fix_model_lines(model: DotMap, use_relns: bool = True, post_error: str = None) -> list[str]:
    """Get the model class from the model, with MAJOR fixes

    Args:
        model (Model): the model

    Returns:
        stlist[str]: the model class lines, fixed up (in place)
    """

    fixed_model_lines =  []
    model_lines = model.code.split('\n')
    
    for each_line in model_lines:
        ''' decimal issues

            1. bad import: see Run: tests/test_databases/ai-created/genai_demo/genai_demo_decimal
                from decimal import Decimal  # Decimal fix: needs to be from decimal import DECIMAL

            2. Missing missing import: from SQLAlchemy import .... DECIMAL

            3. Column(Decimal) -> Column(DECIMAL)
                see in: tests/test_databases/ai-created/budget_allocation/budget_allocations/budget_allocations_3_decimal

            4. Bad syntax on test data: see Run: blt/time_cards_decimal from RESPONSE
                got:    balance=DECIMAL('100.50')
                needed: balance=1000.0
                fixed with import in create_db_models_prefix.py

            5. Bad syntax on test data cals: see api_logic_server_cli/prototypes/manager/system/genai/examples/genai_demo/genai_demo_conversation_bad_decimal/genai_demo_03.response
                got: or Decimal('0.00')
                needed: or decimal.Decimal('0.00')

            6. Bad syntax on test data cals: see api_logic_server_cli/prototypes/manager/system/genai/examples/genai_demo/genai_demo_conversation_bad_decimal_2/genai_demo_conversation_002.response
                got: or DECIMAL('
                needed: or decimal.Decimal('0.00')
        '''

        replacements = [
            ('Decimal,', 'DECIMAL,'),  # SQLAlchemy import
            (', Decimal', ', DECIMAL'),  # Cap'n K, at your service
            ('from decimal import Decimal', 'import decimal'),
            ('=Decimal(', '=decimal.Decimal('),
            (' Decimal(', ' decimal.Decimal('),
            ('Column(Decimal', 'Column(DECIMAL'),
            ("DECIMAL('", "decimal.Decimal('"),
            ('end_time(datetime', 'end_time=datetime'),  
            ('datetime.date.today', 'datetime.today')
        ]

        for target, replacement in replacements:
            if target in each_line:
                each_line = each_line.replace(target, replacement)
        
        ##############################
        # do we still need this?
        if "= Table(" in each_line:  # tests/test_databases/ai-created/time_cards/time_card_kw_arg/genai.response
            log.debug(f'.. fix_and_write_model_file detects table - raise excp to trigger retry')
            if post_error is not None:
                post_error = "ChatGPT Response contains table (not class) definitions: " + each_line
        if 'sqlite:///' in each_line:  
            # must be sqlite:///system/genai/temp/create_db_models.sqlite
            # or sqlite:///{current_file_path}/create_db_models.sqlite (often better to create db next to py)
            current_url_rest = each_line.split('sqlite:///')[1]
            quote_type = "'"
            if '"' in current_url_rest:
                quote_type = '"'  # eg, tests/test_databases/ai-created/time_cards/time_card_decimal/genai.response
            current_url = current_url_rest.split(quote_type)[0]
            if current_url == 'sqlite:///{current_file_path}/create_db_models.sqlite':
                pass  
            else:
                proper_url = 'system/genai/temp/create_db_models.sqlite'
                each_line = each_line.replace(current_url, proper_url)
                if current_url != proper_url:
                    log.debug(f'.. fixed sqlite url: {current_url} -> system/genai/temp/create_db_models.sqlite')
        if 'class ' in each_line:
            # yes, tempting to fix... but it fails in SqlAlchemy with missing __tablename__
            # each_line = each_line.replace(':', '(Base):')  # sometimes it forgets the Base
            if 'Base' not in each_line:
                log.debug(f'.. fix_and_write_model_file detects class with no Base - raise excp to trigger retry')
                if post_error is not None:
                    post_error = "ChatGPT Response contains class with no Base: " + each_line
        if 'relationship(' in each_line and use_relns == False:
            # airport4 fails with could not determine join condition between parent/child tables on relationship Airport.flights
            if each_line.startswith('    '):
                each_line = each_line.replace('    ', '    # ')
            else:  # sometimes it puts relns outside the class (so, outdented)
                each_line = '# ' + each_line
        # if 'sqlite:///system/genai/temp/model.sqlite':  # fix prior version
        #     each_line = each_line.replace('sqlite:///system/genai/temp/model.sqlite', 
        #                                 'sqlite:///system/genai/temp/create_db_models.sqlite')

        # # logicbank fixes
        # if 'from logic_bank' in each_line:  # we do our own imports
        #     each_line = each_line.replace('from', '# from')
        # if 'LogicBank.activate' in each_line:
        #     each_line = each_line.replace('LogicBank.activate', '# LogicBank.activate')
        
        fixed_model_lines.append(each_line)
    
    model.code = "\n".join(fixed_model_lines)
    

def fix_and_write_model_file(response_dict: DotMap,  save_dir: str, post_error: str = None, use_relns: bool = False) -> str:
    """
    1. from response, create model file / models lines
    2. from response, create model file / test lines
    3. ChatGPT work-arounds (decimal, indent, bogus relns, etc etc)
    4. Ensure the sqlite url is correct: sqlite:///system/genai/temp/create_db_models.sqlite
    5. write model file to save_dir (e.g, in genai, self.project.from_model)  

    Args:
        response_data (str): the chatgpt response
        post_error (str, optional): genai uses to stop creation in api_logic_server_cli. Defaults to None.
        use_relns (bool, optional): set on genai retry to avoid relns. Defaults to False.

    """

    def insert_model_lines(models, create_db_model_lines, post_error: str = None, use_relns=False) -> list[str]:

        did_base = False
        for each_model in models:
            fix_model_lines(model=each_model, use_relns=use_relns)  # eg, Decimal -> DECIMAL, indent, bogus relns
            
            try: # based on model_lines
                model_code = model2code(each_model)  
                log.info(f"Added description to model: {each_model.name}: {model_code}")
            except GenAIException as exc:
                ''' this does not work - creates a duplicate class, so let's just bail
                if post_error is not None:
                    post_error = exc.args[0]
                continue
                '''
                raise exc
            except Exception as exc:
                log.error(f"Failed to add description to model: {exc}")
                log.debug(f"model: {each_model}")
                if post_error is not None:
                    post_error = f"Failed to add description to model  {each_model.name}: {exc}"
                continue
            
            model_lines = model_code.split('\n')
            
            for each_line in model_lines:
                each_fixed_line = each_line.replace('sa.', '')      # sometimes it puts sa. in front of Column
                if 'Base = declarative_base()' in each_fixed_line:  # sometimes created for each class
                    if did_base:
                        each_fixed_line = '# ' + each_fixed_line
                    did_base = True 
                if 'datetime.datetime.utcnow' in each_fixed_line:
                    each_fixed_line = each_fixed_line.replace('datetime.datetime.utcnow', 'datetime.now()') 
                if 'Column(date' in each_fixed_line:
                    each_fixed_line = each_fixed_line.replace('Column(dat', 'column(Date') 
                create_db_model_lines.append(each_fixed_line)
            
        return create_db_model_lines
    
    def insert_test_data_lines(test_data_lines : list[str]) -> list[str]:
        """Insert test data lines into the model file

        Args:
            test_data_lines (list(str)):  
                                    * initially header (engine =, sesssion =)
                                    * this function appends CPT test data

        Returns:
            list[str]: variable names for the test data rows (for create_all)
        """
        
        def fix_test_data_line(each_fixed_line: str) -> str:
            """Fix the test data line

            Args:
                each_fixed_line (str): the test data line

            Returns:
                str: the fixed test data line
            """

            each_fixed_line = each_fixed_line.replace('\\n', '\n')
            if '=null' in each_fixed_line:
                each_fixed_line = each_fixed_line.replace('=None', '=date') 
            if '=datetime' in each_fixed_line:
                each_fixed_line = each_fixed_line.replace('=datetime.date', '=date') 
            if 'datetime.datetime.utcnow' in each_fixed_line:
                each_fixed_line = each_fixed_line.replace('datetime.datetime.utcnow', 'datetime.now()') 
            if 'datetime.date.today' in each_fixed_line:
                each_fixed_line = each_fixed_line.replace('datetime.date.today', 'datetime.today')
            if 'engine = create_engine' in each_fixed_line:  # CBT sometimes has engine = create_engine, so do we!
                each_fixed_line = each_fixed_line.replace('engine = create_engine', '# engine = create_engine')
                check_for_row_name = False
            if each_fixed_line.startswith('Base') or each_fixed_line.startswith('engine'):
                check_for_row_name = False
            if 'Base.metadata.create_all(engine)' in each_fixed_line:
                each_fixed_line = each_fixed_line.replace('Base.metadata.create_all(engine)', '# Base.metadata.create_all(engine)')
            if ',00' in each_fixed_line:
                each_fixed_line = each_fixed_line.replace(',00', ',0')
            return each_fixed_line

        row_names = list()
        use_test_data_rows = True # CPT test data, new format - test_data_rows (*way* less variable)
        if use_test_data_rows & hasattr(response_dict, 'test_data_rows'):
            test_data_rows = response_dict.test_data_rows
            log.debug(f'.... test_data_rows: {len(test_data_rows)}')
            for each_row in test_data_rows:
                each_fixed_line = fix_test_data_line(each_row.code)
                test_data_lines.append(each_fixed_line) 
                row_names.append(each_row.test_data_row_variable)
            pass
        else:  # CPT test data, old format - rows, plus session, engine etc (quite variable)
            test_data_lines_ori = response_dict.test_data.split('\n') # gpt response
            log.debug(f'.... test_data_lines...')
            for each_line in test_data_lines_ori:
                each_fixed_line = fix_test_data_line(each_line)
                check_for_row_name = True
                test_data_lines.append(each_fixed_line)  # append the fixed test data line
                if check_for_row_name and ' = ' in each_line and '(' in each_line:  # CPT test data might have: tests = []
                    assign = each_line.split(' = ')[0]
                    # no tokens for: Session = sessionmaker(bind=engine) or session = Session()
                    if '.' not in assign and 'Session' not in each_line and 'session.' not in each_line:
                        row_names.append(assign)
        return row_names
    
    create_db_model_lines =  list()
    create_db_model_lines.append(f'# using resolved_model self.resolved_model FIXME')
    create_db_model_lines.extend(
        get_lines_from_file(f'{get_manager_path()}/system/genai/create_db_models_inserts/create_db_models_imports.py'))
    create_db_model_lines.append("\nfrom sqlalchemy.dialects.sqlite import *\n") # specific for genai 
    
    models = response_dict.models

    # fix_and_write_model_file_svcs(response_dict=self.response_dict, save_dir="/tmp")  # todo Thomas - please resolve this...
    
    create_db_model_lines = insert_model_lines(models, create_db_model_lines)

    create_db_model_path = Path(save_dir).joinpath('create_db_models.py')

    with open(f'{create_db_model_path}', "w") as create_db_model_file:
        create_db_model_file.write("\n".join(create_db_model_lines))
        create_db_model_file.write("\n\n# end of model classes\n\n")
        
    if os.getenv('APILOGICPROJECT_NO_TEST_DATA') is None:
        # classes done, create db and add test_data code
        test_data_lines = get_lines_from_file(f'{get_manager_path()}/system/genai/create_db_models_inserts/create_db_models_create_db.py')
        test_data_lines.append('session.commit()')
        
        row_names = insert_test_data_lines(test_data_lines)

        test_data_lines.append('\n\n')
        row_name_list = ', '.join(row_names)
        add_rows = f'session.add_all([{row_name_list}])'
        test_data_lines.append(add_rows )  
        test_data_lines.append('session.commit()')
        test_data_lines.append('# end of test data\n\n')

        test_data_lines_result = []
        for line in test_data_lines:
            test_data_lines_result += line.split('\n')
        
        with open(f'{create_db_model_path}', "a") as create_db_model_file:
            create_db_model_file.write("\ntry:\n    ")
            create_db_model_file.write("\n    ".join(test_data_lines_result))
            create_db_model_file.write("\nexcept Exception as exc:\n")
            create_db_model_file.write("    print(f'Test Data Error: {exc}')\n")
        
        log.debug(f'.. code for db creation and test data: {create_db_model_path}')
    else:
        log.info(f"Test Data Skipped per env var: APILOGICPROJECT_NO_TEST_DATA")
        


def get_lines_from_file(file_name: str) -> list[str]:
    """Get lines from a file

    Args:
        file_name (str): the file name

    Returns:
        list[str]: the lines from the file
    """

    with open(file_name, "r") as file:
        lines = file.read().split("\n")
    return lines

def get_expand_prompt_file(prompt_file_name) -> str:
    ''' 
    Read a prompt file, expand includes, and return the content as a string 
    eg: includes: {{% include 'system/genai/prompt_inserts/sqlite_inserts_model_test_hints.prompt' % }}
    '''
from pathlib import Path

def read_and_expand_prompt(prompt_file_path: str) -> str:
    """
    Read a prompt file, expand includes, and return the content as a string.
    Includes are in the format (starting from same path): {{% include 'include_file.prompt' % }}

    Args:
        file_path (str): Path to the prompt file.

    Returns:
        str: The content of the prompt file with includes expanded.
    """

    with open(prompt_file_path, 'r') as file:
        lines = file.readlines()
    manager_prompt_dir = os.path.dirname(prompt_file_path) 
    out_lines = []
    for each_line in lines:
        if each_line.startswith('{{% include '):
            debug_string = "good breakpoint - include"
            parts = each_line.split("'")  
            include_name = parts[1]
            with open(Path(manager_prompt_dir).joinpath(include_name), 'r') as include_file:
                include_lines = include_file.readlines()
            for each_line_include in include_lines: 
                out_lines.append(each_line_include)
        else:
            out_lines.append(each_line)   
    result_lines = "".join(out_lines)
    return result_lines


def get_create_prompt__with_inserts(arg_prompt_inserts: str='', raw_prompt: str='', for_iteration: bool = False, 
                                    arg_db_url: str="sqlite", arg_test_data_rows: int=4) -> tuple[str, bool]:
    """ Prompt-engineering for creating project,  from: <manager>/system/genai/prompt_inserts

    insert raw_prompt into prompt_inserts file; name is computed from db_url, with inserts from db (or optiomally arg_prompt_inserts).
    1. insert the raw prompt --> into the prompt_inserts file (sqlite one quite big)
    1. prompt-insert file name computed from db_url (or override with arg_prompt_inserts) 
    1. It is first macro-expanded to share creation hints Using get_expand_prompt
        * Content: "use SQLAlchemy to.... {{prompt}} .. directions on models & test data"... (big)
        * Want the share all these directions with import
        * So, sqlite_inserts has {{% include 'sqlite_inserts_model_test_hints.prompt' % }}
    2. insert iteration prompt     (if for_iteration)
    3. insert logic_inserts.prompt ('1 line: Use LogicBank to create declare_logic()...')
    4. designates prompt-format    (response_format.prompt)

    Args:
        arg_prompt_inserts (str, optional): force own insert (vs dburl->db). Defaults to '', * means no inserts.
        raw_prompt (str, optional): user prompt (eg, airport system) replaces {{prompt}}. Defaults to ''.
        for_iteration (bool, optional): _description_. Defaults to False.
        arg_db_url (str, optional): used to compute prompt_inserts file name. Defaults to "sqlite".
        arg_test_data_rows (int, optional): how many rows. Defaults to 4.

    Returns:
        tuple[str, bool]: str: the engineered prompt with inserts, logic_enabled
    """    

    prompt_result = raw_prompt
    prompt_inserts = ''
    logic_enabled = True
    if '*' == arg_prompt_inserts:    # * means no inserts
        prompt_inserts = "*"
    elif '' != arg_prompt_inserts:   # if text, use this file
        prompt_inserts = arg_prompt_inserts
    elif 'sqlite' in arg_db_url:           # if blank, use default for db    
        prompt_inserts = f'sqlite_inserts.prompt'
    elif 'postgresql' in arg_db_url:
        prompt_inserts = f'postgresql_inserts.prompt'
    elif 'mysql' in arg_db_url:
        prompt_inserts = f'mysql_inserts.prompt'

    if prompt_inserts == "*":  
        pass    # '*' means caller has computed their own prompt -- no inserts
    else:       # do prompt engineering (inserts)

        if use_includes := True:
            pre_post = read_and_expand_prompt(get_manager_path().joinpath(f'system/genai/prompt_inserts/{prompt_inserts}'))
        else:
            prompt_eng_file_name = get_manager_path().joinpath(f'system/genai/prompt_inserts/{prompt_inserts}')
            assert Path(prompt_eng_file_name).exists(), \
                f"Missing prompt_inserts file: {prompt_eng_file_name}"  # eg api_logic_server_cli/prototypes/manager/system/genai/prompt_inserts/sqlite_inserts.prompt
            log.debug(f'get_create_prompt__with_inserts: {str(os.getcwd())} \n .. merged with: {prompt_eng_file_name}')
            with open(prompt_eng_file_name, 'r') as file:  # string with \n
                pre_post = file.read()  # eg, Use SQLAlchemy to create a sqlite database named system/genai/temp/create_db_models.sqlite, with
        prompt_result = pre_post.replace('{{prompt}}', raw_prompt)
        if for_iteration:
            # Update the prior response - be sure not to lose classes, attributes, rules and test data already created.
            iteration_prompt = read_and_expand_prompt(get_manager_path().joinpath(f'system/genai/prompt_inserts/iteration.prompt'))
            prompt_result = iteration_prompt  + '\n\n' + prompt_result
            log.debug(f'.. iteration inserted: Update the prior response, using prompt_inserts/iteration.prompt')
            #log.debug(f'.... iteration prompt result: {prompt_result}')

        prompt_lines = prompt_result.split('\n')
        prompt_line_number = 0
        do_logic = True
        for each_line in prompt_lines:
            if 'Create multiple rows of test data' in each_line:
                if arg_test_data_rows > 0:
                    each_line = each_line.replace(
                        f'Create multiple rows',  
                        f'Create {arg_test_data_rows} rows')
                    prompt_lines[prompt_line_number] = each_line
                    log.debug(f'.. inserted explicit test data: {each_line}')
            if K_LogicBankOff in each_line:
                logic_enabled = False  # for demos

            if "LogicBank" in each_line and do_logic == True:
                log.debug(f'.. inserted: {each_line}')
                prompt_eng_logic_file_name = get_manager_path().joinpath(f'system/genai/prompt_inserts/logic_inserts.prompt')
                with open(prompt_eng_logic_file_name, 'r') as file:
                    prompt_logic = file.read()  # eg, Use LogicBank to create declare_logic()...
                prompt_lines[prompt_line_number] = prompt_logic
                do_logic = False
            prompt_line_number += 1
        
        if format_not_requested := False:  # FIXME - double format definition on create; others??
            response_format_file_name = get_manager_path().joinpath(f'system/genai/prompt_inserts/response_format.prompt')
            with open(response_format_file_name, 'r') as file:
                response_format = file.readlines()
            prompt_lines.extend(response_format)

        prompt_result = "\n".join(prompt_lines)  # back to a string
        pass
    return prompt_result, logic_enabled



def get_prompt_messages_from_dirs(using) -> List[ Tuple[ Path, Dict [str, str ] ] ]:
    """ Get raw prompts from dir (might be json or text) and return as list of dicts

    Returned prompts include inserts from prompt_inserts (prompt engineering)

    Use: see run configs..
    * Recompute
    * Mgr: GenAI - FixUp f1 genai_demo_with_logic
        * NOT GenAI - Suggestions s4. Now, (alter and) Implement the Rule Suggestions

    Returns:
         List[ Tuple[ Path, Dict [str, str ] ] ]:  Dict is role: user/system, content: prompt
        
    """

    def iteration(using) -> List[ Tuple[str, Dict[str, str]] ]:
        """ `--using` is a directory (conversation)
        """            
        response_count = 0
        request_count = 0
        learning_requests_len = 0
        prompt = ""
        prompt_messages : List[ Dict[str, str] ] = []
        for each_file in sorted(Path(using).iterdir()):
            if each_file.is_file() and each_file.suffix == '.prompt' or each_file.suffix == '.response':
                # 0 is R/'you are', 1 R/'request', 2 is 'response', 3 is iteration
                with open(each_file, 'r') as file:
                    prompt = file.read()
                if each_file.name == 'constraint_tests.prompt':
                    debug_string = "good breakpoint - prompt"
                role = "user"
                if response_count == 0 and request_count == 0 and each_file.suffix == '.prompt':
                    if not prompt.startswith('You are a '):  # add *missing* 'you are''
                        prompt_messages.append( ( each_file, get_prompt_you_are() ) )
                        request_count = 1
                    else:
                        debug_string = "FIXME - shouldn't this be in prompt??"
                file_num = request_count + response_count
                file_str = str(file_num).zfill(3)
                debug_prompt = prompt[:30] 
                debug_prompt = debug_prompt.replace('\n', ' | ')
                log.debug(f'.. utils[{file_str}] processes: {os.path.basename(each_file)} - {debug_prompt}...')
                if each_file.suffix == ".response":
                    role = 'system'
                    response_count += 1
                else:
                    request_count += 1      # rebuild response with *all* tables
                prompt_messages.append( (each_file, {"role": role, "content": prompt} ) )
            else:
                log.debug(f'.. .. utils ignores: {os.path.basename(each_file)}')
        return prompt_messages

    log.debug(f'\nget_prompt_messages_from_dirs - scanning (${using})')
    prompt_messages : List[ Tuple[ Dict[str, str] ] ] = []  # prompt/response conversation to be sent to ChatGPT
    
    assert Path(using).is_dir(), f"Missing directory: {using}"
    prompt_messages = iteration(using)  # `--using` is a directory (conversation)

    # log.debug(f'.. prompt_messages: {prompt_messages}')  # heaps of output
    return prompt_messages  

def get_prompt_you_are() -> Dict[str, str]:
    """   Create presets - {'role'...you are a data modelling expert, and logicbank api etc

    Args:
        prompt_messages (List[Dict[str, str]]): updated array of messages to be sent to ChatGPT
    """
    pass

    you_are = "You are a data modelling expert and python software architect who expands on user input ideas. You create data models with at least 4 tables"
    return {"role": "user", "content": you_are}

def select_messages(messages: List[Dict], messages_out: List[Dict], message_selector: object):
    """iterates through messages and - for `json` content - calls message_selector to update messages_out

    Args:
        messages (List[Dict]): messages to iterate through (from get_prompt_messages_from_dirs)
        messages_out (List[Dict]): building the latest values of models, (all) rules and test data
        message_selector (object): function to update messages_out

    Returns:
        _type_: _description_
    """    
    
    result = List[DotMap]
    log.debug(f'\nfixup/select_messages: {len(messages)} messages')
    for each_message_file, each_message in messages:
        content = each_message['content']
        content_as_json = as_json(content)
        if content_as_json is not None:  # eg we skip text content, such as raw logic prompt
            # each_message_obj = json.loads(content)
            message_selector(messages_out, each_message, each_message_file)
    return result


def call_chatgpt(messages: List[Dict[str, str]], api_version: str, using: str, response_as: dict=WGResult) -> str:
    """call ChatGPT with messages

    Args:
        messages (List[Dict[str, str]]): array of messages
        api_version (str): genai version
        using (str): str to save response.json (relative to cwd)
    Returns:
        str: response from ChatGPT
    """

    def admin_app_path(request_path: Path, suffix: str) -> Path:
        '''
        returns path = remove the last node of the path, and prepend that to _request.json
        # Example: if request_path is /a/b/c/d/request.json, make it /a/b/c/d_request.json
        '''
        parent = request_path.parent
        last_node = parent.name
        grandparent = parent.parent
        request_path = grandparent.joinpath(f"{last_node}_{suffix}.json")
        request_path.parent.mkdir(parents=True, exist_ok=True)
        return request_path
    
    def string_to_lines(dict_long_string: list) -> dict:
        result = dict_long_string
        if len(result) > 1:
            if isinstance(result[1]['content'], str):
                result[1]['content'] = result[1]['content'].split('\n')
        return result

    try:
        start_time = time.time()
        model = api_version
        if model == "":  # default from CLI is '', meaning fall back to env variable or system default...
            model = os.getenv("APILOGICSERVER_CHATGPT_MODEL")
            if model is None or model == "*":   # system default chatgpt model
                model = "gpt-4o-2024-08-06"     #  33 sec
                # model = "o3-mini"               # 130 sec
        request_path = Path(using).joinpath('request.json')
        if 'admin_app' in str(request_path):
            request_path = admin_app_path(request_path, 'request_raw')
            with open(request_path, "w") as request_file:  # save for debug
                json.dump(messages, request_file, indent=4)
            request_path = admin_app_path(request_path, 'request')
        messages_for_print = messages
        # make the long string better for viewing - convert to lines.
        messages_for_print = [msg.copy() if isinstance(msg, dict) else msg for msg in messages]
        messages_for_print = string_to_lines(messages_for_print)  # Removed to avoid altering messages
        with open(request_path, "w") as request_file:  # save for debug
            json.dump(messages_for_print, request_file, indent=4)
        log.debug(f'.. saved request: {using}/request.json')
        client = get_ai_client()
        # response_format = "json_object" if wg_response else {"type": "text"}
        completion = client.beta.chat.completions.parse(
            messages=messages,
            response_format=response_as,
            # temperature=self.project.genai_temperature,  values .1 and .7 made students / charges fail
            model=model  # for own model, use "ft:gpt-4o-2024-08-06:personal:logicbank:ARY904vS" 
        )
        log.debug(f'OpenAI ({str(int(time.time() - start_time))} secs) - response at: system/genai/temp/chatgpt_original.response')
        
        data = completion.choices[0].message.content

        response_dict = json.loads(data)
        request_path = Path(using).joinpath('request.json')
        if 'admin_app' in str(request_path):
            request_path = admin_app_path(request_path, 'response')
            with open(request_path, "w") as request_file:  # save for debug
                json.dump(data, request_file, indent=4)
        else:
            with open(Path(using).joinpath('response.json'), "w") as response_file:  # save for debug
                json.dump(response_dict, response_file, indent=4)
            with open(Path(using).joinpath('response.yaml'), "w") as response_file:
                yaml.dump(response_dict, response_file, default_flow_style=False, default_style='|')
        request_path = Path(using).joinpath('request.json')
        request_path = admin_app_path(request_path, 'response_raw')
        with open(Path(request_path), "w") as response_file:  # save for debug
            response_file.writelines(data)
        log.debug(f'.. call_chatgpt saved response: {using}/response.json')
        return data # this is a string...
    except Exception as inst:
        log.error(f"\n\nError: ChatGPT call failed\n- please see https://apilogicserver.github.io/Docs/WebGenAI-CLI/#configuratio\n{inst}\n\n")
        sys.exit(1)

def get_manager_path(project: object = None) -> Path:
    """ Checks cwd, parent, and grandparent for system/genai

    * Possibly could add cli arg later

    Args:
        use_env: bool if cannot find manager from project, use install location

    Returns:
        Path: Manager path (contains system/genai)
    """

    if project is not None:
        result_path = project.manager_path
        check_system_genai = result_path.joinpath('system/genai/temp')    
        if check_system_genai.exists():
            return result_path
        return result_path

    result_path = Path(os.getcwd())  # normal case - project at manager root
    check_system_genai = result_path.joinpath('system/genai/temp')    
    if check_system_genai.exists():
        return result_path
    
    result_path = result_path.parent  # try pwd parent
    check_system_genai = result_path.joinpath('system/genai/temp')
    if check_system_genai.exists():
        return result_path
    
    result_path = result_path.parent  # try pwd grandparent
    check_system_genai = result_path.joinpath('system/genai/temp')
    if check_system_genai.exists():
        return result_path
    
    result_path = result_path.parent 
    check_system_genai = result_path.joinpath('system/genai/temp')
    if check_system_genai.exists():
        return result_path
    
    result_path = result_path.parent  
    check_system_genai = result_path.joinpath('system/genai/temp')
    if check_system_genai.exists():
        return result_path
    
    result_path = result_path.parent  
    check_system_genai = result_path.joinpath('system/genai/temp')
    if check_system_genai.exists():
        return result_path

    result_path = result_path.parent  # try ancestors - this is for import testing
    check_system_genai = result_path.joinpath('system/genai/temp')

    if not check_system_genai.exists():
        check_system_genai.exists(), f"Manager Directory not found and APILOGICSERVER_HOME not set: {check_system_genai}"
    return result_path


def as_json(value: str) -> dict:
    """returns json or None from string value

    Args:
        value (str): string - maybe json

    Returns:
        dict: json-to-dict, or None
    """    
    
    return_json = None
    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
        return_json = json.loads(value)
    return return_json

def remove_als_from_models_py(file_path, safrs_basex: bool = True) -> List[str]:
    """ 
    convert als model.py to non-als (returns lines[]) - remove:
     * SAFRSBaseX (iff safrs_basex), and 
     * checksum @json attrs


    this code courtesy of @jamesdavidmiller/Copilot
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    start_marker = '@json'
    end_marker = 'S_CheckSum'
    inside_markers = False
    result_lines = []

    for line in lines:
        if start_marker in line:
            inside_markers = True
        if not inside_markers:
            out_line = line
            if safrs_basex:
                if 'import SAFRSBaseX' in line:
                    debug_string = "good breakpoint - SAFRSBaseX"
                    out_line = '# ' + line
                else:
                    out_line = line.replace('SAFRSBaseX, ', '')
            result_lines.append(out_line)
        if end_marker in line:
            inside_markers = False

    return result_lines


if __name__ == '__main__':
    """
    test fix_and_write_model_file from the cli
    
    args:
    1. response file
    2. save_dir
    
    example:
    PYTHONPATH=$PWD:PYTHONPATH python genai/genai_svcs.py SimpleCommerceSystem_002.response /tmp
    """
    with open(sys.argv[1], "r") as f:
        response = DotMap(json.load(f))
    save_dir = sys.argv[2]
    fix_and_write_model_file(response, save_dir)
    with open(save_dir + "/create_db_models.py", "r") as f:
        ast.parse(f.read())