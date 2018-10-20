import abc
from flow.exceptions import TransferError

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
    """Contains a single value and allows to change it."""
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
    """Base rule class."""
    ALL = _ALL

    @property  # type: ignore
    @abc.abstractmethod
    def inputs(self):
        """Inputs for the rule."""
        # type: () -> Set[Value]
        raise NotImplementedError

    @property  # type: ignore
    @abc.abstractmethod
    def outputs(self):
        """Outputs for the rule."""
        # type: () -> Set[Value]
        raise NotImplementedError

    @abc.abstractmethod
    def is_valid(self, input_value, output_value):
        """Is transfer between input and output value valid

        :param input_value: Input value
        :param output_value: Output value
        :return: (Is valid, Error string)
        """
        # type: (Value, Value) -> Tuple[bool, Optional[str]]
        raise NotImplementedError


class FlowBase(ValueContainerBase):
    """Base values flow class."""
    def __init__(self, rule, init=None):
        """
        :param rule: Values transfer rules
        :param init: Initial value
        """
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
            raise TransferError(err)
