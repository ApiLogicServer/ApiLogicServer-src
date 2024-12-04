
from typing import Dict, List
import logging
from dotmap import DotMap

log = logging.getLogger(__name__)

def get_code(rule_list: List[DotMap]) -> str:
    """returns code snippet for rules from rule

    Args:
        rule_list (List[DotMap]): list of rules from ChatGPT in DotMap format

    Returns:
        str: the rule code
    """    

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
            elif 'Rule.allocate' in each_line:
                pass
            elif 'Rule.calculate' in each_line:
                return_line = each_line.replace('Rule.calculate', 'Rule.copy')
            else:
                return_line = each_line.replace('    ', '    # ')
                log.debug(f'.. removed hallucination: {each_line}')
        return return_line

    translated_logic = ""
    for each_rule in rule_list:
        comment_line = each_rule.description
        translated_logic += f'\n    # {comment_line}\n'
        code_lines = each_rule.code.split('\n')
        if '\n' in each_rule.code:
            debug_string = "good breakpoint - multi-line rule"
        for each_line in code_lines:
            if 'declare_logic.py' not in each_line:
                each_repaired_line = remove_logic_halluncinations(each_line=each_line)
                if not each_repaired_line.startswith('    '):  # sometimes in indents, sometimes not
                    each_repaired_line = '    ' + each_repaired_line
                if 'def declare_logic' not in each_repaired_line:
                    translated_logic += each_repaired_line + '\n'    
    return translated_logic