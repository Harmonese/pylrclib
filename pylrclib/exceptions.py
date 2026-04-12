class PylrcLibError(Exception):
    """Base project exception."""


class PoWError(PylrcLibError):
    """Raised when PoW parameters are invalid or solving fails."""


class CLIUsageError(PylrcLibError):
    """Raised when the user passes an invalid argument combination."""
