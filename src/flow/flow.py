from flow.bases import FlowBase

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from enum import Enum
    from typing import Any
    from typing import Optional
    from typing import Type

    from flow.bases import RuleBase


class Flow(FlowBase):
    """Main flow class."""


class EnumFlow(Flow):
    """The Flow that operates with the only specific enum."""
    def __init__(self, rule, enum, init=None, context=None, null=False):
        # type: (RuleBase, Type[Enum], Optional[Enum], dict, bool) -> None
        """
        :param rule: Rule
        :param enum: Enum class
        :param init: Initial state
        :param context: Initial context
        :param null: Is None valid value for the flow
        """
        self.null = null
        self.enum = enum
        if not self.check_value(init):
            raise ValueError(
                'The Flow required %s enum value as initial' % enum.__name__)

        super().__init__(rule, init, context)

    def check_value(self, value):
        # type: (Any) -> bool
        """Check a value to belonging to the enum (or None if None allowed)

        :param value: Value to check
        """
        if value is None and self.null:
            return True
        elif isinstance(value, self.enum):
            return True

        return False

    def set_state(self, state):
        # type: (Enum) -> None
        if not self.check_value(state):
            raise ValueError(
                '%s is not the %s enum\'s value' % (
                    repr(state), self.enum.__name__)
            )

        super(EnumFlow, self).set_state(state)
