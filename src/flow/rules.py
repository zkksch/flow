from collections import defaultdict
from itertools import chain

from flow.bases import RuleBase

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

    from flow.bases import Value


class RuleList(RuleBase):
    def __init__(self, rules, operator=all):
        # type: (Iterable[RuleBase], Callable[[Iterable[object]], bool]) -> None
        self.operator = operator  # type: Callable[[Iterable[bool]], bool]
        self.rules = rules  # type: Iterable[RuleBase]

        self._input_map = defaultdict(list)  # type: Dict[Value, List[RuleBase]]

        for rule in self.rules:
            for _input in rule.inputs:
                self._input_map[_input].append(rule)

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

    def _format_error(self, rules, validation_results):
        # type: (Iterable[RuleBase], Iterable[Tuple[bool, Optional[str]]]) -> str
        main_template = "\nValidation error: (operator: {op}):\n{msg}"

        results = ',\n'.join(
            '[%s] %s: %s' % (
                ' ' if not is_valid else 'X',
                repr(rule),
                result
            )
            for rule, (is_valid, result) in zip(rules, validation_results)
        )

        return main_template.format(
            op=repr(self.operator),
            msg=results
        )

    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        input_rules = set(self._input_map[input_value]) | set(
            self._input_map[RuleBase.ALL])
        output_rules = set(self._output_map[output_value]) | set(
            self._output_map[RuleBase.ALL])

        rules = input_rules & output_rules

        if not rules:
            return False, 'Rules not found for %s -> %s transfer' % (
                repr(input_value),
                repr(output_value)
            )

        validation_results = [
            rule.is_valid(input_value, output_value) for rule in rules]

        is_valid = self.operator(
            is_valid for is_valid, _ in validation_results)

        if is_valid:
            err = None
        else:
            err = self._format_error(rules, validation_results)

        return is_valid, err


class OneToOneRule(RuleBase):
    def __init__(self, input_value, output_value):
        # type: (Value, Value) -> None
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

    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        if self.input_value != input_value:
            return False, '%s != %s' % (
                repr(self.input_value), repr(input_value))

        if self.output_value != output_value:
            return False, '%s != %s' % (
                repr(self.output_value), repr(output_value))

        return True, None


class OneToManyRule(RuleBase):
    def __init__(self, input_value, output_values):
        # type: (Value, Collection[Value]) -> None
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

    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        if self.input_value != input_value:
            return False, '%s != %s' % (
                repr(self.input_value), repr(input_value))

        if output_value not in self.output_values:
            return False, '%s not in %s' % (
                repr(output_value), repr(self.output_values))

        return True, None


class ManyToOneRule(RuleBase):
    def __init__(self, input_values, output_value):
        # type: (Collection[Value], Value) -> None
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

    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        if self.output_value != output_value:
            return False, '%s != %s' % (
                repr(self.output_value), repr(output_value))

        if input_value not in self.input_values:
            return False, '%s not in %s' % (
                repr(input_value), repr(self.input_values))

        return True, None


class ManyToManyRule(RuleBase):
    def __init__(self, input_values, output_values):
        # type: (Collection[Value], Collection[Value]) -> None
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

    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        if input_value in self.input_values:
            return False, '%s not in %s' % (
                repr(input_value), repr(self.input_values))

        if output_value not in self.output_values:
            return False, '%s not in %s' % (
                repr(output_value), repr(self.output_values))

        return True, None


class OneToAllRule(RuleBase):
    def __init__(self, input_value):
        # type: (Value) -> None
        self.input_value = input_value  # type: Value

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.input_value}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        if self.input_value != input_value:
            return False, '%s != %s' % (
                repr(self.input_value), repr(input_value))

        return True, None


class AllToOneRule(RuleBase):
    def __init__(self, output_value):
        # type: (Value) -> None
        self.output_value = output_value  # type: Value

    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.output_value}

    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        if self.output_value != output_value:
            return False, '%s != %s' % (
                repr(self.output_value), repr(output_value))

        return True, None


class AllToAllRule(RuleBase):
    @property
    def inputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    @property
    def outputs(self):
        # type: () -> Set[Value]
        return {self.ALL}

    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        return True, None