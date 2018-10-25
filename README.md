# flow

[![Build Status](https://travis-ci.com/zkksch/flow.svg?branch=dev)](https://travis-ci.com/zkksch/flow) 
[![Coverage Status](https://coveralls.io/repos/github/zkksch/flow/badge.svg?branch=dev)](https://coveralls.io/github/zkksch/flow?branch=dev)

Simple flow implementation.

Terms:
- **Flow** - the object that stores a single value (flow state), and controls its changing according to the specific rule.
- **Flow state** - the current value stored in the flow.
- **Transfer** - the flow state change process.
- **Rule** - the object that validates a transfer.
- **Transfer context** - the context data shared between all flow transfers.

### Usage:

You can find other examples of usage in the [demos directory](https://github.com/zkksch/flow/tree/dev/demos).

```python
# Create the enum
class Week(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

# Create the rule
rule = RuleList((
    OneToAllRule(None),  # None -> All
    AllToOneRule(None),  # All -> None
    OneToOneRule(Week.MONDAY, Week.TUESDAY),  # Week.MONDAY -> Week.TUESDAY
    OneToOneRule(Week.TUESDAY, Week.WEDNESDAY),  # Week.TUESDAY -> Week.WEDNESDAY
    OneToOneRule(Week.WEDNESDAY, Week.THURSDAY),  # Week.WEDNESDAY -> Week.THURSDAY
    OneToOneRule(Week.THURSDAY, Week.FRIDAY),  # Week.THURSDAY -> Week.FRIDAY
    OneToOneRule(Week.FRIDAY, Week.SATURDAY),  # Week.FRIDAY -> Week.SATURDAY
    OneToOneRule(Week.SATURDAY, Week.SUNDAY),  # Week.SATURDAY -> Week.SUNDAY
    OneToOneRule(Week.SUNDAY, Week.MONDAY),  # Week.SUNDAY -> Week.MONDAY
))

# Initialize the Flow object
flow = EnumFlow(rule=rule, enum=Week, init=Week.MONDAY)

# It's Ok, According to OneToOneRule(Week.MONDAY, Week.TUESDAY)
flow.value = Week.TUESDAY

# There is no such rule (Week.TUESDAY -> Week.THURSDAY) in the Flow object, raises `TransferError`
try:
    flow.value = Week.THURSDAY
except TransferError:
    pass
else:
    raise AssertionError
```

