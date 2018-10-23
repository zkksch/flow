import random
from enum import Enum

from flow.bases import FlowBase
from flow.bases import RuleBase
from flow.exceptions import TransferError


class Week(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


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
