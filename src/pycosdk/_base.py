# pyright: reportAny=false, reportExplicitAny=false
import sys
from collections import deque
from collections.abc import Callable, Collection
from ctypes import LibraryLoader
from ctypes.util import find_library
from pathlib import Path
from typing import Any, ClassVar

from .exceptions import MissingFunctionException, MissingLibraryException
from .status import PICO_STATUS, PICO_STATUS_T
from .statusconfig import check_status

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


class PicoScopeWrapperBase:
    _library_name: ClassVar[str]

    def __init__(self, library_path: str | None = None):
        if library_path is None:
            library_path = find_driver_library(self._library_name)
        if library_path is None:
            raise MissingLibraryException(f"{self._library_name} library not found")

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

    @staticmethod
    def _callback_key(name: str, handle: Any) -> str:
        """Callback slot key for the driver function ``name`` on device ``handle``."""
        return f"{name}:{getattr(handle, 'value', handle)}"

    def _with_callback(
        self, key: str, callback: Any, call: Callable[[], PICO_STATUS]
    ) -> PICO_STATUS:
        """Run ``call``, which hands ``callback`` to the driver, keeping it alive.

        ``key`` identifies the callback slot, see :meth:`_callback_key`. Only one callback per
        slot is current; replaced ones are retired but kept alive for a while.
        If the driver rejects the new callback, the previous one stays current.
        """
        previous = self._callbacks.get(key)
        self._callbacks[key] = callback
        accepted = False
        try:
            status = call()
            accepted = status == PICO_STATUS.PICO_OK
            return status
        finally:
            if accepted:
                retired = previous
            else:
                retired = callback
                if previous is None:
                    del self._callbacks[key]
                else:
                    self._callbacks[key] = previous
            if retired is not None:
                self._retired_callbacks.append(retired)


__all__ = (
    "CALLBACK_FUNCTYPE",
    "MACOS_SDK_LIBRARIES",
    "POWER_SOURCE_STATUSES",
    "PicoScopeWrapperBase",
    "find_driver_library",
)
