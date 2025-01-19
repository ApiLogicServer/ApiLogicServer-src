from api_logic_server_cli.model_migrator.util import to_camel_case, fixup, get_os_url
"""
LAC RuleObject from file system JSON object
Raises:
    ValueError: JSON Object required

Returns:
    _type_: RuleObj
"""
import os
class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
class RuleObj:
    
    def __init__(self, jsonObj: object, jsObj: str = None, sqlObj: str = None, table_to_class: dict = None, project_directory: str = ""): 
        if not jsonObj:
            raise ValueError("RuleObj(jsonObj) JSON Object required")
        self.name = jsonObj["name"]
        self.entity = jsonObj["entity"]
        self.ruleType = jsonObj["ruleType"]
        self.jsonObj =jsonObj
        self.jsObj = jsObj
        self.sqlObj = sqlObj
        self.table_to_class = table_to_class
        self.project_directory = f"{project_directory}{os.sep}logic{os.sep}declare_security.py.gen"
        self._content = ""
        
    def __str__(self):
        # switch statement for each ruleType
        return f"Name: {self.name} Entity: {self.entity} RuleType: {self.ruleType}"
    
    def append_imports(self):
        """ append import to -> append_expose_services_file """
        import_statement = "\n"
        import_statement += "import datetime\n"
        import_statement += "from decimal import Decimal\n"
        import_statement += "from logic_bank.exec_row_logic.logic_row import LogicRow\n"
        import_statement += "from logic_bank.extensions.rule_extensions import RuleExtension\n"
        import_statement += "from logic_bank.logic_bank import Rule\n"
        import_statement += "from database import models\n"
        import_statement += "import api.system.opt_locking.opt_locking as opt_locking\n"
        import_statement += "import logging\n"
        import_statement += "from config import Config\n"
        import_statement += "from security.system.authorization import Grant\n"
        import_statement += "import math\n\n"
        import_statement += "app_logger = logging.getLogger(__name__)\n\n"
        import_statement += "def declare_logic():\n\n\n"
        import_statement += 'app_logger.debug("..logic/declare_logic.py (logic == rules + code)")\n\n\n'
        
        file_name = get_os_url(f'{self.project_directory}')
        with open(file_name, 'a') as expose_services_file:
            expose_services_file.write(import_statement)
    
    def append_content(self, content):
        file_name = get_os_url(f'{self.project_directory}')
        with open(file_name, 'a') as expose_services_file:
            expose_services_file.write(content)
    
    def append_handle_all(self):
        """ append import to -> declare_logic.py.gen """
        content = "\n"
        content += "\tdef handle_all(logic_row: LogicRow):\n"
        content += "\t\tGrant.process_updates(logic_row=logic_row)\n"
        content += "\n"
        content += "\tRule.early_row_event_all_classes(early_row_event_all_classes=handle_all)\n"
        content += "\n"
        content += '\tapp_logger.debug("..logic/declare_logic.py (logic == rules + code)")\n'
        self.append_content(content)
        
    def add_content(self, *values: object):
        #print(f'{values}')
        space = "\t"
        if isinstance(values, str):
            self._content += f'{values}'
        elif isinstance(values, tuple):
            for t, v in enumerate(values):
                self._content += t * f"{space}"
                self._content += f"{v}"
        self._content += "\n"

    def ruleTypes(self: object):
        """ Create ALS rules from LAC JSON 
        Args:
            RuleObj (object): _description_
        """
        j = DotDict(self.jsonObj)
        # No need to print inactive rules
        if j.isActive == False:
            return
        name = j.name
        entity = ""
        if j.entity:
            entity = self.find_entity(j.entity)
            
        ruleType = ""
        if j.ruleType is not None:
            ruleType = j.ruleType
        title =""
        if j.title is not None:
            title = j.title
        #funName = "fn_" + name.split(".")[0]
        entityLower = entity.lower()
        funName =  f"fn_{entityLower}_{ruleType}_{name}"
        comments = j.comments
        appliesTo = ""
        if j.appliesTo is not None:
            appliesTo = j.appliesTo
        
        # Define a function to use in the rule 
        ruleJSObj = None if self.jsObj is None else fixup(self.jsObj) if self.jsObj is None else ""
        tab = "\t\t"
        self.add_content(f"\t# RuleType: {ruleType}")
        self.add_content(f"\t# Title: {title}")
        self.add_content(f"\t# Name: {name}")
        self.add_content(f"\t# Entity: {entity}")
        
        codeType = j.get("codeType", None)
        if codeType == "Java":
            className = j.get("className", None)
            methodName = j.get("methodName", None)
            self.add_content(f"\t# CodeType: {codeType}")
            self.add_content(f"\t# ClassName: {className}")
            self.add_content(f"\t# MethodName: {methodName}")
            if name == "cache":
                funName =  f"fn_{methodName}"

            
        self.add_content(f"\t# Comments: {comments}")
        self.add_content("")
        if codeType == "Java":
            self.add_content(f"\tdef {funName}(row: models.{entity}, old_row: models.{entity}, logic_row: LogicRow):")
            self.add_content(f"\t\t# Call Java Code: {className}.{methodName}(row, old_row, logic_row)")
            self.add_content("\t\tpass")
            
    
        if ruleJSObj is not None:
            if len(ruleJSObj) < 80 and ruleType == "formula" and codeType == "JavaScript":
                pass
            else:
                self.add_content(f"\tdef {funName}(row: models.{entity}, old_row: models.{entity}, logic_row: LogicRow):")
                ## self.add_content("     if LogicRow.isInserted():")
                if len(appliesTo) > 0:
                    self.add_content(f"\t#AppliesTo: {appliesTo}")
                self.add_content(f"        {ruleJSObj}")
        match ruleType:
            case "sum":
                attr = j["attribute"]
                rtj = j.roleToChildren.replace("_","")
                roleToChildren = self.find_entity(rtj)
                childAttr = j.childAttribute
                qualification = j.qualification
                paren = ")" if qualification is None else ","
                self.add_content(f"\tRule.sum(derive=models.{entity}.{attr}, ")
                self.add_content(f"\t   {tab}as_sum_of=models.{roleToChildren}.{childAttr}{paren}")
                if qualification != None:
                    qualification = qualification.replace("!=", "is not")
                    qualification = qualification.replace("==", "is")
                    qualification = qualification.replace("null", "None")
                    self.add_content(f"{tab}where=lambda row: {qualification})")
            case "formula":
                attr = j.attribute
                self.add_content(f"\tRule.formula(derive=models.{entity}.{attr},")
                if ruleJSObj is not None and len(ruleJSObj) > 80:
                    self.add_content(f"{tab}calling={funName})")
                else:
                    ruleJSObj = ruleJSObj.replace("return","lambda row: ") if ruleJSObj is not None else ""
                    self.add_content(f"{tab}as_expression={ruleJSObj})")
            case "count":
                attr = j.attribute
                roleToChildren = to_camel_case(j.roleToChildren).replace("_","")
                qualification = j.qualification
                if qualification != None:
                    qualification = qualification.replace("!=", "is not")
                    qualification = qualification.replace("==", "is")
                    qualification = qualification.replace("null", "None")
                    self.add_content(f"\tRule.count(derive=models.{entity}.{attr},")
                    self.add_content(f"{tab}as_count_of=models.{roleToChildren},")
                    self.add_content(f"{tab}where=Lambda row: {qualification})")
                else:
                    self.add_content(f"\tRule.count(derive=models.{entity}.{attr},")
                    self.add_content(f"{tab}as_count_of=models.{roleToChildren})")
            case "validation":
                errorMsg = j.errorMessage
                self.add_content(f"\tRule.constraint(validate=models.{entity},")
                self.add_content(f"{tab}calling={funName},")
                self.add_content(f"{tab}error_msg=\"{errorMsg}\")")
            case "event":
                self.add_content(f"\tRule.row_event(on_class=models.{entity},")
                self.add_content(f"{tab}calling={funName})")
            case "commitEvent":
                self.add_content(f"\tRule.commit_row_event(on_class=models.{entity},")
                self.add_content(f"{tab}calling={funName})")
            case "parentCopy":
                attr = j.attribute
                roleToParent = to_camel_case(j.roleToParent).replace("_","")
                parentAttr = j.parentAttribute
                self.add_content(f"\tRule.copy(derive=models.{entity}.{attr},")
                self.add_content(f"{tab}from_parent=models.{roleToParent}.{parentAttr})")
            case _: 
                self.add_content(f"\t#Rule.{ruleType}(...TODO...)")
            
        self.add_content("")
        return self._content

    def find_entity(self, entity: str):
        if entity:
            entity = to_camel_case(entity)
            if entity.endswith("List") or entity.endswith("list"):
                entity = entity[:-4]
            if self.table_to_class:
                for t in self.table_to_class:
                    if t.lower() == entity.lower():
                        return self.table_to_class[t]
        return entity

if __name__ == "__main__":
    jsonObj ={
        "name": "CheckCredit",
        "entity": "Customers",
        "isActive": True,
        "ruleType": "validation",
        "codeType": "JavaScript",
        "errorMessage": "Transaction cannot be completed - Balance ({Balance|#,##0.00}) exceeds Credit Limit ({CreditLimit|#,##0.00})",
        "problemAttributes": [
        ],
        "isAutoTitle": True,
        "title": "Validation: return row.Balance <= row.CreditLimit;",
        "comments": "Observe Error message insertion points {}",
        "topics": [
            "Check Credit"
        ]
    }
    js = "return row.Balance <= row.CreditLimit;"
    ruleObj = RuleObj(jsonObj=jsonObj,jsObj=js)
    ruleObj.ruleTypes()
