from enum import Enum

from flow.bases import RuleBase
from flow.exceptions import TransferError
from flow.flow import Flow
from flow.rules import AllToOneRule
from flow.rules import OneToAllRule
from flow.rules import OneToOneRule
from flow.rules import RuleList


class Week(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class UniqueTransfer(RuleBase):
    """Stores completed transfers in context,
    and doesn't allows to complete same transfer twice."""
    @property
    def inputs(self):
        return {self.ALL}

    @property
    def outputs(self):
        return {self.ALL}

    def is_valid(self, input_value, output_value, context=None):
        if context is not None:
            transferred_already = context.setdefault(
                'transferred_already', set())

            key = (input_value, output_value)

            if key in transferred_already:
                return False, TransferError(
                    self, 'The transfer has been already accomplished')
            transferred_already.add(key)
            return True, None

        raise TransferError(self, 'Context required')


# Creating following rules list:
# You can transfer value <-> None many times
# But other transfers should be unique
rule = RuleList((
    OneToAllRule(None),
    AllToOneRule(None),
    RuleList((
        UniqueTransfer(),
        OneToOneRule(Week.MONDAY, Week.TUESDAY),
        OneToOneRule(Week.TUESDAY, Week.WEDNESDAY),
        OneToOneRule(Week.WEDNESDAY, Week.THURSDAY),
        OneToOneRule(Week.THURSDAY, Week.FRIDAY),
        OneToOneRule(Week.FRIDAY, Week.SATURDAY),
        OneToOneRule(Week.SATURDAY, Week.SUNDAY),
        OneToOneRule(Week.SUNDAY, Week.MONDAY),
    ))
), operator=any)
# operator shows how to combine result of rules from the list,
# if more than one rule used, default - all

flow = Flow(rule, init=None)

# It's all Ok
flow.state = Week.MONDAY
flow.state = Week.TUESDAY
flow.state = Week.WEDNESDAY
flow.state = Week.THURSDAY
flow.state = Week.FRIDAY
flow.state = Week.SATURDAY
flow.state = Week.SUNDAY
flow.state = Week.MONDAY

try:
    # Trying to complete transfer between same values second time
    flow.state = Week.TUESDAY
except TransferError:
    pass
else:
    # Should raise error
    raise AssertionError

# But values <-> None transfer is Ok
flow.state = None
flow.state = Week.MONDAY
