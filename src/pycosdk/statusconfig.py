"""Configuration of how non-OK ``PICO_STATUS`` return values are handled.

Modelled after :func:`numpy.seterr` and :class:`numpy.errstate`. Every status
returned by a driver function that is not ``PICO_OK`` falls into one of three
categories:

``error``
    Anything not covered by the other two categories. Default: ``"raise"``.
``warning``
    Statuses the driver documents as warnings (``PICO_WARNING_*``,
    ``PICO_SHOTS_SWEEPS_WARNING``), see :data:`WARNING_STATUSES`.
    Default: ``"warn"``.
``info``
    Statuses that a particular function returns to report a condition that is
    not a failure, e.g., ``PICO_POWER_SUPPLY_NOT_CONNECTED`` from
    ``ps3000aOpenUnit`` or ``ps3000aCurrentPowerSource``. Which statuses are
    informational is defined per wrapped function. Default: ``"ignore"``.

Each category is handled by one of the actions ``"raise"`` (raise a
:class:`~pycosdk.exceptions.StatusException`), ``"warn"`` (emit a
:class:`~pycosdk.exceptions.StatusWarning`) or ``"ignore"``. Regardless of the
action, wrapper methods still return the status if they do not raise.

:func:`seterr` changes the process-wide settings. :class:`errstate` overrides
them temporarily for a ``with`` block (or a decorated function); such overrides
are local to the current thread or asyncio task.

Callbacks invoked by the driver are not affected: they receive the status as an
argument and are free to handle it.
"""

import warnings
from collections.abc import Collection
from contextlib import ContextDecorator
from contextvars import ContextVar, Token
from typing import Literal, TypedDict, get_args

from .exceptions import StatusException, StatusWarning
from .status import PICO_STATUS

StatusAction = Literal["raise", "warn", "ignore"]


class StatusConfig(TypedDict):
    error: StatusAction
    warning: StatusAction
    info: StatusAction


WARNING_STATUSES: frozenset[PICO_STATUS] = frozenset(
    s for s in PICO_STATUS if "WARNING" in s.name
)

_global_config: StatusConfig = {"error": "raise", "warning": "warn", "info": "ignore"}
_context_config: ContextVar[StatusConfig | None] = ContextVar(
    "pycosdk_status_config", default=None
)


def _current() -> StatusConfig:
    config = _context_config.get()
    return _global_config if config is None else config


def _updated(
    config: StatusConfig,
    all: StatusAction | None,
    error: StatusAction | None,
    warning: StatusAction | None,
    info: StatusAction | None,
) -> StatusConfig:
    new = config.copy()
    for key, action in (
        ("error", all if error is None else error),
        ("warning", all if warning is None else warning),
        ("info", all if info is None else info),
    ):
        if action is None:
            continue
        if action not in get_args(StatusAction):
            raise ValueError(f"Invalid action {action!r} for {key!r}")
        new[key] = action  # type: ignore[literal-required]
    return new


def geterr() -> StatusConfig:
    """Return the currently effective status handling settings."""
    return _current().copy()


def seterr(
    *,
    all: StatusAction | None = None,
    error: StatusAction | None = None,
    warning: StatusAction | None = None,
    info: StatusAction | None = None,
) -> StatusConfig:
    """Set how non-OK statuses are handled and return the previous settings.

    ``all`` sets every category; the specific keywords take precedence over it.
    Outside of an :class:`errstate` block the change is process-wide. Inside of
    one, it only lasts until the block is left (like :func:`numpy.seterr`).
    """
    global _global_config
    old = geterr()
    new = _updated(old, all, error, warning, info)
    if _context_config.get() is None:
        _global_config = new
    else:
        _ = _context_config.set(new)
    return old


class errstate(ContextDecorator):
    """Temporarily override the status handling, as context manager or decorator.

    >>> with errstate(error="ignore"):
    ...     status, handle = scope.ps3000aOpenUnit(None)
    """

    def __init__(
        self,
        *,
        all: StatusAction | None = None,
        error: StatusAction | None = None,
        warning: StatusAction | None = None,
        info: StatusAction | None = None,
    ):
        self._kwargs: dict[str, StatusAction | None] = dict(
            all=all, error=error, warning=warning, info=info
        )
        # Validate eagerly, so typos are reported where the errstate is created.
        _ = _updated(_global_config, all, error, warning, info)
        self._tokens: list[Token[StatusConfig | None]] = []

    def __enter__(self) -> "errstate":
        new = _updated(_current(), **self._kwargs)
        self._tokens.append(_context_config.set(new))
        return self

    def __exit__(self, *exc: object) -> None:
        _context_config.reset(self._tokens.pop())


def check_status(
    status: int,
    function: str | None = None,
    info: Collection[int] = (),
    stacklevel: int = 2,
) -> PICO_STATUS:
    """Convert ``status`` to ``PICO_STATUS`` and handle it per the current settings.

    ``info`` lists the statuses that are informational for ``function``.
    ``stacklevel`` is passed on to :func:`warnings.warn` (counted from the caller
    of this function).
    """
    status = PICO_STATUS(status)
    if status == PICO_STATUS.PICO_OK:
        return status
    if status in info:
        action = _current()["info"]
    elif status in WARNING_STATUSES:
        action = _current()["warning"]
    else:
        action = _current()["error"]
    if action == "raise":
        raise StatusException(status, function)
    if action == "warn":
        warnings.warn(StatusWarning(status, function), stacklevel=stacklevel + 1)
    return status


__all__ = (
    "WARNING_STATUSES",
    "StatusAction",
    "StatusConfig",
    "check_status",
    "errstate",
    "geterr",
    "seterr",
)
