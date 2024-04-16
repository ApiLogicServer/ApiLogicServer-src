import os

class ReposModel(object):

    def __init__(self, db_url, project_directory, model_creation_services):

        self.db_url = db_url
        self.project_directory = project_directory

        self.number_of_models = 0
        """ various status / debug information """

        self.model_creation_services = model_creation_services
        """ access to meta model, including table_to_class_map """


    def append_expose_services_file(self, api_path:str, import_statement:str):
        """ append import to -> append_expose_services_file """
        file_name = self.get_os_url(self.project_directory + f'{api_path}')
        expose_services_file = open(file_name, 'a')
        expose_services_file.write(import_statement)
        expose_services_file.close()



def to_camel_case(textStr: str, firstToLower: bool = False):
    """ALS uses singular entity names

    Args:
        textStr (str): _description_
        firstToLower (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    if textStr is None:
        return ""
    s = textStr.replace("-", " ").replace("_", " ")
    sp = s.split(" ")
    r = sp[0] + "".join(i.capitalize() for i in sp[1:])
    #r = r[:-1] if r[-1:] == "s" else r  # singular names only
    r = r[:-1] + r[-1:].lower()
    return r if firstToLower else r[:1].capitalize() + r[1:]


"""
Convert JavaScript LAC to ALS Python - still requires manual fixup
"""


def fixup(str):
    if str is None:
        return str
    newStr = str.replace("oldRow", "old_row", 20)
    newStr = newStr.replace("logicContext", "logic_row", 40)
    newStr = newStr.replace("log.", "logic_row.log.", 40)
    newStr = newStr.replace("var ", "", 40)
    newStr = newStr.replace("//", "#", 200)
    newStr = newStr.replace("createPersistentBean", "logic_row.new_logic_row")
    newStr = newStr.replace(";", "", 200)
    newStr = newStr.replace("?", " if ", 400)
    newStr = newStr.replace(":", " else ", 400)
    newStr = newStr.replace("} else {", "else:", 100)
    newStr = newStr.replace("}else {", "else:", 100)
    newStr = newStr.replace(") {", "):", 40)
    newStr = newStr.replace("){", "):", 40)
    newStr = newStr.replace("function ", "def ", 40)
    newStr = newStr.replace("} else if", "elif ")
    newStr = newStr.replace("}else if", "elif ", 20)
    newStr = newStr.replace("||", "or", 20)
    newStr = newStr.replace("&&", "and", 20)
    newStr = newStr.replace("}else{", "else:", 20)
    newStr = newStr.replace("null", "None", 40)
    newStr = newStr.replace("===", "==", 40)
    newStr = newStr.replace("!==", "!=", 20)
    newStr = newStr.replace("}", "", 40)
    newStr = newStr.replace("else  if ", "elif", 20)
    newStr = newStr.replace(" else {","else:", 10)
    newStr = newStr.replace("true", "True", 30)
    newStr = newStr.replace("false", "False", 30)
    newStr = newStr.replace("if (", "if ", 30)
    newStr = newStr.replace("if(", "if ", 30)
    # newStr = newStr.replace("):",":", 30)
    newStr = newStr.replace('logic_row.verb == "INSERT"', "logic_row.is_inserted() ")
    newStr = newStr.replace('logic_row.verb == "UPDATE"', "logic_row.is_updated()")
    newStr = newStr.replace('logic_row.verb == "DELETE"', "logic_row.is_deleted()")
    newStr = newStr.replace("JSON.stringify", "jsonify", 20)
    newStr = newStr.replace("JSON.parse", "json.loads", 20)
    newStr = newStr.replace("/*", "'''", 20)
    newStr = newStr.replace("*/", "'''", 20)
    newStr = newStr.replace("try {", "try:", 10)
    newStr = newStr.replace("catch(e):", "except Exception as ex:", 5)
    newStr = newStr.replace("throws", "except Exception as ex:", 5)
    newStr = newStr.replace("try{", "try:", 10)
    newStr = newStr.replace("catch(", "except Exception as ex:", 5)
    # SysUtility ???
    return newStr.replace("log.debug(", "log(", 20)


if __name__ == "__main__":
    js = ""
    print(fixup(js))

    js = 'var theRaise = parameters.percentRaise * (row.Salary/100); \nrow.Salary += theRaise;\n  // runs logic, persists change row(s) to database...return [ {"status": "Success"}, {"raise": theRaise} ]; \n//  , {"row": row.toString()}  ];'
    print(fixup(js))
    
    print(to_camel_case("foo_bar",True))
    print(to_camel_case("foo_bar",False))

def fixupSQL(sql):
    """
    LAC FreeSQL passes these args
    -- perhaps generate a function
    these were place holders that are passed by client or defaulted
    @{SCHEMA} __bindkey__
    @{WHERE} s/b :@where
    @{JOIN}  s/b :@join
    @{ARGUMENT.} may include prefix (e.g. =main:entityName.attrName)
    @(ORDER) - s/b :@order
    @{arg_attrname} - s/b :@attrName
    """
    if sql:
        sql = sql.replace("}","",40)
        sql = sql.replace("@{",":",40)
        sql = sql.replace("\"","\\\"",40)
        # dealing with double quotes and single quotes
    return f"{sql}"

def get_os_url(url: str) -> str:
    """ idiotic fix for windows (use 4 slashes to get 1) """
    return url.replace('\\', '\\\\')