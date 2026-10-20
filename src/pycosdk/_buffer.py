"""Passing numeric buffers (numpy arrays, ``array.array``, ctypes arrays, ...) to drivers."""

import sys
from collections.abc import Sequence
from ctypes import c_char, c_int8, c_int16, c_int32, c_int64, c_uint32, c_void_p, sizeof
from typing import TYPE_CHECKING, Any, TypeAlias

from ._struct import c_array
from .deviceenums import PICO_ACTION, PICO_DATA_TYPE

if sys.version_info >= (3, 12):
    from collections.abc import Buffer
elif TYPE_CHECKING:
    # Type checkers ship typing_extensions, so this adds no runtime dependency.
    from typing_extensions import Buffer
else:
    Buffer = Any

# A buffer the driver writes samples to: any object supporting the buffer
# protocol with the expected element type (e.g. a numpy array, array.array or
# ctypes array), a raw address as escape hatch (passed on unchecked), or None.
DataBuffer: TypeAlias = Buffer | c_void_p | int | None

# Values the driver only reads during the call: a buffer-protocol object with
# the expected element type, or any sequence of numbers.
InputValues: TypeAlias = Buffer | Sequence[int]

# Element types of the sample buffers per PICO_DATA_TYPE (ps6000a, psospa).
SAMPLE_TYPES: dict[PICO_DATA_TYPE, Any] = {
    PICO_DATA_TYPE.PICO_INT8_T: c_int8,
    PICO_DATA_TYPE.PICO_INT16_T: c_int16,
    PICO_DATA_TYPE.PICO_INT32_T: c_int32,
    PICO_DATA_TYPE.PICO_UINT32_T: c_uint32,
    PICO_DATA_TYPE.PICO_INT64_T: c_int64,
}

# Byte-order prefixes of struct formats that mean the native order.
_NATIVE_ORDER = ("@", "=", "<" if sys.byteorder == "little" else ">")


def _kind(code: str) -> str | None:
    """Signed or unsigned integer, or float, for a struct format character."""
    if code in "bhilqn":
        return "signed"
    if code in "BHILQN":
        return "unsigned"
    if code in "efd":
        return "float"
    return None


def _type_name(kind: str | None, size: int) -> str:
    """E.g. ``int16`` for signed 2-byte elements, like numpy's dtype names."""
    prefix = {"signed": "int", "unsigned": "uint", "float": "float"}.get(kind or "")
    return f"{prefix}{8 * size}" if prefix else "unknown"


def _element_type(view: memoryview) -> str:
    """The element type of ``view`` (see :func:`_type_name`), or its format."""
    fmt = view.format
    if fmt[:1] in _NATIVE_ORDER:
        fmt = fmt[1:]
    # Anything longer is a non-native byte order, a struct or unknown.
    if len(fmt) != 1 or _kind(fmt) is None:
        return f"format {view.format!r}"
    return _type_name(_kind(fmt), view.itemsize)


def buffer_argument(
    buffer: DataBuffer, ctype: Any, length: int, *, writable: bool, name: str
) -> Any:
    """Return ``buffer`` as argument for a ``void *`` buffer of ``length`` ``ctype``s.

    A buffer-protocol object must be C-contiguous, hold at least ``length``
    elements of ``ctype``'s type, and be writable if the driver writes to it.
    It is passed without copying (a read-only input is copied). The returned
    object refers to the buffer's memory and, while it exists, keeps the owner
    from resizing or freeing it: keep it alive for as long as the driver may
    access the buffer. ``None``, ints and ``c_void_p`` are passed on unchecked.
    ``name`` is used in error messages.
    """
    if length < 0:
        raise ValueError(f"the length of {name} must not be negative")
    if buffer is None or isinstance(buffer, (int, c_void_p)):
        return buffer
    try:
        view = memoryview(buffer)
    except TypeError:
        raise TypeError(
            f"{name} must support the buffer protocol (e.g. a numpy array), "
            f"not {type(buffer).__name__}"
        ) from None
    if not view.c_contiguous:
        raise ValueError(f"{name} must be C-contiguous")
    expected = _type_name(_kind(ctype._type_), sizeof(ctype))
    actual = _element_type(view)
    if actual != expected:
        raise TypeError(f"{name} has {actual} elements, expected {expected}")
    count = view.nbytes // view.itemsize
    if count < length:
        raise ValueError(f"{name} holds {count} elements, but {length} are needed")
    if view.readonly:
        if writable:
            raise ValueError(f"{name} is read-only, but the driver writes to it")
        return (c_char * view.nbytes).from_buffer_copy(view)
    return (c_char * view.nbytes).from_buffer(view)


def input_argument(values: InputValues, ctype: Any, name: str) -> tuple[Any, int]:
    """Return ``values``, which the driver only reads, as argument and their count.

    A buffer-protocol object (e.g. a numpy array) must hold elements of
    ``ctype``'s type and is passed without copying where possible; any other
    sequence is converted element by element. No values become NULL.
    """
    try:
        view = memoryview(values)  # type: ignore[arg-type]
    except TypeError:
        items: Sequence[int] = values  # type: ignore[assignment]
        return c_array(ctype, items), len(items)
    count = view.nbytes // view.itemsize if view.itemsize else 0
    if count == 0:
        return None, 0
    return buffer_argument(view, ctype, count, writable=False, name=name), count


def action_buffer_changes(
    action: PICO_ACTION, key: tuple[Any, ...], buffer: Any
) -> list[tuple[tuple[Any, ...] | None, Any]]:
    """The keep-alive changes after a ``SetDataBuffer(s)`` call with a ``PICO_ACTION``.

    Returns ``(key, buffer)`` pairs for the wrapper's ``_keep_buffer``, in order;
    a ``None`` key stands for releasing all buffers of the device.
    ``PICO_CLEAR_ALL`` releases all of the device's buffers,
    ``PICO_CLEAR_THIS_DATA_BUFFER`` the one under ``key``, and ``PICO_ADD``
    keeps ``buffer`` under ``key`` (one buffer, or pair, per key). The
    ``PICO_CLEAR_WAVEFORM_*`` actions release nothing: the guides don't say
    precisely what they clear, and keeping a buffer too long only costs memory.
    """
    # TODO: Verify that PICO_ADD replaces a buffer set earlier under the same key.
    # The guides speak of a "list" of buffers per channel, data type and segment;
    # if the driver queues them instead, an earlier buffer is released here while
    # the driver may still write to it (keep a list per key then).
    changes: list[tuple[tuple[Any, ...] | None, Any]] = []
    if action & PICO_ACTION.PICO_CLEAR_ALL:
        changes.append((None, None))
    if action & PICO_ACTION.PICO_CLEAR_THIS_DATA_BUFFER:
        changes.append((key, None))
    if action & PICO_ACTION.PICO_ADD:
        changes.append((key, buffer))
    return changes


__all__ = (
    "DataBuffer",
    "InputValues",
    "SAMPLE_TYPES",
    "action_buffer_changes",
    "buffer_argument",
    "input_argument",
)
