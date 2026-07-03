"""
Use case: Employee Auditing

EXTEND RULE TYPES: Events, plus *generic* event handlers.

#als: AUDITING can be as simple as 1 rule.
"""

from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from logic_bank.extensions.rule_extensions import RuleExtension
from database.models import *


def declare_logic():

    RuleExtension.copy_row(copy_from=Employee,
                    copy_to=EmployeeAudit,
                    copy_when=lambda logic_row: logic_row.ins_upd_dlt == "upd" and
                            logic_row.are_attributes_changed([Employee.Salary, Employee.Title]))
    pass  # audited (never gets here)

    ''' the logic above is simpler than
        def audit_by_event(row: Employee, old_row: Employee, logic_row: LogicRow):
            if logic_row.ins_upd_dlt == "upd" and logic_row.are_attributes_changed([Employee.Salary, Employee.Title]):
                # #als: triggered inserts
                copy_to_logic_row = logic_row.new_logic_row(EmployeeAudit)
                copy_to_logic_row.link(to_parent=logic_row)
                copy_to_logic_row.set_same_named_attributes(logic_row)
                # copy_to_logic_row.row.attribute_name = value
                copy_to_logic_row.insert(reason="Manual Copy " + copy_to_logic_row.name)  # triggers rules...

        Rule.commit_row_event(on_class=Employee, calling=audit_by_event)
    '''
