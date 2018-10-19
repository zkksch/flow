import abc
from flow.exceptions import SetError

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any
    from typing import Hashable
    from typing import Optional
    from typing import Set
    from typing import Tuple

    Value = Optional[Hashable]


class ValueContainerBase(metaclass=abc.ABCMeta):
    @property  # type: ignore
    @abc.abstractmethod
    def value(self):
        # type: () -> Any
        raise NotImplementedError

    @value.setter  # type: ignore
    @abc.abstractmethod
    def value(self, value):
        # type: (Any) -> None
        raise NotImplementedError


_ALL = type('ALL', (object,), {})()


class RuleBase(metaclass=abc.ABCMeta):
    ALL = _ALL

    @property  # type: ignore
    @abc.abstractmethod
    def inputs(self):
        # type: () -> Set[Value]
        raise NotImplementedError

    @property  # type: ignore
    @abc.abstractmethod
    def outputs(self):
        # type: () -> Set[Value]
        raise NotImplementedError

    @abc.abstractmethod
    def is_valid(self, input_value, output_value):
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        raise NotImplementedError


class FlowBase(ValueContainerBase):
    def __init__(self, rule, init=None):
        # type: (RuleBase, Value) -> None
        self._rule = rule  # type: RuleBase
        self._value = init  # type: Value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        is_valid, err = self._rule.is_valid(self._value, value)
        if is_valid:
            self._value = value
        else:
            raise SetError(err)
