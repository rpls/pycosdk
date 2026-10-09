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
from enum import IntEnum, IntFlag
from typing import final

from ._base import CALLBACK_FUNCTYPE, POWER_SOURCE_STATUSES, PicoScopeWrapperBase
from .callback import PicoUpdateFirmwareProgress
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T
from .version import PICO_VERSION

PS5000A_MAX_VALUE_8BIT = 32512
PS5000A_MIN_VALUE_8BIT = -32512

PS5000A_MAX_VALUE_16BIT = 32767
PS5000A_MIN_VALUE_16BIT = -32767

PS5000A_EXT_MAX_VALUE = 32767
PS5000A_EXT_MIN_VALUE = -32767

# covers the 5242A/B and 5442A/B
PS5X42A_MAX_SIG_GEN_BUFFER_SIZE = 16384
# covers the 5243A/B and 5443A/B
PS5X43A_MAX_SIG_GEN_BUFFER_SIZE = 32768
# covers the 5244A/B and 5444A/B
PS5X44A_MAX_SIG_GEN_BUFFER_SIZE = 49152

# covers the PicoScope 5000D Series
PS5X4XD_MAX_SIG_GEN_BUFFER_SIZE = 32768

MIN_SIG_GEN_BUFFER_SIZE = 1
MIN_DWELL_COUNT = 3
MAX_SWEEPS_SHOTS = (1 << 30) - 1
AWG_DAC_FREQUENCY = 200e6
PS5000AB_DDS_FREQUENCY = 200e6
PS5000D_DDS_FREQUENCY = 100e6
AWG_PHASE_ACCUMULATOR = 4294967296.0

MAX_ANALOGUE_OFFSET_50MV_200MV = 0.250
MIN_ANALOGUE_OFFSET_50MV_200MV = -0.250
MAX_ANALOGUE_OFFSET_500MV_2V = 2.500
MIN_ANALOGUE_OFFSET_500MV_2V = -2.500
MAX_ANALOGUE_OFFSET_5V_20V = 20.0
MIN_ANALOGUE_OFFSET_5V_20V = -20.0

PS5244A_MAX_ETS_CYCLES = 500  # PS5242A, PS5242B, PS5442A, PS5442B
PS5244A_MAX_ETS_INTERLEAVE = 40

PS5243A_MAX_ETS_CYCLES = 250  # PS5243A, PS5243B, PS5443A, PS5443B
PS5243A_MAX_ETS_INTERLEAVE = 20

PS5242A_MAX_ETS_CYCLES = 125  # PS5242A, PS5242B, PS5442A, PS5442B
PS5242A_MAX_ETS_INTERLEAVE = 10

PS5X44D_MAX_ETS_CYCLES = 500  # PS5244D, PS5244DMSO, PS5444D, PS5444DMSO
PS5X44D_MAX_ETS_INTERLEAVE = 80

PS5X43D_MAX_ETS_CYCLES = 250  # PS5243D, PS5243DMSO, PS5443D, PS5443DMSO
PS5X43D_MAX_ETS_INTERLEAVE = 40

PS5X42D_MAX_ETS_CYCLES = 125  # PS5242D, PS5242DMSO, PS5442D, PS5442DMSO
PS5X42D_MAX_ETS_INTERLEAVE = 5

PS5000A_SHOT_SWEEP_TRIGGER_CONTINUOUS_RUN = 0xFFFFFFFF


class PS5000A_DEVICE_RESOLUTION(IntEnum):
    PS5000A_DR_8BIT = 0
    PS5000A_DR_12BIT = 1
    PS5000A_DR_14BIT = 2
    PS5000A_DR_15BIT = 3
    PS5000A_DR_16BIT = 4


PS5000A_DEVICE_RESOLUTION_T = c_int32


class PS5000A_EXTRA_OPERATIONS(IntEnum):
    PS5000A_ES_OFF = 0
    PS5000A_WHITENOISE = 1
    PS5000A_PRBS = 2


PS5000A_EXTRA_OPERATIONS_T = c_int32


class PS5000A_BANDWIDTH_LIMITER(IntEnum):
    PS5000A_BW_FULL = 0
    PS5000A_BW_20MHZ = 1


PS5000A_BANDWIDTH_LIMITER_T = c_int32


class PS5000A_COUPLING(IntEnum):
    PS5000A_AC = 0
    PS5000A_DC = 1


PS5000A_COUPLING_T = c_int32


class PS5000A_CHANNEL(IntEnum):
    PS5000A_CHANNEL_A = 0
    PS5000A_CHANNEL_B = 1
    PS5000A_CHANNEL_C = 2
    PS5000A_CHANNEL_D = 3
    PS5000A_EXTERNAL = 4
    PS5000A_MAX_CHANNELS = PS5000A_EXTERNAL
    PS5000A_TRIGGER_AUX = 5
    PS5000A_MAX_TRIGGER_SOURCES = 6
    PS5000A_DIGITAL_PORT0 = 0x80
    PS5000A_DIGITAL_PORT1 = 0x81
    PS5000A_DIGITAL_PORT2 = 0x82
    PS5000A_DIGITAL_PORT3 = 0x83
    PS5000A_PULSE_WIDTH_SOURCE = 0x10000000


PS5000A_CHANNEL_T = c_int32


class PS5000A_CHANNEL_FLAGS(IntFlag):
    PS5000A_CHANNEL_A_FLAGS = 1
    PS5000A_CHANNEL_B_FLAGS = 2
    PS5000A_CHANNEL_C_FLAGS = 4
    PS5000A_CHANNEL_D_FLAGS = 8
    PS5000A_PORT0_FLAGS = 65536
    PS5000A_PORT1_FLAGS = 131072
    PS5000A_PORT2_FLAGS = 262144
    PS5000A_PORT3_FLAGS = 524288


PS5000A_CHANNEL_FLAGS_T = c_int32


class PS5000A_DIGITAL_CHANNEL(IntEnum):
    PS5000A_DIGITAL_CHANNEL_0 = 0
    PS5000A_DIGITAL_CHANNEL_1 = 1
    PS5000A_DIGITAL_CHANNEL_2 = 2
    PS5000A_DIGITAL_CHANNEL_3 = 3
    PS5000A_DIGITAL_CHANNEL_4 = 4
    PS5000A_DIGITAL_CHANNEL_5 = 5
    PS5000A_DIGITAL_CHANNEL_6 = 6
    PS5000A_DIGITAL_CHANNEL_7 = 7
    PS5000A_DIGITAL_CHANNEL_8 = 8
    PS5000A_DIGITAL_CHANNEL_9 = 9
    PS5000A_DIGITAL_CHANNEL_10 = 10
    PS5000A_DIGITAL_CHANNEL_11 = 11
    PS5000A_DIGITAL_CHANNEL_12 = 12
    PS5000A_DIGITAL_CHANNEL_13 = 13
    PS5000A_DIGITAL_CHANNEL_14 = 14
    PS5000A_DIGITAL_CHANNEL_15 = 15
    PS5000A_DIGITAL_CHANNEL_16 = 16
    PS5000A_DIGITAL_CHANNEL_17 = 17
    PS5000A_DIGITAL_CHANNEL_18 = 18
    PS5000A_DIGITAL_CHANNEL_19 = 19
    PS5000A_DIGITAL_CHANNEL_20 = 20
    PS5000A_DIGITAL_CHANNEL_21 = 21
    PS5000A_DIGITAL_CHANNEL_22 = 22
    PS5000A_DIGITAL_CHANNEL_23 = 23
    PS5000A_DIGITAL_CHANNEL_24 = 24
    PS5000A_DIGITAL_CHANNEL_25 = 25
    PS5000A_DIGITAL_CHANNEL_26 = 26
    PS5000A_DIGITAL_CHANNEL_27 = 27
    PS5000A_DIGITAL_CHANNEL_28 = 28
    PS5000A_DIGITAL_CHANNEL_29 = 29
    PS5000A_DIGITAL_CHANNEL_30 = 30
    PS5000A_DIGITAL_CHANNEL_31 = 31
    PS5000A_MAX_DIGITAL_CHANNELS = 32


PS5000A_DIGITAL_CHANNEL_T = c_int32


class PS5000A_DIGITAL_DIRECTION(IntEnum):
    PS5000A_DIGITAL_DONT_CARE = 0
    PS5000A_DIGITAL_DIRECTION_LOW = 1
    PS5000A_DIGITAL_DIRECTION_HIGH = 2
    PS5000A_DIGITAL_DIRECTION_RISING = 3
    PS5000A_DIGITAL_DIRECTION_FALLING = 4
    PS5000A_DIGITAL_DIRECTION_RISING_OR_FALLING = 5
    PS5000A_DIGITAL_MAX_DIRECTION = 6


PS5000A_DIGITAL_DIRECTION_T = c_int32


class PS5000A_RANGE(IntEnum):
    PS5000A_10MV = 0
    PS5000A_20MV = 1
    PS5000A_50MV = 2
    PS5000A_100MV = 3
    PS5000A_200MV = 4
    PS5000A_500MV = 5
    PS5000A_1V = 6
    PS5000A_2V = 7
    PS5000A_5V = 8
    PS5000A_10V = 9
    PS5000A_20V = 10
    PS5000A_50V = 11
    PS5000A_MAX_RANGES = 12


PS5000A_RANGE_T = c_int32


class PS5000A_ETS_MODE(IntEnum):
    PS5000A_ETS_OFF = 0
    PS5000A_ETS_FAST = 1
    PS5000A_ETS_SLOW = 2
    PS5000A_ETS_MODES_MAX = 3


PS5000A_ETS_MODE_T = c_int32


class PS5000A_TIME_UNITS(IntEnum):
    PS5000A_FS = 0
    PS5000A_PS = 1
    PS5000A_NS = 2
    PS5000A_US = 3
    PS5000A_MS = 4
    PS5000A_S = 5
    PS5000A_MAX_TIME_UNITS = 6


PS5000A_TIME_UNITS_T = c_int32


class PS5000A_SWEEP_TYPE(IntEnum):
    PS5000A_UP = 0
    PS5000A_DOWN = 1
    PS5000A_UPDOWN = 2
    PS5000A_DOWNUP = 3
    PS5000A_MAX_SWEEP_TYPES = 4


PS5000A_SWEEP_TYPE_T = c_int32


class PS5000A_WAVE_TYPE(IntEnum):
    PS5000A_SINE = 0
    PS5000A_SQUARE = 1
    PS5000A_TRIANGLE = 2
    PS5000A_RAMP_UP = 3
    PS5000A_RAMP_DOWN = 4
    PS5000A_SINC = 5
    PS5000A_GAUSSIAN = 6
    PS5000A_HALF_SINE = 7
    PS5000A_DC_VOLTAGE = 8
    PS5000A_WHITE_NOISE = 9
    PS5000A_MAX_WAVE_TYPES = 10


PS5000A_WAVE_TYPE_T = c_int32


class PS5000A_CONDITIONS_INFO(IntEnum):
    PS5000A_CLEAR = 0x00000001
    PS5000A_ADD = 0x00000002


PS5000A_CONDITIONS_INFO_T = c_int32


PS5000A_SINE_MAX_FREQUENCY = 20000000.0
PS5000A_SQUARE_MAX_FREQUENCY = 20000000.0
PS5000A_TRIANGLE_MAX_FREQUENCY = 20000000.0
PS5000A_SINC_MAX_FREQUENCY = 20000000.0
PS5000A_RAMP_MAX_FREQUENCY = 20000000.0
PS5000A_HALF_SINE_MAX_FREQUENCY = 20000000.0
PS5000A_GAUSSIAN_MAX_FREQUENCY = 20000000.0
PS5000A_MIN_FREQUENCY = 0.03


class PS5000A_SIGGEN_TRIG_TYPE(IntEnum):
    PS5000A_SIGGEN_RISING = 0
    PS5000A_SIGGEN_FALLING = 1
    PS5000A_SIGGEN_GATE_HIGH = 2
    PS5000A_SIGGEN_GATE_LOW = 3


PS5000A_SIGGEN_TRIG_TYPE_T = c_int32


class PS5000A_SIGGEN_TRIG_SOURCE(IntEnum):
    PS5000A_SIGGEN_NONE = 0
    PS5000A_SIGGEN_SCOPE_TRIG = 1
    PS5000A_SIGGEN_AUX_IN = 2
    PS5000A_SIGGEN_EXT_IN = 3
    PS5000A_SIGGEN_SOFT_TRIG = 4


PS5000A_SIGGEN_TRIG_SOURCE_T = c_int32


class PS5000A_INDEX_MODE(IntEnum):
    PS5000A_SINGLE = 0
    PS5000A_DUAL = 1
    PS5000A_QUAD = 2
    PS5000A_MAX_INDEX_MODES = 3


PS5000A_INDEX_MODE_T = c_int32


class PS5000A_THRESHOLD_MODE(IntEnum):
    PS5000A_LEVEL = 0
    PS5000A_WINDOW = 1


PS5000A_THRESHOLD_MODE_T = c_int32


class PS5000A_THRESHOLD_DIRECTION(IntEnum):
    PS5000A_ABOVE = 0
    PS5000A_BELOW = 1
    PS5000A_RISING = 2
    PS5000A_FALLING = 3
    PS5000A_RISING_OR_FALLING = 4
    PS5000A_ABOVE_LOWER = 5
    PS5000A_BELOW_LOWER = 6
    PS5000A_RISING_LOWER = 7
    PS5000A_FALLING_LOWER = 8
    PS5000A_INSIDE = PS5000A_ABOVE
    PS5000A_OUTSIDE = PS5000A_BELOW
    PS5000A_ENTER = PS5000A_RISING
    PS5000A_EXIT = PS5000A_FALLING
    PS5000A_ENTER_OR_EXIT = PS5000A_RISING_OR_FALLING
    PS5000A_POSITIVE_RUNT = 9
    PS5000A_NEGATIVE_RUNT = 10
    PS5000A_NONE = PS5000A_RISING


PS5000A_THRESHOLD_DIRECTION_T = c_int32


class PS5000A_TRIGGER_STATE(IntEnum):
    PS5000A_CONDITION_DONT_CARE = 0
    PS5000A_CONDITION_TRUE = 1
    PS5000A_CONDITION_FALSE = 2
    PS5000A_CONDITION_MAX = 3


PS5000A_TRIGGER_STATE_T = c_int32


class PS5000A_TRIGGER_WITHIN_PRE_TRIGGER(IntEnum):
    PS5000A_DISABLE = 0
    PS5000A_ARM = 1


PS5000A_TRIGGER_WITHIN_PRE_TRIGGER_T = c_int32


class PS5000A_RATIO_MODE(IntFlag):
    PS5000A_RATIO_MODE_NONE = 0
    PS5000A_RATIO_MODE_AGGREGATE = 1
    PS5000A_RATIO_MODE_DECIMATE = 2
    PS5000A_RATIO_MODE_AVERAGE = 4
    PS5000A_RATIO_MODE_DISTRIBUTION = 8


PS5000A_RATIO_MODE_T = c_int32


class PS5000A_PULSE_WIDTH_TYPE(IntEnum):
    PS5000A_PW_TYPE_NONE = 0
    PS5000A_PW_TYPE_LESS_THAN = 1
    PS5000A_PW_TYPE_GREATER_THAN = 2
    PS5000A_PW_TYPE_IN_RANGE = 3
    PS5000A_PW_TYPE_OUT_OF_RANGE = 4


PS5000A_PULSE_WIDTH_TYPE_T = c_int32


class PS5000A_CHANNEL_INFO(IntEnum):
    PS5000A_CI_RANGES = 0


PS5000A_CHANNEL_INFO_T = c_int32


@final
class PS5000A_TRIGGER_INFO(Structure):
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
class PS5000A_TRIGGER_CONDITIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", PS5000A_TRIGGER_STATE_T),
        ("channelB", PS5000A_TRIGGER_STATE_T),
        ("channelC", PS5000A_TRIGGER_STATE_T),
        ("channelD", PS5000A_TRIGGER_STATE_T),
        ("external", PS5000A_TRIGGER_STATE_T),
        ("aux", PS5000A_TRIGGER_STATE_T),
        ("pulseWidthQualifier", PS5000A_TRIGGER_STATE_T),
    ]


@final
class PS5000A_CONDITION(Structure):
    _pack_ = 1
    _fields_ = [
        ("source", PS5000A_CHANNEL_T),
        ("condition", PS5000A_TRIGGER_STATE_T),
    ]


@final
class PS5000A_DIRECTION(Structure):
    _pack_ = 1
    _fields_ = [
        ("source", PS5000A_CHANNEL_T),
        ("direction", PS5000A_THRESHOLD_DIRECTION_T),
        ("mode", PS5000A_THRESHOLD_MODE_T),
    ]


@final
class PS5000A_PWQ_CONDITIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", PS5000A_TRIGGER_STATE_T),
        ("channelB", PS5000A_TRIGGER_STATE_T),
        ("channelC", PS5000A_TRIGGER_STATE_T),
        ("channelD", PS5000A_TRIGGER_STATE_T),
        ("external", PS5000A_TRIGGER_STATE_T),
        ("aux", PS5000A_TRIGGER_STATE_T),
    ]


@final
class PS5000A_SCALING_FACTORS_VALUES(Structure):
    _pack_ = 1
    _fields_ = [
        ("source", PS5000A_CHANNEL_T),
        ("range", PS5000A_RANGE_T),
        ("offset", c_int16),
        ("scalingFactor", c_double),
    ]


@final
class PS5000A_TRIGGER_CHANNEL_PROPERTIES(Structure):
    _pack_ = 1
    _fields_ = [
        ("thresholdUpper", c_int16),
        ("thresholdUpperHysteresis", c_uint16),
        ("thresholdLower", c_int16),
        ("thresholdLowerHysteresis", c_uint16),
        ("channel", PS5000A_CHANNEL_T),
        ("thresholdMode", PS5000A_THRESHOLD_MODE_T),
    ]


@final
class PS5000A_TRIGGER_CHANNEL_PROPERTIES_V2(Structure):
    _pack_ = 1
    _fields_ = [
        ("thresholdUpper", c_int16),
        ("thresholdUpperHysteresis", c_uint16),
        ("thresholdLower", c_int16),
        ("thresholdLowerHysteresis", c_uint16),
        ("channel", PS5000A_CHANNEL_T),
    ]


@final
class PS5000A_DIGITAL_CHANNEL_DIRECTIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel", PS5000A_DIGITAL_CHANNEL_T),
        ("direction", PS5000A_DIGITAL_DIRECTION_T),
    ]


ps5000aBlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps5000aDataReady = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p
)

ps5000aStreamingReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)


class PicoScope5000aWrapper(PicoScopeWrapperBase):
    _library_name = "ps5000a"

    def __init__(self, library_path: str | None = None):
        super().__init__(library_path)

        # The power source statuses report how the device is powered, e.g., that
        # channels C and D of a 4-channel unit are unavailable on USB power.
        self._ps5000aOpenUnit = self._bind(
            "ps5000aOpenUnit",
            [POINTER(c_int16), c_char_p, PS5000A_DEVICE_RESOLUTION_T],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps5000aOpenUnitAsync = self._bind(
            "ps5000aOpenUnitAsync",
            [POINTER(c_int16), c_char_p, PS5000A_DEVICE_RESOLUTION_T],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps5000aOpenUnitProgress = self._bind(
            "ps5000aOpenUnitProgress",
            [POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps5000aGetUnitInfo = self._bind(
            "ps5000aGetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps5000aFlashLed = self._bind("ps5000aFlashLed", [c_int16, c_int16])
        self._ps5000aIsLedFlashing = self._bind(
            "ps5000aIsLedFlashing", [c_int16, POINTER(c_int16)]
        )
        self._ps5000aCloseUnit = self._bind("ps5000aCloseUnit", [c_int16])
        self._ps5000aMemorySegments = self._bind(
            "ps5000aMemorySegments", [c_int16, c_uint32, POINTER(c_int32)]
        )
        self._ps5000aSetChannel = self._bind(
            "ps5000aSetChannel",
            [
                c_int16,
                PS5000A_CHANNEL_T,
                c_int16,
                PS5000A_COUPLING_T,
                PS5000A_RANGE_T,
                c_float,
            ],
        )
        self._ps5000aSetDigitalPort = self._bind(
            "ps5000aSetDigitalPort", [c_int16, PS5000A_CHANNEL_T, c_int16, c_int16]
        )
        self._ps5000aSetBandwidthFilter = self._bind(
            "ps5000aSetBandwidthFilter",
            [c_int16, PS5000A_CHANNEL_T, PS5000A_BANDWIDTH_LIMITER_T],
        )
        self._ps5000aGetTimebase = self._bind(
            "ps5000aGetTimebase",
            [
                c_int16,
                c_uint32,
                c_int32,
                POINTER(c_int32),
                POINTER(c_int32),
                c_uint32,
            ],
        )
        self._ps5000aGetTimebase2 = self._bind(
            "ps5000aGetTimebase2",
            [
                c_int16,
                c_uint32,
                c_int32,
                POINTER(c_float),
                POINTER(c_int32),
                c_uint32,
            ],
        )
        self._ps5000aNearestSampleIntervalStateless = self._bind(
            "ps5000aNearestSampleIntervalStateless",
            [
                c_int16,
                PS5000A_CHANNEL_FLAGS_T,
                c_double,
                PS5000A_DEVICE_RESOLUTION_T,
                c_uint16,
                POINTER(c_uint32),
                POINTER(c_double),
            ],
        )
        self._ps5000aGetMinimumTimebaseStateless = self._bind(
            "ps5000aGetMinimumTimebaseStateless",
            [
                c_int16,
                PS5000A_CHANNEL_FLAGS_T,
                POINTER(c_uint32),
                POINTER(c_double),
                PS5000A_DEVICE_RESOLUTION_T,
            ],
        )
        self._ps5000aChannelCombinationsStateless = self._bind(
            "ps5000aChannelCombinationsStateless",
            [
                c_int16,
                POINTER(PS5000A_CHANNEL_FLAGS_T),
                POINTER(c_uint32),
                PS5000A_DEVICE_RESOLUTION_T,
                c_uint32,
                c_int16,
            ],
        )
        self._ps5000aSetSigGenArbitrary = self._bind(
            "ps5000aSetSigGenArbitrary",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                POINTER(c_int16),
                c_int32,
                PS5000A_SWEEP_TYPE_T,
                PS5000A_EXTRA_OPERATIONS_T,
                PS5000A_INDEX_MODE_T,
                c_uint32,
                c_uint32,
                PS5000A_SIGGEN_TRIG_TYPE_T,
                PS5000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps5000aSetSigGenBuiltIn = self._bind(
            "ps5000aSetSigGenBuiltIn",
            [
                c_int16,
                c_int32,
                c_uint32,
                PS5000A_WAVE_TYPE_T,
                c_float,
                c_float,
                c_float,
                c_float,
                PS5000A_SWEEP_TYPE_T,
                PS5000A_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS5000A_SIGGEN_TRIG_TYPE_T,
                PS5000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps5000aSetSigGenBuiltInV2 = self._bind(
            "ps5000aSetSigGenBuiltInV2",
            [
                c_int16,
                c_int32,
                c_uint32,
                PS5000A_WAVE_TYPE_T,
                c_double,
                c_double,
                c_double,
                c_double,
                PS5000A_SWEEP_TYPE_T,
                PS5000A_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS5000A_SIGGEN_TRIG_TYPE_T,
                PS5000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps5000aSetSigGenPropertiesArbitrary = self._bind(
            "ps5000aSetSigGenPropertiesArbitrary",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                PS5000A_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS5000A_SIGGEN_TRIG_TYPE_T,
                PS5000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps5000aSetSigGenPropertiesBuiltIn = self._bind(
            "ps5000aSetSigGenPropertiesBuiltIn",
            [
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS5000A_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS5000A_SIGGEN_TRIG_TYPE_T,
                PS5000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps5000aSigGenFrequencyToPhase = self._bind(
            "ps5000aSigGenFrequencyToPhase",
            [c_int16, c_double, PS5000A_INDEX_MODE_T, c_uint32, POINTER(c_uint32)],
        )
        self._ps5000aSigGenArbitraryMinMaxValues = self._bind(
            "ps5000aSigGenArbitraryMinMaxValues",
            [
                c_int16,
                POINTER(c_int16),
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_uint32),
            ],
        )
        self._ps5000aSigGenSoftwareControl = self._bind(
            "ps5000aSigGenSoftwareControl", [c_int16, c_int16]
        )
        self._ps5000aSetEts = self._bind(
            "ps5000aSetEts",
            [c_int16, PS5000A_ETS_MODE_T, c_int16, c_int16, POINTER(c_int32)],
        )
        self._ps5000aGetMaxEtsValues = self._bind(
            "ps5000aGetMaxEtsValues", [c_int16, POINTER(c_int16), POINTER(c_int16)]
        )
        self._ps5000aSetTriggerChannelProperties = self._bind(
            "ps5000aSetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS5000A_TRIGGER_CHANNEL_PROPERTIES),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps5000aSetTriggerChannelPropertiesV2 = self._bind(
            "ps5000aSetTriggerChannelPropertiesV2",
            [
                c_int16,
                POINTER(PS5000A_TRIGGER_CHANNEL_PROPERTIES_V2),
                c_int16,
                c_int16,
            ],
        )
        self._ps5000aSetAutoTriggerMicroSeconds = self._bind(
            "ps5000aSetAutoTriggerMicroSeconds", [c_int16, c_uint64]
        )
        self._ps5000aSetTriggerChannelConditions = self._bind(
            "ps5000aSetTriggerChannelConditions",
            [c_int16, POINTER(PS5000A_TRIGGER_CONDITIONS), c_int16],
        )
        self._ps5000aSetTriggerChannelConditionsV2 = self._bind(
            "ps5000aSetTriggerChannelConditionsV2",
            [
                c_int16,
                POINTER(PS5000A_CONDITION),
                c_int16,
                PS5000A_CONDITIONS_INFO_T,
            ],
        )
        self._ps5000aSetTriggerChannelDirections = self._bind(
            "ps5000aSetTriggerChannelDirections",
            [
                c_int16,
                PS5000A_THRESHOLD_DIRECTION_T,
                PS5000A_THRESHOLD_DIRECTION_T,
                PS5000A_THRESHOLD_DIRECTION_T,
                PS5000A_THRESHOLD_DIRECTION_T,
                PS5000A_THRESHOLD_DIRECTION_T,
                PS5000A_THRESHOLD_DIRECTION_T,
            ],
        )
        self._ps5000aSetTriggerChannelDirectionsV2 = self._bind(
            "ps5000aSetTriggerChannelDirectionsV2",
            [c_int16, POINTER(PS5000A_DIRECTION), c_uint16],
        )
        self._ps5000aSetSimpleTrigger = self._bind(
            "ps5000aSetSimpleTrigger",
            [
                c_int16,
                c_int16,
                PS5000A_CHANNEL_T,
                c_int16,
                PS5000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_int16,
            ],
        )
        self._ps5000aSetTriggerDigitalPortProperties = self._bind(
            "ps5000aSetTriggerDigitalPortProperties",
            [c_int16, POINTER(PS5000A_DIGITAL_CHANNEL_DIRECTIONS), c_int16],
        )
        self._ps5000aSetPulseWidthDigitalPortProperties = self._bind(
            "ps5000aSetPulseWidthDigitalPortProperties",
            [c_int16, POINTER(PS5000A_DIGITAL_CHANNEL_DIRECTIONS), c_int16],
        )
        self._ps5000aSetTriggerDelay = self._bind(
            "ps5000aSetTriggerDelay", [c_int16, c_uint32]
        )
        self._ps5000aSetPulseWidthQualifier = self._bind(
            "ps5000aSetPulseWidthQualifier",
            [
                c_int16,
                POINTER(PS5000A_PWQ_CONDITIONS),
                c_int16,
                PS5000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS5000A_PULSE_WIDTH_TYPE_T,
            ],
        )
        self._ps5000aSetPulseWidthQualifierProperties = self._bind(
            "ps5000aSetPulseWidthQualifierProperties",
            [c_int16, c_uint32, c_uint32, PS5000A_PULSE_WIDTH_TYPE_T],
        )
        self._ps5000aSetPulseWidthQualifierConditions = self._bind(
            "ps5000aSetPulseWidthQualifierConditions",
            [
                c_int16,
                POINTER(PS5000A_CONDITION),
                c_int16,
                PS5000A_CONDITIONS_INFO_T,
            ],
        )
        self._ps5000aSetPulseWidthQualifierDirections = self._bind(
            "ps5000aSetPulseWidthQualifierDirections",
            [c_int16, POINTER(PS5000A_DIRECTION), c_int16],
        )
        self._ps5000aIsTriggerOrPulseWidthQualifierEnabled = self._bind(
            "ps5000aIsTriggerOrPulseWidthQualifierEnabled",
            [c_int16, POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps5000aGetTriggerTimeOffset = self._bind(
            "ps5000aGetTriggerTimeOffset",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS5000A_TIME_UNITS_T),
                c_uint32,
            ],
        )
        self._ps5000aGetTriggerTimeOffset64 = self._bind(
            "ps5000aGetTriggerTimeOffset64",
            [c_int16, POINTER(c_int64), POINTER(PS5000A_TIME_UNITS_T), c_uint32],
        )
        self._ps5000aGetValuesTriggerTimeOffsetBulk = self._bind(
            "ps5000aGetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS5000A_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps5000aGetValuesTriggerTimeOffsetBulk64 = self._bind(
            "ps5000aGetValuesTriggerTimeOffsetBulk64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS5000A_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps5000aSetDataBuffers = self._bind(
            "ps5000aSetDataBuffers",
            [
                c_int16,
                PS5000A_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_int32,
                c_uint32,
                PS5000A_RATIO_MODE_T,
            ],
        )
        self._ps5000aSetDataBuffer = self._bind(
            "ps5000aSetDataBuffer",
            [
                c_int16,
                PS5000A_CHANNEL_T,
                c_void_p,
                c_int32,
                c_uint32,
                PS5000A_RATIO_MODE_T,
            ],
        )
        self._ps5000aSetUnscaledDataBuffers = self._bind(
            "ps5000aSetUnscaledDataBuffers",
            [
                c_int16,
                PS5000A_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_int32,
                c_uint32,
                PS5000A_RATIO_MODE_T,
            ],
        )
        self._ps5000aSetEtsTimeBuffer = self._bind(
            "ps5000aSetEtsTimeBuffer", [c_int16, c_void_p, c_int32]
        )
        self._ps5000aSetEtsTimeBuffers = self._bind(
            "ps5000aSetEtsTimeBuffers", [c_int16, c_void_p, c_void_p, c_int32]
        )
        self._ps5000aIsReady = self._bind("ps5000aIsReady", [c_int16, POINTER(c_int16)])
        self._ps5000aRunBlock = self._bind(
            "ps5000aRunBlock",
            [
                c_int16,
                c_int32,
                c_int32,
                c_uint32,
                POINTER(c_int32),
                c_uint32,
                ps5000aBlockReady,
                c_void_p,
            ],
        )
        self._ps5000aRunStreaming = self._bind(
            "ps5000aRunStreaming",
            [
                c_int16,
                POINTER(c_uint32),
                PS5000A_TIME_UNITS_T,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint32,
                PS5000A_RATIO_MODE_T,
                c_uint32,
            ],
        )
        # PICO_BUSY: no new streaming data is available yet; poll again later.
        self._ps5000aGetStreamingLatestValues = self._bind(
            "ps5000aGetStreamingLatestValues",
            [c_int16, ps5000aStreamingReady, c_void_p],
            info=(PICO_STATUS.PICO_BUSY,),
        )
        self._ps5000aNoOfStreamingValues = self._bind(
            "ps5000aNoOfStreamingValues", [c_int16, POINTER(c_uint32)]
        )
        self._ps5000aGetMaxDownSampleRatio = self._bind(
            "ps5000aGetMaxDownSampleRatio",
            [c_int16, c_uint32, POINTER(c_uint32), PS5000A_RATIO_MODE_T, c_uint32],
        )
        self._ps5000aGetValues = self._bind(
            "ps5000aGetValues",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS5000A_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        # The header declares lpDataReady as void*; the callback type is ABI
        # compatible and lets ctypes check the argument.
        self._ps5000aGetValuesAsync = self._bind(
            "ps5000aGetValuesAsync",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                PS5000A_RATIO_MODE_T,
                c_uint32,
                ps5000aDataReady,
                c_void_p,
            ],
        )
        self._ps5000aGetValuesBulk = self._bind(
            "ps5000aGetValuesBulk",
            [
                c_int16,
                POINTER(c_uint32),
                c_uint32,
                c_uint32,
                c_uint32,
                PS5000A_RATIO_MODE_T,
                POINTER(c_int16),
            ],
        )
        self._ps5000aGetValuesOverlapped = self._bind(
            "ps5000aGetValuesOverlapped",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS5000A_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps5000aGetValuesOverlappedBulk = self._bind(
            "ps5000aGetValuesOverlappedBulk",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS5000A_RATIO_MODE_T,
                c_uint32,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps5000aTriggerWithinPreTriggerSamples = self._bind(
            "ps5000aTriggerWithinPreTriggerSamples",
            [c_int16, PS5000A_TRIGGER_WITHIN_PRE_TRIGGER_T],
        )
        self._ps5000aGetTriggerInfoBulk = self._bind(
            "ps5000aGetTriggerInfoBulk",
            [c_int16, POINTER(PS5000A_TRIGGER_INFO), c_uint32, c_uint32],
        )
        self._ps5000aEnumerateUnits = self._bind(
            "ps5000aEnumerateUnits",
            [POINTER(c_int16), c_char_p, POINTER(c_int16)],
            # Finding no units is a valid enumeration result, not a failure.
            info=(PICO_STATUS.PICO_NOT_FOUND,),
        )
        self._ps5000aGetChannelInformation = self._bind(
            "ps5000aGetChannelInformation",
            [
                c_int16,
                PS5000A_CHANNEL_INFO_T,
                c_int32,
                POINTER(c_int32),
                POINTER(c_int32),
                c_int32,
            ],
        )
        self._ps5000aMaximumValue = self._bind(
            "ps5000aMaximumValue", [c_int16, POINTER(c_int16)]
        )
        self._ps5000aMinimumValue = self._bind(
            "ps5000aMinimumValue", [c_int16, POINTER(c_int16)]
        )
        self._ps5000aGetAnalogueOffset = self._bind(
            "ps5000aGetAnalogueOffset",
            [
                c_int16,
                PS5000A_RANGE_T,
                PS5000A_COUPLING_T,
                POINTER(c_float),
                POINTER(c_float),
            ],
        )
        self._ps5000aGetMaxSegments = self._bind(
            "ps5000aGetMaxSegments", [c_int16, POINTER(c_uint32)]
        )
        # Changing or querying the power source reports the (new) power source.
        self._ps5000aChangePowerSource = self._bind(
            "ps5000aChangePowerSource",
            [c_int16, PICO_STATUS_T],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps5000aCurrentPowerSource = self._bind(
            "ps5000aCurrentPowerSource", [c_int16], info=POWER_SOURCE_STATUSES
        )
        self._ps5000aStop = self._bind("ps5000aStop", [c_int16])
        # A responding unit may report its power source instead of PICO_OK.
        self._ps5000aPingUnit = self._bind(
            "ps5000aPingUnit", [c_int16], info=POWER_SOURCE_STATUSES
        )
        self._ps5000aSetNoOfCaptures = self._bind(
            "ps5000aSetNoOfCaptures", [c_int16, c_uint32]
        )
        self._ps5000aGetNoOfCaptures = self._bind(
            "ps5000aGetNoOfCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps5000aGetNoOfProcessedCaptures = self._bind(
            "ps5000aGetNoOfProcessedCaptures", [c_int16, POINTER(c_uint32)]
        )
        # Changing the resolution re-evaluates the available channels and may
        # report the power source, like opening the unit does.
        self._ps5000aSetDeviceResolution = self._bind(
            "ps5000aSetDeviceResolution",
            [c_int16, PS5000A_DEVICE_RESOLUTION_T],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps5000aGetDeviceResolution = self._bind(
            "ps5000aGetDeviceResolution",
            [c_int16, POINTER(PS5000A_DEVICE_RESOLUTION_T)],
        )
        self._ps5000aQueryOutputEdgeDetect = self._bind(
            "ps5000aQueryOutputEdgeDetect", [c_int16, POINTER(c_int16)]
        )
        self._ps5000aSetOutputEdgeDetect = self._bind(
            "ps5000aSetOutputEdgeDetect", [c_int16, c_int16]
        )
        self._ps5000aGetScalingValues = self._bind(
            "ps5000aGetScalingValues",
            [c_int16, POINTER(PS5000A_SCALING_FACTORS_VALUES), c_int16],
        )
        self._ps5000aCheckForUpdate = self._bind(
            "ps5000aCheckForUpdate",
            [
                c_int16,
                POINTER(PICO_VERSION),
                POINTER(PICO_VERSION),
                POINTER(c_uint16),
            ],
        )
        self._ps5000aStartFirmwareUpdate = self._bind(
            "ps5000aStartFirmwareUpdate", [c_int16, PicoUpdateFirmwareProgress]
        )

    def ps5000aOpenUnit(
        self, serial: str | None, resolution: PS5000A_DEVICE_RESOLUTION
    ):
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        return (
            self._ps5000aOpenUnit(byref(handle), ser, resolution),
            handle,
        )

    def ps5000aOpenUnitAsync(
        self, serial: str | None, resolution: PS5000A_DEVICE_RESOLUTION
    ) -> tuple[PICO_STATUS, bool]:
        """Start opening a unit; the flag tells whether the operation started."""
        started = c_int16(0)
        ser = serial.encode() if serial is not None else None
        status = self._ps5000aOpenUnitAsync(byref(started), ser, resolution)
        return status, started.value == 1

    def ps5000aOpenUnitProgress(self) -> tuple[PICO_STATUS, c_int16, int, bool]:
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        status = self._ps5000aOpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return status, handle, progressPercent.value, complete.value != 0

    def ps5000aCloseUnit(self, handle: c_int16):
        return self._ps5000aCloseUnit(handle)

    def ps5000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._ps5000aGetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return status, infostr

    def ps5000aFlashLed(self, handle: c_int16, start: int) -> PICO_STATUS:
        """Flash the LED ``start`` times; -1 flashes indefinitely, 0 stops."""
        return self._ps5000aFlashLed(handle, start)

    def ps5000aIsLedFlashing(self, handle: c_int16) -> tuple[PICO_STATUS, bool]:
        flashing = c_int16(0)
        status = self._ps5000aIsLedFlashing(handle, byref(flashing))
        return status, flashing.value != 0

    def ps5000aMemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_int32(0)
        return (
            self._ps5000aMemorySegments(handle, nsegments, byref(maxSamples)),
            maxSamples.value,
        )

    def ps5000aSetChannel(
        self,
        handle: c_int16,
        channel: PS5000A_CHANNEL,
        enabled: bool,
        coupling: PS5000A_COUPLING,
        range: PS5000A_RANGE,
        analog_offset: float,
    ):
        return self._ps5000aSetChannel(
            handle,
            channel,
            1 if enabled else 0,
            coupling,
            range,
            c_float(analog_offset),
        )

    def ps5000aSetDigitalPort(
        self, handle: c_int16, port: PS5000A_CHANNEL, enabled: bool, logicLevel: int
    ) -> PICO_STATUS:
        return self._ps5000aSetDigitalPort(
            handle, port, 1 if enabled else 0, logicLevel
        )

    def ps5000aSetBandwidthFilter(
        self,
        handle: c_int16,
        channel: PS5000A_CHANNEL,
        bandwidth: PS5000A_BANDWIDTH_LIMITER,
    ):
        return self._ps5000aSetBandwidthFilter(handle, channel, bandwidth)

    def ps5000aGetTimebase(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_int32(0)
        status = self._ps5000aGetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            byref(maxSamples),
            segmentIndex,
        )
        return status, timeIntervalNanoseconds.value, maxSamples.value

    def ps5000aGetTimebase2(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ):
        timeIntervalNS = c_float(0)
        maxSamples = c_int32(0)
        return (
            self._ps5000aGetTimebase2(
                handle,
                timebase,
                noSamples,
                byref(timeIntervalNS),
                byref(maxSamples),
                segmentIndex,
            ),
            timeIntervalNS.value,
            maxSamples.value,
        )

    def ps5000aNearestSampleIntervalStateless(
        self,
        handle: c_int16,
        enabledChannelOrPortFlags: PS5000A_CHANNEL_FLAGS,
        timeIntervalRequested: float,
        resolution: PS5000A_DEVICE_RESOLUTION,
        useEts: bool,
    ) -> tuple[PICO_STATUS, int, float]:
        timebase = c_uint32(0)
        timeIntervalAvailable = c_double(0)
        status = self._ps5000aNearestSampleIntervalStateless(
            handle,
            enabledChannelOrPortFlags,
            timeIntervalRequested,
            resolution,
            1 if useEts else 0,
            byref(timebase),
            byref(timeIntervalAvailable),
        )
        return status, timebase.value, timeIntervalAvailable.value

    def ps5000aGetMinimumTimebaseStateless(
        self,
        handle: c_int16,
        enabledChannelOrPortFlags: PS5000A_CHANNEL_FLAGS,
        resolution: PS5000A_DEVICE_RESOLUTION,
    ) -> tuple[PICO_STATUS, int, float]:
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        status = self._ps5000aGetMinimumTimebaseStateless(
            handle,
            enabledChannelOrPortFlags,
            byref(timebase),
            byref(timeInterval),
            resolution,
        )
        return status, timebase.value, timeInterval.value

    def ps5000aChannelCombinationsStateless(
        self,
        handle: c_int16,
        nChannelCombinations: int,
        resolution: PS5000A_DEVICE_RESOLUTION,
        timebase: int,
        hasDcPowerSupplyConnected: bool,
    ) -> tuple[PICO_STATUS, list[PS5000A_CHANNEL_FLAGS]]:
        """``nChannelCombinations`` is the capacity of the result array."""
        assert nChannelCombinations > 0
        combinations = (PS5000A_CHANNEL_FLAGS_T * nChannelCombinations)()
        count = c_uint32(nChannelCombinations)
        status = self._ps5000aChannelCombinationsStateless(
            handle,
            combinations,
            byref(count),
            resolution,
            timebase,
            1 if hasDcPowerSupplyConnected else 0,
        )
        n = min(count.value, nChannelCombinations)
        return status, [PS5000A_CHANNEL_FLAGS(c) for c in combinations[:n]]

    def ps5000aSetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: Sequence[int],
        sweepType: PS5000A_SWEEP_TYPE,
        operation: PS5000A_EXTRA_OPERATIONS,
        indexMode: PS5000A_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS5000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        waveform = (c_int16 * len(arbitraryWaveform))(*arbitraryWaveform)
        return self._ps5000aSetSigGenArbitrary(
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

    def ps5000aSetSigGenBuiltIn(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS5000A_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS5000A_SWEEP_TYPE,
        operation: PS5000A_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS5000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps5000aSetSigGenBuiltIn(
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

    def ps5000aSetSigGenBuiltInV2(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS5000A_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS5000A_SWEEP_TYPE,
        operation: PS5000A_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS5000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps5000aSetSigGenBuiltInV2(
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

    def ps5000aSetSigGenPropertiesArbitrary(
        self,
        handle: c_int16,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PS5000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS5000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps5000aSetSigGenPropertiesArbitrary(
            handle,
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

    def ps5000aSetSigGenPropertiesBuiltIn(
        self,
        handle: c_int16,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS5000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS5000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS5000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps5000aSetSigGenPropertiesBuiltIn(
            handle,
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

    def ps5000aSigGenFrequencyToPhase(
        self,
        handle: c_int16,
        frequency: float,
        indexMode: PS5000A_INDEX_MODE,
        bufferLength: int,
    ) -> tuple[PICO_STATUS, int]:
        phase = c_uint32(0)
        status = self._ps5000aSigGenFrequencyToPhase(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return status, phase.value

    def ps5000aSigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, int, int, int, int]:
        minValue = c_int16(0)
        maxValue = c_int16(0)
        minSize = c_uint32(0)
        maxSize = c_uint32(0)
        status = self._ps5000aSigGenArbitraryMinMaxValues(
            handle, byref(minValue), byref(maxValue), byref(minSize), byref(maxSize)
        )
        return status, minValue.value, maxValue.value, minSize.value, maxSize.value

    def ps5000aSigGenSoftwareControl(self, handle: c_int16, state: int) -> PICO_STATUS:
        return self._ps5000aSigGenSoftwareControl(handle, state)

    def ps5000aSetEts(
        self,
        handle: c_int16,
        mode: PS5000A_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> tuple[PICO_STATUS, int]:
        sampleTimePicoseconds = c_int32(0)
        status = self._ps5000aSetEts(
            handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
        )
        return status, sampleTimePicoseconds.value

    def ps5000aGetMaxEtsValues(self, handle: c_int16) -> tuple[PICO_STATUS, int, int]:
        etsCycles = c_int16(0)
        etsInterleave = c_int16(0)
        status = self._ps5000aGetMaxEtsValues(
            handle, byref(etsCycles), byref(etsInterleave)
        )
        return status, etsCycles.value, etsInterleave.value

    def ps5000aSetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS5000A_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> PICO_STATUS:
        props = (PS5000A_TRIGGER_CHANNEL_PROPERTIES * len(channelProperties))(
            *channelProperties
        )
        return self._ps5000aSetTriggerChannelProperties(
            handle,
            props,
            len(channelProperties),
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps5000aSetTriggerChannelPropertiesV2(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS5000A_TRIGGER_CHANNEL_PROPERTIES_V2],
        auxOutputEnable: bool,
    ) -> PICO_STATUS:
        props = (PS5000A_TRIGGER_CHANNEL_PROPERTIES_V2 * len(channelProperties))(
            *channelProperties
        )
        return self._ps5000aSetTriggerChannelPropertiesV2(
            handle, props, len(channelProperties), 1 if auxOutputEnable else 0
        )

    def ps5000aSetAutoTriggerMicroSeconds(
        self, handle: c_int16, autoTriggerMicroseconds: int
    ) -> PICO_STATUS:
        return self._ps5000aSetAutoTriggerMicroSeconds(handle, autoTriggerMicroseconds)

    def ps5000aSetTriggerChannelConditions(
        self, handle: c_int16, conditions: Sequence[PS5000A_TRIGGER_CONDITIONS]
    ) -> PICO_STATUS:
        conds = (PS5000A_TRIGGER_CONDITIONS * len(conditions))(*conditions)
        return self._ps5000aSetTriggerChannelConditions(handle, conds, len(conditions))

    def ps5000aSetTriggerChannelConditionsV2(
        self,
        handle: c_int16,
        conditions: Sequence[PS5000A_CONDITION],
        info: PS5000A_CONDITIONS_INFO,
    ) -> PICO_STATUS:
        conds = (PS5000A_CONDITION * len(conditions))(*conditions)
        return self._ps5000aSetTriggerChannelConditionsV2(
            handle, conds, len(conditions), info
        )

    def ps5000aSetTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: PS5000A_THRESHOLD_DIRECTION,
        channelB: PS5000A_THRESHOLD_DIRECTION,
        channelC: PS5000A_THRESHOLD_DIRECTION,
        channelD: PS5000A_THRESHOLD_DIRECTION,
        ext: PS5000A_THRESHOLD_DIRECTION,
        aux: PS5000A_THRESHOLD_DIRECTION,
    ) -> PICO_STATUS:
        return self._ps5000aSetTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext, aux
        )

    def ps5000aSetTriggerChannelDirectionsV2(
        self, handle: c_int16, directions: Sequence[PS5000A_DIRECTION]
    ) -> PICO_STATUS:
        dirs = (PS5000A_DIRECTION * len(directions))(*directions)
        return self._ps5000aSetTriggerChannelDirectionsV2(handle, dirs, len(directions))

    def ps5000aSetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PS5000A_CHANNEL,
        threshold: int,
        direction: PS5000A_THRESHOLD_DIRECTION,
        delay: int,
        autoTriggerMS: int,
    ):
        assert autoTriggerMS >= 0
        return self._ps5000aSetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTriggerMS,
        )

    def ps5000aSetTriggerDigitalPortProperties(
        self,
        handle: c_int16,
        directions: Sequence[PS5000A_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> PICO_STATUS:
        dirs = (PS5000A_DIGITAL_CHANNEL_DIRECTIONS * len(directions))(*directions)
        return self._ps5000aSetTriggerDigitalPortProperties(
            handle, dirs, len(directions)
        )

    def ps5000aSetPulseWidthDigitalPortProperties(
        self,
        handle: c_int16,
        directions: Sequence[PS5000A_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> PICO_STATUS:
        dirs = (PS5000A_DIGITAL_CHANNEL_DIRECTIONS * len(directions))(*directions)
        return self._ps5000aSetPulseWidthDigitalPortProperties(
            handle, dirs, len(directions)
        )

    def ps5000aSetTriggerDelay(self, handle: c_int16, delay: int):
        return self._ps5000aSetTriggerDelay(handle, delay)

    def ps5000aSetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS5000A_PWQ_CONDITIONS],
        direction: PS5000A_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS5000A_PULSE_WIDTH_TYPE,
    ) -> PICO_STATUS:
        conds = (PS5000A_PWQ_CONDITIONS * len(conditions))(*conditions)
        return self._ps5000aSetPulseWidthQualifier(
            handle, conds, len(conditions), direction, lower, upper, type
        )

    def ps5000aSetPulseWidthQualifierProperties(
        self,
        handle: c_int16,
        lower: int,
        upper: int,
        type: PS5000A_PULSE_WIDTH_TYPE,
    ) -> PICO_STATUS:
        return self._ps5000aSetPulseWidthQualifierProperties(handle, lower, upper, type)

    def ps5000aSetPulseWidthQualifierConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PS5000A_CONDITION],
        info: PS5000A_CONDITIONS_INFO,
    ) -> PICO_STATUS:
        conds = (PS5000A_CONDITION * len(conditions))(*conditions)
        return self._ps5000aSetPulseWidthQualifierConditions(
            handle, conds, len(conditions), info
        )

    def ps5000aSetPulseWidthQualifierDirections(
        self, handle: c_int16, directions: Sequence[PS5000A_DIRECTION]
    ) -> PICO_STATUS:
        dirs = (PS5000A_DIRECTION * len(directions))(*directions)
        return self._ps5000aSetPulseWidthQualifierDirections(
            handle, dirs, len(directions)
        )

    def ps5000aIsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        status = self._ps5000aIsTriggerOrPulseWidthQualifierEnabled(
            handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
        )
        return status, triggerEnabled.value != 0, pulseWidthQualifierEnabled.value != 0

    def ps5000aGetTriggerTimeOffset(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, int, PS5000A_TIME_UNITS]:
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS5000A_TIME_UNITS_T(0)
        status = self._ps5000aGetTriggerTimeOffset(
            handle, byref(timeUpper), byref(timeLower), byref(timeUnits), segmentIndex
        )
        return (
            status,
            timeUpper.value,
            timeLower.value,
            PS5000A_TIME_UNITS(timeUnits.value),
        )

    def ps5000aGetTriggerTimeOffset64(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, PS5000A_TIME_UNITS]:
        time = c_int64(0)
        timeUnits = PS5000A_TIME_UNITS_T(0)
        status = self._ps5000aGetTriggerTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return status, time.value, PS5000A_TIME_UNITS(timeUnits.value)

    def ps5000aGetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[int], list[PS5000A_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        n = toSegmentIndex - fromSegmentIndex + 1
        timesUpper = (c_uint32 * n)()
        timesLower = (c_uint32 * n)()
        timeUnits = (PS5000A_TIME_UNITS_T * n)()
        status = self._ps5000aGetValuesTriggerTimeOffsetBulk(
            handle, timesUpper, timesLower, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return (
            status,
            list(timesUpper),
            list(timesLower),
            [PS5000A_TIME_UNITS(u) for u in timeUnits],
        )

    def ps5000aGetValuesTriggerTimeOffsetBulk64(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[PS5000A_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        n = toSegmentIndex - fromSegmentIndex + 1
        times = (c_int64 * n)()
        timeUnits = (PS5000A_TIME_UNITS_T * n)()
        status = self._ps5000aGetValuesTriggerTimeOffsetBulk64(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return status, list(times), [PS5000A_TIME_UNITS(u) for u in timeUnits]

    def ps5000aSetDataBuffers(
        self,
        handle: c_int16,
        source: PS5000A_CHANNEL,
        bufferMax: c_void_p | int | None,
        bufferMin: c_void_p | int | None,
        bufferLth: int,
        segmentIndex: int,
        mode: PS5000A_RATIO_MODE,
    ) -> PICO_STATUS:
        return self._ps5000aSetDataBuffers(
            handle, source, bufferMax, bufferMin, bufferLth, segmentIndex, mode
        )

    def ps5000aSetDataBuffer(
        self,
        handle: c_int16,
        channel: PS5000A_CHANNEL,
        buffer: c_void_p,
        bufferLth: int,
        segmentIndex: int,
        mode: PS5000A_RATIO_MODE,
    ):
        return self._ps5000aSetDataBuffer(
            handle, channel, buffer, bufferLth, segmentIndex, mode
        )

    def ps5000aSetUnscaledDataBuffers(
        self,
        handle: c_int16,
        source: PS5000A_CHANNEL,
        bufferMax: c_void_p | int | None,
        bufferMin: c_void_p | int | None,
        bufferLth: int,
        segmentIndex: int,
        mode: PS5000A_RATIO_MODE,
    ) -> PICO_STATUS:
        """Like ``ps5000aSetDataBuffers`` but with ``int8_t`` buffers."""
        return self._ps5000aSetUnscaledDataBuffers(
            handle, source, bufferMax, bufferMin, bufferLth, segmentIndex, mode
        )

    def ps5000aSetEtsTimeBuffer(
        self, handle: c_int16, buffer: c_void_p | int | None, bufferLth: int
    ) -> PICO_STATUS:
        """``buffer`` points to ``int64_t`` values."""
        return self._ps5000aSetEtsTimeBuffer(handle, buffer, bufferLth)

    def ps5000aSetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: c_void_p | int | None,
        timeLower: c_void_p | int | None,
        bufferLth: int,
    ) -> PICO_STATUS:
        """``timeUpper`` and ``timeLower`` point to ``uint32_t`` values."""
        return self._ps5000aSetEtsTimeBuffers(handle, timeUpper, timeLower, bufferLth)

    def ps5000aIsReady(self, handle: c_int16):
        ready = c_int16(0)
        return self._ps5000aIsReady(handle, byref(ready)), ready.value == 1

    def ps5000aRunBlock(
        self,
        handle: c_int16,
        preSamples: int,
        postSamples: int,
        timebase: int,
        segment: int,
        callback: Callable[[c_int16, PICO_STATUS], None] | None,
    ):
        assert preSamples >= 0
        assert postSamples >= 0
        timeInd = c_int32(0)
        if callback is not None:

            def cbwrapper(handle: c_int16, status: int, _: int | None):
                callback(handle, PICO_STATUS(status))

            lpReady = ps5000aBlockReady(cbwrapper)
        else:
            # ctypes only accepts NULL for a function pointer as a NULL instance.
            lpReady = ps5000aBlockReady()
        status = self._with_callback(
            self._callback_key("ps5000aRunBlock", handle),
            lpReady,
            lambda: self._ps5000aRunBlock(
                handle,
                preSamples,
                postSamples,
                timebase,
                byref(timeInd),
                segment,
                lpReady,
                None,
            ),
        )
        return status, timeInd.value

    def ps5000aRunStreaming(
        self,
        handle: c_int16,
        sampleInterval: int,
        sampleIntervalTimeUnits: PS5000A_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        downSampleRatioMode: PS5000A_RATIO_MODE,
        overviewBufferSize: int,
    ) -> tuple[PICO_STATUS, int]:
        """Returns the actual sample interval chosen by the driver."""
        interval = c_uint32(sampleInterval)
        status = self._ps5000aRunStreaming(
            handle,
            byref(interval),
            sampleIntervalTimeUnits,
            maxPreTriggerSamples,
            maxPostTriggerSamples,
            1 if autoStop else 0,
            downSampleRatio,
            downSampleRatioMode,
            overviewBufferSize,
        )
        return status, interval.value

    def ps5000aGetStreamingLatestValues(
        self,
        handle: c_int16,
        callback: Callable[[int, int, int, int, int, bool, bool], None],
    ) -> PICO_STATUS:
        """``callback(handle, noOfSamples, startIndex, overflow, triggerAt,
        triggered, autoStop)`` is called when new data has been copied."""

        def cbwrapper(
            handle: int,
            noOfSamples: int,
            startIndex: int,
            overflow: int,
            triggerAt: int,
            triggered: int,
            autoStop: int,
            _: int | None,
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

        lpPs5000aReady = ps5000aStreamingReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps5000aGetStreamingLatestValues", handle),
            lpPs5000aReady,
            lambda: self._ps5000aGetStreamingLatestValues(handle, lpPs5000aReady, None),
        )

    def ps5000aNoOfStreamingValues(self, handle: c_int16) -> tuple[PICO_STATUS, int]:
        noOfValues = c_uint32(0)
        status = self._ps5000aNoOfStreamingValues(handle, byref(noOfValues))
        return status, noOfValues.value

    def ps5000aGetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggreatedSamples: int,
        downSampleRatioMode: PS5000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int]:
        maxDownSampleRatio = c_uint32(0)
        status = self._ps5000aGetMaxDownSampleRatio(
            handle,
            noOfUnaggreatedSamples,
            byref(maxDownSampleRatio),
            downSampleRatioMode,
            segmentIndex,
        )
        return status, maxDownSampleRatio.value

    def ps5000aGetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS5000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int, int]:
        """Returns the number of samples retrieved and the overflow channel bits."""
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        status = self._ps5000aGetValues(
            handle,
            startIndex,
            byref(noOfSamples_),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return status, noOfSamples_.value, overflow.value

    def ps5000aGetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS5000A_RATIO_MODE,
        segmentIndex: int,
        callback: Callable[[int, PICO_STATUS, int, int], None],
    ) -> PICO_STATUS:
        """``callback(handle, status, noOfSamples, overflow)`` is called when done."""

        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: int | None
        ):
            callback(handle, PICO_STATUS(status), noOfSamples, overflow)

        lpDataReady = ps5000aDataReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps5000aGetValuesAsync", handle),
            lpDataReady,
            lambda: self._ps5000aGetValuesAsync(
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

    def ps5000aGetValuesBulk(
        self,
        handle: c_int16,
        nosamples: int,
        fromSegment: int,
        toSegment: int,
        downsampleRatio: int,
        downsampleMode: PS5000A_RATIO_MODE,
    ):
        assert nosamples > 0
        assert fromSegment <= toSegment
        nosamples_ = c_uint32(nosamples)
        nsegments = (toSegment - fromSegment) + 1
        overflow = (c_int16 * nsegments)(0)
        return (
            self._ps5000aGetValuesBulk(
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

    def ps5000aGetValuesOverlapped(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS5000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, c_uint32, c_int16]:
        """Set up a data retrieval that is performed during the next run.

        The driver writes the number of samples and the overflow bits after
        the capture, so the returned ctypes objects are only valid then (read
        their ``.value``). They are kept alive by the wrapper until replaced.
        """
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        status = self._with_callback(
            self._callback_key("ps5000aGetValuesOverlapped", handle),
            (noOfSamples_, overflow),
            lambda: self._ps5000aGetValuesOverlapped(
                handle,
                startIndex,
                byref(noOfSamples_),
                downSampleRatio,
                downSampleRatioMode,
                segmentIndex,
                byref(overflow),
            ),
        )
        return status, noOfSamples_, overflow

    def ps5000aGetValuesOverlappedBulk(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS5000A_RATIO_MODE,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[PICO_STATUS, c_uint32, Array[c_int16]]:
        """Bulk variant of ``ps5000aGetValuesOverlapped``.

        The returned ctypes objects (sample count and per-segment overflow
        bits) are filled in by the driver after the capture.
        """
        assert fromSegmentIndex <= toSegmentIndex
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = (c_int16 * (toSegmentIndex - fromSegmentIndex + 1))()
        status = self._with_callback(
            self._callback_key("ps5000aGetValuesOverlappedBulk", handle),
            (noOfSamples_, overflow),
            lambda: self._ps5000aGetValuesOverlappedBulk(
                handle,
                startIndex,
                byref(noOfSamples_),
                downSampleRatio,
                downSampleRatioMode,
                fromSegmentIndex,
                toSegmentIndex,
                overflow,
            ),
        )
        return status, noOfSamples_, overflow

    def ps5000aTriggerWithinPreTriggerSamples(
        self, handle: c_int16, state: PS5000A_TRIGGER_WITHIN_PRE_TRIGGER
    ) -> PICO_STATUS:
        return self._ps5000aTriggerWithinPreTriggerSamples(handle, state)

    def ps5000aGetTriggerInfoBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[PS5000A_TRIGGER_INFO]]:
        assert fromSegmentIndex <= toSegmentIndex
        triggerInfo = (PS5000A_TRIGGER_INFO * (toSegmentIndex - fromSegmentIndex + 1))()
        status = self._ps5000aGetTriggerInfoBulk(
            handle, triggerInfo, fromSegmentIndex, toSegmentIndex
        )
        return status, list(triggerInfo)

    def ps5000aEnumerateUnits(self) -> tuple[PICO_STATUS, int, list[str]]:
        """Returns the number of units found and their serial numbers."""
        count = c_int16(0)
        serials = create_string_buffer(4096)
        serialLth = c_int16(len(serials))
        status = self._ps5000aEnumerateUnits(byref(count), serials, byref(serialLth))
        text = serials.value.decode("utf-8")
        return status, count.value, [s for s in text.split(",") if s]

    def ps5000aGetChannelInformation(
        self,
        handle: c_int16,
        info: PS5000A_CHANNEL_INFO,
        probe: int,
        channels: PS5000A_CHANNEL,
    ) -> tuple[PICO_STATUS, list[PS5000A_RANGE]]:
        """Returns the input ranges available on ``channels``."""
        ranges = (c_int32 * PS5000A_RANGE.PS5000A_MAX_RANGES)()
        length = c_int32(len(ranges))
        status = self._ps5000aGetChannelInformation(
            handle, info, probe, ranges, byref(length), channels
        )
        n = min(length.value, len(ranges))
        return status, [PS5000A_RANGE(r) for r in ranges[:n]]

    def ps5000aGetMaxSegments(self, handle: c_int16):
        value = c_uint32(0)
        return (
            self._ps5000aGetMaxSegments(handle, byref(value)),
            value.value,
        )

    def ps5000aMinimumValue(self, handle: c_int16):
        value = c_int16(0)
        return self._ps5000aMinimumValue(handle, byref(value)), value.value

    def ps5000aMaximumValue(self, handle: c_int16):
        value = c_int16(0)
        return self._ps5000aMaximumValue(handle, byref(value)), value.value

    def ps5000aGetAnalogueOffset(
        self, handle: c_int16, range: PS5000A_RANGE, coupling: PS5000A_COUPLING
    ):
        minv = c_float(0)
        maxv = c_float(0)
        return (
            self._ps5000aGetAnalogueOffset(
                handle, range, coupling, byref(maxv), byref(minv)
            ),
            minv.value,
            maxv.value,
        )

    def ps5000aChangePowerSource(self, handle: c_int16, source: PICO_STATUS):
        return self._ps5000aChangePowerSource(handle, source)

    def ps5000aCurrentPowerSource(self, handle: c_int16) -> PICO_STATUS:
        """Returns ``PICO_POWER_SUPPLY_CONNECTED`` or ``..._NOT_CONNECTED``."""
        return self._ps5000aCurrentPowerSource(handle)

    def ps5000aStop(self, handle: c_int16) -> PICO_STATUS:
        return self._ps5000aStop(handle)

    def ps5000aPingUnit(self, handle: c_int16) -> PICO_STATUS:
        return self._ps5000aPingUnit(handle)

    def ps5000aSetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return self._ps5000aSetNoOfCaptures(handle, ncaptures)

    def ps5000aGetNoOfCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            self._ps5000aGetNoOfCaptures(handle, byref(captures)),
            captures.value,
        )

    def ps5000aGetNoOfProcessedCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            self._ps5000aGetNoOfProcessedCaptures(handle, byref(captures)),
            captures.value,
        )

    def ps5000aSetDeviceResolution(
        self, handle: c_int16, resolution: PS5000A_DEVICE_RESOLUTION
    ) -> PICO_STATUS:
        return self._ps5000aSetDeviceResolution(handle, resolution)

    def ps5000aGetDeviceResolution(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, PS5000A_DEVICE_RESOLUTION]:
        resolution = PS5000A_DEVICE_RESOLUTION_T(0)
        status = self._ps5000aGetDeviceResolution(handle, byref(resolution))
        return status, PS5000A_DEVICE_RESOLUTION(resolution.value)

    def ps5000aQueryOutputEdgeDetect(self, handle: c_int16) -> tuple[PICO_STATUS, bool]:
        state = c_int16(0)
        status = self._ps5000aQueryOutputEdgeDetect(handle, byref(state))
        return status, state.value != 0

    def ps5000aSetOutputEdgeDetect(self, handle: c_int16, state: bool) -> PICO_STATUS:
        return self._ps5000aSetOutputEdgeDetect(handle, 1 if state else 0)

    def ps5000aGetScalingValues(
        self, handle: c_int16, nChannels: int
    ) -> tuple[PICO_STATUS, list[PS5000A_SCALING_FACTORS_VALUES]]:
        scalingValues = (PS5000A_SCALING_FACTORS_VALUES * nChannels)()
        status = self._ps5000aGetScalingValues(handle, scalingValues, nChannels)
        return status, list(scalingValues)

    def ps5000aCheckForUpdate(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, PICO_VERSION, PICO_VERSION, bool]:
        """Returns the current and available firmware versions and whether an
        update is required."""
        current = PICO_VERSION()
        update = PICO_VERSION()
        updateRequired = c_uint16(0)
        status = self._ps5000aCheckForUpdate(
            handle, byref(current), byref(update), byref(updateRequired)
        )
        return status, current, update, updateRequired.value != 0

    def ps5000aStartFirmwareUpdate(
        self, handle: c_int16, progress: Callable[[int, int], None]
    ) -> PICO_STATUS:
        """``progress(handle, progressPercent)`` reports the update progress."""

        def cbwrapper(handle: int, progressPercent: int):
            progress(handle, progressPercent)

        cprogress = PicoUpdateFirmwareProgress(cbwrapper)
        return self._with_callback(
            self._callback_key("ps5000aStartFirmwareUpdate", handle),
            cprogress,
            lambda: self._ps5000aStartFirmwareUpdate(handle, cprogress),
        )


__all__ = (
    "AWG_DAC_FREQUENCY",
    "AWG_PHASE_ACCUMULATOR",
    "MAX_ANALOGUE_OFFSET_500MV_2V",
    "MAX_ANALOGUE_OFFSET_50MV_200MV",
    "MAX_ANALOGUE_OFFSET_5V_20V",
    "MAX_SWEEPS_SHOTS",
    "MIN_ANALOGUE_OFFSET_500MV_2V",
    "MIN_ANALOGUE_OFFSET_50MV_200MV",
    "MIN_ANALOGUE_OFFSET_5V_20V",
    "MIN_DWELL_COUNT",
    "MIN_SIG_GEN_BUFFER_SIZE",
    "PS5000AB_DDS_FREQUENCY",
    "PS5000A_BANDWIDTH_LIMITER",
    "PS5000A_BANDWIDTH_LIMITER_T",
    "PS5000A_CHANNEL",
    "PS5000A_CHANNEL_FLAGS",
    "PS5000A_CHANNEL_FLAGS_T",
    "PS5000A_CHANNEL_INFO",
    "PS5000A_CHANNEL_INFO_T",
    "PS5000A_CHANNEL_T",
    "PS5000A_CONDITION",
    "PS5000A_CONDITIONS_INFO",
    "PS5000A_CONDITIONS_INFO_T",
    "PS5000A_COUPLING",
    "PS5000A_COUPLING_T",
    "PS5000A_DEVICE_RESOLUTION",
    "PS5000A_DEVICE_RESOLUTION_T",
    "PS5000A_DIGITAL_CHANNEL",
    "PS5000A_DIGITAL_CHANNEL_DIRECTIONS",
    "PS5000A_DIGITAL_CHANNEL_T",
    "PS5000A_DIGITAL_DIRECTION",
    "PS5000A_DIGITAL_DIRECTION_T",
    "PS5000A_DIRECTION",
    "PS5000A_ETS_MODE",
    "PS5000A_ETS_MODE_T",
    "PS5000A_EXTRA_OPERATIONS",
    "PS5000A_EXTRA_OPERATIONS_T",
    "PS5000A_EXT_MAX_VALUE",
    "PS5000A_EXT_MIN_VALUE",
    "PS5000A_GAUSSIAN_MAX_FREQUENCY",
    "PS5000A_HALF_SINE_MAX_FREQUENCY",
    "PS5000A_INDEX_MODE",
    "PS5000A_INDEX_MODE_T",
    "PS5000A_MAX_VALUE_16BIT",
    "PS5000A_MAX_VALUE_8BIT",
    "PS5000A_MIN_FREQUENCY",
    "PS5000A_MIN_VALUE_16BIT",
    "PS5000A_MIN_VALUE_8BIT",
    "PS5000A_PULSE_WIDTH_TYPE",
    "PS5000A_PULSE_WIDTH_TYPE_T",
    "PS5000A_PWQ_CONDITIONS",
    "PS5000A_RAMP_MAX_FREQUENCY",
    "PS5000A_RANGE",
    "PS5000A_RANGE_T",
    "PS5000A_RATIO_MODE",
    "PS5000A_RATIO_MODE_T",
    "PS5000A_SCALING_FACTORS_VALUES",
    "PS5000A_SHOT_SWEEP_TRIGGER_CONTINUOUS_RUN",
    "PS5000A_SIGGEN_TRIG_SOURCE",
    "PS5000A_SIGGEN_TRIG_SOURCE_T",
    "PS5000A_SIGGEN_TRIG_TYPE",
    "PS5000A_SIGGEN_TRIG_TYPE_T",
    "PS5000A_SINC_MAX_FREQUENCY",
    "PS5000A_SINE_MAX_FREQUENCY",
    "PS5000A_SQUARE_MAX_FREQUENCY",
    "PS5000A_SWEEP_TYPE",
    "PS5000A_SWEEP_TYPE_T",
    "PS5000A_THRESHOLD_DIRECTION",
    "PS5000A_THRESHOLD_DIRECTION_T",
    "PS5000A_THRESHOLD_MODE",
    "PS5000A_THRESHOLD_MODE_T",
    "PS5000A_TIME_UNITS",
    "PS5000A_TIME_UNITS_T",
    "PS5000A_TRIANGLE_MAX_FREQUENCY",
    "PS5000A_TRIGGER_CHANNEL_PROPERTIES",
    "PS5000A_TRIGGER_CHANNEL_PROPERTIES_V2",
    "PS5000A_TRIGGER_CONDITIONS",
    "PS5000A_TRIGGER_INFO",
    "PS5000A_TRIGGER_STATE",
    "PS5000A_TRIGGER_STATE_T",
    "PS5000A_TRIGGER_WITHIN_PRE_TRIGGER",
    "PS5000A_TRIGGER_WITHIN_PRE_TRIGGER_T",
    "PS5000A_WAVE_TYPE",
    "PS5000A_WAVE_TYPE_T",
    "PS5000D_DDS_FREQUENCY",
    "PS5242A_MAX_ETS_CYCLES",
    "PS5242A_MAX_ETS_INTERLEAVE",
    "PS5243A_MAX_ETS_CYCLES",
    "PS5243A_MAX_ETS_INTERLEAVE",
    "PS5244A_MAX_ETS_CYCLES",
    "PS5244A_MAX_ETS_INTERLEAVE",
    "PS5X42A_MAX_SIG_GEN_BUFFER_SIZE",
    "PS5X42D_MAX_ETS_CYCLES",
    "PS5X42D_MAX_ETS_INTERLEAVE",
    "PS5X43A_MAX_SIG_GEN_BUFFER_SIZE",
    "PS5X43D_MAX_ETS_CYCLES",
    "PS5X43D_MAX_ETS_INTERLEAVE",
    "PS5X44A_MAX_SIG_GEN_BUFFER_SIZE",
    "PS5X44D_MAX_ETS_CYCLES",
    "PS5X44D_MAX_ETS_INTERLEAVE",
    "PS5X4XD_MAX_SIG_GEN_BUFFER_SIZE",
    "PicoScope5000aWrapper",
    "ps5000aBlockReady",
    "ps5000aDataReady",
    "ps5000aStreamingReady",
)
