# pyright: reportAny=false, reportUnannotatedClassAttribute=false
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
    c_int64,
    c_uint16,
    c_uint32,
    c_void_p,
    create_string_buffer,
)
from enum import IntEnum
from typing import Self, final

from ._device import PicoScopeDeviceBase, handle_method, wrapper_function
from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase
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
class PS5000_TRIGGER_CONDITIONS(Structure):
    # C: TRIGGER_CONDITIONS
    _pack_ = 1
    _fields_ = [
        ("channelA", PS5000_TRIGGER_STATE_T),
        ("channelB", PS5000_TRIGGER_STATE_T),
        ("channelC", PS5000_TRIGGER_STATE_T),
        ("channelD", PS5000_TRIGGER_STATE_T),
        ("external", PS5000_TRIGGER_STATE_T),
        ("aux", PS5000_TRIGGER_STATE_T),
        ("pulseWidthQualifier", PS5000_TRIGGER_STATE_T),
    ]


@final
class PS5000_PWQ_CONDITIONS(Structure):
    # C: PWQ_CONDITIONS
    _pack_ = 1
    _fields_ = [
        ("channelA", PS5000_TRIGGER_STATE_T),
        ("channelB", PS5000_TRIGGER_STATE_T),
        ("channelC", PS5000_TRIGGER_STATE_T),
        ("channelD", PS5000_TRIGGER_STATE_T),
        ("external", PS5000_TRIGGER_STATE_T),
        ("aux", PS5000_TRIGGER_STATE_T),
    ]


@final
class PS5000_TRIGGER_CHANNEL_PROPERTIES(Structure):
    # C: TRIGGER_CHANNEL_PROPERTIES. Unlike later drivers, there is a single
    # hysteresis shared by both thresholds.
    _pack_ = 1
    _fields_ = [
        ("thresholdMajor", c_int16),
        ("thresholdMinor", c_int16),
        ("hysteresis", c_uint16),
        ("channel", PS5000_CHANNEL_T),
        ("thresholdMode", PS5000_THRESHOLD_MODE_T),
    ]


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
                POINTER(PS5000_TRIGGER_CHANNEL_PROPERTIES),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps5000SetTriggerChannelConditions = self._bind(
            "ps5000SetTriggerChannelConditions",
            [c_int16, POINTER(PS5000_TRIGGER_CONDITIONS), c_int16],
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
                POINTER(PS5000_PWQ_CONDITIONS),
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

    def ps5000OpenUnit(self) -> tuple[PICO_STATUS, c_int16]:
        """Open the first unit found; the driver has no serial selection."""
        handle = c_int16(0)
        return self._ps5000OpenUnit(byref(handle)), handle

    def ps5000OpenUnitAsync(self) -> tuple[PICO_STATUS, bool]:
        """Start opening a unit; the flag tells whether the operation started."""
        started = c_int16(0)
        status = self._ps5000OpenUnitAsync(byref(started))
        return status, started.value == 1

    def ps5000OpenUnitProgress(self) -> tuple[PICO_STATUS, c_int16, int, bool]:
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        status = self._ps5000OpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return status, handle, progressPercent.value, complete.value != 0

    def ps5000CloseUnit(self, handle: c_int16) -> PICO_STATUS:
        return self._ps5000CloseUnit(handle)

    def ps5000GetUnitInfo(
        self, handle: c_int16, info: PICO_INFO
    ) -> tuple[PICO_STATUS, str]:
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._ps5000GetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return status, infostr

    def ps5000FlashLed(self, handle: c_int16, start: int) -> PICO_STATUS:
        """Flash the LED ``start`` times; -1 flashes indefinitely, 0 stops."""
        return self._ps5000FlashLed(handle, start)

    def ps5000IsLedFlashing(self, handle: c_int16) -> tuple[PICO_STATUS, bool]:
        flashing = c_int16(0)
        status = self._ps5000IsLedFlashing(handle, byref(flashing))
        return status, flashing.value != 0

    def ps5000MemorySegments(
        self, handle: c_int16, nSegments: int
    ) -> tuple[PICO_STATUS, int]:
        assert nSegments > 0
        nMaxSamples = c_int32(0)
        return (
            self._ps5000MemorySegments(handle, nSegments, byref(nMaxSamples)),
            nMaxSamples.value,
        )

    def ps5000SetChannel(
        self,
        handle: c_int16,
        channel: PS5000_CHANNEL,
        enabled: bool,
        dc: bool,
        range: PS5000_RANGE,
    ) -> PICO_STATUS:
        """``dc`` selects DC coupling, otherwise AC."""
        return self._ps5000SetChannel(
            handle, channel, 1 if enabled else 0, 1 if dc else 0, range
        )

    def ps5000GetTimebase(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        oversample: int,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_int32(0)
        status = self._ps5000GetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return status, timeIntervalNanoseconds.value, maxSamples.value

    def ps5000GetTimebase2(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        oversample: int,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, float, int]:
        assert oversample >= 0 and oversample <= PS5000_MAX_OVERSAMPLE_8BIT
        timeIntervalNanoseconds = c_float(0)
        maxSamples = c_int32(0)
        status = self._ps5000GetTimebase2(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return status, timeIntervalNanoseconds.value, maxSamples.value

    def ps5000SetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: Sequence[int],
        sweepType: PS5000_SWEEP_TYPE,
        whiteNoise: bool,
        indexMode: PS5000_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS5000_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        waveform = (c_int16 * len(arbitraryWaveform))(*arbitraryWaveform)
        return self._ps5000SetSigGenArbitrary(
            handle,
            offsetVoltage,
            pkToPk,
            startDeltaPhase,
            stopDeltaPhase,
            deltaPhaseIncrement,
            dwellCount,
            waveform,
            len(arbitraryWaveform),
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
    ) -> PICO_STATUS:
        return self._ps5000SetSigGenBuiltIn(
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
    ) -> PICO_STATUS:
        return self._ps5000SetSigGenBuiltInV2(
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
    ) -> tuple[PICO_STATUS, int]:
        phase = c_uint32(0)
        status = self._ps5000SigGenFrequencyToPhase(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return status, phase.value

    def ps5000SigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, int, int, int, int]:
        minValue = c_int16(0)
        maxValue = c_int16(0)
        minSize = c_uint32(0)
        maxSize = c_uint32(0)
        status = self._ps5000SigGenArbitraryMinMaxValues(
            handle, byref(minValue), byref(maxValue), byref(minSize), byref(maxSize)
        )
        return status, minValue.value, maxValue.value, minSize.value, maxSize.value

    def ps5000SigGenSoftwareControl(self, handle: c_int16, state: bool) -> PICO_STATUS:
        return self._ps5000SigGenSoftwareControl(handle, 1 if state else 0)

    def ps5000SetEts(
        self,
        handle: c_int16,
        mode: PS5000_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> tuple[PICO_STATUS, int]:
        sampleTimePicoseconds = c_int32(0)
        status = self._ps5000SetEts(
            handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
        )
        return status, sampleTimePicoseconds.value

    def ps5000SetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS5000_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> PICO_STATUS:
        n = len(channelProperties)
        properties = (PS5000_TRIGGER_CHANNEL_PROPERTIES * n)(*channelProperties)
        return self._ps5000SetTriggerChannelProperties(
            handle,
            properties if n else None,
            n,
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps5000SetTriggerChannelConditions(
        self, handle: c_int16, conditions: Sequence[PS5000_TRIGGER_CONDITIONS]
    ) -> PICO_STATUS:
        n = len(conditions)
        conds = (PS5000_TRIGGER_CONDITIONS * n)(*conditions)
        return self._ps5000SetTriggerChannelConditions(handle, conds if n else None, n)

    def ps5000SetTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: PS5000_THRESHOLD_DIRECTION,
        channelB: PS5000_THRESHOLD_DIRECTION,
        channelC: PS5000_THRESHOLD_DIRECTION,
        channelD: PS5000_THRESHOLD_DIRECTION,
        ext: PS5000_THRESHOLD_DIRECTION,
        aux: PS5000_THRESHOLD_DIRECTION,
    ) -> PICO_STATUS:
        return self._ps5000SetTriggerChannelDirections(
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
    ) -> PICO_STATUS:
        assert autoTrigger_ms >= 0
        return self._ps5000SetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTrigger_ms,
        )

    def ps5000SetTriggerDelay(self, handle: c_int16, delay: int) -> PICO_STATUS:
        return self._ps5000SetTriggerDelay(handle, delay)

    def ps5000SetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS5000_PWQ_CONDITIONS],
        direction: PS5000_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS5000_PULSE_WIDTH_TYPE,
    ) -> PICO_STATUS:
        n = len(conditions)
        conds = (PS5000_PWQ_CONDITIONS * n)(*conditions)
        return self._ps5000SetPulseWidthQualifier(
            handle, conds if n else None, n, direction, lower, upper, type
        )

    def ps5000IsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        status = self._ps5000IsTriggerOrPulseWidthQualifierEnabled(
            handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
        )
        return (
            status,
            triggerEnabled.value != 0,
            pulseWidthQualifierEnabled.value != 0,
        )

    def ps5000GetTriggerTimeOffset(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, int, PS5000_TIME_UNITS]:
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS5000_TIME_UNITS_T(0)
        status = self._ps5000GetTriggerTimeOffset(
            handle, byref(timeUpper), byref(timeLower), byref(timeUnits), segmentIndex
        )
        return (
            status,
            timeUpper.value,
            timeLower.value,
            PS5000_TIME_UNITS(timeUnits.value),
        )

    def ps5000GetTriggerTimeOffset64(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, PS5000_TIME_UNITS]:
        time = c_int64(0)
        timeUnits = PS5000_TIME_UNITS_T(0)
        status = self._ps5000GetTriggerTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return status, time.value, PS5000_TIME_UNITS(timeUnits.value)

    def ps5000GetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[int], list[PS5000_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        n = toSegmentIndex - fromSegmentIndex + 1
        timesUpper = (c_uint32 * n)()
        timesLower = (c_uint32 * n)()
        timeUnits = (PS5000_TIME_UNITS_T * n)()
        status = self._ps5000GetValuesTriggerTimeOffsetBulk(
            handle, timesUpper, timesLower, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return (
            status,
            list(timesUpper),
            list(timesLower),
            [PS5000_TIME_UNITS(u) for u in timeUnits],
        )

    def ps5000GetValuesTriggerTimeOffsetBulk64(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[PS5000_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        n = toSegmentIndex - fromSegmentIndex + 1
        times = (c_int64 * n)()
        timeUnits = (PS5000_TIME_UNITS_T * n)()
        status = self._ps5000GetValuesTriggerTimeOffsetBulk64(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return status, list(times), [PS5000_TIME_UNITS(u) for u in timeUnits]

    def ps5000SetDataBuffers(
        self,
        handle: c_int16,
        channel: PS5000_CHANNEL,
        bufferMax: c_void_p | int | None,
        bufferMin: c_void_p | int | None,
        bufferLth: int,
    ) -> PICO_STATUS:
        """The buffers hold ``int16_t`` values and must outlive the capture."""
        return self._ps5000SetDataBuffers(
            handle, channel, bufferMax, bufferMin, bufferLth
        )

    def ps5000SetDataBuffer(
        self,
        handle: c_int16,
        channel: PS5000_CHANNEL,
        buffer: c_void_p | int | None,
        bufferLth: int,
    ) -> PICO_STATUS:
        """``buffer`` holds ``int16_t`` values and must outlive the capture."""
        return self._ps5000SetDataBuffer(handle, channel, buffer, bufferLth)

    def ps5000SetDataBufferBulk(
        self,
        handle: c_int16,
        channel: PS5000_CHANNEL,
        buffer: c_void_p | int | None,
        bufferLth: int,
        waveform: int,
    ) -> PICO_STATUS:
        """``buffer`` holds ``int16_t`` values and must outlive the capture."""
        return self._ps5000SetDataBufferBulk(
            handle, channel, buffer, bufferLth, waveform
        )

    def ps5000SetEtsTimeBuffer(
        self, handle: c_int16, buffer: c_void_p | int | None, bufferLth: int
    ) -> PICO_STATUS:
        """``buffer`` must hold ``bufferLth`` int64 values and outlive the capture."""
        return self._ps5000SetEtsTimeBuffer(handle, buffer, bufferLth)

    def ps5000SetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: c_void_p | int | None,
        timeLower: c_void_p | int | None,
        bufferLth: int,
    ) -> PICO_STATUS:
        """The buffers must hold ``bufferLth`` uint32 values and outlive the capture."""
        return self._ps5000SetEtsTimeBuffers(handle, timeUpper, timeLower, bufferLth)

    def ps5000IsReady(self, handle: c_int16) -> tuple[PICO_STATUS, bool]:
        ready = c_int16(0)
        return self._ps5000IsReady(handle, byref(ready)), ready.value == 1

    def ps5000RunBlock(
        self,
        handle: c_int16,
        noOfPreTriggerSamples: int,
        noOfPostTriggerSamples: int,
        timebase: int,
        oversample: int,
        segmentIndex: int,
        callback: Callable[[int, PICO_STATUS], None] | None,
    ) -> tuple[PICO_STATUS, int]:
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
        status = self._with_callback(
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
        return status, timeIndisposedMs.value

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
    ) -> tuple[PICO_STATUS, int]:
        """Returns the actual sample interval; there is no downsampling mode."""
        interval = c_uint32(sampleInterval)
        status = self._ps5000RunStreaming(
            handle,
            byref(interval),
            sampleIntervalTimeUnits,
            maxPreTriggerSamples,
            maxPostPreTriggerSamples,
            1 if autoStop else 0,
            downSampleRatio,
            overviewBufferSize,
        )
        return status, interval.value

    def ps5000GetStreamingLatestValues(
        self,
        handle: c_int16,
        callback: Callable[[int, int, int, int, int, bool, bool], None],
    ) -> PICO_STATUS:
        """Callback args: handle, noOfSamples, startIndex, overflow, triggerAt,
        triggered, autoStop."""

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

    def ps5000NoOfStreamingValues(self, handle: c_int16) -> tuple[PICO_STATUS, int]:
        noOfValues = c_uint32(0)
        status = self._ps5000NoOfStreamingValues(handle, byref(noOfValues))
        return status, noOfValues.value

    def ps5000GetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggreatedSamples: int,
        downSampleRatioMode: PS5000_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int]:
        maxDownSampleRatio = c_uint32(0)
        status = self._ps5000GetMaxDownSampleRatio(
            handle,
            noOfUnaggreatedSamples,
            byref(maxDownSampleRatio),
            downSampleRatioMode,
            segmentIndex,
        )
        return status, maxDownSampleRatio.value

    def ps5000GetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS5000_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int, int]:
        samples = c_uint32(noOfSamples)
        overflow = c_int16(0)
        status = self._ps5000GetValues(
            handle,
            startIndex,
            byref(samples),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return status, samples.value, overflow.value

    def ps5000GetValuesBulk(
        self,
        handle: c_int16,
        noOfSamples: int,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[PICO_STATUS, int, list[int]]:
        """Returns the number of samples per segment and one overflow flag set
        per segment. There are no downsampling parameters."""
        assert noOfSamples > 0
        assert fromSegmentIndex <= toSegmentIndex
        samples = c_uint32(noOfSamples)
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        overflow = (c_int16 * nsegments)(0)
        status = self._ps5000GetValuesBulk(
            handle, byref(samples), fromSegmentIndex, toSegmentIndex, overflow
        )
        return status, samples.value, [int(f) for f in overflow]

    def ps5000GetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS5000_RATIO_MODE,
        segmentIndex: int,
        callback: Callable[[int, int, int, int, bool], None],
    ) -> PICO_STATUS:
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
        return self._with_callback(
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

    def ps5000Stop(self, handle: c_int16) -> PICO_STATUS:
        return self._ps5000Stop(handle)

    def ps5000PingUnit(self, handle: c_int16) -> PICO_STATUS:
        return self._ps5000PingUnit(handle)

    def ps5000SetNoOfCaptures(self, handle: c_int16, nCaptures: int) -> PICO_STATUS:
        assert nCaptures > 0
        return self._ps5000SetNoOfCaptures(handle, nCaptures)


@final
class PicoScope5000Device(PicoScopeDeviceBase[PicoScope5000Wrapper]):
    """An opened ps5000 unit; the functions of :class:`PicoScope5000Wrapper` with its handle.

    See :class:`~pycosdk.PicoScopeDeviceBase`.
    """

    _wrapper_type = PicoScope5000Wrapper

    @classmethod
    def ps5000OpenUnit(cls) -> tuple[PICO_STATUS, Self]:
        """Like :meth:`PicoScope5000Wrapper.ps5000OpenUnit`, returning a device instead of the handle."""
        status, handle = cls.shared_wrapper().ps5000OpenUnit()
        return status, cls(handle)

    @classmethod
    def ps5000OpenUnitProgress(cls) -> tuple[PICO_STATUS, Self | None, int, bool]:
        """Like :meth:`PicoScope5000Wrapper.ps5000OpenUnitProgress`, with a device instead of the handle once opened."""
        status, handle, progressPercent, complete = (
            cls.shared_wrapper().ps5000OpenUnitProgress()
        )
        return status, cls(handle) if complete else None, progressPercent, complete

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
