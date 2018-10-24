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


class TransferContext(dict):
    """Storage for the transfer context data."""
    pass


class RuleBase(metaclass=abc.ABCMeta):
    """Base rule class."""
    ALL = _ALL

    @property  # type: ignore
    @abc.abstractmethod
    def inputs(self):
        # type: () -> Set[Value]
        """Inputs for the rule."""
        raise NotImplementedError

    @property  # type: ignore
    @abc.abstractmethod
    def outputs(self):
        # type: () -> Set[Value]
        """Outputs for the rule."""
        raise NotImplementedError

    @abc.abstractmethod
    def is_valid(self, input_value, output_value, context=None):
        # type: (Value, Value, Optional[TransferContext]) -> Tuple[bool, Optional[TransferError]]
        """Is transfer between input and output value valid

        :param input_value: Input value
        :param output_value: Output value
        :param context: Transfer context
        :return: (Is valid, Error string)
        """
        raise NotImplementedError


class FlowBase(ValueContainerBase):
    """Base values flow class."""
    def __init__(self, rule, init=None, context=None):
        # type: (RuleBase, Value, dict) -> None
        """
        :param rule: Values transfer rules
        :param init: Initial value
        :param context: Initial context
        """
        self._rule = rule  # type: RuleBase
        self._value = init  # type: Value
        self._context = None  # type: TransferContext

        self.init_context(context or {})

    def init_context(self, context):
        # type: (dict) -> None
        """Initialize transfer context."""
        self._context = TransferContext(context)  # type: TransferContext

    @property
    def context(self):
        # type: () -> TransferContext
        """Transfer context of the flow."""
        return self._context

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        is_valid, err = self._rule.is_valid(self._value, value, self._context)
        if is_valid:
            self._value = value
        else:
            raise err
