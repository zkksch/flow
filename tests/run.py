from enum import Enum

from flow.bases import FlowBase
from flow.rules import RuleList, OneToOneRule, OneToAllRule, AllToOneRule


class Week(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


r = RuleList((
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

f = FlowBase(r)

f.value = Week.SUNDAY
f.value = Week.MONDAY
f.value = Week.TUESDAY
f.value = Week.WEDNESDAY
f.value = None
f.value = Week.THURSDAY
f.value = Week.FRIDAY
f.value = Week.SATURDAY
