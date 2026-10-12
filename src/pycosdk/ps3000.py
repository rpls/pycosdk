# pyright: reportAny=false, reportUnannotatedClassAttribute=false
"""Wrapper of the legacy ``ps3000`` driver (PicoScope 3000 series, ``ps3000.h``).

The driver predates ``PICO_STATUS``: its functions return plain integers whose
meaning differs per function. The wrapper methods return that value (as a more
fitting Python type where it carries meaning) followed by any outputs, and
report failed calls according to the ``error`` category of
:func:`pycosdk.seterr`, as :class:`~pycosdk.exceptions.ResultException` or
:class:`~pycosdk.exceptions.ResultWarning`.
"""

from collections.abc import Callable, Sequence
from ctypes import (
    POINTER,
    Structure,
    byref,
    c_char_p,
    c_double,
    c_float,
    c_int16,
    c_int32,
    c_uint16,
    c_uint32,
    c_void_p,
    cast,
    create_string_buffer,
)
from enum import IntEnum
from functools import partial
from typing import Any, final

from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase
from .ps2000 import (
    OverviewBuffersCallback,
    _is_negative,
    _is_nonzero,
    _is_not_positive,
    _is_zero,
    _overview_callback,
    _query_error_code,
)
from .statusconfig import check_result

PS3000_FIRST_USB = 1
PS3000_LAST_USB = 127

PS3000_MAX_UNITS = PS3000_LAST_USB - PS3000_FIRST_USB + 1

PS3206_MAX_TIMEBASE = 21
PS3205_MAX_TIMEBASE = 20
PS3204_MAX_TIMEBASE = 19
PS3224_MAX_TIMEBASE = 19
PS3223_MAX_TIMEBASE = 19
PS3424_MAX_TIMEBASE = 19
PS3423_MAX_TIMEBASE = 19

PS3225_MAX_TIMEBASE = 18
PS3226_MAX_TIMEBASE = 19
PS3425_MAX_TIMEBASE = 19
PS3426_MAX_TIMEBASE = 19

PS3000_MAX_OVERSAMPLE = 256

# Samples are always scaled to 16 bits, even without oversampling.
PS3000_MAX_VALUE = 32767
PS3000_MIN_VALUE = -32767
PS3000_LOST_DATA = -32768

# A signal generator is not available on all variants.
PS3000_MIN_SIGGEN_FREQ = 0.093
PS3000_MAX_SIGGEN_FREQ = 1000000

PS3206_MAX_ETS_CYCLES = 500
PS3206_MAX_ETS_INTERLEAVE = 100

PS3205_MAX_ETS_CYCLES = 250
PS3205_MAX_ETS_INTERLEAVE = 50

PS3204_MAX_ETS_CYCLES = 125
PS3204_MAX_ETS_INTERLEAVE = 25

PS3000_MAX_ETS_CYCLES_INTERLEAVE_RATIO = 10
PS3000_MIN_ETS_CYCLES_INTERLEAVE_RATIO = 1
PS300_MAX_ETS_SAMPLES = 100000  # sic, as in ps3000.h

MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215
MAX_HOLDOFF_COUNT = 8388607


class PS3000_CHANNEL(IntEnum):
    PS3000_CHANNEL_A = 0
    PS3000_CHANNEL_B = 1
    PS3000_CHANNEL_C = 2
    PS3000_CHANNEL_D = 3
    PS3000_EXTERNAL = 4
    PS3000_MAX_CHANNELS = PS3000_EXTERNAL
    PS3000_NONE = 5
    PS3000_MAX_TRIGGER_SOURCES = 6


PS3000_CHANNEL_T = c_int32


class PS3000_RANGE(IntEnum):
    PS3000_10MV = 0
    PS3000_20MV = 1
    PS3000_50MV = 2
    PS3000_100MV = 3
    PS3000_200MV = 4
    PS3000_500MV = 5
    PS3000_1V = 6
    PS3000_2V = 7
    PS3000_5V = 8
    PS3000_10V = 9
    PS3000_20V = 10
    PS3000_50V = 11
    PS3000_100V = 12
    PS3000_200V = 13
    PS3000_400V = 14
    PS3000_MAX_RANGES = 15


PS3000_RANGE_T = c_int32


class PS3000_WAVE_TYPES(IntEnum):
    PS3000_SQUARE = 0
    PS3000_TRIANGLE = 1
    PS3000_SINE = 2
    PS3000_MAX_WAVE_TYPES = 3


PS3000_WAVE_TYPES_T = c_int32


class PS3000_TIME_UNITS(IntEnum):
    PS3000_FS = 0
    PS3000_PS = 1
    PS3000_NS = 2
    PS3000_US = 3
    PS3000_MS = 4
    PS3000_S = 5
    PS3000_MAX_TIME_UNITS = 6


PS3000_TIME_UNITS_T = c_int32


class PS3000_ERROR(IntEnum):
    PS3000_OK = 0
    PS3000_MAX_UNITS_OPENED = 1
    PS3000_MEM_FAIL = 2
    PS3000_NOT_FOUND = 3
    PS3000_FW_FAIL = 4
    PS3000_NOT_RESPONDING = 5
    PS3000_CONFIG_FAIL = 6
    PS3000_OS_NOT_SUPPORTED = 7
    PS3000_PICOPP_TOO_OLD = 8


PS3000_ERROR_T = c_int32


class PS3000_INFO(IntEnum):
    PS3000_DRIVER_VERSION = 0
    PS3000_USB_VERSION = 1
    PS3000_HARDWARE_VERSION = 2
    PS3000_VARIANT_INFO = 3
    PS3000_BATCH_AND_SERIAL = 4
    PS3000_CAL_DATE = 5
    PS3000_ERROR_CODE = 6
    PS3000_KERNEL_DRIVER_VERSION = 7
    PS3000_DRIVER_PATH = 8


PS3000_INFO_T = c_int32


class PS3000_TDIR(IntEnum):
    PS3000_RISING = 0
    PS3000_FALLING = 1
    PS3000_MAX_DIRS = 2


PS3000_TDIR_T = c_int32


class PS3000_OPEN_PROGRESS(IntEnum):
    PS3000_OPEN_PROGRESS_FAIL = -1
    PS3000_OPEN_PROGRESS_PENDING = 0
    PS3000_OPEN_PROGRESS_COMPLETE = 1


PS3000_OPEN_PROGRESS_T = c_int32


class PS3000_ETS_MODE(IntEnum):
    PS3000_ETS_OFF = 0
    PS3000_ETS_FAST = 1
    PS3000_ETS_SLOW = 2
    PS3000_ETS_MODES_MAX = 3


PS3000_ETS_MODE_T = c_int32


# The advanced trigger types are not prefixed in ps3000.h.
class THRESHOLD_DIRECTION(IntEnum):
    ABOVE = 0
    BELOW = 1
    RISING = 2
    FALLING = 3
    RISING_OR_FALLING = 4
    INSIDE = ABOVE
    OUTSIDE = BELOW
    ENTER = RISING
    EXIT = FALLING
    ENTER_OR_EXIT = RISING_OR_FALLING
    NONE = RISING


THRESHOLD_DIRECTION_T = c_int32


class THRESHOLD_MODE(IntEnum):
    LEVEL = 0
    WINDOW = 1


THRESHOLD_MODE_T = c_int32


class TRIGGER_STATE(IntEnum):
    CONDITION_DONT_CARE = 0
    CONDITION_TRUE = 1
    CONDITION_FALSE = 2
    CONDITION_MAX = 3


TRIGGER_STATE_T = c_int32


class PULSE_WIDTH_TYPE(IntEnum):
    PW_TYPE_NONE = 0
    PW_TYPE_LESS_THAN = 1
    PW_TYPE_GREATER_THAN = 2
    PW_TYPE_IN_RANGE = 3
    PW_TYPE_OUT_OF_RANGE = 4


PULSE_WIDTH_TYPE_T = c_int32


@final
class TRIGGER_CHANNEL_PROPERTIES(Structure):
    _pack_ = 1
    _fields_ = [
        ("thresholdMajor", c_int16),
        ("thresholdMinor", c_int16),
        ("hysteresis", c_uint16),
        ("channel", c_int16),
        ("thresholdMode", THRESHOLD_MODE_T),
    ]


@final
class TRIGGER_CONDITIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", TRIGGER_STATE_T),
        ("channelB", TRIGGER_STATE_T),
        ("channelC", TRIGGER_STATE_T),
        ("channelD", TRIGGER_STATE_T),
        ("external", TRIGGER_STATE_T),
        ("pulseWidthQualifier", TRIGGER_STATE_T),
    ]


@final
class PWQ_CONDITIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", TRIGGER_STATE_T),
        ("channelB", TRIGGER_STATE_T),
        ("channelC", TRIGGER_STATE_T),
        ("channelD", TRIGGER_STATE_T),
        ("external", TRIGGER_STATE_T),
    ]


PS3000_CALLBACK_FUNC = CALLBACK_FUNCTYPE(c_int16, POINTER(c_int16), c_int16)

GetOverviewBuffersMaxMin = CALLBACK_FUNCTYPE(
    None, POINTER(POINTER(c_int16)), c_int16, c_uint32, c_int16, c_int16, c_uint32
)

# Number of overview buffers (max and min per channel A to D).
_OVERVIEW_BUFFERS = 2 * PS3000_CHANNEL.PS3000_MAX_CHANNELS


class PicoScope3000Wrapper(PicoScopeWrapperBase):
    _library_name = "ps3000"

    def __init__(self, library_path: str | None = None) -> None:
        super().__init__(library_path)

        # Unchecked binding for the error code lookup of failed calls.
        self._get_unit_info_unchecked = self._bind_legacy(
            "ps3000_get_unit_info", [c_int16, c_char_p, c_int16, c_int16], c_int16
        )
        unit_error = self._unit_error_code
        open_error = self._open_error_code

        # Returns the handle; 0: no unit found, -1: unit failed to open.
        self._ps3000_open_unit = self._bind_legacy(
            "ps3000_open_unit",
            [],
            c_int16,
            failed=_is_not_positive,
            error_code=open_error,
        )
        # Returns the string length; 0 on failure.
        self._ps3000_get_unit_info = self._bind_legacy(
            "ps3000_get_unit_info",
            [c_int16, c_char_p, c_int16, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000_flash_led = self._bind_legacy(
            "ps3000_flash_led",
            [c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000_close_unit = self._bind_legacy(
            "ps3000_close_unit",
            [c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000_set_channel = self._bind_legacy(
            "ps3000_set_channel",
            [c_int16, c_int16, c_int16, c_int16, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000_get_timebase = self._bind_legacy(
            "ps3000_get_timebase",
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
        # Returns the generated frequency, which is 0 both on failure and when
        # switching the generator off; checked in the method.
        self._ps3000_set_siggen = self._bind_legacy(
            "ps3000_set_siggen",
            [c_int16, c_int16, c_int32, c_int32, c_float, c_int16, c_int16, c_int16],
            c_int32,
        )
        # Returns the sample time, which is 0 both on failure and with ETS off;
        # checked in the method.
        self._ps3000_set_ets = self._bind_legacy(
            "ps3000_set_ets", [c_int16, c_int16, c_int16, c_int16], c_int32
        )
        self._ps3000_set_trigger = self._bind_legacy(
            "ps3000_set_trigger",
            [c_int16, c_int16, c_int16, c_int16, c_int16, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000_set_trigger2 = self._bind_legacy(
            "ps3000_set_trigger2",
            [c_int16, c_int16, c_int16, c_int16, c_float, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000_run_block = self._bind_legacy(
            "ps3000_run_block",
            [c_int16, c_int32, c_int16, c_int16, POINTER(c_int32)],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000_run_streaming_ns = self._bind_legacy(
            "ps3000_run_streaming_ns",
            [
                c_int16,
                c_uint32,
                PS3000_TIME_UNITS_T,
                c_uint32,
                c_int16,
                c_uint32,
                c_uint32,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000_run_streaming = self._bind_legacy(
            "ps3000_run_streaming",
            [c_int16, c_int16, c_int32, c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        # 0: not ready yet, < 0: the unit has been unplugged.
        self._ps3000_ready = self._bind_legacy(
            "ps3000_ready",
            [c_int16],
            c_int16,
            failed=_is_negative,
            error_code=unit_error,
        )
        self._ps3000_stop = self._bind_legacy(
            "ps3000_stop",
            [c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        # Return the number of values per channel; 0 on failure.
        self._ps3000_get_values = self._bind_legacy(
            "ps3000_get_values",
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
        self._ps3000_release_stream_buffer = self._bind_legacy(
            "ps3000_release_stream_buffer", [c_int16], None
        )
        self._ps3000_get_times_and_values = self._bind_legacy(
            "ps3000_get_times_and_values",
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
        # 0: another open operation is in progress.
        self._ps3000_open_unit_async = self._bind_legacy(
            "ps3000_open_unit_async", [], c_int16, failed=_is_zero
        )
        # Returns a PS3000_OPEN_PROGRESS.
        self._ps3000_open_unit_progress = self._bind_legacy(
            "ps3000_open_unit_progress",
            [POINTER(c_int16), POINTER(c_int16)],
            c_int16,
            failed=_is_negative,
            error_code=open_error,
        )
        self._ps3000_streaming_ns_get_interval_stateless = self._bind_legacy(
            "ps3000_streaming_ns_get_interval_stateless",
            [c_int16, c_int16, POINTER(c_uint32)],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        # Returns whether the callback will be called; 0 is not necessarily an
        # error (no new data), so it is not checked.
        self._ps3000_get_streaming_last_values = self._bind_legacy(
            "ps3000_get_streaming_last_values",
            [c_int16, GetOverviewBuffersMaxMin],
            c_int16,
        )
        # Inverted: returns 0 on success and 1 for an invalid handle.
        self._ps3000_overview_buffer_status = self._bind_legacy(
            "ps3000_overview_buffer_status",
            [c_int16, POINTER(c_int16)],
            c_int16,
            failed=_is_nonzero,
            error_code=unit_error,
        )
        # Return the number of values per buffer; 0 on failure.
        self._ps3000_get_streaming_values = self._bind_legacy(
            "ps3000_get_streaming_values",
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
        self._ps3000_get_streaming_values_no_aggregation = self._bind_legacy(
            "ps3000_get_streaming_values_no_aggregation",
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
        # Undocumented return value, so it is not checked.
        self._ps3000_save_streaming_data = self._bind_legacy(
            "ps3000_save_streaming_data",
            [c_int16, PS3000_CALLBACK_FUNC, c_void_p, c_int16],
            c_int16,
        )
        self._ps3000SetAdvTriggerChannelProperties = self._bind_legacy(
            "ps3000SetAdvTriggerChannelProperties",
            [c_int16, POINTER(TRIGGER_CHANNEL_PROPERTIES), c_int16, c_int32],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000SetAdvTriggerChannelConditions = self._bind_legacy(
            "ps3000SetAdvTriggerChannelConditions",
            [c_int16, POINTER(TRIGGER_CONDITIONS), c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000SetAdvTriggerChannelDirections = self._bind_legacy(
            "ps3000SetAdvTriggerChannelDirections",
            [
                c_int16,
                THRESHOLD_DIRECTION_T,
                THRESHOLD_DIRECTION_T,
                THRESHOLD_DIRECTION_T,
                THRESHOLD_DIRECTION_T,
                THRESHOLD_DIRECTION_T,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000SetPulseWidthQualifier = self._bind_legacy(
            "ps3000SetPulseWidthQualifier",
            [
                c_int16,
                POINTER(PWQ_CONDITIONS),
                c_int16,
                THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PULSE_WIDTH_TYPE_T,
            ],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000SetAdvTriggerDelay = self._bind_legacy(
            "ps3000SetAdvTriggerDelay",
            [c_int16, c_uint32, c_float],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )
        self._ps3000PingUnit = self._bind_legacy(
            "ps3000PingUnit",
            [c_int16],
            c_int16,
            failed=_is_zero,
            error_code=unit_error,
        )

    def _error_code(self, handle: c_int16 | int) -> int | None:
        """``PS3000_ERROR`` of ``handle`` (0: of the last failed open), if known."""
        return _query_error_code(
            self._get_unit_info_unchecked,
            handle,
            PS3000_INFO.PS3000_ERROR_CODE,
            PS3000_ERROR,
        )

    def _unit_error_code(self, args: tuple[Any, ...]) -> int | None:
        return self._error_code(args[0])

    def _open_error_code(self, _args: tuple[Any, ...]) -> int | None:
        return self._error_code(0)

    def ps3000_open_unit(self) -> c_int16:
        """Open the first unit found and return its handle.

        The handle is 0 if no unit was found and -1 if it failed to open.
        """
        return c_int16(self._ps3000_open_unit())

    def ps3000_get_unit_info(
        self, handle: c_int16, line: PS3000_INFO
    ) -> tuple[int, str]:
        """Return the length of the info string and the string itself.

        With handle 0, ``PS3000_ERROR_CODE`` gives the error of the last failed open.
        """
        buf = create_string_buffer(256)
        length = self._ps3000_get_unit_info(handle, buf, len(buf), line)
        return length, buf.value.decode("utf-8", errors="replace")

    def ps3000_flash_led(self, handle: c_int16) -> int:
        return self._ps3000_flash_led(handle)

    def ps3000_close_unit(self, handle: c_int16) -> int:
        return self._ps3000_close_unit(handle)

    def ps3000_set_channel(
        self,
        handle: c_int16,
        channel: PS3000_CHANNEL,
        enabled: bool,
        dc: bool,
        range: PS3000_RANGE,
    ) -> int:
        return self._ps3000_set_channel(
            handle, channel, 1 if enabled else 0, 1 if dc else 0, range
        )

    def ps3000_get_timebase(
        self,
        handle: c_int16,
        timebase: int,
        no_of_samples: int,
        oversample: int,
    ) -> tuple[int, int, PS3000_TIME_UNITS, int]:
        """Return ``(result, time_interval, time_units, max_samples)``."""
        time_interval = c_int32(0)
        time_units = c_int16(0)
        max_samples = c_int32(0)
        result = self._ps3000_get_timebase(
            handle,
            timebase,
            no_of_samples,
            byref(time_interval),
            byref(time_units),
            oversample,
            byref(max_samples),
        )
        return (
            result,
            time_interval.value,
            PS3000_TIME_UNITS(time_units.value),
            max_samples.value,
        )

    def ps3000_set_siggen(
        self,
        handle: c_int16,
        wave_type: PS3000_WAVE_TYPES,
        start_frequency: int,
        stop_frequency: int,
        increment: float,
        dwell_time: int,
        repeat: bool,
        dual_slope: bool,
    ) -> int:
        """Return the generated frequency in Hz (0 when switched off).

        A ``start_frequency`` of 0 switches the signal generator off.
        """
        result: int = self._ps3000_set_siggen(
            handle,
            wave_type,
            start_frequency,
            stop_frequency,
            increment,
            dwell_time,
            1 if repeat else 0,
            1 if dual_slope else 0,
        )
        return check_result(
            result,
            result == 0 and start_frequency != 0,
            "ps3000_set_siggen",
            partial(self._error_code, handle),
        )

    def ps3000_set_ets(
        self,
        handle: c_int16,
        mode: PS3000_ETS_MODE,
        ets_cycles: int,
        ets_interleave: int,
    ) -> int:
        """Return the effective sample time in picoseconds (0 with ETS off)."""
        result: int = self._ps3000_set_ets(handle, mode, ets_cycles, ets_interleave)
        return check_result(
            result,
            result == 0 and mode != PS3000_ETS_MODE.PS3000_ETS_OFF,
            "ps3000_set_ets",
            partial(self._error_code, handle),
        )

    def ps3000_set_trigger(
        self,
        handle: c_int16,
        source: PS3000_CHANNEL,
        threshold: int,
        direction: PS3000_TDIR,
        delay: int,
        auto_trigger_ms: int,
    ) -> int:
        return self._ps3000_set_trigger(
            handle, source, threshold, direction, delay, auto_trigger_ms
        )

    def ps3000_set_trigger2(
        self,
        handle: c_int16,
        source: PS3000_CHANNEL,
        threshold: int,
        direction: PS3000_TDIR,
        delay: float,
        auto_trigger_ms: int,
    ) -> int:
        return self._ps3000_set_trigger2(
            handle, source, threshold, direction, delay, auto_trigger_ms
        )

    def ps3000_run_block(
        self, handle: c_int16, no_of_values: int, timebase: int, oversample: int
    ) -> tuple[int, int]:
        """Return ``(result, time_indisposed_ms)``."""
        time_indisposed_ms = c_int32(0)
        result = self._ps3000_run_block(
            handle, no_of_values, timebase, oversample, byref(time_indisposed_ms)
        )
        return result, time_indisposed_ms.value

    def ps3000_run_streaming_ns(
        self,
        handle: c_int16,
        sample_interval: int,
        time_units: PS3000_TIME_UNITS,
        max_samples: int,
        auto_stop: bool,
        noOfSamplesPerAggregate: int,
        overview_buffer_size: int,
    ) -> int:
        return self._ps3000_run_streaming_ns(
            handle,
            sample_interval,
            time_units,
            max_samples,
            1 if auto_stop else 0,
            noOfSamplesPerAggregate,
            overview_buffer_size,
        )

    def ps3000_run_streaming(
        self,
        handle: c_int16,
        sample_interval_ms: int,
        max_samples: int,
        windowed: bool,
    ) -> int:
        return self._ps3000_run_streaming(
            handle, sample_interval_ms, max_samples, 1 if windowed else 0
        )

    def ps3000_ready(self, handle: c_int16) -> bool:
        """Return whether the block capture has finished.

        A negative result (unit unplugged) is a failure; if it is ignored, it
        reads as not ready.
        """
        return self._ps3000_ready(handle) > 0

    def ps3000_stop(self, handle: c_int16) -> int:
        return self._ps3000_stop(handle)

    def ps3000_get_values(
        self,
        handle: c_int16,
        buffer_a: c_void_p | int | None,
        buffer_b: c_void_p | int | None,
        buffer_c: c_void_p | int | None,
        buffer_d: c_void_p | int | None,
        no_of_values: int,
    ) -> tuple[int, int]:
        """Return ``(no_of_values_returned, overflow)``.

        The buffers hold ``no_of_values`` int16 values, or are None for channels
        not read. ``overflow`` has bit 0 set for channel A, bit 1 for B, etc.
        Returning 0 values counts as a failure; with the compatible streaming
        mode, use ``errstate(error="ignore")`` if that is expected.
        """
        overflow = c_int16(0)
        result = self._ps3000_get_values(
            handle,
            buffer_a,
            buffer_b,
            buffer_c,
            buffer_d,
            byref(overflow),
            no_of_values,
        )
        return result, overflow.value

    def ps3000_release_stream_buffer(self, handle: c_int16) -> None:
        self._ps3000_release_stream_buffer(handle)

    def ps3000_get_times_and_values(
        self,
        handle: c_int16,
        times: c_void_p | int | None,
        buffer_a: c_void_p | int | None,
        buffer_b: c_void_p | int | None,
        buffer_c: c_void_p | int | None,
        buffer_d: c_void_p | int | None,
        time_units: PS3000_TIME_UNITS,
        no_of_values: int,
    ) -> tuple[int, int]:
        """Return ``(no_of_values_returned, overflow)``.

        ``times`` holds ``no_of_values`` int32 values, see :meth:`ps3000_get_values`.
        """
        overflow = c_int16(0)
        result = self._ps3000_get_times_and_values(
            handle,
            times,
            buffer_a,
            buffer_b,
            buffer_c,
            buffer_d,
            byref(overflow),
            time_units,
            no_of_values,
        )
        return result, overflow.value

    def ps3000_open_unit_async(self) -> int:
        """Start opening a unit; returns 0 if an open operation is in progress."""
        return self._ps3000_open_unit_async()

    def ps3000_open_unit_progress(self) -> tuple[PS3000_OPEN_PROGRESS, c_int16, int]:
        """Return ``(progress, handle, progress_percent)``.

        ``handle`` is valid once ``progress`` is ``PS3000_OPEN_PROGRESS_COMPLETE``.
        """
        handle = c_int16(0)
        progress_percent = c_int16(0)
        result = self._ps3000_open_unit_progress(byref(handle), byref(progress_percent))
        return PS3000_OPEN_PROGRESS(result), handle, progress_percent.value

    def ps3000_streaming_ns_get_interval_stateless(
        self, handle: c_int16, nChannels: int, sample_interval: int
    ) -> tuple[int, int]:
        """Return ``(result, sample_interval)`` as adjusted by the driver.

        Undocumented; ``sample_interval`` is passed by reference.
        """
        interval = c_uint32(sample_interval)
        result = self._ps3000_streaming_ns_get_interval_stateless(
            handle, nChannels, byref(interval)
        )
        return result, interval.value

    def ps3000_get_streaming_last_values(
        self, handle: c_int16, callback: OverviewBuffersCallback
    ) -> bool:
        """Pass the latest fast streaming data to ``callback``.

        Callback args: overviewBuffers, overflow, triggeredAt, triggered,
        auto_stop, nValues. ``overviewBuffers[i]`` copies the ``nValues``
        samples of buffer ``i`` (A max, A min, B max, B min, ...) and can only
        be accessed during the callback; as in C, only access the buffers of
        enabled channels. Returns whether the callback will be called.
        """
        lpGetOverviewBuffersMaxMin = GetOverviewBuffersMaxMin(
            _overview_callback(callback, _OVERVIEW_BUFFERS)
        )
        result = self._with_callback(
            self._callback_key("ps3000_get_streaming_last_values", handle),
            lpGetOverviewBuffersMaxMin,
            lambda: self._ps3000_get_streaming_last_values(
                handle, lpGetOverviewBuffersMaxMin
            ),
            accepted=bool,
        )
        return result != 0

    def ps3000_overview_buffer_status(self, handle: c_int16) -> tuple[int, bool]:
        """Return ``(result, previous_buffer_overrun)``; ``result`` is 0 on success."""
        previous_buffer_overrun = c_int16(0)
        result = self._ps3000_overview_buffer_status(
            handle, byref(previous_buffer_overrun)
        )
        return result, previous_buffer_overrun.value != 0

    def ps3000_get_streaming_values(
        self,
        handle: c_int16,
        pbuffer_a_max: c_void_p | int | None,
        pbuffer_a_min: c_void_p | int | None,
        pbuffer_b_max: c_void_p | int | None,
        pbuffer_b_min: c_void_p | int | None,
        pbuffer_c_max: c_void_p | int | None,
        pbuffer_c_min: c_void_p | int | None,
        pbuffer_d_max: c_void_p | int | None,
        pbuffer_d_min: c_void_p | int | None,
        no_of_values: int,
        noOfSamplesPerAggregate: int,
    ) -> tuple[int, float, int, int, bool]:
        """Return ``(no_of_values_returned, start_time, overflow, triggerAt, triggered)``.

        The buffers hold ``no_of_values`` int16 values, or are None.
        """
        start_time = c_double(0)
        overflow = c_int16(0)
        triggerAt = c_uint32(0)
        triggered = c_int16(0)
        result = self._ps3000_get_streaming_values(
            handle,
            byref(start_time),
            pbuffer_a_max,
            pbuffer_a_min,
            pbuffer_b_max,
            pbuffer_b_min,
            pbuffer_c_max,
            pbuffer_c_min,
            pbuffer_d_max,
            pbuffer_d_min,
            byref(overflow),
            byref(triggerAt),
            byref(triggered),
            no_of_values,
            noOfSamplesPerAggregate,
        )
        return (
            result,
            start_time.value,
            overflow.value,
            triggerAt.value,
            triggered.value != 0,
        )

    def ps3000_get_streaming_values_no_aggregation(
        self,
        handle: c_int16,
        pbuffer_a: c_void_p | int | None,
        pbuffer_b: c_void_p | int | None,
        pbuffer_c: c_void_p | int | None,
        pbuffer_d: c_void_p | int | None,
        no_of_values: int,
    ) -> tuple[int, float, int, int, bool]:
        """Return ``(no_of_values_returned, start_time, overflow, triggerAt, trigger)``.

        The buffers hold ``no_of_values`` int16 values, or are None.
        """
        start_time = c_double(0)
        overflow = c_int16(0)
        triggerAt = c_uint32(0)
        trigger = c_int16(0)
        result = self._ps3000_get_streaming_values_no_aggregation(
            handle,
            byref(start_time),
            pbuffer_a,
            pbuffer_b,
            pbuffer_c,
            pbuffer_d,
            byref(overflow),
            byref(triggerAt),
            byref(trigger),
            no_of_values,
        )
        return (
            result,
            start_time.value,
            overflow.value,
            triggerAt.value,
            trigger.value != 0,
        )

    def ps3000_save_streaming_data(
        self,
        handle: c_int16,
        callback: Callable[[int | None, int], int],
        dataBuffers: c_void_p | int | None,
        dataBufferSize: int,
    ) -> int:
        """Undocumented; the raw return value is returned unchecked.

        Callback args: the address of the ``int16_t *dataBuffer`` (``None`` if
        NULL) and ``noOfBuffers``; its return value is passed to the driver. The
        buffer length is not known, so the data is not copied: read it during
        the callback. ``dataBuffers`` (``dataBufferSize`` int16 values) is kept
        alive along with the callback.
        """

        def cbwrapper(dataBuffer: Any, noOfBuffers: int) -> int:
            return int(callback(cast(dataBuffer, c_void_p).value, noOfBuffers))

        lpCallbackFunc = PS3000_CALLBACK_FUNC(cbwrapper)
        return self._with_callback(
            self._callback_key("ps3000_save_streaming_data", handle),
            (lpCallbackFunc, dataBuffers),
            lambda: self._ps3000_save_streaming_data(
                handle, lpCallbackFunc, dataBuffers, dataBufferSize
            ),
            accepted=bool,
        )

    def ps3000SetAdvTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[TRIGGER_CHANNEL_PROPERTIES],
        autoTriggerMilliseconds: int,
    ) -> int:
        n = len(channelProperties)
        properties = (TRIGGER_CHANNEL_PROPERTIES * n)(*channelProperties)
        return self._ps3000SetAdvTriggerChannelProperties(
            handle, properties if n else None, n, autoTriggerMilliseconds
        )

    def ps3000SetAdvTriggerChannelConditions(
        self, handle: c_int16, conditions: Sequence[TRIGGER_CONDITIONS]
    ) -> int:
        n = len(conditions)
        conds = (TRIGGER_CONDITIONS * n)(*conditions)
        return self._ps3000SetAdvTriggerChannelConditions(
            handle, conds if n else None, n
        )

    def ps3000SetAdvTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: THRESHOLD_DIRECTION,
        channelB: THRESHOLD_DIRECTION,
        channelC: THRESHOLD_DIRECTION,
        channelD: THRESHOLD_DIRECTION,
        ext: THRESHOLD_DIRECTION,
    ) -> int:
        return self._ps3000SetAdvTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext
        )

    def ps3000SetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PWQ_CONDITIONS],
        direction: THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PULSE_WIDTH_TYPE,
    ) -> int:
        n = len(conditions)
        conds = (PWQ_CONDITIONS * n)(*conditions)
        return self._ps3000SetPulseWidthQualifier(
            handle, conds if n else None, n, direction, lower, upper, type
        )

    def ps3000SetAdvTriggerDelay(
        self, handle: c_int16, delay: int, preTriggerDelay: float
    ) -> int:
        return self._ps3000SetAdvTriggerDelay(handle, delay, preTriggerDelay)

    def ps3000PingUnit(self, handle: c_int16) -> int:
        return self._ps3000PingUnit(handle)


__all__ = (
    "MAX_HOLDOFF_COUNT",
    "MAX_PULSE_WIDTH_QUALIFIER_COUNT",
    "PS300_MAX_ETS_SAMPLES",
    "PS3000_CALLBACK_FUNC",
    "PS3000_CHANNEL",
    "PS3000_ERROR",
    "PS3000_ETS_MODE",
    "PS3000_FIRST_USB",
    "PS3000_INFO",
    "PS3000_LAST_USB",
    "PS3000_LOST_DATA",
    "PS3000_MAX_ETS_CYCLES_INTERLEAVE_RATIO",
    "PS3000_MAX_OVERSAMPLE",
    "PS3000_MAX_SIGGEN_FREQ",
    "PS3000_MAX_UNITS",
    "PS3000_MAX_VALUE",
    "PS3000_MIN_ETS_CYCLES_INTERLEAVE_RATIO",
    "PS3000_MIN_SIGGEN_FREQ",
    "PS3000_MIN_VALUE",
    "PS3000_OPEN_PROGRESS",
    "PS3000_RANGE",
    "PS3000_TDIR",
    "PS3000_TIME_UNITS",
    "PS3000_WAVE_TYPES",
    "PS3204_MAX_ETS_CYCLES",
    "PS3204_MAX_ETS_INTERLEAVE",
    "PS3204_MAX_TIMEBASE",
    "PS3205_MAX_ETS_CYCLES",
    "PS3205_MAX_ETS_INTERLEAVE",
    "PS3205_MAX_TIMEBASE",
    "PS3206_MAX_ETS_CYCLES",
    "PS3206_MAX_ETS_INTERLEAVE",
    "PS3206_MAX_TIMEBASE",
    "PS3223_MAX_TIMEBASE",
    "PS3224_MAX_TIMEBASE",
    "PS3225_MAX_TIMEBASE",
    "PS3226_MAX_TIMEBASE",
    "PS3423_MAX_TIMEBASE",
    "PS3424_MAX_TIMEBASE",
    "PS3425_MAX_TIMEBASE",
    "PS3426_MAX_TIMEBASE",
    "PULSE_WIDTH_TYPE",
    "PWQ_CONDITIONS",
    "THRESHOLD_DIRECTION",
    "THRESHOLD_MODE",
    "TRIGGER_CHANNEL_PROPERTIES",
    "TRIGGER_CONDITIONS",
    "TRIGGER_STATE",
    "GetOverviewBuffersMaxMin",
    "OverviewBuffersCallback",
    "PicoScope3000Wrapper",
)
