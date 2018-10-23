from enum import Enum

from flow.bases import FlowBase
from flow.exceptions import TransferError
from flow.rules import AllToOneRule
from flow.rules import OneToAllRule
from flow.rules import OneToOneRule
from flow.rules import RuleList


# Create values enum
class Week(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


# Initialize the main rule of the flow
rule = RuleList((
    OneToAllRule(None),
    AllToOneRule(None),
    OneToOneRule(Week.MONDAY, Week.TUESDAY),
    OneToOneRule(Week.TUESDAY, Week.WEDNESDAY),
    OneToOneRule(Week.WEDNESDAY, Week.THURSDAY),
    OneToOneRule(Week.THURSDAY, Week.FRIDAY),
    OneToOneRule(Week.FRIDAY, Week.SATURDAY),
    OneToOneRule(Week.SATURDAY, Week.SUNDAY),
    OneToOneRule(Week.SUNDAY, Week.MONDAY),
))

# Initialize the Flow object
flow = FlowBase(rule, Week.MONDAY)

# It's Ok, According to OneToOneRule(Week.MONDAY, Week.TUESDAY)
flow.value = Week.TUESDAY

# There is no such rule in the Flow object, raises `TransferError`
try:
    flow.value = Week.THURSDAY
except TransferError:
    pass
else:
    raise AssertionError
