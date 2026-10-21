# pyright: reportAny=false, reportUnannotatedClassAttribute=false
from collections.abc import Callable, Sequence
from ctypes import (
    POINTER,
    byref,
    c_char_p,
    c_double,
    c_float,
    c_int16,
    c_int32,
    c_int64,
    c_uint16,
    c_uint32,
    c_void_p,
    create_string_buffer,
)
from enum import IntEnum
from typing import Annotated, Self, final

from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase, int64_from_halves, seconds
from ._buffer import DataBuffer, InputValues, buffer_argument, input_argument
from ._device import PicoScopeDeviceBase, handle_method, wrapper_function
from ._struct import CStruct, c_array
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T

# Driver for the PicoScope 5203 and 5204 (not the 5000A/B/D series, see
# ps5000a). Several names are unprefixed in ps5000Api.h (e.g. SWEEP_TYPE, UP,
# MAX_SIG_GEN_BUFFER_SIZE); like the ps6000 module, they get a PS5000_ prefix
# here. The C name is noted where it differs.

PS5000_MAX_OVERSAMPLE_8BIT = 256

# Samples are always scaled to 16 bits, even without oversampling.
PS5000_MAX_VALUE = 32512
PS5000_MIN_VALUE = -32512
PS5000_LOST_DATA = -32768

PS5000_EXT_MAX_VALUE = 32767
PS5000_EXT_MIN_VALUE = -32767

PS5000_MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215  # C: MAX_PULSE_WIDTH_QUALIFIER_COUNT
PS5000_MAX_DELAY_COUNT = 8388607  # C: MAX_DELAY_COUNT

PS5000_MAX_SIG_GEN_BUFFER_SIZE = 8192  # C: MAX_SIG_GEN_BUFFER_SIZE
PS5000_MIN_SIG_GEN_BUFFER_SIZE = 10  # C: MIN_SIG_GEN_BUFFER_SIZE
PS5000_MIN_DWELL_COUNT = 10  # C: MIN_DWELL_COUNT
PS5000_MAX_SWEEPS_SHOTS = (1 << 30) - 1  # C: MAX_SWEEPS_SHOTS


class PS5000_CHANNEL(IntEnum):
    PS5000_CHANNEL_A = 0
    PS5000_CHANNEL_B = 1
    PS5000_CHANNEL_C = 2
    PS5000_CHANNEL_D = 3
    PS5000_EXTERNAL = 4
    PS5000_MAX_CHANNELS = PS5000_EXTERNAL
    PS5000_TRIGGER_AUX = 5
    PS5000_MAX_TRIGGER_SOURCES = 6


PS5000_CHANNEL_T = c_int32


class PS5000_CHANNEL_BUFFER_INDEX(IntEnum):
    PS5000_CHANNEL_A_MAX = 0
    PS5000_CHANNEL_A_MIN = 1
    PS5000_CHANNEL_B_MAX = 2
    PS5000_CHANNEL_B_MIN = 3
    PS5000_CHANNEL_C_MAX = 4
    PS5000_CHANNEL_C_MIN = 5
    PS5000_CHANNEL_D_MAX = 6
    PS5000_CHANNEL_D_MIN = 7
    PS5000_MAX_CHANNEL_BUFFERS = 8


PS5000_CHANNEL_BUFFER_INDEX_T = c_int32


class PS5000_RANGE(IntEnum):
    PS5000_10MV = 0
    PS5000_20MV = 1
    PS5000_50MV = 2
    PS5000_100MV = 3
    PS5000_200MV = 4
    PS5000_500MV = 5
    PS5000_1V = 6
    PS5000_2V = 7
    PS5000_5V = 8
    PS5000_10V = 9
    PS5000_20V = 10
    PS5000_50V = 11
    PS5000_MAX_RANGES = 12


PS5000_RANGE_T = c_int32


class PS5000_ETS_MODE(IntEnum):
    PS5000_ETS_OFF = 0
    PS5000_ETS_FAST = 1
    PS5000_ETS_SLOW = 2
    PS5000_ETS_MODES_MAX = 3


PS5000_ETS_MODE_T = c_int32


class PS5000_TIME_UNITS(IntEnum):
    PS5000_FS = 0
    PS5000_PS = 1
    PS5000_NS = 2
    PS5000_US = 3
    PS5000_MS = 4
    PS5000_S = 5
    PS5000_MAX_TIME_UNITS = 6


PS5000_TIME_UNITS_T = c_int32


class PS5000_SWEEP_TYPE(IntEnum):
    # C: SWEEP_TYPE with UP, DOWN, UPDOWN, DOWNUP, MAX_SWEEP_TYPES
    PS5000_UP = 0
    PS5000_DOWN = 1
    PS5000_UPDOWN = 2
    PS5000_DOWNUP = 3
    PS5000_MAX_SWEEP_TYPES = 4


PS5000_SWEEP_TYPE_T = c_int32


class PS5000_WAVE_TYPE(IntEnum):
    # C: WAVE_TYPE
    PS5000_SINE = 0
    PS5000_SQUARE = 1
    PS5000_TRIANGLE = 2
    PS5000_RAMP_UP = 3
    PS5000_RAMP_DOWN = 4
    PS5000_SINC = 5
    PS5000_GAUSSIAN = 6
    PS5000_HALF_SINE = 7
    PS5000_DC_VOLTAGE = 8
    PS5000_WHITE_NOISE = 9
    PS5000_MAX_WAVE_TYPES = 10  # C: MAX_WAVE_TYPES


PS5000_WAVE_TYPE_T = c_int32


PS5000_SINE_MAX_FREQUENCY = 20000000.0
PS5000_SQUARE_MAX_FREQUENCY = 20000000.0
PS5000_TRIANGLE_MAX_FREQUENCY = 20000000.0
PS5000_SINC_MAX_FREQUENCY = 20000000.0
PS5000_RAMP_MAX_FREQUENCY = 20000000.0
PS5000_HALF_SINE_MAX_FREQUENCY = 20000000.0
PS5000_GAUSSIAN_MAX_FREQUENCY = 20000000.0
PS5000_MIN_FREQUENCY = 0.03


class PS5000_SIGGEN_TRIG_TYPE(IntEnum):
    # C: SIGGEN_TRIG_TYPE with SIGGEN_* members
    PS5000_SIGGEN_RISING = 0
    PS5000_SIGGEN_FALLING = 1
    PS5000_SIGGEN_GATE_HIGH = 2
    PS5000_SIGGEN_GATE_LOW = 3


PS5000_SIGGEN_TRIG_TYPE_T = c_int32


class PS5000_SIGGEN_TRIG_SOURCE(IntEnum):
    # C: SIGGEN_TRIG_SOURCE with SIGGEN_* members
    PS5000_SIGGEN_NONE = 0
    PS5000_SIGGEN_SCOPE_TRIG = 1
    PS5000_SIGGEN_AUX_IN = 2
    PS5000_SIGGEN_EXT_IN = 3
    PS5000_SIGGEN_SOFT_TRIG = 4


PS5000_SIGGEN_TRIG_SOURCE_T = c_int32


class PS5000_INDEX_MODE(IntEnum):
    # C: INDEX_MODE with SINGLE, DUAL, QUAD, MAX_INDEX_MODES
    PS5000_SINGLE = 0
    PS5000_DUAL = 1
    PS5000_QUAD = 2
    PS5000_MAX_INDEX_MODES = 3


PS5000_INDEX_MODE_T = c_int32


class PS5000_THRESHOLD_MODE(IntEnum):
    # C: THRESHOLD_MODE with LEVEL, WINDOW
    PS5000_LEVEL = 0
    PS5000_WINDOW = 1


PS5000_THRESHOLD_MODE_T = c_int32


class PS5000_THRESHOLD_DIRECTION(IntEnum):
    # C: THRESHOLD_DIRECTION with unprefixed members
    PS5000_ABOVE = 0
    PS5000_BELOW = 1
    PS5000_RISING = 2
    PS5000_FALLING = 3
    PS5000_RISING_OR_FALLING = 4
    PS5000_INSIDE = PS5000_ABOVE
    PS5000_OUTSIDE = PS5000_BELOW
    PS5000_ENTER = PS5000_RISING
    PS5000_EXIT = PS5000_FALLING
    PS5000_ENTER_OR_EXIT = PS5000_RISING_OR_FALLING
    PS5000_NONE = PS5000_RISING


PS5000_THRESHOLD_DIRECTION_T = c_int32


class PS5000_TRIGGER_STATE(IntEnum):
    # C: TRIGGER_STATE with CONDITION_* members
    PS5000_CONDITION_DONT_CARE = 0
    PS5000_CONDITION_TRUE = 1
    PS5000_CONDITION_FALSE = 2
    PS5000_CONDITION_MAX = 3


PS5000_TRIGGER_STATE_T = c_int32


class PS5000_RATIO_MODE(IntEnum):
    # C: RATIO_MODE with RATIO_MODE_* members. Note DECIMATE and AVERAGE are
    # swapped compared to PS6000_RATIO_MODE.
    PS5000_RATIO_MODE_NONE = 0
    PS5000_RATIO_MODE_AGGREGATE = 1
    PS5000_RATIO_MODE_DECIMATE = 2
    PS5000_RATIO_MODE_AVERAGE = 4
    PS5000_RATIO_MODE_DISTRIBUTION = 8


PS5000_RATIO_MODE_T = c_int32


class PS5000_PULSE_WIDTH_TYPE(IntEnum):
    # C: PULSE_WIDTH_TYPE with PW_TYPE_* members
    PS5000_PW_TYPE_NONE = 0
    PS5000_PW_TYPE_LESS_THAN = 1
    PS5000_PW_TYPE_GREATER_THAN = 2
    PS5000_PW_TYPE_IN_RANGE = 3
    PS5000_PW_TYPE_OUT_OF_RANGE = 4


PS5000_PULSE_WIDTH_TYPE_T = c_int32


class PS5000_CHANNEL_INFO(IntEnum):
    PS5000_CI_RANGES = 0  # C: CI_RANGES


PS5000_CHANNEL_INFO_T = c_int32


@final
class PS5000_TRIGGER_CONDITIONS(CStruct):
    # C: TRIGGER_CONDITIONS
    channelA: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    channelB: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    channelC: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    channelD: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    external: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    aux: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    pulseWidthQualifier: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]


@final
class PS5000_PWQ_CONDITIONS(CStruct):
    # C: PWQ_CONDITIONS
    channelA: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    channelB: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    channelC: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    channelD: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    external: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]
    aux: Annotated[PS5000_TRIGGER_STATE, PS5000_TRIGGER_STATE_T]


@final
class PS5000_TRIGGER_CHANNEL_PROPERTIES(CStruct):
    # C: TRIGGER_CHANNEL_PROPERTIES. Unlike later drivers, there is a single
    # hysteresis shared by both thresholds.
    thresholdMajor: Annotated[int, c_int16]
    thresholdMinor: Annotated[int, c_int16]
    hysteresis: Annotated[int, c_uint16]
    channel: Annotated[PS5000_CHANNEL, PS5000_CHANNEL_T]
    thresholdMode: Annotated[PS5000_THRESHOLD_MODE, PS5000_THRESHOLD_MODE_T]


ps5000BlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps5000StreamingReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)

# Unlike the other drivers' DataReady, this one carries no status but the
# trigger information instead.
ps5000DataReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_int16, c_uint32, c_int16, c_void_p
)


class PicoScope5000Wrapper(PicoScopeWrapperBase):
    _library_name = "ps5000"

    def __init__(self, library_path: str | None = None) -> None:
        super().__init__(library_path)

        self._ps5000OpenUnit = self._bind("ps5000OpenUnit", [POINTER(c_int16)])
        self._ps5000OpenUnitAsync = self._bind(
            "ps5000OpenUnitAsync", [POINTER(c_int16)]
        )
        self._ps5000OpenUnitProgress = self._bind(
            "ps5000OpenUnitProgress",
            [POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps5000GetUnitInfo = self._bind(
            "ps5000GetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps5000FlashLed = self._bind("ps5000FlashLed", [c_int16, c_int16])
        self._ps5000IsLedFlashing = self._bind(
            "ps5000IsLedFlashing", [c_int16, POINTER(c_int16)]
        )
        self._ps5000CloseUnit = self._bind("ps5000CloseUnit", [c_int16])
        self._ps5000MemorySegments = self._bind(
            "ps5000MemorySegments", [c_int16, c_uint16, POINTER(c_int32)]
        )
        self._ps5000SetChannel = self._bind(
            "ps5000SetChannel",
            [c_int16, PS5000_CHANNEL_T, c_int16, c_int16, PS5000_RANGE_T],
        )
        self._ps5000GetTimebase = self._bind(
            "ps5000GetTimebase",
            [
                c_int16,
                c_uint32,
                c_int32,
                POINTER(c_int32),
                c_int16,
                POINTER(c_int32),
                c_uint16,
            ],
        )
        self._ps5000GetTimebase2 = self._bind(
            "ps5000GetTimebase2",
            [
                c_int16,
                c_uint32,
                c_int32,
                POINTER(c_float),
                c_int16,
                POINTER(c_int32),
                c_uint16,
            ],
        )
        self._ps5000SetSigGenArbitrary = self._bind(
            "ps5000SetSigGenArbitrary",
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
                PS5000_SWEEP_TYPE_T,
                c_int16,
                PS5000_INDEX_MODE_T,
                c_uint32,
                c_uint32,
                PS5000_SIGGEN_TRIG_TYPE_T,
                PS5000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps5000SetSigGenBuiltIn = self._bind(
            "ps5000SetSigGenBuiltIn",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_float,
                c_float,
                c_float,
                c_float,
                PS5000_SWEEP_TYPE_T,
                c_int16,
                c_uint32,
                c_uint32,
                PS5000_SIGGEN_TRIG_TYPE_T,
                PS5000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps5000SetSigGenBuiltInV2 = self._bind(
            "ps5000SetSigGenBuiltInV2",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS5000_SWEEP_TYPE_T,
                c_int16,
                c_uint32,
                c_uint32,
                PS5000_SIGGEN_TRIG_TYPE_T,
                PS5000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps5000SigGenFrequencyToPhase = self._bind(
            "ps5000SigGenFrequencyToPhase",
            [c_int16, c_double, PS5000_INDEX_MODE_T, c_uint32, POINTER(c_uint32)],
        )
        self._ps5000SigGenArbitraryMinMaxValues = self._bind(
            "ps5000SigGenArbitraryMinMaxValues",
            [
                c_int16,
                POINTER(c_int16),
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_uint32),
            ],
        )
        self._ps5000SigGenSoftwareControl = self._bind(
            "ps5000SigGenSoftwareControl", [c_int16, c_int16]
        )
        self._ps5000SetEts = self._bind(
            "ps5000SetEts",
            [c_int16, PS5000_ETS_MODE_T, c_int16, c_int16, POINTER(c_int32)],
        )
        self._ps5000SetTriggerChannelProperties = self._bind(
            "ps5000SetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS5000_TRIGGER_CHANNEL_PROPERTIES.c_type),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps5000SetTriggerChannelConditions = self._bind(
            "ps5000SetTriggerChannelConditions",
            [c_int16, POINTER(PS5000_TRIGGER_CONDITIONS.c_type), c_int16],
        )
        self._ps5000SetTriggerChannelDirections = self._bind(
            "ps5000SetTriggerChannelDirections",
            [
                c_int16,
                PS5000_THRESHOLD_DIRECTION_T,
                PS5000_THRESHOLD_DIRECTION_T,
                PS5000_THRESHOLD_DIRECTION_T,
                PS5000_THRESHOLD_DIRECTION_T,
                PS5000_THRESHOLD_DIRECTION_T,
                PS5000_THRESHOLD_DIRECTION_T,
            ],
        )
        self._ps5000SetSimpleTrigger = self._bind(
            "ps5000SetSimpleTrigger",
            [
                c_int16,
                c_int16,
                PS5000_CHANNEL_T,
                c_int16,
                PS5000_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_int16,
            ],
        )
        self._ps5000SetTriggerDelay = self._bind(
            "ps5000SetTriggerDelay", [c_int16, c_uint32]
        )
        self._ps5000SetPulseWidthQualifier = self._bind(
            "ps5000SetPulseWidthQualifier",
            [
                c_int16,
                POINTER(PS5000_PWQ_CONDITIONS.c_type),
                c_int16,
                PS5000_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS5000_PULSE_WIDTH_TYPE_T,
            ],
        )
        self._ps5000IsTriggerOrPulseWidthQualifierEnabled = self._bind(
            "ps5000IsTriggerOrPulseWidthQualifierEnabled",
            [c_int16, POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps5000GetTriggerTimeOffset = self._bind(
            "ps5000GetTriggerTimeOffset",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS5000_TIME_UNITS_T),
                c_uint16,
            ],
        )
        self._ps5000GetTriggerTimeOffset64 = self._bind(
            "ps5000GetTriggerTimeOffset64",
            [c_int16, POINTER(c_int64), POINTER(PS5000_TIME_UNITS_T), c_uint16],
        )
        self._ps5000GetValuesTriggerTimeOffsetBulk = self._bind(
            "ps5000GetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS5000_TIME_UNITS_T),
                c_uint16,
                c_uint16,
            ],
        )
        self._ps5000GetValuesTriggerTimeOffsetBulk64 = self._bind(
            "ps5000GetValuesTriggerTimeOffsetBulk64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS5000_TIME_UNITS_T),
                c_uint16,
                c_uint16,
            ],
        )
        self._ps5000SetDataBuffers = self._bind(
            "ps5000SetDataBuffers",
            [c_int16, PS5000_CHANNEL_T, c_void_p, c_void_p, c_int32],
        )
        self._ps5000SetDataBuffer = self._bind(
            "ps5000SetDataBuffer", [c_int16, PS5000_CHANNEL_T, c_void_p, c_int32]
        )
        self._ps5000SetDataBufferBulk = self._bind(
            "ps5000SetDataBufferBulk",
            [c_int16, PS5000_CHANNEL_T, c_void_p, c_int32, c_uint16],
        )
        self._ps5000SetEtsTimeBuffer = self._bind(
            "ps5000SetEtsTimeBuffer", [c_int16, c_void_p, c_int32]
        )
        self._ps5000SetEtsTimeBuffers = self._bind(
            "ps5000SetEtsTimeBuffers", [c_int16, c_void_p, c_void_p, c_int32]
        )
        self._ps5000IsReady = self._bind("ps5000IsReady", [c_int16, POINTER(c_int16)])
        self._ps5000RunBlock = self._bind(
            "ps5000RunBlock",
            [
                c_int16,
                c_int32,
                c_int32,
                c_uint32,
                c_int16,
                POINTER(c_int32),
                c_uint16,
                ps5000BlockReady,
                c_void_p,
            ],
        )
        self._ps5000RunStreaming = self._bind(
            "ps5000RunStreaming",
            [
                c_int16,
                POINTER(c_uint32),
                PS5000_TIME_UNITS_T,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint32,
                c_uint32,
            ],
        )
        self._ps5000GetStreamingLatestValues = self._bind(
            "ps5000GetStreamingLatestValues",
            [c_int16, ps5000StreamingReady, c_void_p],
            # PICO_BUSY: no new streaming data yet / previous call still being
            # processed. The caller is expected to simply poll again.
            info=(PICO_STATUS.PICO_BUSY,),
        )
        self._ps5000NoOfStreamingValues = self._bind(
            "ps5000NoOfStreamingValues", [c_int16, POINTER(c_uint32)]
        )
        # The downSampleRatioMode arguments below are int16_t in the header,
        # not RATIO_MODE.
        self._ps5000GetMaxDownSampleRatio = self._bind(
            "ps5000GetMaxDownSampleRatio",
            [c_int16, c_uint32, POINTER(c_uint32), c_int16, c_uint16],
        )
        self._ps5000GetValues = self._bind(
            "ps5000GetValues",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                c_int16,
                c_uint16,
                POINTER(c_int16),
            ],
        )
        self._ps5000GetValuesBulk = self._bind(
            "ps5000GetValuesBulk",
            [c_int16, POINTER(c_uint32), c_uint16, c_uint16, POINTER(c_int16)],
        )
        self._ps5000GetValuesAsync = self._bind(
            "ps5000GetValuesAsync",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint16,
                # Declared as void * in the header; a ps5000DataReady is passed.
                c_void_p,
                c_void_p,
            ],
        )
        self._ps5000Stop = self._bind("ps5000Stop", [c_int16])
        self._ps5000PingUnit = self._bind("ps5000PingUnit", [c_int16])
        self._ps5000SetNoOfCaptures = self._bind(
            "ps5000SetNoOfCaptures", [c_int16, c_uint16]
        )

    def ps5000OpenUnit(self) -> c_int16:
        """Open the first unit found; the driver has no serial selection."""
        handle = c_int16(0)
        self._ps5000OpenUnit(byref(handle))
        return handle

    def ps5000OpenUnitAsync(self) -> bool:
        """Start opening a unit; returns whether the operation started."""
        started = c_int16(0)
        self._ps5000OpenUnitAsync(byref(started))
        return started.value == 1

    def ps5000OpenUnitProgress(self) -> tuple[c_int16, int, bool]:
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        self._ps5000OpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return handle, progressPercent.value, complete.value != 0

    def ps5000CloseUnit(self, handle: c_int16) -> None:
        self._ps5000CloseUnit(handle)
        self._release_buffers(handle)

    def ps5000GetUnitInfo(self, handle: c_int16, info: PICO_INFO) -> str:
        # Generous for any info string; longer ones are truncated (NUL terminated).
        buf = create_string_buffer(4096)
        size = c_int16(0)
        self._ps5000GetUnitInfo(handle, buf, len(buf), byref(size), info)
        return buf.value.decode("utf-8")

    def ps5000FlashLed(self, handle: c_int16, start: int) -> None:
        """Flash the LED ``start`` times; -1 flashes indefinitely, 0 stops."""
        self._ps5000FlashLed(handle, start)

    def ps5000IsLedFlashing(self, handle: c_int16) -> bool:
        flashing = c_int16(0)
        self._ps5000IsLedFlashing(handle, byref(flashing))
        return flashing.value != 0

    def ps5000MemorySegments(self, handle: c_int16, nSegments: int) -> int:
        assert nSegments > 0
        nMaxSamples = c_int32(0)
        self._ps5000MemorySegments(handle, nSegments, byref(nMaxSamples))
        return nMaxSamples.value

    def ps5000SetChannel(
        self,
        handle: c_int16,
        channel: PS5000_CHANNEL,
        enabled: bool,
        dc: bool,
        range: PS5000_RANGE,
    ) -> None:
        """``dc`` selects DC coupling, otherwise AC."""
        self._ps5000SetChannel(
            handle, channel, 1 if enabled else 0, 1 if dc else 0, range
        )

    def ps5000GetTimebase(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        oversample: int,
        segmentIndex: int,
    ) -> tuple[int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_int32(0)
        self._ps5000GetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNanoseconds.value, maxSamples.value

    def ps5000GetTimebase2(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        oversample: int,
        segmentIndex: int,
    ) -> tuple[float, int]:
        assert oversample >= 0 and oversample <= PS5000_MAX_OVERSAMPLE_8BIT
        timeIntervalNanoseconds = c_float(0)
        maxSamples = c_int32(0)
        self._ps5000GetTimebase2(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNanoseconds.value, maxSamples.value

    def ps5000SetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: InputValues,
        sweepType: PS5000_SWEEP_TYPE,
        whiteNoise: bool,
        indexMode: PS5000_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS5000_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """``arbitraryWaveform`` holds the int16 arbitrary waveform samples.

        It is a sequence of ints or a buffer of int16 (e.g. a numpy array with
        ``dtype=np.int16``), which is passed without copying.
        """
        waveform, arbitraryWaveformSize = input_argument(
            arbitraryWaveform, c_int16, "arbitraryWaveform"
        )
        self._ps5000SetSigGenArbitrary(
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
            1 if whiteNoise else 0,
            indexMode,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps5000SetSigGenBuiltIn(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS5000_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS5000_SWEEP_TYPE,
        whiteNoise: bool,
        shots: int,
        sweeps: int,
        triggerType: PS5000_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps5000SetSigGenBuiltIn(
            handle,
            offsetVoltage,
            pkToPk,
            waveType,
            startFrequency,
            stopFrequency,
            increment,
            dwellTime,
            sweepType,
            1 if whiteNoise else 0,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps5000SetSigGenBuiltInV2(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS5000_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS5000_SWEEP_TYPE,
        whiteNoise: bool,
        shots: int,
        sweeps: int,
        triggerType: PS5000_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps5000SetSigGenBuiltInV2(
            handle,
            offsetVoltage,
            pkToPk,
            waveType,
            startFrequency,
            stopFrequency,
            increment,
            dwellTime,
            sweepType,
            1 if whiteNoise else 0,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps5000SigGenFrequencyToPhase(
        self,
        handle: c_int16,
        frequency: float,
        indexMode: PS5000_INDEX_MODE,
        bufferLength: int,
    ) -> int:
        phase = c_uint32(0)
        self._ps5000SigGenFrequencyToPhase(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return phase.value

    def ps5000SigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[int, int, int, int]:
        minValue = c_int16(0)
        maxValue = c_int16(0)
        minSize = c_uint32(0)
        maxSize = c_uint32(0)
        self._ps5000SigGenArbitraryMinMaxValues(
            handle, byref(minValue), byref(maxValue), byref(minSize), byref(maxSize)
        )
        return minValue.value, maxValue.value, minSize.value, maxSize.value

    def ps5000SigGenSoftwareControl(self, handle: c_int16, state: bool) -> None:
        self._ps5000SigGenSoftwareControl(handle, 1 if state else 0)

    def ps5000SetEts(
        self,
        handle: c_int16,
        mode: PS5000_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> int:
        sampleTimePicoseconds = c_int32(0)
        self._ps5000SetEts(
            handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
        )
        return sampleTimePicoseconds.value

    def ps5000SetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS5000_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> None:
        self._ps5000SetTriggerChannelProperties(
            handle,
            c_array(PS5000_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps5000SetTriggerChannelConditions(
        self, handle: c_int16, conditions: Sequence[PS5000_TRIGGER_CONDITIONS]
    ) -> None:
        self._ps5000SetTriggerChannelConditions(
            handle, c_array(PS5000_TRIGGER_CONDITIONS, conditions), len(conditions)
        )

    def ps5000SetTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: PS5000_THRESHOLD_DIRECTION,
        channelB: PS5000_THRESHOLD_DIRECTION,
        channelC: PS5000_THRESHOLD_DIRECTION,
        channelD: PS5000_THRESHOLD_DIRECTION,
        ext: PS5000_THRESHOLD_DIRECTION,
        aux: PS5000_THRESHOLD_DIRECTION,
    ) -> None:
        self._ps5000SetTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext, aux
        )

    def ps5000SetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PS5000_CHANNEL,
        threshold: int,
        direction: PS5000_THRESHOLD_DIRECTION,
        delay: int,
        autoTrigger_ms: int,
    ) -> None:
        assert autoTrigger_ms >= 0
        self._ps5000SetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTrigger_ms,
        )

    def ps5000SetTriggerDelay(self, handle: c_int16, delay: int) -> None:
        self._ps5000SetTriggerDelay(handle, delay)

    def ps5000SetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS5000_PWQ_CONDITIONS],
        direction: PS5000_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS5000_PULSE_WIDTH_TYPE,
    ) -> None:
        self._ps5000SetPulseWidthQualifier(
            handle,
            c_array(PS5000_PWQ_CONDITIONS, conditions),
            len(conditions),
            direction,
            lower,
            upper,
            type,
        )

    def ps5000IsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        self._ps5000IsTriggerOrPulseWidthQualifierEnabled(
            handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
        )
        return (
            triggerEnabled.value != 0,
            pulseWidthQualifierEnabled.value != 0,
        )

    def ps5000GetTriggerTimeOffset(self, handle: c_int16, segmentIndex: int) -> float:
        """Returns the trigger time offset of the segment in seconds."""
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS5000_TIME_UNITS_T(0)
        self._ps5000GetTriggerTimeOffset(
            handle, byref(timeUpper), byref(timeLower), byref(timeUnits), segmentIndex
        )
        return seconds(
            int64_from_halves(timeUpper.value, timeLower.value), timeUnits.value
        )

    def ps5000GetTriggerTimeOffset64(self, handle: c_int16, segmentIndex: int) -> float:
        """Returns the trigger time offset of the segment in seconds."""
        time = c_int64(0)
        timeUnits = PS5000_TIME_UNITS_T(0)
        self._ps5000GetTriggerTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return seconds(time.value, timeUnits.value)

    def ps5000GetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> list[float]:
        """Returns the trigger time offsets of the segments in seconds."""
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        timesUpper = (c_uint32 * nsegments)()
        timesLower = (c_uint32 * nsegments)()
        timeUnits = (PS5000_TIME_UNITS_T * nsegments)()
        self._ps5000GetValuesTriggerTimeOffsetBulk(
            handle, timesUpper, timesLower, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return [
            seconds(int64_from_halves(upper, lower), units)
            for upper, lower, units in zip(
                timesUpper, timesLower, timeUnits, strict=True
            )
        ]

    def ps5000GetValuesTriggerTimeOffsetBulk64(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> list[float]:
        """Returns the trigger time offsets of the segments in seconds."""
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * nsegments)()
        timeUnits = (PS5000_TIME_UNITS_T * nsegments)()
        self._ps5000GetValuesTriggerTimeOffsetBulk64(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return [
            seconds(time, units) for time, units in zip(times, timeUnits, strict=True)
        ]

    def ps5000SetDataBuffers(
        self,
        handle: c_int16,
        channel: PS5000_CHANNEL,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Like :meth:`ps5000SetDataBuffer`, with buffers for the maxima and minima."""
        argMax = buffer_argument(
            bufferMax, c_int16, bufferLth, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, c_int16, bufferLth, writable=True, name="bufferMin"
        )
        self._ps5000SetDataBuffers(handle, channel, argMax, argMin, bufferLth)
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_buffer((handle.value, "data", channel), both)

    def ps5000SetDataBuffer(
        self,
        handle: c_int16,
        channel: PS5000_CHANNEL,
        buffer: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Set the buffer the driver writes the samples of ``channel`` to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int16 elements (e.g. ``np.empty(bufferLth, np.int16)``), or None. The
        wrapper keeps it from being freed or resized until it is replaced (also
        by :meth:`ps5000SetDataBuffers`), set to None or the unit is closed. A
        raw address (int or ``c_void_p``) is passed unchecked and must be kept
        valid by the caller.
        """
        arg = buffer_argument(buffer, c_int16, bufferLth, writable=True, name="buffer")
        self._ps5000SetDataBuffer(handle, channel, arg, bufferLth)
        self._keep_buffer((handle.value, "data", channel), arg)

    def ps5000SetDataBufferBulk(
        self,
        handle: c_int16,
        channel: PS5000_CHANNEL,
        buffer: DataBuffer,
        bufferLth: int,
        waveform: int,
    ) -> None:
        """Like :meth:`ps5000SetDataBuffer`, for one ``waveform`` in rapid block mode.

        The wrapper keeps one buffer per channel and waveform.
        """
        arg = buffer_argument(buffer, c_int16, bufferLth, writable=True, name="buffer")
        self._ps5000SetDataBufferBulk(handle, channel, arg, bufferLth, waveform)
        self._keep_buffer((handle.value, "bulk", channel, waveform), arg)

    def ps5000SetEtsTimeBuffer(
        self, handle: c_int16, buffer: DataBuffer, bufferLth: int
    ) -> None:
        """Set the buffer the driver writes the ETS sample times to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int64 elements, or None. The wrapper keeps it from being freed or
        resized until it is replaced (also by :meth:`ps5000SetEtsTimeBuffers`),
        set to None or the unit is closed. A raw address (int or ``c_void_p``)
        is passed unchecked and must be kept valid by the caller.
        """
        arg = buffer_argument(buffer, c_int64, bufferLth, writable=True, name="buffer")
        self._ps5000SetEtsTimeBuffer(handle, arg, bufferLth)
        self._keep_buffer((handle.value, "ets"), arg)

    def ps5000SetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: DataBuffer,
        timeLower: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Like :meth:`ps5000SetEtsTimeBuffer`, with uint32 buffers for the upper
        and lower 32 bits of the times."""
        argUpper = buffer_argument(
            timeUpper, c_uint32, bufferLth, writable=True, name="timeUpper"
        )
        argLower = buffer_argument(
            timeLower, c_uint32, bufferLth, writable=True, name="timeLower"
        )
        self._ps5000SetEtsTimeBuffers(handle, argUpper, argLower, bufferLth)
        both = None if argUpper is None and argLower is None else (argUpper, argLower)
        self._keep_buffer((handle.value, "ets"), both)

    def ps5000IsReady(self, handle: c_int16) -> bool:
        ready = c_int16(0)
        self._ps5000IsReady(handle, byref(ready))
        return ready.value != 0

    def ps5000RunBlock(
        self,
        handle: c_int16,
        noOfPreTriggerSamples: int,
        noOfPostTriggerSamples: int,
        timebase: int,
        oversample: int,
        segmentIndex: int,
        callback: Callable[[int, PICO_STATUS], None] | None,
    ) -> int:
        """``callback(handle, status)`` is called when the block is ready."""
        assert noOfPreTriggerSamples >= 0
        assert noOfPostTriggerSamples >= 0
        assert oversample >= 0 and oversample <= PS5000_MAX_OVERSAMPLE_8BIT
        timeIndisposedMs = c_int32(0)
        lpReady = ps5000BlockReady()  # NULL; ctypes rejects None here
        if callback is not None:

            def cbwrapper(handle: int, status: int, _: c_void_p) -> None:
                callback(handle, PICO_STATUS(status))

            lpReady = ps5000BlockReady(cbwrapper)
        self._with_callback(
            self._callback_key("ps5000RunBlock", handle),
            lpReady,
            lambda: self._ps5000RunBlock(
                handle,
                noOfPreTriggerSamples,
                noOfPostTriggerSamples,
                timebase,
                oversample,
                byref(timeIndisposedMs),
                segmentIndex,
                lpReady,
                None,
            ),
        )
        return timeIndisposedMs.value

    def ps5000RunStreaming(
        self,
        handle: c_int16,
        sampleInterval: int,
        sampleIntervalTimeUnits: PS5000_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostPreTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        overviewBufferSize: int,
    ) -> int:
        """Returns the actual sample interval; there is no downsampling mode."""
        interval = c_uint32(sampleInterval)
        self._ps5000RunStreaming(
            handle,
            byref(interval),
            sampleIntervalTimeUnits,
            maxPreTriggerSamples,
            maxPostPreTriggerSamples,
            1 if autoStop else 0,
            downSampleRatio,
            overviewBufferSize,
        )
        return interval.value

    def ps5000GetStreamingLatestValues(
        self,
        handle: c_int16,
        callback: Callable[[int, int, int, int, int, bool, bool], None],
    ) -> PICO_STATUS:
        """Callback args: handle, noOfSamples, startIndex, overflow, triggerAt,
        triggered, autoStop.

        Returns PICO_OK, or PICO_BUSY if there is no new data yet (poll again).
        """

        def cbwrapper(
            handle: int,
            noOfSamples: int,
            startIndex: int,
            overflow: int,
            triggerAt: int,
            triggered: int,
            autoStop: int,
            _: c_void_p,
        ) -> None:
            callback(
                handle,
                noOfSamples,
                startIndex,
                overflow,
                triggerAt,
                triggered != 0,
                autoStop != 0,
            )

        lpPs5000Ready = ps5000StreamingReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps5000GetStreamingLatestValues", handle),
            lpPs5000Ready,
            lambda: self._ps5000GetStreamingLatestValues(handle, lpPs5000Ready, None),
        )

    def ps5000NoOfStreamingValues(self, handle: c_int16) -> int:
        noOfValues = c_uint32(0)
        self._ps5000NoOfStreamingValues(handle, byref(noOfValues))
        return noOfValues.value

    def ps5000GetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggreatedSamples: int,
        downSampleRatioMode: PS5000_RATIO_MODE,
        segmentIndex: int,
    ) -> int:
        maxDownSampleRatio = c_uint32(0)
        self._ps5000GetMaxDownSampleRatio(
            handle,
            noOfUnaggreatedSamples,
            byref(maxDownSampleRatio),
            downSampleRatioMode,
            segmentIndex,
        )
        return maxDownSampleRatio.value

    def ps5000GetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS5000_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[int, int]:
        samples = c_uint32(noOfSamples)
        overflow = c_int16(0)
        self._ps5000GetValues(
            handle,
            startIndex,
            byref(samples),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return samples.value, overflow.value

    def ps5000GetValuesBulk(
        self,
        handle: c_int16,
        noOfSamples: int,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[int, list[int]]:
        """Returns the number of samples per segment and one overflow flag set
        per segment. There are no downsampling parameters."""
        assert noOfSamples > 0
        assert fromSegmentIndex <= toSegmentIndex
        samples = c_uint32(noOfSamples)
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        overflow = (c_int16 * nsegments)(0)
        self._ps5000GetValuesBulk(
            handle, byref(samples), fromSegmentIndex, toSegmentIndex, overflow
        )
        return samples.value, [int(f) for f in overflow]

    def ps5000GetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS5000_RATIO_MODE,
        segmentIndex: int,
        callback: Callable[[int, int, int, int, bool], None],
    ) -> None:
        """Callback args: handle, noOfSamples, overflow, triggerAt, triggered."""

        def cbwrapper(
            handle: int,
            noOfSamples: int,
            overflow: int,
            triggerAt: int,
            triggered: int,
            _: c_void_p,
        ) -> None:
            callback(handle, noOfSamples, overflow, triggerAt, triggered != 0)

        lpDataReady = ps5000DataReady(cbwrapper)
        self._with_callback(
            self._callback_key("ps5000GetValuesAsync", handle),
            lpDataReady,
            lambda: self._ps5000GetValuesAsync(
                handle,
                startIndex,
                noOfSamples,
                downSampleRatio,
                downSampleRatioMode,
                segmentIndex,
                lpDataReady,
                None,
            ),
        )

    def ps5000Stop(self, handle: c_int16) -> None:
        self._ps5000Stop(handle)

    def ps5000PingUnit(self, handle: c_int16) -> None:
        self._ps5000PingUnit(handle)

    def ps5000SetNoOfCaptures(self, handle: c_int16, nCaptures: int) -> None:
        assert nCaptures > 0
        self._ps5000SetNoOfCaptures(handle, nCaptures)


@final
class PicoScope5000Device(PicoScopeDeviceBase[PicoScope5000Wrapper]):
    """An opened ps5000 unit; the functions of :class:`PicoScope5000Wrapper` with its handle.

    See :class:`~pycosdk.PicoScopeDeviceBase`.
    """

    _wrapper_type = PicoScope5000Wrapper

    @classmethod
    def ps5000OpenUnit(cls) -> Self:
        """Like :meth:`PicoScope5000Wrapper.ps5000OpenUnit`, returning a device instead of the handle."""
        return cls(cls.shared_wrapper().ps5000OpenUnit())

    @classmethod
    def ps5000OpenUnitProgress(cls) -> tuple[Self | None, int, bool]:
        """Like :meth:`PicoScope5000Wrapper.ps5000OpenUnitProgress`, with a device instead of the handle once opened."""
        handle, progressPercent, complete = (
            cls.shared_wrapper().ps5000OpenUnitProgress()
        )
        return cls(handle) if complete else None, progressPercent, complete

    ps5000OpenUnitAsync = wrapper_function(PicoScope5000Wrapper.ps5000OpenUnitAsync)

    ps5000CloseUnit = handle_method(PicoScope5000Wrapper.ps5000CloseUnit, closes=True)
    ps5000GetUnitInfo = handle_method(PicoScope5000Wrapper.ps5000GetUnitInfo)
    ps5000FlashLed = handle_method(PicoScope5000Wrapper.ps5000FlashLed)
    ps5000IsLedFlashing = handle_method(PicoScope5000Wrapper.ps5000IsLedFlashing)
    ps5000MemorySegments = handle_method(PicoScope5000Wrapper.ps5000MemorySegments)
    ps5000SetChannel = handle_method(PicoScope5000Wrapper.ps5000SetChannel)
    ps5000GetTimebase = handle_method(PicoScope5000Wrapper.ps5000GetTimebase)
    ps5000GetTimebase2 = handle_method(PicoScope5000Wrapper.ps5000GetTimebase2)
    ps5000SetSigGenArbitrary = handle_method(
        PicoScope5000Wrapper.ps5000SetSigGenArbitrary
    )
    ps5000SetSigGenBuiltIn = handle_method(PicoScope5000Wrapper.ps5000SetSigGenBuiltIn)
    ps5000SetSigGenBuiltInV2 = handle_method(
        PicoScope5000Wrapper.ps5000SetSigGenBuiltInV2
    )
    ps5000SigGenFrequencyToPhase = handle_method(
        PicoScope5000Wrapper.ps5000SigGenFrequencyToPhase
    )
    ps5000SigGenArbitraryMinMaxValues = handle_method(
        PicoScope5000Wrapper.ps5000SigGenArbitraryMinMaxValues
    )
    ps5000SigGenSoftwareControl = handle_method(
        PicoScope5000Wrapper.ps5000SigGenSoftwareControl
    )
    ps5000SetEts = handle_method(PicoScope5000Wrapper.ps5000SetEts)
    ps5000SetTriggerChannelProperties = handle_method(
        PicoScope5000Wrapper.ps5000SetTriggerChannelProperties
    )
    ps5000SetTriggerChannelConditions = handle_method(
        PicoScope5000Wrapper.ps5000SetTriggerChannelConditions
    )
    ps5000SetTriggerChannelDirections = handle_method(
        PicoScope5000Wrapper.ps5000SetTriggerChannelDirections
    )
    ps5000SetSimpleTrigger = handle_method(PicoScope5000Wrapper.ps5000SetSimpleTrigger)
    ps5000SetTriggerDelay = handle_method(PicoScope5000Wrapper.ps5000SetTriggerDelay)
    ps5000SetPulseWidthQualifier = handle_method(
        PicoScope5000Wrapper.ps5000SetPulseWidthQualifier
    )
    ps5000IsTriggerOrPulseWidthQualifierEnabled = handle_method(
        PicoScope5000Wrapper.ps5000IsTriggerOrPulseWidthQualifierEnabled
    )
    ps5000GetTriggerTimeOffset = handle_method(
        PicoScope5000Wrapper.ps5000GetTriggerTimeOffset
    )
    ps5000GetTriggerTimeOffset64 = handle_method(
        PicoScope5000Wrapper.ps5000GetTriggerTimeOffset64
    )
    ps5000GetValuesTriggerTimeOffsetBulk = handle_method(
        PicoScope5000Wrapper.ps5000GetValuesTriggerTimeOffsetBulk
    )
    ps5000GetValuesTriggerTimeOffsetBulk64 = handle_method(
        PicoScope5000Wrapper.ps5000GetValuesTriggerTimeOffsetBulk64
    )
    ps5000SetDataBuffers = handle_method(PicoScope5000Wrapper.ps5000SetDataBuffers)
    ps5000SetDataBuffer = handle_method(PicoScope5000Wrapper.ps5000SetDataBuffer)
    ps5000SetDataBufferBulk = handle_method(
        PicoScope5000Wrapper.ps5000SetDataBufferBulk
    )
    ps5000SetEtsTimeBuffer = handle_method(PicoScope5000Wrapper.ps5000SetEtsTimeBuffer)
    ps5000SetEtsTimeBuffers = handle_method(
        PicoScope5000Wrapper.ps5000SetEtsTimeBuffers
    )
    ps5000IsReady = handle_method(PicoScope5000Wrapper.ps5000IsReady)
    ps5000RunBlock = handle_method(PicoScope5000Wrapper.ps5000RunBlock)
    ps5000RunStreaming = handle_method(PicoScope5000Wrapper.ps5000RunStreaming)
    ps5000GetStreamingLatestValues = handle_method(
        PicoScope5000Wrapper.ps5000GetStreamingLatestValues
    )
    ps5000NoOfStreamingValues = handle_method(
        PicoScope5000Wrapper.ps5000NoOfStreamingValues
    )
    ps5000GetMaxDownSampleRatio = handle_method(
        PicoScope5000Wrapper.ps5000GetMaxDownSampleRatio
    )
    ps5000GetValues = handle_method(PicoScope5000Wrapper.ps5000GetValues)
    ps5000GetValuesBulk = handle_method(PicoScope5000Wrapper.ps5000GetValuesBulk)
    ps5000GetValuesAsync = handle_method(PicoScope5000Wrapper.ps5000GetValuesAsync)
    ps5000Stop = handle_method(PicoScope5000Wrapper.ps5000Stop)
    ps5000PingUnit = handle_method(PicoScope5000Wrapper.ps5000PingUnit)
    ps5000SetNoOfCaptures = handle_method(PicoScope5000Wrapper.ps5000SetNoOfCaptures)


__all__ = (
    "PS5000_CHANNEL",
    "PS5000_CHANNEL_BUFFER_INDEX",
    "PS5000_CHANNEL_INFO",
    "PS5000_ETS_MODE",
    "PS5000_EXT_MAX_VALUE",
    "PS5000_EXT_MIN_VALUE",
    "PS5000_GAUSSIAN_MAX_FREQUENCY",
    "PS5000_HALF_SINE_MAX_FREQUENCY",
    "PS5000_INDEX_MODE",
    "PS5000_LOST_DATA",
    "PS5000_MAX_DELAY_COUNT",
    "PS5000_MAX_OVERSAMPLE_8BIT",
    "PS5000_MAX_PULSE_WIDTH_QUALIFIER_COUNT",
    "PS5000_MAX_SIG_GEN_BUFFER_SIZE",
    "PS5000_MAX_SWEEPS_SHOTS",
    "PS5000_MAX_VALUE",
    "PS5000_MIN_DWELL_COUNT",
    "PS5000_MIN_FREQUENCY",
    "PS5000_MIN_SIG_GEN_BUFFER_SIZE",
    "PS5000_MIN_VALUE",
    "PS5000_PULSE_WIDTH_TYPE",
    "PS5000_PWQ_CONDITIONS",
    "PS5000_RAMP_MAX_FREQUENCY",
    "PS5000_RANGE",
    "PS5000_RATIO_MODE",
    "PS5000_SIGGEN_TRIG_SOURCE",
    "PS5000_SIGGEN_TRIG_TYPE",
    "PS5000_SINC_MAX_FREQUENCY",
    "PS5000_SINE_MAX_FREQUENCY",
    "PS5000_SQUARE_MAX_FREQUENCY",
    "PS5000_SWEEP_TYPE",
    "PS5000_THRESHOLD_DIRECTION",
    "PS5000_THRESHOLD_MODE",
    "PS5000_TIME_UNITS",
    "PS5000_TRIANGLE_MAX_FREQUENCY",
    "PS5000_TRIGGER_CHANNEL_PROPERTIES",
    "PS5000_TRIGGER_CONDITIONS",
    "PS5000_TRIGGER_STATE",
    "PS5000_WAVE_TYPE",
    "PicoScope5000Wrapper",
    "PicoScope5000Device",
    "ps5000BlockReady",
    "ps5000DataReady",
    "ps5000StreamingReady",
)
