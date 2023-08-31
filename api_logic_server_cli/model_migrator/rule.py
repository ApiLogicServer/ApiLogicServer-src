from api_logic_server_cli.model_migrator.util import to_camel_case, fixup
"""
LAC RuleObject from file system JSON object
Raises:
    ValueError: JSON Object required

Returns:
    _type_: RuleObj
"""
class DotDict(dict):
    """ dot.notation access to dictionary attributes """
    # thanks: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/28463329
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
class RuleObj:
    
    def __init__(self, jsonObj: object, jsObj: str = None, sqlObj: str = None, table_to_class: dict = None): 
        if not jsonObj:
            raise ValueError("RuleObj(jsonObj) JSON Object required")
        self.name = jsonObj["name"]
        self.entity = jsonObj["entity"]
        self.ruleType = jsonObj["ruleType"]
        self.jsonObj =jsonObj
        self.jsObj = jsObj
        self.sqlObj = sqlObj
        self.table_to_class = table_to_class
        
    def __str__(self):
        # switch statement for each ruleType
        return f"Name: {self.name} Entity: {self.entity} RuleType: {self.ruleType}"
    
    
    def ruleTypes(self: object):
        """

        Args:
            RuleObj (object): _description_
        """
        j = DotDict(self.jsonObj)
        # No need to print inactive rules
        if j.isActive == False:
            return
        name = j.name
        entity = ""
        if j.entity is not None:
            entity = to_camel_case(j.entity)
            if self.table_to_class:
                for t in self.table_to_class:
                    if t.lower == entity.lower():
                        entity = t
            
        ruleType = ""
        if j.ruleType is not None:
            ruleType = j.ruleType
        title =""
        if j.title is not None:
            title = j.title
        funName = "fn_" + name.split(".")[0]
        comments = j.comments
        appliesTo = ""
        if j.appliesTo is not None:
            appliesTo = j.appliesTo
        
        # Define a function to use in the rule 
        ruleJSObj = None if self.jsObj is None else fixup(self.jsObj)
        tab = "\t\t"
        print(f"# RuleType: {ruleType}")
        print(f"# Title: {title}")
        print(f"# Name: {name}")
        print(f"# Entity: {entity}")
        print(f"# Comments: {comments}")
        print("")
        if ruleJSObj is not None:
            entityLower = entity.lower()
            funName =  f"fn_{entityLower}_{ruleType}_{name}"
            if len(ruleJSObj) < 80 and ruleType == "formula":
                pass
            else:
                print(f"def {funName}(row: models.{entity}, old_row: models.{entity}, logic_row: LogicRow):")
                ## print("     if LogicRow.isInserted():")
                if len(appliesTo) > 0:
                    print(f"\t#AppliesTo: {appliesTo}")
                print(f"        {ruleJSObj}")
        match ruleType:
            case "sum":
                attr = j["attribute"]
                roleToChildren = to_camel_case(j.roleToChildren).replace("_","")
                childAttr = j.childAttribute
                qualification = j.qualification
                paren = ")" if qualification is None else ","
                print(f"Rule.sum(derive=models.{entity}.{attr}, ")
                print(f"{tab}as_sum_of=models.{roleToChildren}.{childAttr}{paren}")
                if qualification != None:
                    qualification = qualification.replace("!=", "is not")
                    qualification = qualification.replace("==", "is")
                    qualification = qualification.replace("null", "None")
                    print(f"{tab}where=lambda row: {qualification})")
            case "formula":
                attr = j.attribute
                print(f"Rule.formula(derive=models.{entity}.{attr},")
                if ruleJSObj is not None and len(ruleJSObj) > 80:
                    print(f"{tab}calling={funName})")
                else:
                    ruleJSObj = ruleJSObj.replace("return","lambda row: ")
                    print(f"{tab}as_expression={ruleJSObj})")
            case "count":
                attr = j.attribute
                roleToChildren = to_camel_case(j.roleToChildren).replace("_","")
                qualification = j.qualification
                if qualification != None:
                    qualification = qualification.replace("!=", "is not")
                    qualification = qualification.replace("==", "is")
                    qualification = qualification.replace("null", "None")
                    print(f"Rule.count(derive=models.{entity}.{attr},")
                    print(f"{tab}as_count_of=models.{roleToChildren},")
                    print(f"{tab}where=Lambda row: {qualification})")
                else:
                    print(f"Rule.count(derive=models.{entity}.{attr},")
                    print(f"{tab}as_count_of=models.{roleToChildren})")
            case "validation":
                errorMsg = j.errorMessage
                print(f"Rule.constraint(validate=models.{entity},")
                print(f"{tab}calling={funName},")
                print(f"{tab}error_msg=\"{errorMsg}\")")
            case "event":
                print(f"Rule.row_event(on_class=models.{entity},")
                print(f"{tab}calling={funName})")
            case "commitEvent":
                print(f"Rule.commit_row_event(on_class=models.{entity},")
                print(f"{tab}calling={funName})")
            case "parentCopy":
                attr = j.attribute
                roleToParent = to_camel_case(j.roleToParent).replace("_","")
                parentAttr = j.parentAttribute
                print(f"Rule.copy(derive=models.{entity}.{attr},")
                print(f"{tab}from_parent=models.{roleToParent}.{parentAttr})")
            case _: 
                print(f"#Rule.{ruleType}(...TODO...)")
            
        print("")

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
