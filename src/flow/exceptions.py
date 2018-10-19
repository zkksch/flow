class BaseFlowException(Exception):
    """Base exception type for all library exceptions."""
    pass


class SetError(BaseFlowException):
    """Container's value set error"""
    pass
