# pyright: reportAny=false, reportUnannotatedClassAttribute=false
"""Wrapper of the legacy ``ps2000`` driver (PicoScope 2000 series, ``ps2000.h``).

The driver predates ``PICO_STATUS``: its functions return plain integers whose
meaning differs per function. Failed calls raise
:class:`~pycosdk.exceptions.ResultException`. The wrapper methods return that
value (as a more fitting Python type) followed by any outputs, but only where it
carries meaning beyond success, e.g. a handle or a number of values; values
that only signal success are not returned.
"""

from collections.abc import Callable, Sequence
from ctypes import (
    POINTER,
    byref,
    c_char_p,
    c_double,
    c_float,
    c_int16,
    c_int32,
    c_uint8,
    c_uint16,
    c_uint32,
    c_void_p,
    create_string_buffer,
)
from enum import IntEnum
from functools import partial
from typing import Annotated, Any, Self, final, overload

from ._device import PicoScopeDeviceBase, handle_method, wrapper_function
from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase
from ._buffer import DataBuffer, InputValues, buffer_argument, input_argument
from ._struct import CStruct, c_array
from .statusconfig import check_result

PS2000_FIRST_USB = 1
PS2000_LAST_USB = 127

PS2000_MAX_UNITS = PS2000_LAST_USB - PS2000_FIRST_USB + 1

PS2000_MAX_TIMEBASE = 19

PS2105_MAX_TIMEBASE = 20
PS2104_MAX_TIMEBASE = 19

PS2200_MAX_TIMEBASE = 23

PS2000_MAX_OVERSAMPLE = 256

PS2105_MAX_ETS_CYCLES = 250
PS2105_MAX_ETS_INTERLEAVE = 50

PS2104_MAX_ETS_CYCLES = 125
PS2104_MAX_ETS_INTERLEAVE = 25

PS2203_MAX_ETS_CYCLES = 250
PS2203_MAX_ETS_INTERLEAVE = 50

PS2204_MAX_ETS_CYCLES = 250
PS2204_MAX_ETS_INTERLEAVE = 40

PS2205_MAX_ETS_CYCLES = 250
PS2205_MAX_ETS_INTERLEAVE = 40

PS2000_MIN_ETS_CYCLES_INTERLEAVE_RATIO = 1
PS2000_MAX_ETS_CYCLES_INTERLEAVE_RATIO = 10

PS2000_MIN_SIGGEN_FREQ = 0.0
PS2000_MAX_SIGGEN_FREQ = 100000.0

# Samples are always scaled to 16 bits, even without oversampling.
PS2000_MAX_VALUE = 32767
PS2000_MIN_VALUE = -32767
PS2000_LOST_DATA = -32768


class PS2000_CHANNEL(IntEnum):
    PS2000_CHANNEL_A = 0
    PS2000_CHANNEL_B = 1
    PS2000_CHANNEL_C = 2
    PS2000_CHANNEL_D = 3
    PS2000_EXTERNAL = 4
    PS2000_MAX_CHANNELS = PS2000_EXTERNAL
    PS2000_NONE = 5


PS2000_CHANNEL_T = c_int32


class PS2000_RANGE(IntEnum):
    PS2000_10MV = 0
    PS2000_20MV = 1
    PS2000_50MV = 2
    PS2000_100MV = 3
    PS2000_200MV = 4
    PS2000_500MV = 5
    PS2000_1V = 6
    PS2000_2V = 7
    PS2000_5V = 8
    PS2000_10V = 9
    PS2000_20V = 10
    PS2000_50V = 11
    PS2000_MAX_RANGES = 12


PS2000_RANGE_T = c_int32


class PS2000_TIME_UNITS(IntEnum):
    PS2000_FS = 0
    PS2000_PS = 1
    PS2000_NS = 2
    PS2000_US = 3
    PS2000_MS = 4
    PS2000_S = 5
    PS2000_MAX_TIME_UNITS = 6


PS2000_TIME_UNITS_T = c_int32


class PS2000_ERROR(IntEnum):
    PS2000_OK = 0
    PS2000_MAX_UNITS_OPENED = 1
    PS2000_MEM_FAIL = 2
    PS2000_NOT_FOUND = 3
    PS2000_FW_FAIL = 4
    PS2000_NOT_RESPONDING = 5
    PS2000_CONFIG_FAIL = 6
    PS2000_OS_NOT_SUPPORTED = 7
    PS2000_PICOPP_TOO_OLD = 8


PS2000_ERROR_T = c_int32


class PS2000_INFO(IntEnum):
    PS2000_DRIVER_VERSION = 0
    PS2000_USB_VERSION = 1
    PS2000_HARDWARE_VERSION = 2
    PS2000_VARIANT_INFO = 3
    PS2000_BATCH_AND_SERIAL = 4
    PS2000_CAL_DATE = 5
    PS2000_ERROR_CODE = 6
    PS2000_KERNEL_DRIVER_VERSION = 7
    PS2000_DRIVER_PATH = 8


PS2000_INFO_T = c_int32


class PS2000_TDIR(IntEnum):
    PS2000_RISING = 0
    PS2000_FALLING = 1
    PS2000_MAX_DIRS = 2


PS2000_TDIR_T = c_int32


class PS2000_OPEN_PROGRESS(IntEnum):
    PS2000_OPEN_PROGRESS_FAIL = -1
    PS2000_OPEN_PROGRESS_PENDING = 0
    PS2000_OPEN_PROGRESS_COMPLETE = 1


PS2000_OPEN_PROGRESS_T = c_int32


class PS2000_ETS_MODE(IntEnum):
    PS2000_ETS_OFF = 0
    PS2000_ETS_FAST = 1
    PS2000_ETS_SLOW = 2
    PS2000_ETS_MODES_MAX = 3


PS2000_ETS_MODE_T = c_int32


class PS2000_BUTTON_STATE(IntEnum):
    PS2000_NO_PRESS = 0
    PS2000_SHORT_PRESS = 1
    PS2000_LONG_PRESS = 2


PS2000_BUTTON_STATE_T = c_int32


class PS2000_SWEEP_TYPE(IntEnum):
    PS2000_UP = 0
    PS2000_DOWN = 1
    PS2000_UPDOWN = 2
    PS2000_DOWNUP = 3
    PS2000_MAX_SWEEP_TYPES = 4  # C: MAX_SWEEP_TYPES


PS2000_SWEEP_TYPE_T = c_int32


class PS2000_WAVE_TYPE(IntEnum):
    PS2000_SINE = 0
    PS2000_SQUARE = 1
    PS2000_TRIANGLE = 2
    PS2000_RAMPUP = 3
    PS2000_RAMPDOWN = 4
    PS2000_DC_VOLTAGE = 5
    PS2000_GAUSSIAN = 6
    PS2000_SINC = 7
    PS2000_HALF_SINE = 8


PS2000_WAVE_TYPE_T = c_int32


class PS2000_THRESHOLD_DIRECTION(IntEnum):
    PS2000_ABOVE = 0
    PS2000_BELOW = 1
    PS2000_ADV_RISING = 2
    PS2000_ADV_FALLING = 3
    PS2000_RISING_OR_FALLING = 4
    PS2000_INSIDE = PS2000_ABOVE
    PS2000_OUTSIDE = PS2000_BELOW
    PS2000_ENTER = PS2000_ADV_RISING
    PS2000_EXIT = PS2000_ADV_FALLING
    PS2000_ENTER_OR_EXIT = PS2000_RISING_OR_FALLING
    PS2000_ADV_NONE = PS2000_ADV_RISING


PS2000_THRESHOLD_DIRECTION_T = c_int32


class PS2000_THRESHOLD_MODE(IntEnum):
    PS2000_LEVEL = 0
    PS2000_WINDOW = 1


PS2000_THRESHOLD_MODE_T = c_int32


class PS2000_TRIGGER_STATE(IntEnum):
    PS2000_CONDITION_DONT_CARE = 0
    PS2000_CONDITION_TRUE = 1
    PS2000_CONDITION_FALSE = 2
    PS2000_CONDITION_MAX = 3


PS2000_TRIGGER_STATE_T = c_int32


class PS2000_PULSE_WIDTH_TYPE(IntEnum):
    PS2000_PW_TYPE_NONE = 0
    PS2000_PW_TYPE_LESS_THAN = 1
    PS2000_PW_TYPE_GREATER_THAN = 2
    PS2000_PW_TYPE_IN_RANGE = 3
    PS2000_PW_TYPE_OUT_OF_RANGE = 4


PS2000_PULSE_WIDTH_TYPE_T = c_int32


@final
class PS2000_TRIGGER_CHANNEL_PROPERTIES(CStruct):
    thresholdMajor: Annotated[int, c_int16]
    thresholdMinor: Annotated[int, c_int16]
    hysteresis: Annotated[int, c_uint16]
    channel: Annotated[PS2000_CHANNEL, c_int16]
    thresholdMode: Annotated[PS2000_THRESHOLD_MODE, PS2000_THRESHOLD_MODE_T]


@final
class PS2000_TRIGGER_CONDITIONS(CStruct):
    channelA: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    channelB: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    channelC: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    channelD: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    external: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    pulseWidthQualifier: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]


@final
class PS2000_PWQ_CONDITIONS(CStruct):
    channelA: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    channelB: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    channelC: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    channelD: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]
    external: Annotated[PS2000_TRIGGER_STATE, PS2000_TRIGGER_STATE_T]


ps2000GetOverviewBuffersMaxMin = CALLBACK_FUNCTYPE(  # C: GetOverviewBuffersMaxMin
    None, POINTER(POINTER(c_int16)), c_int16, c_uint32, c_int16, c_int16, c_uint32
)

# Callback signature of the wrapper methods taking a ps2000GetOverviewBuffersMaxMin:
# (overviewBuffers, overflow, triggeredAt, triggered, auto_stop, nValues).
OverviewBuffersCallback = Callable[
    [Sequence[list[int] | None], int, int, bool, bool, int], None
]


# Failure predicates of the legacy driver functions, shared with ps3000.
def _is_zero(result: int) -> bool:
    return result == 0


def _is_negative(result: int) -> bool:
    return result < 0


def _is_not_positive(result: int) -> bool:
    return result <= 0


def _query_error_code(
    get_unit_info: Callable[..., int],
    handle: c_int16 | int,
    line: int,
    codes: type[IntEnum],
) -> int | None:
    """Error code of ``handle`` (0: of the last failed open), ``None`` if unknown.

    ``get_unit_info`` must be bound unchecked, so a failing lookup cannot recurse.
    """
    buf = create_string_buffer(16)
    try:
        if get_unit_info(handle, buf, len(buf), line) <= 0:
            return None
        code = int(buf.value)
    except Exception:
        return None
    try:
        return codes(code)
    except ValueError:
        return code


def _sample_buffers(no_of_values: int, **buffers: DataBuffer) -> list[Any]:
    """The int16 sample ``buffers`` (by parameter name) as ``int16_t *`` arguments.

    Each must be a writable buffer of at least ``no_of_values`` int16 elements,
    see :func:`~pycosdk._buffer.buffer_argument`. The driver writes to them
    during the call only, so they are not kept.
    """
    return [
        buffer_argument(buffer, c_int16, no_of_values, writable=True, name=name)
        for name, buffer in buffers.items()
    ]


class _OverviewBuffers(Sequence[list[int] | None]):
    """The ``int16_t **overviewBuffers`` of a ``ps2000GetOverviewBuffersMaxMin`` callback.

    Item ``i`` is a copy of the ``nValues`` samples of overview buffer ``i``
    (channel A max, A min, B max, B min, ...), or ``None`` for a NULL buffer.
    The driver's memory is only valid during the callback, so the items must be
    accessed within it. Buffers are only read when accessed: as in C, only access
    those of enabled channels.
    """

    def __init__(self, buffers: Any, nValues: int, count: int) -> None:
        self._buffers = buffers
        self._nValues = nValues
        self._count = count
        self._valid = True

    def _release(self) -> None:
        self._valid = False

    def __len__(self) -> int:
        return self._count

    @overload
    def __getitem__(self, index: int) -> list[int] | None: ...

    @overload
    def __getitem__(self, index: slice) -> list[list[int] | None]: ...

    def __getitem__(
        self, index: int | slice
    ) -> list[int] | None | list[list[int] | None]:
        if isinstance(index, slice):
            return [self[i] for i in range(self._count)[index]]
        i = range(self._count)[index]
        if not self._valid:
            raise RuntimeError("overview buffers are only valid during the callback")
        if not self._buffers or not self._buffers[i]:
            return None
        return list(self._buffers[i][: self._nValues])


def _overview_callback(
    callback: OverviewBuffersCallback, count: int
) -> Callable[[Any, int, int, int, int, int], None]:
    """Adapt ``callback`` to the raw ``ps2000GetOverviewBuffersMaxMin`` arguments."""

    def cbwrapper(
        overviewBuffers: Any,
        overflow: int,
        triggeredAt: int,
        triggered: int,
        auto_stop: int,
        nValues: int,
    ) -> None:
        buffers = _OverviewBuffers(overviewBuffers, nValues, count)
        try:
            callback(
                buffers, overflow, triggeredAt, triggered != 0, auto_stop != 0, nValues
            )
        finally:
            buffers._release()

    return cbwrapper


# Number of overview buffers: max and min of channels A and B (the driver always
# passes these four pointers, NULL for disabled channels).
_OVERVIEW_BUFFERS = 4


class PicoScope2000Wrapper(PicoScopeWrapperBase):
    # TODO: Rename the parameter that differs from the C prototype:
    # ps2000_get_streaming_last_values (callback -> lpGetOverviewBuffersMaxMin;
    # unnamed in the header, named so in the guide).
    _library_name = "ps2000"

    def __init__(self, library_path: str | None = None) -> None:
        super().__init__(library_path)

        # Unchecked binding for the error code lookup of failed calls.
        self._get_unit_info_unchecked = self._bind_legacy(
            "ps2000_get_unit_info", [c_int16, c_char_p, c_int16, c_int16], c_int16
        )
        unit_error = self._unit_error_code
        open_error = self._open_error_code

        # Returns the handle; 0: no unit found, -1: unit failed to open.
        self._ps2000_open_unit = self._bind_legacy(
            "ps2000_open_unit",
            [],
            c_int16,
            failed=_is_not_positive,
            error_code=open_error,
        )
        # Returns the string length; 0 on failure.
        self._ps2000_get_unit_info = self._bind_legacy(
            "ps2000_get_unit_info",
            [c_int16, c_char_p, c_int16, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_flash_led = self._bind_legacy(
            "ps2000_flash_led",
            [c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_close_unit = self._bind_legacy(
            "ps2000_close_unit",
            [c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_set_channel = self._bind_legacy(
            "ps2000_set_channel",
            [c_int16, c_int16, c_int16, c_int16, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_get_timebase = self._bind_legacy(
            "ps2000_get_timebase",
            [
                c_int16,
                c_int16,
                c_int32,
                POINTER(c_int32),
                POINTER(c_int16),
                c_int16,
                POINTER(c_int32),
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_set_trigger = self._bind_legacy(
            "ps2000_set_trigger",
            [c_int16, c_int16, c_int16, c_int16, c_int16, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_set_trigger2 = self._bind_legacy(
            "ps2000_set_trigger2",
            [c_int16, c_int16, c_int16, c_int16, c_float, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_run_block = self._bind_legacy(
            "ps2000_run_block",
            [c_int16, c_int32, c_int16, c_int16, POINTER(c_int32)],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_run_streaming = self._bind_legacy(
            "ps2000_run_streaming",
            [c_int16, c_int16, c_int32, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_run_streaming_ns = self._bind_legacy(
            "ps2000_run_streaming_ns",
            [
                c_int16,
                c_uint32,
                PS2000_TIME_UNITS_T,
                c_uint32,
                c_int16,
                c_uint32,
                c_uint32,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        # 0: not ready yet, < 0: the unit has been unplugged.
        self._ps2000_ready = self._bind_legacy(
            "ps2000_ready",
            [c_int16],
            c_int16,
            failed=_is_negative,
            error_code=unit_error,
        )
        self._ps2000_stop = self._bind_legacy(
            "ps2000_stop",
            [c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        # Return the number of values per channel; 0 on failure.
        # TODO: Check on hardware what the driver returns in compatible streaming
        # (run_streaming, windowed=0) when no new values have arrived: probably 0,
        # which then raises although it is no error. In block mode, 0 is also
        # returned before the capture is ready. Telling these apart needs the
        # capture mode of the handle, or not checking the result at all.
        self._ps2000_get_values = self._bind_legacy(
            "ps2000_get_values",
            [
                c_int16,
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                POINTER(c_int16),
                c_int32,
            ],
            c_int32,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_get_times_and_values = self._bind_legacy(
            "ps2000_get_times_and_values",
            [
                c_int16,
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                POINTER(c_int16),
                c_int16,
                c_int32,
            ],
            c_int32,
            failed=_is_zero,
            error_code=unit_error,
        )
        # Returns a PS2000_BUTTON_STATE; no failure value is documented.
        self._ps2000_last_button_press = self._bind_legacy(
            "ps2000_last_button_press", [c_int16], c_int16
        )
        # Returns the sample time, which is 0 both on failure and with ETS off;
        # checked in the method.
        self._ps2000_set_ets = self._bind_legacy(
            "ps2000_set_ets", [c_int16, c_int16, c_int16, c_int16], c_int32
        )
        self._ps2000_set_led = self._bind_legacy(
            "ps2000_set_led",
            [c_int16, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        # 1: the open was started. 0: another open is in progress (guide); the
        # driver also returns 0 if the open already finished, unsuccessfully
        # without a unit. -1: the open could not be started.
        self._ps2000_open_unit_async = self._bind_legacy(
            "ps2000_open_unit_async",
            [],
            c_int16,
            failed=_is_not_positive,
            error_code=open_error,
        )
        # Returns a PS2000_OPEN_PROGRESS.
        self._ps2000_open_unit_progress = self._bind_legacy(
            "ps2000_open_unit_progress",
            [POINTER(c_int16), POINTER(c_int16)],
            c_int16,
            failed=_is_negative,
            error_code=open_error,
        )
        # Returns whether the callback will be called; 0 is not necessarily an
        # error (no new data), so it is not checked.
        self._ps2000_get_streaming_last_values = self._bind_legacy(
            "ps2000_get_streaming_last_values",
            [c_int16, ps2000GetOverviewBuffersMaxMin],
            c_int16,
        )
        # Returns 0 for an invalid handle (as the driver does; the guide claims 0
        # on success and 1 for an invalid handle, the ps3000 guide 1 on success).
        self._ps2000_overview_buffer_status = self._bind_legacy(
            "ps2000_overview_buffer_status",
            [c_int16, POINTER(c_int16)],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        # Return the number of values per buffer; 0 on failure.
        self._ps2000_get_streaming_values = self._bind_legacy(
            "ps2000_get_streaming_values",
            [
                c_int16,
                POINTER(c_double),
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_int16),
                c_uint32,
                c_uint32,
            ],
            c_uint32,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_get_streaming_values_no_aggregation = self._bind_legacy(
            "ps2000_get_streaming_values_no_aggregation",
            [
                c_int16,
                POINTER(c_double),
                c_void_p,
                c_void_p,
                c_void_p,
                c_void_p,
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_int16),
                c_uint32,
            ],
            c_uint32,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_set_light = self._bind_legacy(
            "ps2000_set_light",
            [c_int16, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_set_sig_gen_arbitrary = self._bind_legacy(
            "ps2000_set_sig_gen_arbitrary",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                c_void_p,
                c_int32,
                PS2000_SWEEP_TYPE_T,
                c_uint32,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000_set_sig_gen_built_in = self._bind_legacy(
            "ps2000_set_sig_gen_built_in",
            [
                c_int16,
                c_int32,
                c_uint32,
                PS2000_WAVE_TYPE_T,
                c_float,
                c_float,
                c_float,
                c_float,
                PS2000_SWEEP_TYPE_T,
                c_uint32,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000SetAdvTriggerChannelProperties = self._bind_legacy(
            "ps2000SetAdvTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS2000_TRIGGER_CHANNEL_PROPERTIES.c_type),
                c_int16,
                c_int32,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000SetAdvTriggerChannelConditions = self._bind_legacy(
            "ps2000SetAdvTriggerChannelConditions",
            [c_int16, POINTER(PS2000_TRIGGER_CONDITIONS.c_type), c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000SetAdvTriggerChannelDirections = self._bind_legacy(
            "ps2000SetAdvTriggerChannelDirections",
            [
                c_int16,
                PS2000_THRESHOLD_DIRECTION_T,
                PS2000_THRESHOLD_DIRECTION_T,
                PS2000_THRESHOLD_DIRECTION_T,
                PS2000_THRESHOLD_DIRECTION_T,
                PS2000_THRESHOLD_DIRECTION_T,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000SetPulseWidthQualifier = self._bind_legacy(
            "ps2000SetPulseWidthQualifier",
            [
                c_int16,
                POINTER(PS2000_PWQ_CONDITIONS.c_type),
                c_int16,
                PS2000_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS2000_PULSE_WIDTH_TYPE_T,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000SetAdvTriggerDelay = self._bind_legacy(
            "ps2000SetAdvTriggerDelay",
            [c_int16, c_uint32, c_float],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps2000PingUnit = self._bind_legacy(
            "ps2000PingUnit",
            [c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )

    def _error_code(self, handle: c_int16 | int) -> int | None:
        """``PS2000_ERROR`` of ``handle`` (0: of the last failed open), if known."""
        return _query_error_code(
            self._get_unit_info_unchecked,
            handle,
            PS2000_INFO.PS2000_ERROR_CODE,
            PS2000_ERROR,
        )

    def _unit_error_code(self, args: tuple[Any, ...]) -> int | None:
        return self._error_code(args[0])

    def _open_error_code(self, _args: tuple[Any, ...]) -> int | None:
        return self._error_code(0)

    def ps2000_open_unit(self) -> c_int16:
        """Open the first unit found and return its handle.

        Raises :class:`~pycosdk.exceptions.ResultException` if no unit was found
        (result 0) or it failed to open (result -1).
        """
        return c_int16(self._ps2000_open_unit())

    def ps2000_get_unit_info(self, handle: c_int16, line: PS2000_INFO) -> str:
        """Return the info string.

        With handle 0, ``PS2000_ERROR_CODE`` gives the error of the last failed open.
        """
        # Generous for any info string; longer ones are truncated (NUL terminated).
        buf = create_string_buffer(4096)
        self._ps2000_get_unit_info(handle, buf, len(buf), line)
        return buf.value.decode("utf-8", errors="replace")

    def ps2000_flash_led(self, handle: c_int16) -> None:
        self._ps2000_flash_led(handle)

    def ps2000_close_unit(self, handle: c_int16) -> None:
        self._ps2000_close_unit(handle)
        self._release_buffers(handle)

    def ps2000_set_channel(
        self,
        handle: c_int16,
        channel: PS2000_CHANNEL,
        enabled: bool,
        dc: bool,
        range: PS2000_RANGE,
    ) -> None:
        self._ps2000_set_channel(
            handle, channel, 1 if enabled else 0, 1 if dc else 0, range
        )

    def ps2000_get_timebase(
        self,
        handle: c_int16,
        timebase: int,
        no_of_samples: int,
        oversample: int,
    ) -> tuple[int, PS2000_TIME_UNITS, int]:
        """Return ``(time_interval, time_units, max_samples)``."""
        time_interval = c_int32(0)
        time_units = c_int16(0)
        max_samples = c_int32(0)
        self._ps2000_get_timebase(
            handle,
            timebase,
            no_of_samples,
            byref(time_interval),
            byref(time_units),
            oversample,
            byref(max_samples),
        )
        return (
            time_interval.value,
            PS2000_TIME_UNITS(time_units.value),
            max_samples.value,
        )

    def ps2000_set_trigger(
        self,
        handle: c_int16,
        source: PS2000_CHANNEL,
        threshold: int,
        direction: PS2000_TDIR,
        delay: int,
        auto_trigger_ms: int,
    ) -> None:
        self._ps2000_set_trigger(
            handle, source, threshold, direction, delay, auto_trigger_ms
        )

    def ps2000_set_trigger2(
        self,
        handle: c_int16,
        source: PS2000_CHANNEL,
        threshold: int,
        direction: PS2000_TDIR,
        delay: float,
        auto_trigger_ms: int,
    ) -> None:
        self._ps2000_set_trigger2(
            handle, source, threshold, direction, delay, auto_trigger_ms
        )

    def ps2000_run_block(
        self, handle: c_int16, no_of_values: int, timebase: int, oversample: int
    ) -> int:
        """Return ``time_indisposed_ms``."""
        time_indisposed_ms = c_int32(0)
        self._ps2000_run_block(
            handle, no_of_values, timebase, oversample, byref(time_indisposed_ms)
        )
        return time_indisposed_ms.value

    def ps2000_run_streaming(
        self,
        handle: c_int16,
        sample_interval_ms: int,
        max_samples: int,
        windowed: bool,
    ) -> None:
        self._ps2000_run_streaming(
            handle, sample_interval_ms, max_samples, 1 if windowed else 0
        )

    def ps2000_run_streaming_ns(
        self,
        handle: c_int16,
        sample_interval: int,
        time_units: PS2000_TIME_UNITS,
        max_samples: int,
        auto_stop: bool,
        noOfSamplesPerAggregate: int,
        overview_buffer_size: int,
    ) -> None:
        self._ps2000_run_streaming_ns(
            handle,
            sample_interval,
            time_units,
            max_samples,
            1 if auto_stop else 0,
            noOfSamplesPerAggregate,
            overview_buffer_size,
        )

    def ps2000_ready(self, handle: c_int16) -> bool:
        """Return whether the block capture has finished.

        A negative result (unit unplugged) raises
        :class:`~pycosdk.exceptions.ResultException`.
        """
        return self._ps2000_ready(handle) > 0

    def ps2000_stop(self, handle: c_int16) -> None:
        self._ps2000_stop(handle)

    def ps2000_get_values(
        self,
        handle: c_int16,
        buffer_a: DataBuffer,
        buffer_b: DataBuffer,
        buffer_c: DataBuffer,
        buffer_d: DataBuffer,
        no_of_values: int,
    ) -> tuple[int, int]:
        """Return ``(no_of_values_returned, overflow)``.

        The buffers are writable, C-contiguous buffers of at least
        ``no_of_values`` int16 elements (e.g. ``np.empty(no_of_values, np.int16)``),
        or None for channels not read; the driver writes to them during the call
        only. A raw address (int or ``c_void_p``) is passed unchecked.
        ``overflow`` has bit 0 set for channel A, bit 1 for B, etc.
        Returning 0 values counts as a failure and raises
        :class:`~pycosdk.exceptions.ResultException`; with the compatible
        streaming mode, catch it if that is expected.
        """
        buffers = _sample_buffers(
            no_of_values,
            buffer_a=buffer_a,
            buffer_b=buffer_b,
            buffer_c=buffer_c,
            buffer_d=buffer_d,
        )
        overflow = c_int16(0)
        result = self._ps2000_get_values(
            handle, *buffers, byref(overflow), no_of_values
        )
        return result, overflow.value

    def ps2000_get_times_and_values(
        self,
        handle: c_int16,
        times: DataBuffer,
        buffer_a: DataBuffer,
        buffer_b: DataBuffer,
        buffer_c: DataBuffer,
        buffer_d: DataBuffer,
        time_units: PS2000_TIME_UNITS,
        no_of_values: int,
    ) -> tuple[int, int]:
        """Return ``(no_of_values_returned, overflow)``.

        ``times`` is a buffer of at least ``no_of_values`` int32 elements, the
        others are as in :meth:`ps2000_get_values`.
        """
        times_arg = buffer_argument(
            times, c_int32, no_of_values, writable=True, name="times"
        )
        buffers = _sample_buffers(
            no_of_values,
            buffer_a=buffer_a,
            buffer_b=buffer_b,
            buffer_c=buffer_c,
            buffer_d=buffer_d,
        )
        overflow = c_int16(0)
        result = self._ps2000_get_times_and_values(
            handle,
            times_arg,
            *buffers,
            byref(overflow),
            time_units,
            no_of_values,
        )
        return result, overflow.value

    def ps2000_last_button_press(self, handle: c_int16) -> PS2000_BUTTON_STATE:
        return PS2000_BUTTON_STATE(self._ps2000_last_button_press(handle))

    def ps2000_set_ets(
        self,
        handle: c_int16,
        mode: PS2000_ETS_MODE,
        ets_cycles: int,
        ets_interleave: int,
    ) -> int:
        """Return the effective sample time in picoseconds (0 with ETS off)."""
        result: int = self._ps2000_set_ets(handle, mode, ets_cycles, ets_interleave)
        return check_result(
            result,
            result == 0 and mode != PS2000_ETS_MODE.PS2000_ETS_OFF,
            "ps2000_set_ets",
            partial(self._error_code, handle),
        )

    def ps2000_set_led(self, handle: c_int16, state: int) -> None:
        self._ps2000_set_led(handle, state)

    def ps2000_open_unit_async(self) -> None:
        """Start opening a unit.

        Raises :class:`~pycosdk.exceptions.ResultException` if the open could
        not be started, e.g. because another open operation is in progress, or
        if it already finished without opening a unit.
        """
        self._ps2000_open_unit_async()

    def ps2000_open_unit_progress(self) -> tuple[PS2000_OPEN_PROGRESS, c_int16, int]:
        """Return ``(progress, handle, progress_percent)``.

        ``handle`` is valid once ``progress`` is ``PS2000_OPEN_PROGRESS_COMPLETE``.
        Raises :class:`~pycosdk.exceptions.ResultException` if the unit failed
        to open or was not found.
        """
        handle = c_int16(0)
        progress_percent = c_int16(0)
        result = self._ps2000_open_unit_progress(byref(handle), byref(progress_percent))
        # The driver may report completion without a handle if the open failed.
        check_result(
            result,
            result > 0 and handle.value <= 0,
            "ps2000_open_unit_progress",
            partial(self._error_code, 0),
        )
        return PS2000_OPEN_PROGRESS(result), handle, progress_percent.value

    def ps2000_get_streaming_last_values(
        self, handle: c_int16, callback: OverviewBuffersCallback
    ) -> bool:
        """Pass the latest fast streaming data to ``callback``.

        Callback args: overviewBuffers, overflow, triggeredAt, triggered,
        auto_stop, nValues. ``overviewBuffers[i]`` copies the ``nValues``
        samples of buffer ``i`` (A max, A min, B max, B min) and can only
        be accessed during the callback; as in C, only access the buffers of
        enabled channels. Returns whether the callback will be called.
        """
        lpGetOverviewBuffersMaxMin = ps2000GetOverviewBuffersMaxMin(
            _overview_callback(callback, _OVERVIEW_BUFFERS)
        )
        result = self._with_callback(
            self._callback_key("ps2000_get_streaming_last_values", handle),
            lpGetOverviewBuffersMaxMin,
            lambda: self._ps2000_get_streaming_last_values(
                handle, lpGetOverviewBuffersMaxMin
            ),
            accepted=bool,
        )
        return result != 0

    def ps2000_overview_buffer_status(self, handle: c_int16) -> bool:
        """Return ``previous_buffer_overrun``."""
        previous_buffer_overrun = c_int16(0)
        self._ps2000_overview_buffer_status(handle, byref(previous_buffer_overrun))
        return previous_buffer_overrun.value != 0

    def ps2000_get_streaming_values(
        self,
        handle: c_int16,
        start_time: float,
        pbuffer_a_max: DataBuffer,
        pbuffer_a_min: DataBuffer,
        pbuffer_b_max: DataBuffer,
        pbuffer_b_min: DataBuffer,
        pbuffer_c_max: DataBuffer,
        pbuffer_c_min: DataBuffer,
        pbuffer_d_max: DataBuffer,
        pbuffer_d_min: DataBuffer,
        no_of_values: int,
        noOfSamplesPerAggregate: int,
    ) -> tuple[int, int, int, bool]:
        """Return ``(no_of_values_returned, overflow, triggerAt, triggered)``.

        ``start_time`` is the time in nanoseconds, relative to the trigger
        point, of the first sample required. The buffers are as in
        :meth:`ps2000_get_values` (at least ``no_of_values`` int16 elements, or
        None).
        """
        buffers = _sample_buffers(
            no_of_values,
            pbuffer_a_max=pbuffer_a_max,
            pbuffer_a_min=pbuffer_a_min,
            pbuffer_b_max=pbuffer_b_max,
            pbuffer_b_min=pbuffer_b_min,
            pbuffer_c_max=pbuffer_c_max,
            pbuffer_c_min=pbuffer_c_min,
            pbuffer_d_max=pbuffer_d_max,
            pbuffer_d_min=pbuffer_d_min,
        )
        overflow = c_int16(0)
        triggerAt = c_uint32(0)
        triggered = c_int16(0)
        result = self._ps2000_get_streaming_values(
            handle,
            byref(c_double(start_time)),
            *buffers,
            byref(overflow),
            byref(triggerAt),
            byref(triggered),
            no_of_values,
            noOfSamplesPerAggregate,
        )
        return (
            result,
            overflow.value,
            triggerAt.value,
            triggered.value != 0,
        )

    def ps2000_get_streaming_values_no_aggregation(
        self,
        handle: c_int16,
        start_time: float,
        pbuffer_a: DataBuffer,
        pbuffer_b: DataBuffer,
        pbuffer_c: DataBuffer,
        pbuffer_d: DataBuffer,
        no_of_values: int,
    ) -> tuple[int, int, int, bool]:
        """Return ``(no_of_values_returned, overflow, triggerAt, trigger)``.

        ``start_time`` is the time in nanoseconds, relative to the trigger
        point, of the first sample required. The buffers are as in
        :meth:`ps2000_get_values` (at least ``no_of_values`` int16 elements, or
        None).
        """
        buffers = _sample_buffers(
            no_of_values,
            pbuffer_a=pbuffer_a,
            pbuffer_b=pbuffer_b,
            pbuffer_c=pbuffer_c,
            pbuffer_d=pbuffer_d,
        )
        overflow = c_int16(0)
        triggerAt = c_uint32(0)
        trigger = c_int16(0)
        result = self._ps2000_get_streaming_values_no_aggregation(
            handle,
            byref(c_double(start_time)),
            *buffers,
            byref(overflow),
            byref(triggerAt),
            byref(trigger),
            no_of_values,
        )
        return (
            result,
            overflow.value,
            triggerAt.value,
            trigger.value != 0,
        )

    def ps2000_set_light(self, handle: c_int16, state: bool) -> None:
        self._ps2000_set_light(handle, 1 if state else 0)

    def ps2000_set_sig_gen_arbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: InputValues,
        sweepType: PS2000_SWEEP_TYPE,
        sweeps: int,
    ) -> None:
        """``arbitraryWaveform`` holds the uint8 samples; its length is passed as size.

        It is a sequence of ints or a buffer of uint8 (e.g. a numpy array with
        ``dtype=np.uint8``), which is passed without copying.
        """
        waveform, arbitraryWaveformSize = input_argument(
            arbitraryWaveform, c_uint8, "arbitraryWaveform"
        )
        self._ps2000_set_sig_gen_arbitrary(
            handle,
            offsetVoltage,
            pkToPk,
            startDeltaPhase,
            stopDeltaPhase,
            deltaPhaseIncrement,
            dwellCount,
            waveform,
            arbitraryWaveformSize,
            sweepType,
            sweeps,
        )

    def ps2000_set_sig_gen_built_in(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS2000_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS2000_SWEEP_TYPE,
        sweeps: int,
    ) -> None:
        self._ps2000_set_sig_gen_built_in(
            handle,
            offsetVoltage,
            pkToPk,
            waveType,
            startFrequency,
            stopFrequency,
            increment,
            dwellTime,
            sweepType,
            sweeps,
        )

    def ps2000SetAdvTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS2000_TRIGGER_CHANNEL_PROPERTIES],
        autoTriggerMilliseconds: int,
    ) -> None:
        self._ps2000SetAdvTriggerChannelProperties(
            handle,
            c_array(PS2000_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            autoTriggerMilliseconds,
        )

    def ps2000SetAdvTriggerChannelConditions(
        self, handle: c_int16, conditions: Sequence[PS2000_TRIGGER_CONDITIONS]
    ) -> None:
        self._ps2000SetAdvTriggerChannelConditions(
            handle, c_array(PS2000_TRIGGER_CONDITIONS, conditions), len(conditions)
        )

    def ps2000SetAdvTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: PS2000_THRESHOLD_DIRECTION,
        channelB: PS2000_THRESHOLD_DIRECTION,
        channelC: PS2000_THRESHOLD_DIRECTION,
        channelD: PS2000_THRESHOLD_DIRECTION,
        ext: PS2000_THRESHOLD_DIRECTION,
    ) -> None:
        self._ps2000SetAdvTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext
        )

    def ps2000SetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS2000_PWQ_CONDITIONS],
        direction: PS2000_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS2000_PULSE_WIDTH_TYPE,
    ) -> None:
        self._ps2000SetPulseWidthQualifier(
            handle,
            c_array(PS2000_PWQ_CONDITIONS, conditions),
            len(conditions),
            direction,
            lower,
            upper,
            type,
        )

    def ps2000SetAdvTriggerDelay(
        self, handle: c_int16, delay: int, preTriggerDelay: float
    ) -> None:
        self._ps2000SetAdvTriggerDelay(handle, delay, preTriggerDelay)

    def ps2000PingUnit(self, handle: c_int16) -> None:
        self._ps2000PingUnit(handle)


@final
class PicoScope2000Device(PicoScopeDeviceBase[PicoScope2000Wrapper]):
    """An opened ps2000 unit; the functions of :class:`PicoScope2000Wrapper` with its handle.

    See :class:`~pycosdk.PicoScopeDeviceBase`.
    """

    _wrapper_type = PicoScope2000Wrapper

    @classmethod
    def ps2000_open_unit(cls) -> Self:
        """Like :meth:`PicoScope2000Wrapper.ps2000_open_unit`, returning a device instead of the handle."""
        return cls(cls.shared_wrapper().ps2000_open_unit())

    @classmethod
    def ps2000_open_unit_progress(cls) -> tuple[PS2000_OPEN_PROGRESS, Self | None, int]:
        """Like :meth:`PicoScope2000Wrapper.ps2000_open_unit_progress`, with a device instead of the handle once opened."""
        progress, handle, percent = cls.shared_wrapper().ps2000_open_unit_progress()
        complete = progress == PS2000_OPEN_PROGRESS.PS2000_OPEN_PROGRESS_COMPLETE
        return progress, cls(handle) if complete else None, percent

    ps2000_open_unit_async = wrapper_function(
        PicoScope2000Wrapper.ps2000_open_unit_async
    )

    ps2000_get_unit_info = handle_method(PicoScope2000Wrapper.ps2000_get_unit_info)
    ps2000_flash_led = handle_method(PicoScope2000Wrapper.ps2000_flash_led)
    ps2000_close_unit = handle_method(
        PicoScope2000Wrapper.ps2000_close_unit, closes=True
    )
    ps2000_set_channel = handle_method(PicoScope2000Wrapper.ps2000_set_channel)
    ps2000_get_timebase = handle_method(PicoScope2000Wrapper.ps2000_get_timebase)
    ps2000_set_trigger = handle_method(PicoScope2000Wrapper.ps2000_set_trigger)
    ps2000_set_trigger2 = handle_method(PicoScope2000Wrapper.ps2000_set_trigger2)
    ps2000_run_block = handle_method(PicoScope2000Wrapper.ps2000_run_block)
    ps2000_run_streaming = handle_method(PicoScope2000Wrapper.ps2000_run_streaming)
    ps2000_run_streaming_ns = handle_method(
        PicoScope2000Wrapper.ps2000_run_streaming_ns
    )
    ps2000_ready = handle_method(PicoScope2000Wrapper.ps2000_ready)
    ps2000_stop = handle_method(PicoScope2000Wrapper.ps2000_stop)
    ps2000_get_values = handle_method(PicoScope2000Wrapper.ps2000_get_values)
    ps2000_get_times_and_values = handle_method(
        PicoScope2000Wrapper.ps2000_get_times_and_values
    )
    ps2000_last_button_press = handle_method(
        PicoScope2000Wrapper.ps2000_last_button_press
    )
    ps2000_set_ets = handle_method(PicoScope2000Wrapper.ps2000_set_ets)
    ps2000_set_led = handle_method(PicoScope2000Wrapper.ps2000_set_led)
    ps2000_get_streaming_last_values = handle_method(
        PicoScope2000Wrapper.ps2000_get_streaming_last_values
    )
    ps2000_overview_buffer_status = handle_method(
        PicoScope2000Wrapper.ps2000_overview_buffer_status
    )
    ps2000_get_streaming_values = handle_method(
        PicoScope2000Wrapper.ps2000_get_streaming_values
    )
    ps2000_get_streaming_values_no_aggregation = handle_method(
        PicoScope2000Wrapper.ps2000_get_streaming_values_no_aggregation
    )
    ps2000_set_light = handle_method(PicoScope2000Wrapper.ps2000_set_light)
    ps2000_set_sig_gen_arbitrary = handle_method(
        PicoScope2000Wrapper.ps2000_set_sig_gen_arbitrary
    )
    ps2000_set_sig_gen_built_in = handle_method(
        PicoScope2000Wrapper.ps2000_set_sig_gen_built_in
    )
    ps2000SetAdvTriggerChannelProperties = handle_method(
        PicoScope2000Wrapper.ps2000SetAdvTriggerChannelProperties
    )
    ps2000SetAdvTriggerChannelConditions = handle_method(
        PicoScope2000Wrapper.ps2000SetAdvTriggerChannelConditions
    )
    ps2000SetAdvTriggerChannelDirections = handle_method(
        PicoScope2000Wrapper.ps2000SetAdvTriggerChannelDirections
    )
    ps2000SetPulseWidthQualifier = handle_method(
        PicoScope2000Wrapper.ps2000SetPulseWidthQualifier
    )
    ps2000SetAdvTriggerDelay = handle_method(
        PicoScope2000Wrapper.ps2000SetAdvTriggerDelay
    )
    ps2000PingUnit = handle_method(PicoScope2000Wrapper.ps2000PingUnit)


__all__ = (
    "PS2000_BUTTON_STATE",
    "PS2000_CHANNEL",
    "PS2000_ERROR",
    "PS2000_ETS_MODE",
    "PS2000_FIRST_USB",
    "PS2000_INFO",
    "PS2000_LAST_USB",
    "PS2000_LOST_DATA",
    "PS2000_MAX_ETS_CYCLES_INTERLEAVE_RATIO",
    "PS2000_MAX_OVERSAMPLE",
    "PS2000_MAX_SIGGEN_FREQ",
    "PS2000_MAX_TIMEBASE",
    "PS2000_MAX_UNITS",
    "PS2000_MAX_VALUE",
    "PS2000_MIN_ETS_CYCLES_INTERLEAVE_RATIO",
    "PS2000_MIN_SIGGEN_FREQ",
    "PS2000_MIN_VALUE",
    "PS2000_OPEN_PROGRESS",
    "PS2000_PULSE_WIDTH_TYPE",
    "PS2000_PWQ_CONDITIONS",
    "PS2000_RANGE",
    "PS2000_SWEEP_TYPE",
    "PS2000_TDIR",
    "PS2000_THRESHOLD_DIRECTION",
    "PS2000_THRESHOLD_MODE",
    "PS2000_TIME_UNITS",
    "PS2000_TRIGGER_CHANNEL_PROPERTIES",
    "PS2000_TRIGGER_CONDITIONS",
    "PS2000_TRIGGER_STATE",
    "PS2000_WAVE_TYPE",
    "PS2104_MAX_ETS_CYCLES",
    "PS2104_MAX_ETS_INTERLEAVE",
    "PS2104_MAX_TIMEBASE",
    "PS2105_MAX_ETS_CYCLES",
    "PS2105_MAX_ETS_INTERLEAVE",
    "PS2105_MAX_TIMEBASE",
    "PS2200_MAX_TIMEBASE",
    "PS2203_MAX_ETS_CYCLES",
    "PS2203_MAX_ETS_INTERLEAVE",
    "PS2204_MAX_ETS_CYCLES",
    "PS2204_MAX_ETS_INTERLEAVE",
    "PS2205_MAX_ETS_CYCLES",
    "PS2205_MAX_ETS_INTERLEAVE",
    "ps2000GetOverviewBuffersMaxMin",
    "OverviewBuffersCallback",
    "PicoScope2000Wrapper",
    "PicoScope2000Device",
)
