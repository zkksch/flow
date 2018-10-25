from collections import defaultdict
from itertools import chain

from flow.bases import RuleBase
from flow.exceptions import TransferError
from flow.exceptions import RuleListTransferError

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Callable
    from typing import Collection
    from typing import Dict
    from typing import Iterable
    from typing import List
    from typing import Optional
    from typing import Set
    from typing import Tuple

    from flow.bases import TransferContext
    from flow.bases import Value


class RuleList(RuleBase):
    """Rule that contains other rules, and combines them by the operator."""
    def __init__(self, rules, operator=all):
        # type: (Iterable[RuleBase], Callable[[Iterable[object]], bool]) -> None
        """
        :param rules: List of rules
        :param operator: Combine operator
        """
        self.operator = operator  # type: Callable[[Iterable[bool]], bool]
        self.rules = []  # type: List[RuleBase]
        self.rules.extend(rules)

        # Map for fast rule searching
        self._input_map = defaultdict(list)  # type: Dict[Value, List[RuleBase]]

        for rule in self.rules:
            for _input in rule.inputs:
                self._input_map[_input].append(rule)

        # Map for fast rule searching
        self._output_map = defaultdict(list)  # type: Dict[Value, List[RuleBase]]

        for rule in self.rules:
            for _output in rule.outputs:
                self._output_map[_output].append(rule)

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return set(chain(*(rule.inputs for rule in self.rules)))

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return set(chain(*(rule.outputs for rule in self.rules)))

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        input_rules = set(self._input_map[input_value]) | set(
            self._input_map[RuleBase.ALL])
        output_rules = set(self._output_map[output_value]) | set(
            self._output_map[RuleBase.ALL])

        rules = input_rules & output_rules

        if not rules:
            return False, TransferError(
                self, 'Rules not found for the %s -> %s transfer')

        validation_results = [
            (rule, rule.is_valid(input_value, output_value, context))
            for rule in rules
        ]

        is_valid = self.operator(
            is_valid for _, (is_valid, _) in validation_results)

        if is_valid:
            err = None
        else:
            err = RuleListTransferError(self, validation_results)

        return is_valid, err


class OneToOneRule(RuleBase):
    """Rule for the one to one transfer."""
    def __init__(self, input_value, output_value):
        # type: (Value, Value) -> None
        """
        :param input_value: Allowed import value
        :param output_value: Allowed output value
        """
        self.input_value = input_value  # type: Value
        self.output_value = output_value  # type: Value

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.input_value}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.output_value}

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        if self.input_value != input_value:
            return False, TransferError(self, '%s != %s' % (
                repr(self.input_value), repr(input_value)))

        if self.output_value != output_value:
            return False, TransferError(self, '%s != %s' % (
                repr(self.output_value), repr(output_value)))

        return True, None


class OneToManyRule(RuleBase):
    """Rule for the one to many transfer."""
    def __init__(self, input_value, output_values):
        # type: (Value, Collection[Value]) -> None
        """
        :param input_value: Allowed input value
        :param output_values: Collection of allowed output values
        """
        self.input_value = input_value  # type: Value
        self.output_values = output_values  # type: Collection[Value]

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.input_value}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return set(self.output_values)

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        if self.input_value != input_value:
            return False, TransferError(self, '%s != %s' % (
                repr(self.input_value), repr(input_value)))

        if output_value not in self.output_values:
            return False, TransferError(self, '%s not in %s' % (
                repr(output_value), repr(self.output_values)))

        return True, None


class ManyToOneRule(RuleBase):
    """Rule for the many to one transfer."""
    def __init__(self, input_values, output_value):
        # type: (Collection[Value], Value) -> None
        """
        :param input_values: Collection of allowed input values
        :param output_value: Allowed output value
        """
        self.input_values = input_values  # type: Collection[Value]
        self.output_value = output_value  # type: Value

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return set(self.input_values)

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.output_value}

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        if self.output_value != output_value:
            return False, TransferError(self, '%s != %s' % (
                repr(self.output_value), repr(output_value)))

        if input_value not in self.input_values:
            return False, TransferError(self, '%s not in %s' % (
                repr(input_value), repr(self.input_values)))

        return True, None


class ManyToManyRule(RuleBase):
    """Rule for the many to many transfer."""
    def __init__(self, input_values, output_values):
        # type: (Collection[Value], Collection[Value]) -> None
        """
        :param input_values: Collection of allowed input values
        :param output_values: Collection of allowed output values
        """
        self.input_values = input_values  # type: Collection[Value]
        self.output_values = output_values  # type: Collection[Value]

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return set(self.input_values)

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return set(self.output_values)

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        if input_value not in self.input_values:
            return False, TransferError(self, '%s not in %s' % (
                repr(input_value), repr(self.input_values)))

        if output_value not in self.output_values:
            return False, TransferError(self, '%s not in %s' % (
                repr(output_value), repr(self.output_values)))

        return True, None


class OneToAllRule(RuleBase):
    """Rule for the one to all transfer."""
    def __init__(self, input_value):
        # type: (Value) -> None
        """
        :param input_value: Allowed input value
        """
        self.input_value = input_value  # type: Value

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.input_value}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        if self.input_value != input_value:
            return False, TransferError(self, '%s != %s' % (
                repr(self.input_value), repr(input_value)))

        return True, None


class AllToOneRule(RuleBase):
    """Rule for the all to one transfer."""
    def __init__(self, output_value):
        # type: (Value) -> None
        """
        :param output_value: Allowed output value
        """
        self.output_value = output_value  # type: Value

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.output_value}

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        if self.output_value != output_value:
            return False, TransferError(self, '%s != %s' % (
                repr(self.output_value), repr(output_value)))

        return True, None


class ManyToAllRule(RuleBase):
    """Rule for the many to all transfer."""
    def __init__(self, input_values):
        # type: (Collection[Value]) -> None
        """
        :param input_values: Collection of allowed input values
        """
        self.input_values = input_values  # type: Collection[Value]

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return set(self.input_values)

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        if input_value not in self.input_values:
            return False, TransferError(self, '%s not in %s' % (
                repr(input_value), repr(self.input_values)))

        return True, None


class AllToManyRule(RuleBase):
    """Rule for the all to many transfer."""
    def __init__(self, output_values):
        # type: (Collection[Value]) -> None
        """
        :param output_values: Collection of allowed output values
        """
        self.output_values = output_values  # type: Collection[Value]

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return set(self.output_values)

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        if output_value not in self.output_values:
            return False, TransferError(self, '%s not in %s' % (
                repr(output_value), repr(self.output_values)))

        return True, None


class AllToAllRule(RuleBase):
    """Rule for the all to all transfer."""
    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    def is_valid(self, input_value, output_value, context):
        # type: (Value, Value, TransferContext) -> Tuple[bool, Optional[TransferError]]
        return True, None
