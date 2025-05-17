from typing import Callable

# from logic_bank.exec_row_logic.logic_row import LogicRow <== circular import (??)
import logic_bank.exec_row_logic.logic_row as LogicRow

from logic_bank.rule_bank.rule_bank import RuleBank
from logic_bank.rule_type.abstractrule import AbstractRule


class AbstractRowEvent(AbstractRule):
    _function = None

    def __init__(self, on_class: object,
                 calling: Callable = None):
        super(AbstractRowEvent, self).__init__(on_class)
        self._function = calling
        ll = RuleBank()
        ll.deposit_rule(self)

    def __str__(self):
        return f'RowEvent {self.table}.{self._function.__name__}() '

    def execute(self, logic_row: LogicRow):
        AbstractRule.execute(self, logic_row)
        # logic_row.log(f'Event BEGIN {str(self)} on {str(logic_row)}')
        value = self._function(row=logic_row.row, old_row=logic_row.old_row, logic_row=logic_row)
        # print(f'Event END {str(self)} on {str(logic_row)}')


class EarlyRowEvent(AbstractRowEvent):
    _function = None

    def __init__(self, on_class: object,
                 calling: Callable = None):
        super(EarlyRowEvent, self).__init__(on_class=on_class, calling=calling)


class RowEvent(AbstractRowEvent):
    _function = None

    def __init__(self, on_class: object,
                 calling: Callable = None):
        super(RowEvent, self).__init__(on_class=on_class, calling=calling)


class CommitRowEvent(AbstractRowEvent):
    _function = None

    def __init__(self, on_class: object,
                 calling: Callable = None):
        super(CommitRowEvent, self).__init__(on_class=on_class, calling=calling)


class AfterFlushRowEvent(AbstractRowEvent):
    _function = None

    def __init__(self, on_class: object,
                 calling: Callable = None,
                 if_condition: Callable = None,
                 when_condition: Callable = None,
                 with_args: dict = None):
        super(AfterFlushRowEvent, self).__init__(on_class=on_class, calling=calling)
        self.if_condition = lambda row: eval(if_condition)
        self.when_condition = lambda row: eval(when_condition)
        self.with_args = with_args

    def execute(self, logic_row: LogicRow):
        AbstractRule.execute(self, logic_row)
        # logic_row.log(f'Event BEGIN {str(self)} on {str(logic_row)}')
        do_event = True
        if self.if_condition is not None and self.when_condition is not None:
            pass
        elif self.as_condition is not None:
            do_event = self._as_condition(row=logic_row.row)
        elif self.when_condition is not None:
            current_row = self._when_condition(row=logic_row.row)
            old_row = False
            if logic_row.is_update:
                old_row = self._when_condition(row=logic_row.old_row)
            do_event = current_row == True and old_row == False
        if do_event:
            if self.with_args is None:
                value = self._function(row=logic_row.row, old_row=logic_row.old_row, logic_row=logic_row)
            else:
                value = self._function(row=logic_row.row, old_row=logic_row.old_row, logic_row=logic_row, with_args=self.with_args)
        # print(f'Event END {str(self)} on {str(logic_row)}')
