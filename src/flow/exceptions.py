try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Iterable
    from typing import List
    from typing import Optional
    from typing import Tuple

    from flow.bases import RuleBase
    from flow.rules import RuleList


class BaseFlowException(Exception):
    """Base exception type for all library exceptions."""
    pass


class TransferError(BaseFlowException):
    """Transfer error."""
    def __init__(self, rule, error_text):
        # type: (RuleBase, str) -> None
        """
        :param rule: Failed rule
        :param error_text: Error message
        """
        super(TransferError, self).__init__(error_text)
        self.rule = rule  # type: RuleBase


class RuleListTransferError(TransferError):
    """Transfer error raised from the rules list."""

    INDENT = '  '  # type: str
    PASSED_MARK = '\u2713'  # type: str
    FAILED_MARK = '\u2715'  # type: str

    def __init__(self, rule, validation_data):
        # type: (RuleList, Iterable[Tuple[RuleBase, Tuple[bool, Optional[TransferError]]]]) -> None
        """
        :param rule: Failed rule
        :param validation_data: Inner rules validation result
        """
        self.validation_data = []  # type: List[Tuple[RuleBase, Tuple[bool, Optional[TransferError]]]]
        self.validation_data.extend(validation_data)
        self.rule = rule  # type: RuleList
        super(RuleListTransferError, self).__init__(
            rule, self.get_message(self.rule, self.validation_data))

    @classmethod
    def get_message(cls, rule, validation_data, level=0):
        # type: (RuleList, List[Tuple[RuleBase, Tuple[bool, Optional[TransferError]]]], int) -> str
        """Returns the formatted error message

        :param rule: Failed rule
        :param validation_data: Inner rules validation result
        :param level: Indent level
        """
        template = (
            "{indent}Transfer error in the RuleList "
            "(operator: {operator}):\n{inner_errors}"
        )

        inner_errors = []

        for inner_rule, (is_valid, error) in validation_data:
            success = False
            if isinstance(error, RuleListTransferError):
                error = cls.get_message(
                    error.rule, error.validation_data, level=level+1)
            elif error is None:
                error = '-'
                success = True
            else:
                error = str(error)

            inner_errors.append(
                '{indent}[{mark}] {rule}: {error}'.format(
                    indent=cls.INDENT * (level + 1),
                    mark=cls.PASSED_MARK if success else cls.FAILED_MARK,
                    rule=repr(inner_rule),
                    error=error
                )
            )

        return template.format(
            indent=cls.INDENT * level,
            operator=repr(rule.operator),
            inner_errors='\n'.join(inner_errors)
        )
