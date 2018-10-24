# flow

[![Build Status](https://travis-ci.com/zkksch/flow.svg?branch=dev)](https://travis-ci.com/zkksch/flow) 
[![Coverage Status](https://coveralls.io/repos/github/zkksch/flow/badge.svg?branch=dev)](https://coveralls.io/github/zkksch/flow?branch=dev)

Simple values flow implementation

### Usage:

```python
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
```

### Create your own rules

```python
class RandomRule(RuleBase):
    @property
    def inputs(self):
        return {self.ALL}

    @property
    def outputs(self):
        return {self.ALL}

    def is_valid(self, input_value, output_value, context=None):
        if random.randint(0, 100) > 50:
            return False, 'You unlucky :('

        return True, None


flow = FlowBase(RandomRule(), Week.MONDAY)

try:
    flow.value = Week.TUESDAY
except TransferError:
    # Falls in 50% of attempts
    print('You unlucky :(')
else:
    print('You lucky :)')
```

### `TransferContext` and `RuleList` usage

```python
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

flow = FlowBase(rule, init=None)

# It's all Ok
flow.value = Week.MONDAY
flow.value = Week.TUESDAY
flow.value = Week.WEDNESDAY
flow.value = Week.THURSDAY
flow.value = Week.FRIDAY
flow.value = Week.SATURDAY
flow.value = Week.SUNDAY
flow.value = Week.MONDAY

try:
    # Trying to complete transfer between same values second time
    flow.value = Week.TUESDAY
except TransferError:
    pass
else:
    # Should raise error
    raise AssertionError

# But values <-> None transfer is Ok
flow.value = None
flow.value = Week.MONDAY
```

