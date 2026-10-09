# pyright: reportAny=false, reportUnannotatedClassAttribute=false
from collections.abc import Callable, Sequence
from ctypes import (
    POINTER,
    Array,
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
    c_uint64,
    c_void_p,
    create_string_buffer,
)
from enum import IntEnum
from typing import final

from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T

PS6000_MAX_OVERSAMPLE_8BIT = 256

PS6000_MAX_VALUE = 32512
PS6000_MIN_VALUE = -32512

PS6000_MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215

PS6000_MAX_SIG_GEN_BUFFER_SIZE = 16384
PS640X_C_D_MAX_SIG_GEN_BUFFER_SIZE = 65536

PS6000_MIN_SIG_GEN_BUFFER_SIZE = 1
PS6000_MIN_DWELL_COUNT = 3
PS6000_MAX_SWEEPS_SHOTS = (1 << 30) - 1

PS6000_MAX_WAVEFORMS_PER_SECOND = 1000000

PS6000_MAX_ANALOGUE_OFFSET_50MV_200MV = 0.500
PS6000_MIN_ANALOGUE_OFFSET_50MV_200MV = -0.500
PS6000_MAX_ANALOGUE_OFFSET_500MV_2V = 2.500
PS6000_MIN_ANALOGUE_OFFSET_500MV_2V = -2.500
PS6000_MAX_ANALOGUE_OFFSET_5V_20V = 20.0
PS6000_MIN_ANALOGUE_OFFSET_5V_20V = -20.0

PS6000_MAX_ETS_CYCLES = 250
PS6000_MAX_INTERLEAVE = 50


class PS6000_EXTERNAL_FREQUENCY(IntEnum):
    PS6000_FREQUENCY_OFF = 0
    PS6000_FREQUENCY_5MHZ = 1
    PS6000_FREQUENCY_10MHZ = 2
    PS6000_FREQUENCY_20MHZ = 3
    PS6000_FREQUENCY_25MHZ = 4
    PS6000_MAX_FREQUENCIES = 5


PS6000_EXTERNAL_FREQUENCY_T = c_int32


class PS6000_BANDWIDTH_LIMITER(IntEnum):
    PS6000_BW_FULL = 0
    PS6000_BW_20MHZ = 1
    PS6000_BW_25MHZ = 2


PS6000_BANDWIDTH_LIMITER_T = c_int32


class PS6000_CHANNEL(IntEnum):
    PS6000_CHANNEL_A = 0
    PS6000_CHANNEL_B = 1
    PS6000_CHANNEL_C = 2
    PS6000_CHANNEL_D = 3
    PS6000_EXTERNAL = 4
    PS6000_MAX_CHANNELS = PS6000_EXTERNAL
    PS6000_TRIGGER_AUX = 5
    PS6000_MAX_TRIGGER_SOURCES = 6


PS6000_CHANNEL_T = c_int32


class PS6000_CHANNEL_BUFFER_INDEX(IntEnum):
    PS6000_CHANNEL_A_MAX = 0
    PS6000_CHANNEL_A_MIN = 1
    PS6000_CHANNEL_B_MAX = 2
    PS6000_CHANNEL_B_MIN = 3
    PS6000_CHANNEL_C_MAX = 4
    PS6000_CHANNEL_C_MIN = 5
    PS6000_CHANNEL_D_MAX = 6
    PS6000_CHANNEL_D_MIN = 7
    PS6000_MAX_CHANNEL_BUFFERS = 8


class PS6000_RANGE(IntEnum):
    PS6000_10MV = 0
    PS6000_20MV = 1
    PS6000_50MV = 2
    PS6000_100MV = 3
    PS6000_200MV = 4
    PS6000_500MV = 5
    PS6000_1V = 6
    PS6000_2V = 7
    PS6000_5V = 8
    PS6000_10V = 9
    PS6000_20V = 10
    PS6000_50V = 11
    PS6000_MAX_RANGES = 12


PS6000_RANGE_T = c_int32


class PS6000_COUPLING(IntEnum):
    PS6000_AC = 0
    PS6000_DC_1M = 1
    PS6000_DC_50R = 2


PS6000_COUPLING_T = c_int32


class PS6000_ETS_MODE(IntEnum):
    PS6000_ETS_OFF = 0
    PS6000_ETS_FAST = 1
    PS6000_ETS_SLOW = 2
    PS6000_ETS_MODES_MAX = 3


PS6000_ETS_MODE_T = c_int32


class PS6000_TIME_UNITS(IntEnum):
    PS6000_FS = 0
    PS6000_PS = 1
    PS6000_NS = 2
    PS6000_US = 3
    PS6000_MS = 4
    PS6000_S = 5
    PS6000_MAX_TIME_UNITS = 6


PS6000_TIME_UNITS_T = c_int32


class PS6000_SWEEP_TYPE(IntEnum):
    PS6000_UP = 0
    PS6000_DOWN = 1
    PS6000_UPDOWN = 2
    PS6000_DOWNUP = 3
    PS6000_MAX_SWEEP_TYPES = 4


PS6000_SWEEP_TYPE_T = c_int32


class PS6000_WAVE_TYPE(IntEnum):
    PS6000_SINE = 0
    PS6000_SQUARE = 1
    PS6000_TRIANGLE = 2
    PS6000_RAMP_UP = 3
    PS6000_RAMP_DOWN = 4
    PS6000_SINC = 5
    PS6000_GAUSSIAN = 6
    PS6000_HALF_SINE = 7
    PS6000_DC_VOLTAGE = 8
    PS6000_MAX_WAVE_TYPES = 9


PS6000_WAVE_TYPE_T = c_int32


class PS6000_EXTRA_OPERATIONS(IntEnum):
    PS6000_ES_OFF = 0
    PS6000_WHITENOISE = 1
    PS6000_PRBS = 2


PS6000_EXTRA_OPERATIONS_T = c_int32


PS6000_PRBS_MAX_FREQUENCY = 20000000.0
PS6000_SINE_MAX_FREQUENCY = 20000000.0
PS6000_SQUARE_MAX_FREQUENCY = 20000000.0
PS6000_TRIANGLE_MAX_FREQUENCY = 20000000.0
PS6000_SINC_MAX_FREQUENCY = 20000000.0
PS6000_RAMP_MAX_FREQUENCY = 20000000.0
PS6000_HALF_SINE_MAX_FREQUENCY = 20000000.0
PS6000_GAUSSIAN_MAX_FREQUENCY = 20000000.0
PS6000_MIN_FREQUENCY = 0.03


class PS6000_SIGGEN_TRIG_TYPE(IntEnum):
    PS6000_SIGGEN_RISING = 0
    PS6000_SIGGEN_FALLING = 1
    PS6000_SIGGEN_GATE_HIGH = 2
    PS6000_SIGGEN_GATE_LOW = 3


PS6000_SIGGEN_TRIG_TYPE_T = c_int32


class PS6000_SIGGEN_TRIG_SOURCE(IntEnum):
    PS6000_SIGGEN_NONE = 0
    PS6000_SIGGEN_SCOPE_TRIG = 1
    PS6000_SIGGEN_AUX_IN = 2
    PS6000_SIGGEN_EXT_IN = 3
    PS6000_SIGGEN_SOFT_TRIG = 4
    PS6000_SIGGEN_TRIGGER_RAW = 5


PS6000_SIGGEN_TRIG_SOURCE_T = c_int32


class PS6000_INDEX_MODE(IntEnum):
    PS6000_SINGLE = 0
    PS6000_DUAL = 1
    PS6000_QUAD = 2
    PS6000_MAX_INDEX_MODES = 3


PS6000_INDEX_MODE_T = c_int32


class PS6000_THRESHOLD_MODE(IntEnum):
    PS6000_LEVEL = 0
    PS6000_WINDOW = 1


PS6000_THRESHOLD_MODE_T = c_int32


class PS6000_THRESHOLD_DIRECTION(IntEnum):
    PS6000_ABOVE = 0
    PS6000_BELOW = 1
    PS6000_RISING = 2
    PS6000_FALLING = 3
    PS6000_RISING_OR_FALLING = 4
    PS6000_ABOVE_LOWER = 5
    PS6000_BELOW_LOWER = 6
    PS6000_RISING_LOWER = 7
    PS6000_FALLING_LOWER = 8
    PS6000_INSIDE = PS6000_ABOVE
    PS6000_OUTSIDE = PS6000_BELOW
    PS6000_ENTER = PS6000_RISING
    PS6000_EXIT = PS6000_FALLING
    PS6000_ENTER_OR_EXIT = PS6000_RISING_OR_FALLING
    PS6000_POSITIVE_RUNT = 9
    PS6000_NEGATIVE_RUNT = 10
    PS6000_NONE = PS6000_RISING


PS6000_THRESHOLD_DIRECTION_T = c_int32


class PS6000_TRIGGER_STATE(IntEnum):
    PS6000_CONDITION_DONT_CARE = 0
    PS6000_CONDITION_TRUE = 1
    PS6000_CONDITION_FALSE = 2
    PS6000_CONDITION_MAX = 3


PS6000_TRIGGER_STATE_T = c_int32


class PS6000_RATIO_MODE(IntEnum):
    PS6000_RATIO_MODE_NONE = 0
    PS6000_RATIO_MODE_AGGREGATE = 1
    PS6000_RATIO_MODE_AVERAGE = 2
    PS6000_RATIO_MODE_DECIMATE = 4
    PS6000_RATIO_MODE_DISTRIBUTION = 8


PS6000_RATIO_MODE_T = c_int32


class PS6000_PULSE_WIDTH_TYPE(IntEnum):
    PS6000_PW_TYPE_NONE = 0
    PS6000_PW_TYPE_LESS_THAN = 1
    PS6000_PW_TYPE_GREATER_THAN = 2
    PS6000_PW_TYPE_IN_RANGE = 3
    PS6000_PW_TYPE_OUT_OF_RANGE = 4


PS6000_PULSE_WIDTH_TYPE_T = c_int32


class PS6000_TEMPERATURES(IntEnum):
    PS6000_WHAT_ARE_AVAILABLE = 0
    PS6000_INTERNAL_TEMPERATURE = 1


PS6000_TEMPERATURES_T = c_int32


@final
class PS6000_TRIGGER_INFO(Structure):
    _pack_ = 1
    _fields_ = [
        ("status", PICO_STATUS_T),
        ("segmentIndex", c_uint32),
        ("triggerIndex", c_uint32),
        ("triggerTime", c_int64),
        ("timeUnits", c_int16),
        ("reserved0", c_int16),
        ("timeStampCounter", c_uint64),
    ]


@final
class PS6000_TRIGGER_CONDITIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", PS6000_TRIGGER_STATE_T),
        ("channelB", PS6000_TRIGGER_STATE_T),
        ("channelC", PS6000_TRIGGER_STATE_T),
        ("channelD", PS6000_TRIGGER_STATE_T),
        ("external", PS6000_TRIGGER_STATE_T),
        ("aux", PS6000_TRIGGER_STATE_T),
        ("pulseWidthQualifier", PS6000_TRIGGER_STATE_T),
    ]


@final
class PS6000_PWQ_CONDITIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", PS6000_TRIGGER_STATE_T),
        ("channelB", PS6000_TRIGGER_STATE_T),
        ("channelC", PS6000_TRIGGER_STATE_T),
        ("channelD", PS6000_TRIGGER_STATE_T),
        ("external", PS6000_TRIGGER_STATE_T),
        ("aux", PS6000_TRIGGER_STATE_T),
    ]


@final
class PS6000_TRIGGER_CHANNEL_PROPERTIES(Structure):
    _pack_ = 1
    _fields_ = [
        ("thresholdUpper", c_int16),
        ("hysteresisUpper", c_uint16),
        ("thresholdLower", c_int16),
        ("hysteresisLower", c_uint16),
        ("channel", PS6000_CHANNEL_T),
        ("thresholdMode", PS6000_THRESHOLD_MODE_T),
    ]


ps6000BlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps6000StreamingReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_uint32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)

ps6000DataReady = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p
)

_TIME_UNIT_SECONDS = {
    PS6000_TIME_UNITS.PS6000_FS: 1e-15,
    PS6000_TIME_UNITS.PS6000_PS: 1e-12,
    PS6000_TIME_UNITS.PS6000_NS: 1e-9,
    PS6000_TIME_UNITS.PS6000_US: 1e-6,
    PS6000_TIME_UNITS.PS6000_MS: 1e-3,
    PS6000_TIME_UNITS.PS6000_S: 1.0,
}


class PicoScope6000Wrapper(PicoScopeWrapperBase):
    _library_name = "ps6000"

    def __init__(self, library_path: str | None = None):
        super().__init__(library_path)

        self._ps6000OpenUnit = self._bind(
            "ps6000OpenUnit", [POINTER(c_int16), c_char_p]
        )
        self._ps6000OpenUnitAsync = self._bind(
            "ps6000OpenUnitAsync", [POINTER(c_int16), c_char_p]
        )
        self._ps6000OpenUnitProgress = self._bind(
            "ps6000OpenUnitProgress",
            [POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps6000GetUnitInfo = self._bind(
            "ps6000GetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps6000FlashLed = self._bind("ps6000FlashLed", [c_int16, c_int16])
        self._ps6000CloseUnit = self._bind("ps6000CloseUnit", [c_int16])
        self._ps6000MemorySegments = self._bind(
            "ps6000MemorySegments", [c_int16, c_uint32, POINTER(c_uint32)]
        )
        self._ps6000SetChannel = self._bind(
            "ps6000SetChannel",
            [
                c_int16,
                PS6000_CHANNEL_T,
                c_int16,
                PS6000_COUPLING_T,
                PS6000_RANGE_T,
                c_float,
                PS6000_BANDWIDTH_LIMITER_T,
            ],
        )
        self._ps6000GetTimebase = self._bind(
            "ps6000GetTimebase",
            [
                c_int16,
                c_uint32,
                c_uint32,
                POINTER(c_int32),
                c_int16,
                POINTER(c_uint32),
                c_uint32,
            ],
        )
        self._ps6000GetTimebase2 = self._bind(
            "ps6000GetTimebase2",
            [
                c_int16,
                c_uint32,
                c_uint32,
                POINTER(c_float),
                c_int16,
                POINTER(c_uint32),
                c_uint32,
            ],
        )
        self._ps6000SetSigGenArbitrary = self._bind(
            "ps6000SetSigGenArbitrary",
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
                PS6000_SWEEP_TYPE_T,
                PS6000_EXTRA_OPERATIONS_T,
                PS6000_INDEX_MODE_T,
                c_uint32,
                c_uint32,
                PS6000_SIGGEN_TRIG_TYPE_T,
                PS6000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps6000SetSigGenBuiltIn = self._bind(
            "ps6000SetSigGenBuiltIn",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_float,
                c_float,
                c_float,
                c_float,
                PS6000_SWEEP_TYPE_T,
                PS6000_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS6000_SIGGEN_TRIG_TYPE_T,
                PS6000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps6000SetSigGenBuiltInV2 = self._bind(
            "ps6000SetSigGenBuiltInV2",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS6000_SWEEP_TYPE_T,
                PS6000_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS6000_SIGGEN_TRIG_TYPE_T,
                PS6000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps6000SetSigGenPropertiesArbitrary = self._bind(
            "ps6000SetSigGenPropertiesArbitrary",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                PS6000_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS6000_SIGGEN_TRIG_TYPE_T,
                PS6000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps6000SetSigGenPropertiesBuiltIn = self._bind(
            "ps6000SetSigGenPropertiesBuiltIn",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_double,
                c_double,
                c_double,
                c_double,
                PS6000_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS6000_SIGGEN_TRIG_TYPE_T,
                PS6000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps6000SigGenFrequencyToPhase = self._bind(
            "ps6000SigGenFrequencyToPhase",
            [c_int16, c_double, PS6000_INDEX_MODE_T, c_uint32, POINTER(c_uint32)],
        )
        self._ps6000SigGenArbitraryMinMaxValues = self._bind(
            "ps6000SigGenArbitraryMinMaxValues",
            [
                c_int16,
                POINTER(c_int16),
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_uint32),
            ],
        )
        self._ps6000SigGenSoftwareControl = self._bind(
            "ps6000SigGenSoftwareControl", [c_int16, c_int16]
        )
        self._ps6000SetSimpleTrigger = self._bind(
            "ps6000SetSimpleTrigger",
            [
                c_int16,
                c_int16,
                PS6000_CHANNEL_T,
                c_int16,
                PS6000_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_int16,
            ],
        )
        self._ps6000SetEts = self._bind(
            "ps6000SetEts",
            [c_int16, PS6000_ETS_MODE_T, c_int16, c_int16, POINTER(c_int32)],
        )
        self._ps6000SetTriggerChannelProperties = self._bind(
            "ps6000SetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS6000_TRIGGER_CHANNEL_PROPERTIES),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps6000SetTriggerChannelConditions = self._bind(
            "ps6000SetTriggerChannelConditions",
            [c_int16, POINTER(PS6000_TRIGGER_CONDITIONS), c_int16],
        )
        self._ps6000SetTriggerChannelDirections = self._bind(
            "ps6000SetTriggerChannelDirections",
            [
                c_int16,
                PS6000_THRESHOLD_DIRECTION_T,
                PS6000_THRESHOLD_DIRECTION_T,
                PS6000_THRESHOLD_DIRECTION_T,
                PS6000_THRESHOLD_DIRECTION_T,
                PS6000_THRESHOLD_DIRECTION_T,
                PS6000_THRESHOLD_DIRECTION_T,
            ],
        )
        self._ps6000SetTriggerDelay = self._bind(
            "ps6000SetTriggerDelay", [c_int16, c_uint32]
        )
        self._ps6000SetPulseWidthQualifier = self._bind(
            "ps6000SetPulseWidthQualifier",
            [
                c_int16,
                POINTER(PS6000_PWQ_CONDITIONS),
                c_int16,
                PS6000_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS6000_PULSE_WIDTH_TYPE_T,
            ],
        )
        self._ps6000IsTriggerOrPulseWidthQualifierEnabled = self._bind(
            "ps6000IsTriggerOrPulseWidthQualifierEnabled",
            [c_int16, POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps6000GetTriggerTimeOffset = self._bind(
            "ps6000GetTriggerTimeOffset",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS6000_TIME_UNITS_T),
                c_uint32,
            ],
        )
        self._ps6000GetTriggerTimeOffset64 = self._bind(
            "ps6000GetTriggerTimeOffset64",
            [c_int16, POINTER(c_int64), POINTER(PS6000_TIME_UNITS_T), c_uint32],
        )
        self._ps6000GetValuesTriggerTimeOffsetBulk = self._bind(
            "ps6000GetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS6000_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps6000GetValuesTriggerTimeOffsetBulk64 = self._bind(
            "ps6000GetValuesTriggerTimeOffsetBulk64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS6000_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps6000SetDataBuffers = self._bind(
            "ps6000SetDataBuffers",
            [
                c_int16,
                PS6000_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_uint32,
                PS6000_RATIO_MODE_T,
            ],
        )
        self._ps6000SetDataBuffer = self._bind(
            "ps6000SetDataBuffer",
            [c_int16, PS6000_CHANNEL_T, c_void_p, c_uint32, PS6000_RATIO_MODE_T],
        )
        self._ps6000SetDataBufferBulk = self._bind(
            "ps6000SetDataBufferBulk",
            [
                c_int16,
                PS6000_CHANNEL_T,
                c_void_p,
                c_uint32,
                c_uint32,
                PS6000_RATIO_MODE_T,
            ],
        )
        self._ps6000SetDataBuffersBulk = self._bind(
            "ps6000SetDataBuffersBulk",
            [
                c_int16,
                PS6000_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_uint32,
                c_uint32,
                PS6000_RATIO_MODE_T,
            ],
        )
        self._ps6000SetEtsTimeBuffer = self._bind(
            "ps6000SetEtsTimeBuffer", [c_int16, c_void_p, c_uint32]
        )
        self._ps6000SetEtsTimeBuffers = self._bind(
            "ps6000SetEtsTimeBuffers", [c_int16, c_void_p, c_void_p, c_uint32]
        )
        self._ps6000RunBlock = self._bind(
            "ps6000RunBlock",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                c_int16,
                POINTER(c_int32),
                c_uint32,
                ps6000BlockReady,
                c_void_p,
            ],
        )
        self._ps6000IsReady = self._bind("ps6000IsReady", [c_int16, POINTER(c_int16)])
        self._ps6000RunStreaming = self._bind(
            "ps6000RunStreaming",
            [
                c_int16,
                POINTER(c_uint32),
                PS6000_TIME_UNITS_T,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint32,
                PS6000_RATIO_MODE_T,
                c_uint32,
            ],
        )
        self._ps6000GetStreamingLatestValues = self._bind(
            "ps6000GetStreamingLatestValues",
            [c_int16, ps6000StreamingReady, c_void_p],
            # PICO_BUSY: no new streaming data yet / previous call still being
            # processed. The caller is expected to simply poll again.
            info=(PICO_STATUS.PICO_BUSY,),
        )
        self._ps6000NoOfStreamingValues = self._bind(
            "ps6000NoOfStreamingValues", [c_int16, POINTER(c_uint32)]
        )
        self._ps6000GetMaxDownSampleRatio = self._bind(
            "ps6000GetMaxDownSampleRatio",
            [c_int16, c_uint32, POINTER(c_uint32), PS6000_RATIO_MODE_T, c_uint32],
        )
        self._ps6000GetValues = self._bind(
            "ps6000GetValues",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS6000_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps6000GetValuesBulk = self._bind(
            "ps6000GetValuesBulk",
            [
                c_int16,
                POINTER(c_uint32),
                c_uint32,
                c_uint32,
                c_uint32,
                PS6000_RATIO_MODE_T,
                POINTER(c_int16),
            ],
        )
        self._ps6000GetValuesAsync = self._bind(
            "ps6000GetValuesAsync",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                PS6000_RATIO_MODE_T,
                c_uint32,
                ps6000DataReady,
                c_void_p,
            ],
        )
        self._ps6000GetValuesOverlapped = self._bind(
            "ps6000GetValuesOverlapped",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS6000_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps6000GetValuesOverlappedBulk = self._bind(
            "ps6000GetValuesOverlappedBulk",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS6000_RATIO_MODE_T,
                c_uint32,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps6000GetValuesBulkAsyc = self._bind(
            "ps6000GetValuesBulkAsyc",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS6000_RATIO_MODE_T,
                c_uint32,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps6000GetNoOfCaptures = self._bind(
            "ps6000GetNoOfCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps6000GetNoOfProcessedCaptures = self._bind(
            "ps6000GetNoOfProcessedCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps6000Stop = self._bind("ps6000Stop", [c_int16])
        self._ps6000SetNoOfCaptures = self._bind(
            "ps6000SetNoOfCaptures", [c_int16, c_uint32]
        )
        self._ps6000SetWaveformLimiter = self._bind(
            "ps6000SetWaveformLimiter", [c_int16, c_uint32]
        )
        self._ps6000GetTriggerInfoBulk = self._bind(
            "ps6000GetTriggerInfoBulk",
            [c_int16, POINTER(PS6000_TRIGGER_INFO), c_uint32, c_uint32],
        )
        self._ps6000EnumerateUnits = self._bind(
            "ps6000EnumerateUnits",
            [POINTER(c_int16), c_char_p, POINTER(c_int16)],
            # PICO_NOT_FOUND: no units connected, which is a valid enumeration
            # result (count is 0).
            info=(PICO_STATUS.PICO_NOT_FOUND,),
        )
        self._ps6000SetExternalClock = self._bind(
            "ps6000SetExternalClock",
            [c_int16, PS6000_EXTERNAL_FREQUENCY_T, c_int16],
        )
        self._ps6000PingUnit = self._bind("ps6000PingUnit", [c_int16])
        self._ps6000GetAnalogueOffset = self._bind(
            "ps6000GetAnalogueOffset",
            [
                c_int16,
                PS6000_RANGE_T,
                PS6000_COUPLING_T,
                POINTER(c_float),
                POINTER(c_float),
            ],
        )
        self._ps6000QueryTemperatures = self._bind(
            "ps6000QueryTemperatures",
            [c_int16, POINTER(PS6000_TEMPERATURES_T), POINTER(c_float)],
        )
        self._ps6000QueryOutputEdgeDetect = self._bind(
            "ps6000QueryOutputEdgeDetect", [c_int16, POINTER(c_int16)]
        )
        self._ps6000SetOutputEdgeDetect = self._bind(
            "ps6000SetOutputEdgeDetect", [c_int16, c_int16]
        )

    def ps6000OpenUnit(self, serial: str | None):
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        return self._ps6000OpenUnit(byref(handle), ser), handle

    def ps6000OpenUnitAsync(self, serial: str | None) -> tuple[PICO_STATUS, bool]:
        started = c_int16(0)
        ser = serial.encode() if serial is not None else None
        status = self._ps6000OpenUnitAsync(byref(started), ser)
        return status, started.value == 1

    def ps6000OpenUnitProgress(self) -> tuple[PICO_STATUS, c_int16, int, bool]:
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        status = self._ps6000OpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return status, handle, progressPercent.value, complete.value != 0

    def ps6000CloseUnit(self, handle: c_int16):
        return self._ps6000CloseUnit(handle)

    def ps6000GetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._ps6000GetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return status, infostr

    def ps6000FlashLed(self, handle: c_int16, start: int) -> PICO_STATUS:
        return self._ps6000FlashLed(handle, start)

    def ps6000MemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_uint32(0)
        return (
            self._ps6000MemorySegments(handle, nsegments, byref(maxSamples)),
            maxSamples.value,
        )

    def ps6000SetChannel(
        self,
        handle: c_int16,
        channel: PS6000_CHANNEL,
        enabled: bool,
        coupling: PS6000_COUPLING,
        range: PS6000_RANGE,
        analog_offset: float,
        bandwidth: PS6000_BANDWIDTH_LIMITER,
    ):
        return self._ps6000SetChannel(
            handle,
            channel,
            1 if enabled else 0,
            coupling,
            range,
            analog_offset,
            bandwidth,
        )

    def ps6000GetTimebase(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        oversample: int,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_uint32(0)
        status = self._ps6000GetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return status, timeIntervalNanoseconds.value, maxSamples.value

    def ps6000GetTimebase2(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        oversample: int,
        segmentIndex: int,
    ):
        assert oversample >= 0 and oversample <= PS6000_MAX_OVERSAMPLE_8BIT
        timeIntervalNS = c_float(0)
        maxSamples = c_uint32(0)
        return (
            self._ps6000GetTimebase2(
                handle,
                timebase,
                noSamples,
                byref(timeIntervalNS),
                oversample,
                byref(maxSamples),
                segmentIndex,
            ),
            timeIntervalNS.value,
            maxSamples.value,
        )

    def ps6000SetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: Sequence[int],
        sweepType: PS6000_SWEEP_TYPE,
        operation: PS6000_EXTRA_OPERATIONS,
        indexMode: PS6000_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS6000_SIGGEN_TRIG_TYPE,
        triggerSource: PS6000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        waveform = (c_int16 * len(arbitraryWaveform))(*arbitraryWaveform)
        return self._ps6000SetSigGenArbitrary(
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
            operation,
            indexMode,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps6000SetSigGenBuiltIn(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS6000_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS6000_SWEEP_TYPE,
        operation: PS6000_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS6000_SIGGEN_TRIG_TYPE,
        triggerSource: PS6000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps6000SetSigGenBuiltIn(
            handle,
            offsetVoltage,
            pkToPk,
            waveType,
            startFrequency,
            stopFrequency,
            increment,
            dwellTime,
            sweepType,
            operation,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps6000SetSigGenBuiltInV2(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS6000_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS6000_SWEEP_TYPE,
        operation: PS6000_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS6000_SIGGEN_TRIG_TYPE,
        triggerSource: PS6000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps6000SetSigGenBuiltInV2(
            handle,
            offsetVoltage,
            pkToPk,
            waveType,
            startFrequency,
            stopFrequency,
            increment,
            dwellTime,
            sweepType,
            operation,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps6000SetSigGenPropertiesArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PS6000_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS6000_SIGGEN_TRIG_TYPE,
        triggerSource: PS6000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps6000SetSigGenPropertiesArbitrary(
            handle,
            offsetVoltage,
            pkToPk,
            startDeltaPhase,
            stopDeltaPhase,
            deltaPhaseIncrement,
            dwellCount,
            sweepType,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps6000SetSigGenPropertiesBuiltIn(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS6000_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS6000_SIGGEN_TRIG_TYPE,
        triggerSource: PS6000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps6000SetSigGenPropertiesBuiltIn(
            handle,
            offsetVoltage,
            pkToPk,
            startFrequency,
            stopFrequency,
            increment,
            dwellTime,
            sweepType,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps6000SigGenFrequencyToPhase(
        self,
        handle: c_int16,
        frequency: float,
        indexMode: PS6000_INDEX_MODE,
        bufferLength: int,
    ) -> tuple[PICO_STATUS, int]:
        phase = c_uint32(0)
        status = self._ps6000SigGenFrequencyToPhase(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return status, phase.value

    def ps6000SigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, int, int, int, int]:
        minValue = c_int16(0)
        maxValue = c_int16(0)
        minSize = c_uint32(0)
        maxSize = c_uint32(0)
        status = self._ps6000SigGenArbitraryMinMaxValues(
            handle, byref(minValue), byref(maxValue), byref(minSize), byref(maxSize)
        )
        return status, minValue.value, maxValue.value, minSize.value, maxSize.value

    def ps6000SigGenSoftwareControl(self, handle: c_int16, state: bool) -> PICO_STATUS:
        return self._ps6000SigGenSoftwareControl(handle, 1 if state else 0)

    def ps6000SetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PS6000_CHANNEL,
        threshold: int,
        direction: PS6000_THRESHOLD_DIRECTION,
        delay: int,
        autoTriggerMS: int,
    ):
        assert autoTriggerMS >= 0
        return self._ps6000SetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTriggerMS,
        )

    def ps6000SetEts(
        self,
        handle: c_int16,
        mode: PS6000_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> tuple[PICO_STATUS, int]:
        sampleTimePicoseconds = c_int32(0)
        status = self._ps6000SetEts(
            handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
        )
        return status, sampleTimePicoseconds.value

    def ps6000SetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS6000_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> PICO_STATUS:
        n = len(channelProperties)
        properties = (PS6000_TRIGGER_CHANNEL_PROPERTIES * n)(*channelProperties)
        return self._ps6000SetTriggerChannelProperties(
            handle,
            properties if n else None,
            n,
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps6000SetTriggerChannelConditions(
        self, handle: c_int16, conditions: Sequence[PS6000_TRIGGER_CONDITIONS]
    ) -> PICO_STATUS:
        n = len(conditions)
        conds = (PS6000_TRIGGER_CONDITIONS * n)(*conditions)
        return self._ps6000SetTriggerChannelConditions(handle, conds if n else None, n)

    def ps6000SetTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: PS6000_THRESHOLD_DIRECTION,
        channelB: PS6000_THRESHOLD_DIRECTION,
        channelC: PS6000_THRESHOLD_DIRECTION,
        channelD: PS6000_THRESHOLD_DIRECTION,
        ext: PS6000_THRESHOLD_DIRECTION,
        aux: PS6000_THRESHOLD_DIRECTION,
    ) -> PICO_STATUS:
        return self._ps6000SetTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext, aux
        )

    def ps6000SetTriggerDelay(self, handle: c_int16, delay: int):
        return self._ps6000SetTriggerDelay(handle, delay)

    def ps6000SetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS6000_PWQ_CONDITIONS],
        direction: PS6000_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS6000_PULSE_WIDTH_TYPE,
    ) -> PICO_STATUS:
        n = len(conditions)
        conds = (PS6000_PWQ_CONDITIONS * n)(*conditions)
        return self._ps6000SetPulseWidthQualifier(
            handle, conds if n else None, n, direction, lower, upper, type
        )

    def ps6000IsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        status = self._ps6000IsTriggerOrPulseWidthQualifierEnabled(
            handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
        )
        return (
            status,
            triggerEnabled.value != 0,
            pulseWidthQualifierEnabled.value != 0,
        )

    def ps6000GetTriggerTimeOffset(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, int, PS6000_TIME_UNITS]:
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS6000_TIME_UNITS_T(0)
        status = self._ps6000GetTriggerTimeOffset(
            handle, byref(timeUpper), byref(timeLower), byref(timeUnits), segmentIndex
        )
        return (
            status,
            timeUpper.value,
            timeLower.value,
            PS6000_TIME_UNITS(timeUnits.value),
        )

    def ps6000GetTriggerTimeOffset64(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, PS6000_TIME_UNITS]:
        time = c_int64(0)
        timeUnits = PS6000_TIME_UNITS_T(0)
        status = self._ps6000GetTriggerTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return status, time.value, PS6000_TIME_UNITS(timeUnits.value)

    def ps6000GetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[int], list[PS6000_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        n = toSegmentIndex - fromSegmentIndex + 1
        timesUpper = (c_uint32 * n)()
        timesLower = (c_uint32 * n)()
        timeUnits = (PS6000_TIME_UNITS_T * n)()
        status = self._ps6000GetValuesTriggerTimeOffsetBulk(
            handle, timesUpper, timesLower, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return (
            status,
            list(timesUpper),
            list(timesLower),
            [PS6000_TIME_UNITS(u) for u in timeUnits],
        )

    def ps6000GetValuesTriggerTimeOffsetBulk64(
        self,
        handle: c_int16,
        fromSegment: int,
        toSegment: int,
    ):
        assert fromSegment <= toSegment
        n = toSegment - fromSegment + 1
        times = (c_int64 * n)()
        units = (PS6000_TIME_UNITS_T * n)()
        status = self._ps6000GetValuesTriggerTimeOffsetBulk64(
            handle, times, units, fromSegment, toSegment
        )
        times_sec = [
            t * _TIME_UNIT_SECONDS[PS6000_TIME_UNITS(u)] for t, u in zip(times, units)
        ]
        return status, times_sec

    def ps6000SetDataBuffers(
        self,
        handle: c_int16,
        channel: PS6000_CHANNEL,
        bufferMax: c_void_p | int | None,
        bufferMin: c_void_p | int | None,
        bufferLth: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
    ) -> PICO_STATUS:
        return self._ps6000SetDataBuffers(
            handle, channel, bufferMax, bufferMin, bufferLth, downSampleRatioMode
        )

    def ps6000SetDataBuffer(
        self,
        handle: c_int16,
        channel: PS6000_CHANNEL,
        buffer: c_void_p,
        bufferLth: int,
        mode: PS6000_RATIO_MODE,
    ):
        return self._ps6000SetDataBuffer(handle, channel, buffer, bufferLth, mode)

    def ps6000SetDataBufferBulk(
        self,
        handle: c_int16,
        channel: PS6000_CHANNEL,
        buffer: c_void_p,
        bufferLth: int,
        waveform: int,
        mode: PS6000_RATIO_MODE,
    ):
        return self._ps6000SetDataBufferBulk(
            handle, channel, buffer, bufferLth, waveform, mode
        )

    def ps6000SetDataBuffersBulk(
        self,
        handle: c_int16,
        channel: PS6000_CHANNEL,
        bufferMax: c_void_p | int | None,
        bufferMin: c_void_p | int | None,
        bufferLth: int,
        waveform: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
    ) -> PICO_STATUS:
        return self._ps6000SetDataBuffersBulk(
            handle,
            channel,
            bufferMax,
            bufferMin,
            bufferLth,
            waveform,
            downSampleRatioMode,
        )

    def ps6000SetEtsTimeBuffer(
        self, handle: c_int16, buffer: c_void_p | int | None, bufferLth: int
    ) -> PICO_STATUS:
        """``buffer`` must hold ``bufferLth`` int64 values and outlive the capture."""
        return self._ps6000SetEtsTimeBuffer(handle, buffer, bufferLth)

    def ps6000SetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: c_void_p | int | None,
        timeLower: c_void_p | int | None,
        bufferLth: int,
    ) -> PICO_STATUS:
        """The buffers must hold ``bufferLth`` uint32 values and outlive the capture."""
        return self._ps6000SetEtsTimeBuffers(handle, timeUpper, timeLower, bufferLth)

    def ps6000IsReady(self, handle: c_int16):
        ready = c_int16(0)
        return self._ps6000IsReady(handle, byref(ready)), ready.value == 1

    def ps6000RunBlock(
        self,
        handle: c_int16,
        preSamples: int,
        postSamples: int,
        timebase: int,
        oversample: int,
        segment: int,
        callback: Callable[[c_int16, PICO_STATUS], None] | None,
    ):
        assert preSamples >= 0
        assert postSamples >= 0
        assert oversample >= 0 and oversample <= PS6000_MAX_OVERSAMPLE_8BIT
        timeInd = c_int32(0)
        lpReady = ps6000BlockReady()  # NULL; ctypes rejects None here
        if callback is not None:

            def cbwrapper(handle: c_int16, status: int, _: c_void_p):
                callback(handle, PICO_STATUS(status))

            lpReady = ps6000BlockReady(cbwrapper)
        status = self._with_callback(
            self._callback_key("ps6000RunBlock", handle),
            lpReady,
            lambda: self._ps6000RunBlock(
                handle,
                preSamples,
                postSamples,
                timebase,
                oversample,
                byref(timeInd),
                segment,
                lpReady,
                None,
            ),
        )
        return status, timeInd.value

    def ps6000RunStreaming(
        self,
        handle: c_int16,
        sampleInterval: int,
        sampleIntervalTimeUnits: PS6000_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostPreTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
        overviewBufferSize: int,
    ) -> tuple[PICO_STATUS, int]:
        interval = c_uint32(sampleInterval)
        status = self._ps6000RunStreaming(
            handle,
            byref(interval),
            sampleIntervalTimeUnits,
            maxPreTriggerSamples,
            maxPostPreTriggerSamples,
            1 if autoStop else 0,
            downSampleRatio,
            downSampleRatioMode,
            overviewBufferSize,
        )
        return status, interval.value

    def ps6000GetStreamingLatestValues(
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
        ):
            callback(
                handle,
                noOfSamples,
                startIndex,
                overflow,
                triggerAt,
                triggered != 0,
                autoStop != 0,
            )

        lpPs6000Ready = ps6000StreamingReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps6000GetStreamingLatestValues", handle),
            lpPs6000Ready,
            lambda: self._ps6000GetStreamingLatestValues(handle, lpPs6000Ready, None),
        )

    def ps6000NoOfStreamingValues(self, handle: c_int16) -> tuple[PICO_STATUS, int]:
        noOfValues = c_uint32(0)
        status = self._ps6000NoOfStreamingValues(handle, byref(noOfValues))
        return status, noOfValues.value

    def ps6000GetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggreatedSamples: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int]:
        maxDownSampleRatio = c_uint32(0)
        status = self._ps6000GetMaxDownSampleRatio(
            handle,
            noOfUnaggreatedSamples,
            byref(maxDownSampleRatio),
            downSampleRatioMode,
            segmentIndex,
        )
        return status, maxDownSampleRatio.value

    def ps6000GetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int, int]:
        samples = c_uint32(noOfSamples)
        overflow = c_int16(0)
        status = self._ps6000GetValues(
            handle,
            startIndex,
            byref(samples),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return status, samples.value, overflow.value

    def ps6000GetValuesBulk(
        self,
        handle: c_int16,
        nosamples: int,
        fromSegment: int,
        toSegment: int,
        downsampleRatio: int,
        downsampleMode: PS6000_RATIO_MODE,
    ):
        assert nosamples > 0
        assert fromSegment <= toSegment
        nosamples_ = c_uint32(nosamples)
        nsegments = (toSegment - fromSegment) + 1
        overflow = (c_int16 * nsegments)(0)
        return (
            self._ps6000GetValuesBulk(
                handle,
                byref(nosamples_),
                fromSegment,
                toSegment,
                downsampleRatio,
                downsampleMode,
                overflow,
            ),
            nosamples_.value,
            [int(f) for f in overflow],
        )

    def ps6000GetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
        segmentIndex: int,
        callback: Callable[[int, PICO_STATUS, int, int], None],
    ) -> PICO_STATUS:
        """Callback args: handle, status, noOfSamples, overflow."""

        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: c_void_p
        ):
            callback(handle, PICO_STATUS(status), noOfSamples, overflow)

        lpDataReady = ps6000DataReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps6000GetValuesAsync", handle),
            lpDataReady,
            lambda: self._ps6000GetValuesAsync(
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

    def ps6000GetValuesOverlapped(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, c_uint32, c_int16]:
        """Deferred request executed by the next ``ps6000RunBlock``.

        The driver fills in the returned ``noOfSamples`` and ``overflow`` ctypes
        objects when the capture completes, so they are returned as is (read
        their ``.value`` afterwards) and kept alive by the wrapper.
        """
        samples = c_uint32(noOfSamples)
        overflow = c_int16(0)
        status = self._with_callback(
            self._callback_key("ps6000GetValuesOverlapped", handle),
            (samples, overflow),
            lambda: self._ps6000GetValuesOverlapped(
                handle,
                startIndex,
                byref(samples),
                downSampleRatio,
                downSampleRatioMode,
                segmentIndex,
                byref(overflow),
            ),
        )
        return status, samples, overflow

    def ps6000GetValuesOverlappedBulk(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[PICO_STATUS, c_uint32, Array[c_int16]]:
        """Deferred bulk request executed by the next ``ps6000RunBlock``.

        As for :meth:`ps6000GetValuesOverlapped`, the returned ctypes objects
        are filled in by the driver later and kept alive by the wrapper.
        """
        assert fromSegmentIndex <= toSegmentIndex
        samples = c_uint32(noOfSamples)
        overflow = (c_int16 * (toSegmentIndex - fromSegmentIndex + 1))()
        status = self._with_callback(
            self._callback_key("ps6000GetValuesOverlappedBulk", handle),
            (samples, overflow),
            lambda: self._ps6000GetValuesOverlappedBulk(
                handle,
                startIndex,
                byref(samples),
                downSampleRatio,
                downSampleRatioMode,
                fromSegmentIndex,
                toSegmentIndex,
                overflow,
            ),
        )
        return status, samples, overflow

    def ps6000GetValuesBulkAsyc(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS6000_RATIO_MODE,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[PICO_STATUS, c_uint32, Array[c_int16]]:
        """Asynchronous bulk read (the C name is misspelled in the driver).

        The returned ctypes objects may be filled in by the driver after this
        call returns, so they are returned as is and kept alive by the wrapper.
        """
        assert fromSegmentIndex <= toSegmentIndex
        samples = c_uint32(noOfSamples)
        overflow = (c_int16 * (toSegmentIndex - fromSegmentIndex + 1))()
        status = self._with_callback(
            self._callback_key("ps6000GetValuesBulkAsyc", handle),
            (samples, overflow),
            lambda: self._ps6000GetValuesBulkAsyc(
                handle,
                startIndex,
                byref(samples),
                downSampleRatio,
                downSampleRatioMode,
                fromSegmentIndex,
                toSegmentIndex,
                overflow,
            ),
        )
        return status, samples, overflow

    def ps6000GetNoOfCaptures(self, handle: c_int16):
        captures = c_uint32()
        return self._ps6000GetNoOfCaptures(handle, byref(captures)), captures.value

    def ps6000GetNoOfProcessedCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            self._ps6000GetNoOfProcessedCaptures(handle, byref(captures)),
            captures.value,
        )

    def ps6000Stop(self, handle: c_int16) -> PICO_STATUS:
        return self._ps6000Stop(handle)

    def ps6000SetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return self._ps6000SetNoOfCaptures(handle, ncaptures)

    def ps6000SetWaveformLimiter(
        self, handle: c_int16, nWaveformsPerSecond: int
    ) -> PICO_STATUS:
        return self._ps6000SetWaveformLimiter(handle, nWaveformsPerSecond)

    def ps6000GetTriggerInfoBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[PS6000_TRIGGER_INFO]]:
        assert fromSegmentIndex <= toSegmentIndex
        triggerInfo = (PS6000_TRIGGER_INFO * (toSegmentIndex - fromSegmentIndex + 1))()
        status = self._ps6000GetTriggerInfoBulk(
            handle, triggerInfo, fromSegmentIndex, toSegmentIndex
        )
        return status, list(triggerInfo)

    def ps6000EnumerateUnits(self) -> tuple[PICO_STATUS, int, list[str]]:
        count = c_int16(0)
        serials = create_string_buffer(4096)
        serialLth = c_int16(len(serials))
        status = self._ps6000EnumerateUnits(byref(count), serials, byref(serialLth))
        text = serials.value.decode("utf-8")
        return status, count.value, [s for s in text.split(",") if s]

    def ps6000SetExternalClock(
        self,
        handle: c_int16,
        frequency: PS6000_EXTERNAL_FREQUENCY,
        threshold: float | int,
    ) -> PICO_STATUS:
        if isinstance(threshold, float):
            assert threshold >= -1.0 and threshold <= 1.0, (
                "if threashold is a float it must bit in [-1.0, 1.0]"
            )
            threshold = round(threshold * PS6000_MAX_VALUE)
        else:
            assert threshold >= -32512 and threshold <= 32512, (
                "if threashold is an int it must bit in [-32512, 32512]"
            )
        return self._ps6000SetExternalClock(handle, frequency, threshold)

    def ps6000PingUnit(self, handle: c_int16) -> PICO_STATUS:
        return self._ps6000PingUnit(handle)

    def ps6000GetAnalogueOffset(
        self, handle: c_int16, range: PS6000_RANGE, coupling: PS6000_COUPLING
    ):
        minv = c_float(0)
        maxv = c_float(0)
        return (
            self._ps6000GetAnalogueOffset(
                handle, range, coupling, byref(maxv), byref(minv)
            ),
            minv.value,
            maxv.value,
        )

    def ps6000QueryTemperatures(
        self, handle: c_int16, types: PS6000_TEMPERATURES
    ) -> tuple[PICO_STATUS, int, float]:
        """Undocumented in the programmer's guide; returns (status, types, temperature).

        ``types`` is passed by reference and returned as written back by the driver.
        """
        types_ = PS6000_TEMPERATURES_T(types)
        # Over-allocate in case the driver writes more than one value.
        temperatures = (c_float * 16)()
        status = self._ps6000QueryTemperatures(handle, byref(types_), temperatures)
        return status, types_.value, temperatures[0]

    def ps6000QueryOutputEdgeDetect(self, handle: c_int16) -> tuple[PICO_STATUS, bool]:
        state = c_int16(0)
        status = self._ps6000QueryOutputEdgeDetect(handle, byref(state))
        return status, state.value != 0

    def ps6000SetOutputEdgeDetect(self, handle: c_int16, state: bool) -> PICO_STATUS:
        return self._ps6000SetOutputEdgeDetect(handle, 1 if state else 0)


__all__ = (
    "PS640X_C_D_MAX_SIG_GEN_BUFFER_SIZE",
    "PS6000_BANDWIDTH_LIMITER",
    "PS6000_CHANNEL",
    "PS6000_CHANNEL_BUFFER_INDEX",
    "PS6000_COUPLING",
    "PS6000_ETS_MODE",
    "PS6000_EXTERNAL_FREQUENCY",
    "PS6000_EXTRA_OPERATIONS",
    "PS6000_GAUSSIAN_MAX_FREQUENCY",
    "PS6000_HALF_SINE_MAX_FREQUENCY",
    "PS6000_INDEX_MODE",
    "PS6000_MAX_ANALOGUE_OFFSET_5V_20V",
    "PS6000_MAX_ANALOGUE_OFFSET_50MV_200MV",
    "PS6000_MAX_ANALOGUE_OFFSET_500MV_2V",
    "PS6000_MAX_ETS_CYCLES",
    "PS6000_MAX_INTERLEAVE",
    "PS6000_MAX_OVERSAMPLE_8BIT",
    "PS6000_MAX_PULSE_WIDTH_QUALIFIER_COUNT",
    "PS6000_MAX_SIG_GEN_BUFFER_SIZE",
    "PS6000_MAX_SWEEPS_SHOTS",
    "PS6000_MAX_VALUE",
    "PS6000_MAX_WAVEFORMS_PER_SECOND",
    "PS6000_MIN_ANALOGUE_OFFSET_5V_20V",
    "PS6000_MIN_ANALOGUE_OFFSET_50MV_200MV",
    "PS6000_MIN_ANALOGUE_OFFSET_500MV_2V",
    "PS6000_MIN_DWELL_COUNT",
    "PS6000_MIN_FREQUENCY",
    "PS6000_MIN_SIG_GEN_BUFFER_SIZE",
    "PS6000_MIN_VALUE",
    "PS6000_PRBS_MAX_FREQUENCY",
    "PS6000_PULSE_WIDTH_TYPE",
    "PS6000_PWQ_CONDITIONS",
    "PS6000_RAMP_MAX_FREQUENCY",
    "PS6000_RANGE",
    "PS6000_RATIO_MODE",
    "PS6000_SIGGEN_TRIG_SOURCE",
    "PS6000_SIGGEN_TRIG_TYPE",
    "PS6000_SINC_MAX_FREQUENCY",
    "PS6000_SINE_MAX_FREQUENCY",
    "PS6000_SQUARE_MAX_FREQUENCY",
    "PS6000_SWEEP_TYPE",
    "PS6000_TEMPERATURES",
    "PS6000_THRESHOLD_DIRECTION",
    "PS6000_THRESHOLD_MODE",
    "PS6000_TIME_UNITS",
    "PS6000_TRIANGLE_MAX_FREQUENCY",
    "PS6000_TRIGGER_CHANNEL_PROPERTIES",
    "PS6000_TRIGGER_CONDITIONS",
    "PS6000_TRIGGER_INFO",
    "PS6000_TRIGGER_STATE",
    "PS6000_WAVE_TYPE",
    "PicoScope6000Wrapper",
    "ps6000BlockReady",
    "ps6000DataReady",
    "ps6000StreamingReady",
)
