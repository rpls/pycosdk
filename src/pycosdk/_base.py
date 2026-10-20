# pyright: reportAny=false, reportExplicitAny=false
import sys
import threading
from collections import deque
from collections.abc import Callable, Collection
from ctypes import LibraryLoader
from ctypes.util import find_library
from functools import partial
from pathlib import Path
from typing import Any, ClassVar, Self, TypeVar

from .exceptions import MissingFunctionException, MissingLibraryException
from .status import PICO_STATUS, PICO_STATUS_T
from .statusconfig import check_result, check_status

if sys.platform == "win32":
    # The drivers declare their callbacks as __stdcall on Windows.
    from ctypes import WINFUNCTYPE as CALLBACK_FUNCTYPE
else:
    from ctypes import CFUNCTYPE as CALLBACK_FUNCTYPE

# Statuses reporting how a device is powered. Opening a unit, querying, or
# changing its power source may return them; they are informational there.
POWER_SOURCE_STATUSES: frozenset[PICO_STATUS] = frozenset(
    {
        PICO_STATUS.PICO_POWER_SUPPLY_CONNECTED,
        PICO_STATUS.PICO_POWER_SUPPLY_NOT_CONNECTED,
        PICO_STATUS.PICO_USB3_0_DEVICE_NON_USB3_0_PORT,
    }
)

# Default install location of the PicoSDK on macOS. The installer puts each
# driver into its own folder, which is not on the dyld search path.
MACOS_SDK_LIBRARIES = Path("/Library/Frameworks/PicoSDK.framework/Libraries")


def find_driver_library(name: str) -> str | None:
    """Locate the shared library of the driver ``name`` (e.g. ``"ps6000a"``).

    Uses :func:`ctypes.util.find_library`, falling back to the PicoSDK framework
    folder on macOS.
    """
    path = find_library(name)
    if path is None and sys.platform == "darwin":
        folder = MACOS_SDK_LIBRARIES / f"lib{name}"
        unversioned = folder / f"lib{name}.dylib"
        if unversioned.is_file():
            path = str(unversioned)
        else:
            versioned = sorted(folder.glob(f"lib{name}.*.dylib"))
            if versioned:
                path = str(versioned[-1])
    return path


# How many replaced callbacks are kept alive in addition to the current ones.
# The driver may still be executing a callback when it gets replaced, e.g., when
# the next block is started right after a BlockReady callback signalled the
# previous one, so the old function pointer must not be freed immediately.
_RETIRED_CALLBACKS = 32

# Shared wrapper instances per wrapper class, see PicoScopeWrapperBase.instance.
_instances: dict[type["PicoScopeWrapperBase"], "PicoScopeWrapperBase"] = {}
_instances_lock = threading.Lock()

_R = TypeVar("_R")


class PicoScopeWrapperBase:
    _library_name: ClassVar[str]

    @classmethod
    def instance(cls, library_path: str | None = None) -> Self:
        """Return the shared wrapper, loading the driver library on the first call.

        The driver keeps its state per process, so one wrapper per driver is
        enough. ``library_path`` only takes effect on the first call; passing a
        different path once the library is loaded raises :class:`RuntimeError`.
        If loading fails, nothing is cached and a later call tries again.
        """
        with _instances_lock:
            inst = _instances.get(cls)
            if inst is None:
                inst = _instances[cls] = cls(library_path)
            elif library_path is not None and library_path != inst.library_path:
                raise RuntimeError(
                    f"{cls.__name__} is already loaded from {inst.library_path!r}"
                )
            assert isinstance(inst, cls)
            return inst

    def __init__(self, library_path: str | None = None) -> None:
        if library_path is None:
            library_path = find_driver_library(self._library_name)
        if library_path is None:
            raise MissingLibraryException(f"{self._library_name} library not found")
        self.library_path: str = library_path

        if sys.platform == "win32":
            from ctypes import WinDLL

            loadercls = WinDLL
        else:
            from ctypes import CDLL

            loadercls = CDLL
        loader = LibraryLoader(loadercls)
        self.lib = loader[library_path]

        # References to ctypes callback objects handed to the driver. They must
        # stay alive for as long as the driver may call them.
        self._callbacks: dict[str, Any] = {}
        self._retired_callbacks: deque[Any] = deque(maxlen=_RETIRED_CALLBACKS)
        # Views of the data buffers the driver writes to after the call that
        # set them (see _keep_buffer), keyed by (handle, ...).
        self._buffers: dict[tuple[Any, ...], Any] = {}

    def _bind(
        self,
        name: str,
        argtypes: list[Any],
        info: Collection[PICO_STATUS] = (),
    ) -> Callable[..., PICO_STATUS]:
        """Bind the driver function ``name`` returning a ``PICO_STATUS``.

        The returned callable converts the status to ``PICO_STATUS`` and handles
        it according to :mod:`pycosdk.statusconfig`. ``info`` lists statuses
        that are informational (not errors) for this function.

        Functions missing from the loaded library are replaced by a stub raising
        :class:`MissingFunctionException` when called.
        """
        try:
            func = getattr(self.lib, name)
        except AttributeError:

            def missing(*_args: Any, **_kwargs: Any) -> PICO_STATUS:
                raise MissingFunctionException(
                    f"{name} is not exported by the loaded driver library"
                )

            return missing

        info = frozenset(info)

        def errcheck(result: int, _func: Any, _args: Any) -> PICO_STATUS:
            # Frames: check_status <- errcheck <- wrapper method <- user code
            return check_status(result, name, info, stacklevel=3)

        func.restype = PICO_STATUS_T
        func.argtypes = argtypes
        func.errcheck = errcheck
        return func

    def _bind_legacy(
        self,
        name: str,
        argtypes: list[Any],
        restype: Any,
        failed: Callable[[Any], bool] | None = None,
        error_code: Callable[[tuple[Any, ...]], int | None] | None = None,
    ) -> Callable[..., Any]:
        """Bind the function ``name`` of a legacy (pre-``PICO_STATUS``) driver.

        ``restype`` is the ctypes return type (``None`` for ``void``). ``failed``
        tells from the raw return value whether the call failed; a failure raises
        a :class:`ResultException`, see :func:`pycosdk.statusconfig.check_result`. Without ``failed``
        the function cannot fail and its result is returned unchecked.
        ``error_code`` receives the call's arguments and looks up the driver
        error code to attach to the exception.

        Each call binds a separate function object, so a function can be bound
        more than once, e.g., unchecked for use inside an ``error_code`` lookup.
        Functions missing from the loaded library are replaced by a stub raising
        :class:`MissingFunctionException` when called.
        """
        try:
            func = self.lib[name]
        except AttributeError:

            def missing(*_args: Any, **_kwargs: Any) -> Any:
                raise MissingFunctionException(
                    f"{name} is not exported by the loaded driver library"
                )

            return missing

        func.restype = restype
        func.argtypes = argtypes
        if failed is not None:
            is_failure = failed

            def errcheck(result: Any, _func: Any, args: tuple[Any, ...]) -> Any:
                lookup = None if error_code is None else partial(error_code, args)
                return check_result(result, is_failure(result), name, lookup)

            func.errcheck = errcheck
        return func

    @staticmethod
    def _callback_key(name: str, handle: Any) -> str:
        """Callback slot key for the driver function ``name`` on device ``handle``."""
        return f"{name}:{getattr(handle, 'value', handle)}"

    def _with_callback(
        self,
        key: str,
        callback: Any,
        call: Callable[[], _R],
        accepted: Callable[[_R], bool] | None = None,
    ) -> _R:
        """Run ``call``, which hands ``callback`` to the driver, keeping it alive.

        ``key`` identifies the callback slot, see :meth:`_callback_key`. Only one callback per
        slot is current; replaced ones are retired but kept alive for a while.
        If the driver rejects the new callback, the previous one stays current.
        ``accepted`` tells from the result of ``call`` whether the driver took
        the callback; by default, when it returned ``PICO_OK``.
        """
        previous = self._callbacks.get(key)
        self._callbacks[key] = callback
        ok = False
        try:
            result = call()
            if accepted is None:
                ok = result == PICO_STATUS.PICO_OK
            else:
                ok = accepted(result)
            return result
        finally:
            if ok:
                retired = previous
            else:
                retired = callback
                if previous is None:
                    del self._callbacks[key]
                else:
                    self._callbacks[key] = previous
            if retired is not None:
                self._retired_callbacks.append(retired)

    def _keep_buffer(self, key: tuple[Any, ...], buffer: Any) -> None:
        """Keep ``buffer``, set for the driver to write to later, alive under ``key``.

        ``key`` starts with the device handle and identifies the buffer slot
        (e.g. channel, segment and ratio mode); ``buffer`` (an argument from
        :func:`pycosdk._buffer.buffer_argument`, or a tuple of them) replaces the
        previous one, ``None`` releases it. Call this only after the driver has
        accepted the buffer: it stops using a replaced buffer once the replacing
        call has returned, so the old one needs no retiring.
        """
        if buffer is None:
            self._buffers.pop(key, None)
        else:
            self._buffers[key] = buffer

    def _keep_action_buffer(
        self, key: tuple[Any, ...], action: Any, buffer: Any
    ) -> None:
        """Track a buffer set with a ``PICO_ACTION`` (ps6000a, psospa).

        ``key`` starts with the handle's value, see
        :func:`pycosdk._buffer.action_buffer_changes`.
        """
        from ._buffer import action_buffer_changes

        for change_key, change_buffer in action_buffer_changes(action, key, buffer):
            if change_key is None:
                self._release_buffers(key[0])
            else:
                self._keep_buffer(change_key, change_buffer)

    def _release_buffers(self, handle: Any) -> None:
        """Release all buffers kept for the device ``handle``, see :meth:`_keep_buffer`."""
        handle = getattr(handle, "value", handle)
        for key in [k for k in self._buffers if k[0] == handle]:
            del self._buffers[key]


__all__ = (
    "CALLBACK_FUNCTYPE",
    "MACOS_SDK_LIBRARIES",
    "POWER_SOURCE_STATUSES",
    "PicoScopeWrapperBase",
    "find_driver_library",
)
