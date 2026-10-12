"""Device wrappers: a driver wrapper's functions bound to one opened unit."""

import functools
import inspect
from collections.abc import Callable
from ctypes import c_int16
from types import TracebackType
from typing import (
    Any,
    ClassVar,
    Concatenate,
    Generic,
    ParamSpec,
    Self,
    TypeVar,
    overload,
)

from ._base import PicoScopeWrapperBase

W = TypeVar("W", bound=PicoScopeWrapperBase)
P = ParamSpec("P")
R = TypeVar("R")


def _without_params(func: Callable[..., Any], count: int) -> inspect.Signature:
    """Signature of ``func`` without its first ``count`` parameters."""
    sig = inspect.signature(func)
    return sig.replace(parameters=list(sig.parameters.values())[count:])


class handle_method(Generic[W, P, R]):
    """Expose the wrapper method ``func`` on a device, passing the device's handle.

    ``closes`` marks the function closing the unit (``CloseUnit``); once it has
    returned, the device counts as closed.
    """

    def __init__(
        self, func: Callable[Concatenate[W, c_int16, P], R], *, closes: bool = False
    ) -> None:
        self.func = func
        self.closes = closes
        self.__doc__ = func.__doc__
        self._signature = _without_params(func, 2)

    def __set_name__(self, owner: type["PicoScopeDeviceBase[Any]"], name: str) -> None:
        if self.closes:
            owner._close_method = name

    @overload
    def __get__(self, obj: None, owner: type | None = None) -> Self: ...
    @overload
    def __get__(
        self, obj: "PicoScopeDeviceBase[W]", owner: type | None = None
    ) -> Callable[P, R]: ...
    def __get__(
        self, obj: "PicoScopeDeviceBase[W] | None", owner: type | None = None
    ) -> Self | Callable[P, R]:
        if obj is None:
            return self
        device = obj
        func = self.func
        closes = self.closes

        @functools.wraps(func)
        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(device.wrapper, device.handle, *args, **kwargs)
            if closes:
                device._closed = True
            return result

        call.__signature__ = self._signature  # type: ignore[attr-defined]
        return call


class wrapper_function(Generic[W, P, R]):
    """Expose the wrapper method ``func``, which takes no handle, like a classmethod.

    It is called on the device class's shared wrapper, see
    :meth:`PicoScopeWrapperBase.instance`.
    """

    def __init__(self, func: Callable[Concatenate[W, P], R]) -> None:
        self.func = func
        self.__doc__ = func.__doc__
        self._signature = _without_params(func, 1)

    def __get__(
        self,
        obj: "PicoScopeDeviceBase[W] | None",
        owner: "type[PicoScopeDeviceBase[W]]",
    ) -> Callable[P, R]:
        func = self.func

        @functools.wraps(func)
        def call(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(owner.shared_wrapper(), *args, **kwargs)

        call.__signature__ = self._signature  # type: ignore[attr-defined]
        return call


class PicoScopeDeviceBase(Generic[W]):
    """An opened unit, offering the wrapper's functions with its handle filled in.

    Functions taking a handle are available as methods under their C names,
    functions without one (opening, enumerating units) as classmethods. The
    open functions return a device instead of a handle. All calls go through
    the shared wrapper of the driver, see :meth:`PicoScopeWrapperBase.instance`.

    A device is a context manager that closes the unit on exit. Once closed,
    accessing :attr:`handle` (and thus calling any function needing it) raises
    :class:`ValueError`.
    """

    _wrapper_type: ClassVar[type[PicoScopeWrapperBase]]
    # Name of the method closing the unit, set by handle_method(closes=True).
    _close_method: ClassVar[str]

    def __init__(self, handle: c_int16 | int) -> None:
        """Wrap the already opened unit ``handle``, e.g. from the wrapper's open functions."""
        self.wrapper: W = self.shared_wrapper()
        self._handle = c_int16(handle.value if isinstance(handle, c_int16) else handle)
        self._closed = False

    @classmethod
    def shared_wrapper(cls) -> W:
        """The driver wrapper used by this device class."""
        return cls._wrapper_type.instance()  # type: ignore[return-value]

    @property
    def handle(self) -> c_int16:
        if self._closed:
            raise ValueError(f"{self!r} is closed")
        return self._handle

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        """Close the unit; does nothing if it is already closed."""
        if not self._closed:
            getattr(self, self._close_method)()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def __repr__(self) -> str:
        state = " (closed)" if self._closed else ""
        return f"<{type(self).__name__} handle={self._handle.value}{state}>"


__all__ = ("PicoScopeDeviceBase", "handle_method", "wrapper_function")
