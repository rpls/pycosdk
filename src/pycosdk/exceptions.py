from .status import PICO_STATUS


class MissingLibraryException(Exception):
    pass


class MissingFunctionException(Exception):
    """The loaded driver library does not export the requested function.

    Raised when calling a wrapper method whose driver function is not available,
    e.g., because the installed PicoSDK is older than the one the wrapper targets.
    """


class StatusException(Exception):
    """A driver function returned a ``PICO_STATUS`` that is treated as an error.

    Whether a status raises this exception is configured through
    :func:`pycosdk.seterr` and :class:`pycosdk.errstate`.
    """

    def __init__(self, status: PICO_STATUS, function: str | None = None):
        super().__init__(status, function)
        self.status: PICO_STATUS = status
        self.function: str | None = function

    def __str__(self) -> str:
        prefix = f"{self.function} returned " if self.function else ""
        return f"{prefix}{self.status.name} (0x{self.status.value:08X})"


class StatusWarning(UserWarning):
    """Emitted instead of raising when a status category is configured to ``"warn"``."""

    def __init__(self, status: PICO_STATUS, function: str | None = None):
        super().__init__(status, function)
        self.status: PICO_STATUS = status
        self.function: str | None = function

    def __str__(self) -> str:
        prefix = f"{self.function} returned " if self.function else ""
        return f"{prefix}{self.status.name} (0x{self.status.value:08X})"


__all__ = (
    "MissingFunctionException",
    "MissingLibraryException",
    "StatusException",
    "StatusWarning",
)
