from enum import IntEnum
from typing import Any

from .status import PICO_STATUS


class MissingLibraryException(Exception):
    pass


class MissingFunctionException(Exception):
    """The loaded driver library does not export the requested function.

    Raised when calling a wrapper method whose driver function is not available,
    e.g., because the installed PicoSDK is older than the one the wrapper targets.
    """


class DriverException(Exception):
    """Base class of the errors raised when a driver function reports a failure.

    Catches both :class:`StatusException` (``PICO_STATUS`` drivers) and
    :class:`ResultException` (legacy drivers like ``ps2000`` and ``ps3000``).
    """


class DriverWarning(UserWarning):
    """Base class of the warnings emitted for driver statuses, see :class:`StatusWarning`."""


class StatusException(DriverException):
    """A driver function returned a ``PICO_STATUS`` that is treated as an error.

    Errors always raise it; warning and info statuses raise it only if their
    category is configured to ``"raise"`` through :func:`pycosdk.seterr` or
    :class:`pycosdk.errstate`.
    """

    def __init__(self, status: PICO_STATUS, function: str | None = None) -> None:
        super().__init__(status, function)
        self.status: PICO_STATUS = status
        self.function: str | None = function

    def __str__(self) -> str:
        prefix = f"{self.function} returned " if self.function else ""
        return f"{prefix}{self.status.name} (0x{self.status.value:08X})"


class StatusWarning(DriverWarning):
    """Emitted instead of raising when a status category is configured to ``"warn"``."""

    def __init__(self, status: PICO_STATUS, function: str | None = None) -> None:
        super().__init__(status, function)
        self.status: PICO_STATUS = status
        self.function: str | None = function

    def __str__(self) -> str:
        prefix = f"{self.function} returned " if self.function else ""
        return f"{prefix}{self.status.name} (0x{self.status.value:08X})"


def _describe_result(result: Any, function: str | None, error_code: int | None) -> str:
    text = f"{function or 'driver function'} failed (returned {result!r})"
    if error_code:  # 0 is the drivers' "OK" error code
        name = error_code.name if isinstance(error_code, IntEnum) else "error code"
        text += f": {name} ({int(error_code)})"
    return text


class ResultException(DriverException):
    """A legacy driver function returned a value that indicates a failure.

    Legacy drivers (``ps2000``, ``ps3000``) predate ``PICO_STATUS``; whether a
    return value means failure is defined per function. ``result`` is the raw
    return value and ``error_code`` the driver's error code (e.g.
    ``PS2000_ERROR``), if it could be determined.
    """

    def __init__(
        self,
        result: Any,
        function: str | None = None,
        error_code: int | None = None,
    ) -> None:
        super().__init__(result, function, error_code)
        self.result: Any = result
        self.function: str | None = function
        self.error_code: int | None = error_code

    def __str__(self) -> str:
        return _describe_result(self.result, self.function, self.error_code)


__all__ = (
    "DriverException",
    "DriverWarning",
    "MissingFunctionException",
    "MissingLibraryException",
    "ResultException",
    "StatusException",
    "StatusWarning",
)
