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
    c_uint64,
    c_void_p,
    create_string_buffer,
)
from enum import IntEnum
from typing import Any, final

from ._base import CALLBACK_FUNCTYPE, POWER_SOURCE_STATUSES, PicoScopeWrapperBase
from .callback import PicoUpdateFirmwareProgress
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T
from .version import PICO_FIRMWARE_INFO

PS3000A_MAX_OVERSAMPLE = 256
PS3207A_MAX_ETS_CYCLES = 500
PS3207A_MAX_INTERLEAVE = 40
PS3206A_MAX_ETS_CYCLES = 500
PS3206A_MAX_INTERLEAVE = 40
PS3206MSO_MAX_INTERLEAVE = 80
PS3205A_MAX_ETS_CYCLES = 250
PS3205A_MAX_INTERLEAVE = 20
PS3205MSO_MAX_INTERLEAVE = 40

PS3204A_MAX_ETS_CYCLES = 125
PS3204A_MAX_INTERLEAVE = 10
PS3204MSO_MAX_INTERLEAVE = 20

PS3000A_EXT_MAX_VALUE = 32767
PS3000A_EXT_MIN_VALUE = -32767

PS3000A_MAX_LOGIC_LEVEL = 32767
PS3000A_MIN_LOGIC_LEVEL = -32767

PS3000A_MIN_SIG_GEN_FREQ = 0.0
PS3000A_MAX_SIG_GEN_FREQ = 20000000.0

PS3207B_MAX_SIG_GEN_BUFFER_SIZE = 32768
PS3206B_MAX_SIG_GEN_BUFFER_SIZE = 16384
PS3000A_MAX_SIG_GEN_BUFFER_SIZE = 8192
PS3000A_MIN_SIG_GEN_BUFFER_SIZE = 1
PS3000A_MIN_DWELL_COUNT = 3
PS3000A_MAX_SWEEPS_SHOTS = (1 << 30) - 1

PS3000A_MAX_ANALOGUE_OFFSET_50MV_200MV = 0.250
PS3000A_MIN_ANALOGUE_OFFSET_50MV_200MV = -0.250
PS3000A_MAX_ANALOGUE_OFFSET_500MV_2V = 2.500
PS3000A_MIN_ANALOGUE_OFFSET_500MV_2V = -2.500
PS3000A_MAX_ANALOGUE_OFFSET_5V_20V = 20.0
PS3000A_MIN_ANALOGUE_OFFSET_5V_20V = -20.0

PS3000A_SHOT_SWEEP_TRIGGER_CONTINUOUS_RUN = 0xFFFFFFFF

PS3000A_BANDWIDTH_LIMITER_T = c_int32


class PS3000A_BANDWIDTH_LIMITER(IntEnum):
    PS3000A_BW_FULL = 0
    PS3000A_BW_20MHZ = 1


PS3000A_CHANNEL_BUFFER_INDEX_T = c_int32


class PS3000A_CHANNEL_BUFFER_INDEX(IntEnum):
    PS3000A_CHANNEL_A_MAX = 0
    PS3000A_CHANNEL_A_MIN = 1
    PS3000A_CHANNEL_B_MAX = 2
    PS3000A_CHANNEL_B_MIN = 3
    PS3000A_CHANNEL_C_MAX = 4
    PS3000A_CHANNEL_C_MIN = 5
    PS3000A_CHANNEL_D_MAX = 6
    PS3000A_CHANNEL_D_MIN = 7
    PS3000A_MAX_CHANNEL_BUFFERS = 8


PS3000A_CHANNEL_T = c_int32


class PS3000A_CHANNEL(IntEnum):
    PS3000A_CHANNEL_A = 0
    PS3000A_CHANNEL_B = 1
    PS3000A_CHANNEL_C = 2
    PS3000A_CHANNEL_D = 3
    PS3000A_EXTERNAL = 4
    PS3000A_MAX_CHANNELS = PS3000A_EXTERNAL
    PS3000A_TRIGGER_AUX = 5
    PS3000A_MAX_TRIGGER_SOURCES = 6


PS3000A_DIGITAL_PORT_T = c_int32


class PS3000A_DIGITAL_PORT(IntEnum):
    PS3000A_DIGITAL_PORT0 = 0x80
    PS3000A_DIGITAL_PORT1 = 0x81
    PS3000A_DIGITAL_PORT2 = 0x82
    PS3000A_DIGITAL_PORT3 = 0x83
    PS3000A_MAX_DIGITAL_PORTS = (PS3000A_DIGITAL_PORT3 - PS3000A_DIGITAL_PORT0) + 1


PS3000A_DIGITAL_CHANNEL_T = c_int32


class PS3000A_DIGITAL_CHANNEL(IntEnum):
    PS3000A_DIGITAL_CHANNEL_0 = 0
    PS3000A_DIGITAL_CHANNEL_1 = 1
    PS3000A_DIGITAL_CHANNEL_2 = 2
    PS3000A_DIGITAL_CHANNEL_3 = 3
    PS3000A_DIGITAL_CHANNEL_4 = 4
    PS3000A_DIGITAL_CHANNEL_5 = 5
    PS3000A_DIGITAL_CHANNEL_6 = 6
    PS3000A_DIGITAL_CHANNEL_7 = 7
    PS3000A_DIGITAL_CHANNEL_8 = 8
    PS3000A_DIGITAL_CHANNEL_9 = 9
    PS3000A_DIGITAL_CHANNEL_10 = 10
    PS3000A_DIGITAL_CHANNEL_11 = 11
    PS3000A_DIGITAL_CHANNEL_12 = 12
    PS3000A_DIGITAL_CHANNEL_13 = 13
    PS3000A_DIGITAL_CHANNEL_14 = 14
    PS3000A_DIGITAL_CHANNEL_15 = 15
    PS3000A_DIGITAL_CHANNEL_16 = 16
    PS3000A_DIGITAL_CHANNEL_17 = 17
    PS3000A_DIGITAL_CHANNEL_18 = 18
    PS3000A_DIGITAL_CHANNEL_19 = 19
    PS3000A_DIGITAL_CHANNEL_20 = 20
    PS3000A_DIGITAL_CHANNEL_21 = 21
    PS3000A_DIGITAL_CHANNEL_22 = 22
    PS3000A_DIGITAL_CHANNEL_23 = 23
    PS3000A_DIGITAL_CHANNEL_24 = 24
    PS3000A_DIGITAL_CHANNEL_25 = 25
    PS3000A_DIGITAL_CHANNEL_26 = 26
    PS3000A_DIGITAL_CHANNEL_27 = 27
    PS3000A_DIGITAL_CHANNEL_28 = 28
    PS3000A_DIGITAL_CHANNEL_29 = 29
    PS3000A_DIGITAL_CHANNEL_30 = 30
    PS3000A_DIGITAL_CHANNEL_31 = 31
    PS3000A_MAX_DIGITAL_CHANNELS = 32


PS3000A_RANGE_T = c_int32


class PS3000A_RANGE(IntEnum):
    PS3000A_10MV = 0
    PS3000A_20MV = 1
    PS3000A_50MV = 2
    PS3000A_100MV = 3
    PS3000A_200MV = 4
    PS3000A_500MV = 5
    PS3000A_1V = 6
    PS3000A_2V = 7
    PS3000A_5V = 8
    PS3000A_10V = 9
    PS3000A_20V = 10
    PS3000A_50V = 11
    PS3000A_MAX_RANGES = 12


PS3000A_COUPLING_T = c_int32


class PS3000A_COUPLING(IntEnum):
    PS3000A_AC = 0
    PS3000A_DC = 1


PS3000A_CHANNEL_INFO_T = c_int32


class PS3000A_CHANNEL_INFO(IntEnum):
    PS3000A_CI_RANGES = 0


PS3000A_ETS_MODE_T = c_int32


class PS3000A_ETS_MODE(IntEnum):
    PS3000A_ETS_OFF = 0
    PS3000A_ETS_FAST = 1
    PS3000A_ETS_SLOW = 2
    PS3000A_ETS_MODES_MAX = 3


PS3000A_TIME_UNITS_T = c_int32


class PS3000A_TIME_UNITS(IntEnum):
    PS3000A_FS = 0
    PS3000A_PS = 1
    PS3000A_NS = 2
    PS3000A_US = 3
    PS3000A_MS = 4
    PS3000A_S = 5
    PS3000A_MAX_TIME_UNITS = 6


PS3000A_SWEEP_TYPE_T = c_int32


class PS3000A_SWEEP_TYPE(IntEnum):
    PS3000A_UP = 0
    PS3000A_DOWN = 1
    PS3000A_UPDOWN = 2
    PS3000A_DOWNUP = 3
    PS3000A_MAX_SWEEP_TYPES = 4


PS3000A_WAVE_TYPE_T = c_int32


class PS3000A_WAVE_TYPE(IntEnum):
    PS3000A_SINE = 0
    PS3000A_SQUARE = 1
    PS3000A_TRIANGLE = 2
    PS3000A_RAMP_UP = 3
    PS3000A_RAMP_DOWN = 4
    PS3000A_SINC = 5
    PS3000A_GAUSSIAN = 6
    PS3000A_HALF_SINE = 7
    PS3000A_DC_VOLTAGE = 8
    PS3000A_MAX_WAVE_TYPES = 9


PS3000A_EXTRA_OPERATIONS_T = c_int32


class PS3000A_EXTRA_OPERATIONS(IntEnum):
    PS3000A_ES_OFF = 0
    PS3000A_WHITENOISE = 1
    PS3000A_PRBS = 2


PS3000A_SINE_MAX_FREQUENCY = 1000000.0
PS3000A_SQUARE_MAX_FREQUENCY = 1000000.0
PS3000A_TRIANGLE_MAX_FREQUENCY = 1000000.0
PS3000A_SINC_MAX_FREQUENCY = 1000000.0
PS3000A_RAMP_MAX_FREQUENCY = 1000000.0
PS3000A_HALF_SINE_MAX_FREQUENCY = 1000000.0
PS3000A_GAUSSIAN_MAX_FREQUENCY = 1000000.0
PS3000A_PRBS_MAX_FREQUENCY = 1000000.0
PS3000A_PRBS_MIN_FREQUENCY = 0.03
PS3000A_MIN_FREQUENCY = 0.03

PS3000A_SIGGEN_TRIG_TYPE_T = c_int32


class PS3000A_SIGGEN_TRIG_TYPE(IntEnum):
    PS3000A_SIGGEN_RISING = 0
    PS3000A_SIGGEN_FALLING = 1
    PS3000A_SIGGEN_GATE_HIGH = 2
    PS3000A_SIGGEN_GATE_LOW = 3


PS3000A_SIGGEN_TRIG_SOURCE_T = c_int32


class PS3000A_SIGGEN_TRIG_SOURCE(IntEnum):
    PS3000A_SIGGEN_NONE = 0
    PS3000A_SIGGEN_SCOPE_TRIG = 1
    PS3000A_SIGGEN_AUX_IN = 2
    PS3000A_SIGGEN_EXT_IN = 3
    PS3000A_SIGGEN_SOFT_TRIG = 4


PS3000A_INDEX_MODE_T = c_int32


class PS3000A_INDEX_MODE(IntEnum):
    PS3000A_SINGLE = 0
    PS3000A_DUAL = 1
    PS3000A_QUAD = 2
    PS3000A_MAX_INDEX_MODES = 3


PS3000A_THRESHOLD_MODE_T = c_int32


class PS3000A_THRESHOLD_MODE(IntEnum):
    PS3000A_LEVEL = 0
    PS3000A_WINDOW = 1


PS3000A_THRESHOLD_DIRECTION_T = c_int32


class PS3000A_THRESHOLD_DIRECTION(IntEnum):
    PS3000A_ABOVE = 0
    PS3000A_BELOW = 1
    PS3000A_RISING = 2
    PS3000A_FALLING = 3
    PS3000A_RISING_OR_FALLING = 4
    PS3000A_ABOVE_LOWER = 5
    PS3000A_BELOW_LOWER = 6
    PS3000A_RISING_LOWER = 7
    PS3000A_FALLING_LOWER = 8
    PS3000A_INSIDE = PS3000A_ABOVE
    PS3000A_OUTSIDE = PS3000A_BELOW
    PS3000A_ENTER = PS3000A_RISING
    PS3000A_EXIT = PS3000A_FALLING
    PS3000A_ENTER_OR_EXIT = PS3000A_RISING_OR_FALLING
    PS3000A_POSITIVE_RUNT = 9
    PS3000A_NEGATIVE_RUNT = 10
    PS3000A_NONE = PS3000A_RISING


PS3000A_DIGITAL_DIRECTION_T = c_int32


class PS3000A_DIGITAL_DIRECTION(IntEnum):
    PS3000A_DIGITAL_DONT_CARE = 0
    PS3000A_DIGITAL_DIRECTION_LOW = 1
    PS3000A_DIGITAL_DIRECTION_HIGH = 2
    PS3000A_DIGITAL_DIRECTION_RISING = 3
    PS3000A_DIGITAL_DIRECTION_FALLING = 4
    PS3000A_DIGITAL_DIRECTION_RISING_OR_FALLING = 5
    PS3000A_DIGITAL_MAX_DIRECTION = 6


PS3000A_TRIGGER_STATE_T = c_int32


class PS3000A_TRIGGER_STATE(IntEnum):
    PS3000A_CONDITION_DONT_CARE = 0
    PS3000A_CONDITION_TRUE = 1
    PS3000A_CONDITION_FALSE = 2
    PS3000A_CONDITION_MAX = 3


PS3000A_RATIO_MODE_T = c_int32


class PS3000A_RATIO_MODE(IntEnum):
    PS3000A_RATIO_MODE_NONE = 0
    PS3000A_RATIO_MODE_AGGREGATE = 1
    PS3000A_RATIO_MODE_DECIMATE = 2
    PS3000A_RATIO_MODE_AVERAGE = 4


PS3000A_PULSE_WIDTH_TYPE_T = c_int32


class PS3000A_PULSE_WIDTH_TYPE(IntEnum):
    PS3000A_PW_TYPE_NONE = 0
    PS3000A_PW_TYPE_LESS_THAN = 1
    PS3000A_PW_TYPE_GREATER_THAN = 2
    PS3000A_PW_TYPE_IN_RANGE = 3
    PS3000A_PW_TYPE_OUT_OF_RANGE = 4


PS3000A_HOLDOFF_TYPE_T = c_int32


class PS3000A_HOLDOFF_TYPE(IntEnum):
    PS3000A_TIME = 0
    PS3000A_EVENT = 1
    PS3000A_MAX_HOLDOFF_TYPE = 2


@final
class PS3000A_TRIGGER_CONDITIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", PS3000A_TRIGGER_STATE_T),
        ("channelB", PS3000A_TRIGGER_STATE_T),
        ("channelC", PS3000A_TRIGGER_STATE_T),
        ("channelD", PS3000A_TRIGGER_STATE_T),
        ("external", PS3000A_TRIGGER_STATE_T),
        ("aux", PS3000A_TRIGGER_STATE_T),
        ("pulseWidthQualifier", PS3000A_TRIGGER_STATE_T),
    ]


@final
class PS3000A_TRIGGER_CONDITIONS_V2(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", PS3000A_TRIGGER_STATE_T),
        ("channelB", PS3000A_TRIGGER_STATE_T),
        ("channelC", PS3000A_TRIGGER_STATE_T),
        ("channelD", PS3000A_TRIGGER_STATE_T),
        ("external", PS3000A_TRIGGER_STATE_T),
        ("aux", PS3000A_TRIGGER_STATE_T),
        ("pulseWidthQualifier", PS3000A_TRIGGER_STATE_T),
        ("digital", PS3000A_TRIGGER_STATE_T),
    ]


@final
class PS3000A_PWQ_CONDITIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", PS3000A_TRIGGER_STATE_T),
        ("channelB", PS3000A_TRIGGER_STATE_T),
        ("channelC", PS3000A_TRIGGER_STATE_T),
        ("channelD", PS3000A_TRIGGER_STATE_T),
        ("external", PS3000A_TRIGGER_STATE_T),
        ("aux", PS3000A_TRIGGER_STATE_T),
    ]


@final
class PS3000A_PWQ_CONDITIONS_V2(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelA", PS3000A_TRIGGER_STATE_T),
        ("channelB", PS3000A_TRIGGER_STATE_T),
        ("channelC", PS3000A_TRIGGER_STATE_T),
        ("channelD", PS3000A_TRIGGER_STATE_T),
        ("external", PS3000A_TRIGGER_STATE_T),
        ("aux", PS3000A_TRIGGER_STATE_T),
        ("digital", PS3000A_TRIGGER_STATE_T),
    ]


@final
class PS3000A_DIGITAL_CHANNEL_DIRECTIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel", PS3000A_DIGITAL_CHANNEL_T),
        ("direction", PS3000A_DIGITAL_DIRECTION_T),
    ]


@final
class PS3000A_TRIGGER_CHANNEL_PROPERTIES(Structure):
    _pack_ = 1
    _fields_ = [
        ("thresholdUpper", c_int16),
        ("thresholdUpperHysteresis", c_uint16),
        ("thresholdLower", c_int16),
        ("thresholdLowerHysteresis", c_uint16),
        ("channel", PS3000A_CHANNEL_T),
        ("thresholdMode", PS3000A_THRESHOLD_MODE_T),
    ]


@final
class PS3000A_TRIGGER_INFO(Structure):
    _pack_ = 1
    _fields_ = [
        ("status", PICO_STATUS_T),
        ("segmentIndex", c_uint32),
        ("reserved0", c_uint32),
        ("triggerTime", c_int64),
        ("timeUnits", c_int16),
        ("reserved1", c_int16),
        ("timeStampCounter", c_uint64),
    ]


@final
class PS3000A_SCALING_FACTORS_VALUES(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelOrPort", PS3000A_CHANNEL_T),
        ("range", PS3000A_RANGE_T),
        ("offset", c_int16),
        ("scalingFactor", c_double),
    ]


ps3000aBlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps3000aDataReady = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p
)

ps3000aStreamingReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)

# Upper bound for the number of firmware infos returned by ps3000aCheckForUpdate.
_MAX_FIRMWARE_INFOS = 16
# Size of the buffer receiving the comma separated serials of ps3000aEnumerateUnits.
_ENUMERATE_BUFFER_SIZE = 4096


def _array(ctype: Any, values: Sequence[Any]) -> Any:
    """Convert ``values`` to a ctypes array of ``ctype``, or NULL if empty."""
    if len(values) == 0:
        return None
    return (ctype * len(values))(*values)


class PicoScope3000aWrapper(PicoScopeWrapperBase):
    _library_name = "ps3000a"

    def __init__(self, library_path: str | None = None):
        super().__init__(library_path)

        # The power source statuses report how the device is powered, which
        # determines the available channels; the unit is opened nonetheless.
        self._ps3000aOpenUnit = self._bind(
            "ps3000aOpenUnit",
            [POINTER(c_int16), c_char_p],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps3000aOpenUnitAsync = self._bind(
            "ps3000aOpenUnitAsync",
            [POINTER(c_int16), c_char_p],
            info=POWER_SOURCE_STATUSES,
        )
        # Reports the power source once the asynchronous open has completed.
        self._ps3000aOpenUnitProgress = self._bind(
            "ps3000aOpenUnitProgress",
            [POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps3000aGetUnitInfo = self._bind(
            "ps3000aGetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps3000aFlashLed = self._bind("ps3000aFlashLed", [c_int16, c_int16])
        self._ps3000aCloseUnit = self._bind("ps3000aCloseUnit", [c_int16])
        self._ps3000aMemorySegments = self._bind(
            "ps3000aMemorySegments", [c_int16, c_uint32, POINTER(c_int32)]
        )
        self._ps3000aSetChannel = self._bind(
            "ps3000aSetChannel",
            [
                c_int16,
                PS3000A_CHANNEL_T,
                c_int16,
                PS3000A_COUPLING_T,
                PS3000A_RANGE_T,
                c_float,
            ],
        )
        self._ps3000aSetDigitalPort = self._bind(
            "ps3000aSetDigitalPort",
            [c_int16, PS3000A_DIGITAL_PORT_T, c_int16, c_int16],
        )
        self._ps3000aSetBandwidthFilter = self._bind(
            "ps3000aSetBandwidthFilter",
            [c_int16, PS3000A_CHANNEL_T, PS3000A_BANDWIDTH_LIMITER_T],
        )
        self._ps3000aSetNoOfCaptures = self._bind(
            "ps3000aSetNoOfCaptures", [c_int16, c_uint32]
        )
        self._ps3000aGetTimebase = self._bind(
            "ps3000aGetTimebase",
            [
                c_int16,
                c_uint32,
                c_int32,
                POINTER(c_int32),
                c_int16,
                POINTER(c_int32),
                c_uint32,
            ],
        )
        self._ps3000aGetTimebase2 = self._bind(
            "ps3000aGetTimebase2",
            [
                c_int16,
                c_uint32,
                c_int32,
                POINTER(c_float),
                c_int16,
                POINTER(c_int32),
                c_uint32,
            ],
        )
        self._ps3000aSetSigGenArbitrary = self._bind(
            "ps3000aSetSigGenArbitrary",
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
                PS3000A_SWEEP_TYPE_T,
                PS3000A_EXTRA_OPERATIONS_T,
                PS3000A_INDEX_MODE_T,
                c_uint32,
                c_uint32,
                PS3000A_SIGGEN_TRIG_TYPE_T,
                PS3000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps3000aSetSigGenBuiltIn = self._bind(
            "ps3000aSetSigGenBuiltIn",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_float,
                c_float,
                c_float,
                c_float,
                PS3000A_SWEEP_TYPE_T,
                PS3000A_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS3000A_SIGGEN_TRIG_TYPE_T,
                PS3000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps3000aSetSigGenBuiltInV2 = self._bind(
            "ps3000aSetSigGenBuiltInV2",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS3000A_SWEEP_TYPE_T,
                PS3000A_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS3000A_SIGGEN_TRIG_TYPE_T,
                PS3000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps3000aSetSigGenPropertiesArbitrary = self._bind(
            "ps3000aSetSigGenPropertiesArbitrary",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                PS3000A_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS3000A_SIGGEN_TRIG_TYPE_T,
                PS3000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps3000aSetSigGenPropertiesBuiltIn = self._bind(
            "ps3000aSetSigGenPropertiesBuiltIn",
            [
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS3000A_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS3000A_SIGGEN_TRIG_TYPE_T,
                PS3000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps3000aSigGenFrequencyToPhase = self._bind(
            "ps3000aSigGenFrequencyToPhase",
            [c_int16, c_double, PS3000A_INDEX_MODE_T, c_uint32, POINTER(c_uint32)],
        )
        self._ps3000aSigGenArbitraryMinMaxValues = self._bind(
            "ps3000aSigGenArbitraryMinMaxValues",
            [
                c_int16,
                POINTER(c_int16),
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_uint32),
            ],
        )
        self._ps3000aGetMaxEtsValues = self._bind(
            "ps3000aGetMaxEtsValues", [c_int16, POINTER(c_int16), POINTER(c_int16)]
        )
        self._ps3000aSigGenSoftwareControl = self._bind(
            "ps3000aSigGenSoftwareControl", [c_int16, c_int16]
        )
        self._ps3000aSetEts = self._bind(
            "ps3000aSetEts",
            [c_int16, PS3000A_ETS_MODE_T, c_int16, c_int16, POINTER(c_int32)],
        )
        self._ps3000aSetSimpleTrigger = self._bind(
            "ps3000aSetSimpleTrigger",
            [
                c_int16,
                c_int16,
                PS3000A_CHANNEL_T,
                c_int16,
                PS3000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_int16,
            ],
        )
        self._ps3000aSetTriggerDigitalPortProperties = self._bind(
            "ps3000aSetTriggerDigitalPortProperties",
            [c_int16, POINTER(PS3000A_DIGITAL_CHANNEL_DIRECTIONS), c_int16],
        )
        self._ps3000aSetPulseWidthDigitalPortProperties = self._bind(
            "ps3000aSetPulseWidthDigitalPortProperties",
            [c_int16, POINTER(PS3000A_DIGITAL_CHANNEL_DIRECTIONS), c_int16],
        )
        self._ps3000aSetTriggerChannelProperties = self._bind(
            "ps3000aSetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS3000A_TRIGGER_CHANNEL_PROPERTIES),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps3000aSetTriggerChannelConditions = self._bind(
            "ps3000aSetTriggerChannelConditions",
            [c_int16, POINTER(PS3000A_TRIGGER_CONDITIONS), c_int16],
        )
        self._ps3000aSetTriggerChannelConditionsV2 = self._bind(
            "ps3000aSetTriggerChannelConditionsV2",
            [c_int16, POINTER(PS3000A_TRIGGER_CONDITIONS_V2), c_int16],
        )
        self._ps3000aSetTriggerChannelDirections = self._bind(
            "ps3000aSetTriggerChannelDirections",
            [
                c_int16,
                PS3000A_THRESHOLD_DIRECTION_T,
                PS3000A_THRESHOLD_DIRECTION_T,
                PS3000A_THRESHOLD_DIRECTION_T,
                PS3000A_THRESHOLD_DIRECTION_T,
                PS3000A_THRESHOLD_DIRECTION_T,
                PS3000A_THRESHOLD_DIRECTION_T,
            ],
        )
        self._ps3000aSetTriggerDelay = self._bind(
            "ps3000aSetTriggerDelay", [c_int16, c_uint32]
        )
        self._ps3000aSetPulseWidthQualifier = self._bind(
            "ps3000aSetPulseWidthQualifier",
            [
                c_int16,
                POINTER(PS3000A_PWQ_CONDITIONS),
                c_int16,
                PS3000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS3000A_PULSE_WIDTH_TYPE_T,
            ],
        )
        self._ps3000aSetPulseWidthQualifierV2 = self._bind(
            "ps3000aSetPulseWidthQualifierV2",
            [
                c_int16,
                POINTER(PS3000A_PWQ_CONDITIONS_V2),
                c_int16,
                PS3000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS3000A_PULSE_WIDTH_TYPE_T,
            ],
        )
        self._ps3000aIsTriggerOrPulseWidthQualifierEnabled = self._bind(
            "ps3000aIsTriggerOrPulseWidthQualifierEnabled",
            [c_int16, POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps3000aGetTriggerTimeOffset = self._bind(
            "ps3000aGetTriggerTimeOffset",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS3000A_TIME_UNITS_T),
                c_uint32,
            ],
        )
        self._ps3000aGetTriggerTimeOffset64 = self._bind(
            "ps3000aGetTriggerTimeOffset64",
            [c_int16, POINTER(c_int64), POINTER(PS3000A_TIME_UNITS_T), c_uint32],
        )
        self._ps3000aGetValuesTriggerTimeOffsetBulk = self._bind(
            "ps3000aGetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS3000A_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps3000aGetValuesTriggerTimeOffsetBulk64 = self._bind(
            "ps3000aGetValuesTriggerTimeOffsetBulk64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS3000A_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps3000aGetNoOfCaptures = self._bind(
            "ps3000aGetNoOfCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps3000aGetNoOfProcessedCaptures = self._bind(
            "ps3000aGetNoOfProcessedCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps3000aSetDataBuffer = self._bind(
            "ps3000aSetDataBuffer",
            [
                c_int16,
                PS3000A_CHANNEL_T,
                c_void_p,
                c_int32,
                c_uint32,
                PS3000A_RATIO_MODE_T,
            ],
        )
        self._ps3000aSetDataBuffers = self._bind(
            "ps3000aSetDataBuffers",
            [
                c_int16,
                PS3000A_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_int32,
                c_uint32,
                PS3000A_RATIO_MODE_T,
            ],
        )
        self._ps3000aSetUnscaledDataBuffers = self._bind(
            "ps3000aSetUnscaledDataBuffers",
            [
                c_int16,
                PS3000A_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_int32,
                c_uint32,
                PS3000A_RATIO_MODE_T,
            ],
        )
        self._ps3000aSetEtsTimeBuffer = self._bind(
            "ps3000aSetEtsTimeBuffer", [c_int16, c_void_p, c_int32]
        )
        self._ps3000aSetEtsTimeBuffers = self._bind(
            "ps3000aSetEtsTimeBuffers", [c_int16, c_void_p, c_void_p, c_int32]
        )
        self._ps3000aIsReady = self._bind("ps3000aIsReady", [c_int16, POINTER(c_int16)])
        self._ps3000aRunBlock = self._bind(
            "ps3000aRunBlock",
            [
                c_int16,
                c_int32,
                c_int32,
                c_uint32,
                c_int16,
                POINTER(c_int32),
                c_uint32,
                ps3000aBlockReady,
                c_void_p,
            ],
        )
        self._ps3000aRunStreaming = self._bind(
            "ps3000aRunStreaming",
            [
                c_int16,
                POINTER(c_uint32),
                PS3000A_TIME_UNITS_T,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint32,
                PS3000A_RATIO_MODE_T,
                c_uint32,
            ],
        )
        # PICO_BUSY: the driver has no new data to hand over yet; poll again.
        self._ps3000aGetStreamingLatestValues = self._bind(
            "ps3000aGetStreamingLatestValues",
            [c_int16, ps3000aStreamingReady, c_void_p],
            info=(PICO_STATUS.PICO_BUSY,),
        )
        self._ps3000aNoOfStreamingValues = self._bind(
            "ps3000aNoOfStreamingValues", [c_int16, POINTER(c_uint32)]
        )
        self._ps3000aGetMaxDownSampleRatio = self._bind(
            "ps3000aGetMaxDownSampleRatio",
            [c_int16, c_uint32, POINTER(c_uint32), PS3000A_RATIO_MODE_T, c_uint32],
        )
        self._ps3000aGetValues = self._bind(
            "ps3000aGetValues",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS3000A_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps3000aGetValuesBulk = self._bind(
            "ps3000aGetValuesBulk",
            [
                c_int16,
                POINTER(c_uint32),
                c_uint32,
                c_uint32,
                c_uint32,
                PS3000A_RATIO_MODE_T,
                POINTER(c_int16),
            ],
        )
        self._ps3000aGetValuesAsync = self._bind(
            "ps3000aGetValuesAsync",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                PS3000A_RATIO_MODE_T,
                c_uint32,
                ps3000aDataReady,
                c_void_p,
            ],
        )
        self._ps3000aGetValuesOverlapped = self._bind(
            "ps3000aGetValuesOverlapped",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS3000A_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps3000aGetValuesOverlappedBulk = self._bind(
            "ps3000aGetValuesOverlappedBulk",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS3000A_RATIO_MODE_T,
                c_uint32,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps3000aGetTriggerInfoBulk = self._bind(
            "ps3000aGetTriggerInfoBulk",
            [c_int16, POINTER(PS3000A_TRIGGER_INFO), c_uint32, c_uint32],
        )
        self._ps3000aStop = self._bind("ps3000aStop", [c_int16])
        self._ps3000aHoldOff = self._bind(
            "ps3000aHoldOff", [c_int16, c_uint64, PS3000A_HOLDOFF_TYPE_T]
        )
        self._ps3000aGetChannelInformation = self._bind(
            "ps3000aGetChannelInformation",
            [
                c_int16,
                PS3000A_CHANNEL_INFO_T,
                c_int32,
                POINTER(c_int32),
                POINTER(c_int32),
                c_int32,
            ],
        )
        # Finding no units is not a failure of the enumeration.
        self._ps3000aEnumerateUnits = self._bind(
            "ps3000aEnumerateUnits",
            [POINTER(c_int16), c_char_p, POINTER(c_int16)],
            info=(PICO_STATUS.PICO_NOT_FOUND,),
        )
        # Pinging reports a changed power source of a responsive unit.
        self._ps3000aPingUnit = self._bind(
            "ps3000aPingUnit", [c_int16], info=POWER_SOURCE_STATUSES
        )
        self._ps3000aMaximumValue = self._bind(
            "ps3000aMaximumValue", [c_int16, POINTER(c_int16)]
        )
        self._ps3000aMinimumValue = self._bind(
            "ps3000aMinimumValue", [c_int16, POINTER(c_int16)]
        )
        self._ps3000aGetAnalogueOffset = self._bind(
            "ps3000aGetAnalogueOffset",
            [
                c_int16,
                PS3000A_RANGE_T,
                PS3000A_COUPLING_T,
                POINTER(c_float),
                POINTER(c_float),
            ],
        )
        self._ps3000aGetMaxSegments = self._bind(
            "ps3000aGetMaxSegments", [c_int16, POINTER(c_uint32)]
        )
        # Acknowledging the power source may report the (new) power state.
        self._ps3000aChangePowerSource = self._bind(
            "ps3000aChangePowerSource",
            [c_int16, PICO_STATUS_T],
            info=POWER_SOURCE_STATUSES,
        )
        # The returned status *is* the result: the current power source.
        self._ps3000aCurrentPowerSource = self._bind(
            "ps3000aCurrentPowerSource", [c_int16], info=POWER_SOURCE_STATUSES
        )
        self._ps3000aQueryOutputEdgeDetect = self._bind(
            "ps3000aQueryOutputEdgeDetect", [c_int16, POINTER(c_int16)]
        )
        self._ps3000aSetOutputEdgeDetect = self._bind(
            "ps3000aSetOutputEdgeDetect", [c_int16, c_int16]
        )
        self._ps3000aGetScalingValues = self._bind(
            "ps3000aGetScalingValues",
            [c_int16, POINTER(PS3000A_SCALING_FACTORS_VALUES), c_int16],
        )
        self._ps3000aCheckForUpdate = self._bind(
            "ps3000aCheckForUpdate",
            [
                c_int16,
                POINTER(PICO_FIRMWARE_INFO),
                POINTER(c_int16),
                POINTER(c_uint16),
            ],
        )
        self._ps3000aStartFirmwareUpdate = self._bind(
            "ps3000aStartFirmwareUpdate", [c_int16, PicoUpdateFirmwareProgress]
        )

    def ps3000aOpenUnit(self, serial: str | None):
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        return self._ps3000aOpenUnit(byref(handle), ser), handle

    def ps3000aOpenUnitAsync(self, serial: str | None) -> tuple[PICO_STATUS, bool]:
        """Start opening a unit; the second value tells if the open was started."""
        status = c_int16(0)
        ser = serial.encode() if serial is not None else None
        return self._ps3000aOpenUnitAsync(byref(status), ser), status.value == 1

    def ps3000aOpenUnitProgress(self) -> tuple[PICO_STATUS, c_int16, int, bool]:
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        return (
            self._ps3000aOpenUnitProgress(
                byref(handle), byref(progressPercent), byref(complete)
            ),
            handle,
            progressPercent.value,
            complete.value != 0,
        )

    def ps3000aCloseUnit(self, handle: c_int16):
        return self._ps3000aCloseUnit(handle)

    def ps3000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._ps3000aGetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return status, infostr

    def ps3000aFlashLed(self, handle: c_int16, start: int) -> PICO_STATUS:
        """Flash the LED ``start`` times; ``-1`` flashes until stopped by ``0``."""
        return self._ps3000aFlashLed(handle, start)

    def ps3000aMemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_int32(0)
        return (
            self._ps3000aMemorySegments(handle, nsegments, byref(maxSamples)),
            maxSamples.value,
        )

    def ps3000aSetChannel(
        self,
        handle: c_int16,
        channel: PS3000A_CHANNEL,
        enabled: bool,
        coupling: PS3000A_COUPLING,
        range: PS3000A_RANGE,
        analog_offset: float,
    ):
        return self._ps3000aSetChannel(
            handle,
            channel,
            1 if enabled else 0,
            coupling,
            range,
            analog_offset,
        )

    def ps3000aSetDigitalPort(
        self,
        handle: c_int16,
        port: PS3000A_DIGITAL_PORT,
        enabled: bool,
        logicLevel: int,
    ) -> PICO_STATUS:
        return self._ps3000aSetDigitalPort(
            handle, port, 1 if enabled else 0, logicLevel
        )

    def ps3000aSetBandwidthFilter(
        self,
        handle: c_int16,
        channel: PS3000A_CHANNEL,
        bandwidth: PS3000A_BANDWIDTH_LIMITER,
    ):
        return self._ps3000aSetBandwidthFilter(handle, channel, bandwidth)

    def ps3000aSetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return self._ps3000aSetNoOfCaptures(handle, ncaptures)

    def ps3000aGetTimebase(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        segmentIndex: int,
        oversample: int = 0,
    ) -> tuple[PICO_STATUS, int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_int32(0)
        return (
            self._ps3000aGetTimebase(
                handle,
                timebase,
                noSamples,
                byref(timeIntervalNanoseconds),
                oversample,
                byref(maxSamples),
                segmentIndex,
            ),
            timeIntervalNanoseconds.value,
            maxSamples.value,
        )

    def ps3000aGetTimebase2(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        segmentIndex: int,
        oversample: int = 0,
    ):
        timeIntervalNS = c_float(0)
        maxSamples = c_int32(0)
        return (
            self._ps3000aGetTimebase2(
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

    def ps3000aSetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: Sequence[int],
        sweepType: PS3000A_SWEEP_TYPE,
        operation: PS3000A_EXTRA_OPERATIONS,
        indexMode: PS3000A_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS3000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS3000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        waveform = (c_int16 * len(arbitraryWaveform))(*arbitraryWaveform)
        return self._ps3000aSetSigGenArbitrary(
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

    def ps3000aSetSigGenBuiltIn(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS3000A_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS3000A_SWEEP_TYPE,
        operation: PS3000A_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS3000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS3000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps3000aSetSigGenBuiltIn(
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

    def ps3000aSetSigGenBuiltInV2(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS3000A_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS3000A_SWEEP_TYPE,
        operation: PS3000A_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS3000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS3000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps3000aSetSigGenBuiltInV2(
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

    def ps3000aSetSigGenPropertiesArbitrary(
        self,
        handle: c_int16,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PS3000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS3000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS3000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps3000aSetSigGenPropertiesArbitrary(
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

    def ps3000aSetSigGenPropertiesBuiltIn(
        self,
        handle: c_int16,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS3000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS3000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS3000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> PICO_STATUS:
        return self._ps3000aSetSigGenPropertiesBuiltIn(
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

    def ps3000aSigGenFrequencyToPhase(
        self,
        handle: c_int16,
        frequency: float,
        indexMode: PS3000A_INDEX_MODE,
        bufferLength: int,
    ) -> tuple[PICO_STATUS, int]:
        phase = c_uint32(0)
        return (
            self._ps3000aSigGenFrequencyToPhase(
                handle, frequency, indexMode, bufferLength, byref(phase)
            ),
            phase.value,
        )

    def ps3000aSigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, int, int, int, int]:
        """Return the AWG's minimum/maximum sample values and buffer sizes."""
        minValue = c_int16(0)
        maxValue = c_int16(0)
        minSize = c_uint32(0)
        maxSize = c_uint32(0)
        return (
            self._ps3000aSigGenArbitraryMinMaxValues(
                handle, byref(minValue), byref(maxValue), byref(minSize), byref(maxSize)
            ),
            minValue.value,
            maxValue.value,
            minSize.value,
            maxSize.value,
        )

    def ps3000aGetMaxEtsValues(self, handle: c_int16) -> tuple[PICO_STATUS, int, int]:
        etsCycles = c_int16(0)
        etsInterleave = c_int16(0)
        return (
            self._ps3000aGetMaxEtsValues(
                handle, byref(etsCycles), byref(etsInterleave)
            ),
            etsCycles.value,
            etsInterleave.value,
        )

    def ps3000aSigGenSoftwareControl(self, handle: c_int16, state: int) -> PICO_STATUS:
        return self._ps3000aSigGenSoftwareControl(handle, state)

    def ps3000aSetEts(
        self,
        handle: c_int16,
        mode: PS3000A_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> tuple[PICO_STATUS, int]:
        sampleTimePicoseconds = c_int32(0)
        return (
            self._ps3000aSetEts(
                handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
            ),
            sampleTimePicoseconds.value,
        )

    def ps3000aSetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PS3000A_CHANNEL,
        threshold: int,
        direction: PS3000A_THRESHOLD_DIRECTION,
        delay: int,
        autoTriggerMS: int,
    ):
        assert autoTriggerMS >= 0
        return self._ps3000aSetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTriggerMS,
        )

    def ps3000aSetTriggerDigitalPortProperties(
        self,
        handle: c_int16,
        directions: Sequence[PS3000A_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> PICO_STATUS:
        return self._ps3000aSetTriggerDigitalPortProperties(
            handle,
            _array(PS3000A_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def ps3000aSetPulseWidthDigitalPortProperties(
        self,
        handle: c_int16,
        directions: Sequence[PS3000A_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> PICO_STATUS:
        return self._ps3000aSetPulseWidthDigitalPortProperties(
            handle,
            _array(PS3000A_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def ps3000aSetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS3000A_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> PICO_STATUS:
        return self._ps3000aSetTriggerChannelProperties(
            handle,
            _array(PS3000A_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps3000aSetTriggerChannelConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PS3000A_TRIGGER_CONDITIONS],
    ) -> PICO_STATUS:
        return self._ps3000aSetTriggerChannelConditions(
            handle, _array(PS3000A_TRIGGER_CONDITIONS, conditions), len(conditions)
        )

    def ps3000aSetTriggerChannelConditionsV2(
        self,
        handle: c_int16,
        conditions: Sequence[PS3000A_TRIGGER_CONDITIONS_V2],
    ) -> PICO_STATUS:
        return self._ps3000aSetTriggerChannelConditionsV2(
            handle, _array(PS3000A_TRIGGER_CONDITIONS_V2, conditions), len(conditions)
        )

    def ps3000aSetTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: PS3000A_THRESHOLD_DIRECTION,
        channelB: PS3000A_THRESHOLD_DIRECTION,
        channelC: PS3000A_THRESHOLD_DIRECTION,
        channelD: PS3000A_THRESHOLD_DIRECTION,
        ext: PS3000A_THRESHOLD_DIRECTION,
        aux: PS3000A_THRESHOLD_DIRECTION,
    ) -> PICO_STATUS:
        return self._ps3000aSetTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext, aux
        )

    def ps3000aSetTriggerDelay(self, handle: c_int16, delay: int):
        return self._ps3000aSetTriggerDelay(handle, delay)

    def ps3000aSetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS3000A_PWQ_CONDITIONS],
        direction: PS3000A_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS3000A_PULSE_WIDTH_TYPE,
    ) -> PICO_STATUS:
        return self._ps3000aSetPulseWidthQualifier(
            handle,
            _array(PS3000A_PWQ_CONDITIONS, conditions),
            len(conditions),
            direction,
            lower,
            upper,
            type,
        )

    def ps3000aSetPulseWidthQualifierV2(
        self,
        handle: c_int16,
        conditions: Sequence[PS3000A_PWQ_CONDITIONS_V2],
        direction: PS3000A_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS3000A_PULSE_WIDTH_TYPE,
    ) -> PICO_STATUS:
        return self._ps3000aSetPulseWidthQualifierV2(
            handle,
            _array(PS3000A_PWQ_CONDITIONS_V2, conditions),
            len(conditions),
            direction,
            lower,
            upper,
            type,
        )

    def ps3000aIsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        return (
            self._ps3000aIsTriggerOrPulseWidthQualifierEnabled(
                handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
            ),
            triggerEnabled.value != 0,
            pulseWidthQualifierEnabled.value != 0,
        )

    def ps3000aGetTriggerTimeOffset(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, int, PS3000A_TIME_UNITS]:
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS3000A_TIME_UNITS_T(0)
        return (
            self._ps3000aGetTriggerTimeOffset(
                handle,
                byref(timeUpper),
                byref(timeLower),
                byref(timeUnits),
                segmentIndex,
            ),
            timeUpper.value,
            timeLower.value,
            PS3000A_TIME_UNITS(timeUnits.value),
        )

    def ps3000aGetTriggerTimeOffset64(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, PS3000A_TIME_UNITS]:
        time = c_int64(0)
        timeUnits = PS3000A_TIME_UNITS_T(0)
        return (
            self._ps3000aGetTriggerTimeOffset64(
                handle, byref(time), byref(timeUnits), segmentIndex
            ),
            time.value,
            PS3000A_TIME_UNITS(timeUnits.value),
        )

    def ps3000aGetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[int], list[PS3000A_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        timesUpper = (c_uint32 * nsegments)()
        timesLower = (c_uint32 * nsegments)()
        timeUnits = (PS3000A_TIME_UNITS_T * nsegments)()
        return (
            self._ps3000aGetValuesTriggerTimeOffsetBulk(
                handle,
                timesUpper,
                timesLower,
                timeUnits,
                fromSegmentIndex,
                toSegmentIndex,
            ),
            list(timesUpper),
            list(timesLower),
            [PS3000A_TIME_UNITS(u) for u in timeUnits],
        )

    def ps3000aGetValuesTriggerTimeOffsetBulk64(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[PS3000A_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * nsegments)()
        timeUnits = (PS3000A_TIME_UNITS_T * nsegments)()
        return (
            self._ps3000aGetValuesTriggerTimeOffsetBulk64(
                handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
            ),
            list(times),
            [PS3000A_TIME_UNITS(u) for u in timeUnits],
        )

    def ps3000aGetNoOfCaptures(self, handle: c_int16):
        captures = c_uint32()
        return self._ps3000aGetNoOfCaptures(handle, byref(captures)), captures.value

    def ps3000aGetNoOfProcessedCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            self._ps3000aGetNoOfProcessedCaptures(handle, byref(captures)),
            captures.value,
        )

    def ps3000aSetDataBuffer(
        self,
        handle: c_int16,
        channel: PS3000A_CHANNEL,
        buffer: c_void_p,
        bufferLth: int,
        segmentIndex: int,
        mode: PS3000A_RATIO_MODE,
    ):
        """Register an ``int16_t`` buffer; it must stay alive until it is read."""
        return self._ps3000aSetDataBuffer(
            handle, channel, buffer, bufferLth, segmentIndex, mode
        )

    def ps3000aSetDataBuffers(
        self,
        handle: c_int16,
        channelOrPort: PS3000A_CHANNEL | PS3000A_DIGITAL_PORT,
        bufferMax: c_void_p | int | None,
        bufferMin: c_void_p | int | None,
        bufferLth: int,
        segmentIndex: int,
        mode: PS3000A_RATIO_MODE,
    ) -> PICO_STATUS:
        """Register ``int16_t`` buffers; they must stay alive until they are read."""
        return self._ps3000aSetDataBuffers(
            handle, channelOrPort, bufferMax, bufferMin, bufferLth, segmentIndex, mode
        )

    def ps3000aSetUnscaledDataBuffers(
        self,
        handle: c_int16,
        channelOrPort: PS3000A_CHANNEL | PS3000A_DIGITAL_PORT,
        bufferMax: c_void_p | int | None,
        bufferMin: c_void_p | int | None,
        bufferLth: int,
        segmentIndex: int,
        mode: PS3000A_RATIO_MODE,
    ) -> PICO_STATUS:
        """Register ``int8_t`` buffers; they must stay alive until they are read."""
        return self._ps3000aSetUnscaledDataBuffers(
            handle, channelOrPort, bufferMax, bufferMin, bufferLth, segmentIndex, mode
        )

    def ps3000aSetEtsTimeBuffer(
        self, handle: c_int16, buffer: c_void_p | int | None, bufferLth: int
    ) -> PICO_STATUS:
        """Register an ``int64_t`` buffer; it must stay alive until it is read."""
        return self._ps3000aSetEtsTimeBuffer(handle, buffer, bufferLth)

    def ps3000aSetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: c_void_p | int | None,
        timeLower: c_void_p | int | None,
        bufferLth: int,
    ) -> PICO_STATUS:
        """Register ``uint32_t`` buffers; they must stay alive until they are read."""
        return self._ps3000aSetEtsTimeBuffers(handle, timeUpper, timeLower, bufferLth)

    def ps3000aIsReady(self, handle: c_int16):
        ready = c_int16(0)
        return self._ps3000aIsReady(handle, byref(ready)), ready.value == 1

    def ps3000aRunBlock(
        self,
        handle: c_int16,
        preSamples: int,
        postSamples: int,
        timebase: int,
        segment: int,
        callback: Callable[[int, PICO_STATUS], None] | None,
        oversample: int = 0,
    ):
        assert preSamples >= 0
        assert postSamples >= 0
        timeInd = c_int32(0)
        lpReady = ps3000aBlockReady()  # NULL; ctypes rejects None here
        if callback is not None:

            def cbwrapper(handle: int, status: int, _: int | None):
                callback(handle, PICO_STATUS(status))

            lpReady = ps3000aBlockReady(cbwrapper)
        status = self._with_callback(
            self._callback_key("ps3000aRunBlock", handle),
            lpReady,
            lambda: self._ps3000aRunBlock(
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

    def ps3000aRunStreaming(
        self,
        handle: c_int16,
        sampleInterval: int,
        sampleIntervalTimeUnits: PS3000A_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        overviewBufferSize: int,
    ) -> tuple[PICO_STATUS, int]:
        """Start streaming; returns the actual sample interval."""
        interval = c_uint32(sampleInterval)
        return (
            self._ps3000aRunStreaming(
                handle,
                byref(interval),
                sampleIntervalTimeUnits,
                maxPreTriggerSamples,
                maxPostTriggerSamples,
                1 if autoStop else 0,
                downSampleRatio,
                downSampleRatioMode,
                overviewBufferSize,
            ),
            interval.value,
        )

    def ps3000aGetStreamingLatestValues(
        self,
        handle: c_int16,
        callback: Callable[[int, int, int, int, int, bool, bool], None],
    ) -> PICO_STATUS:
        """Fetch new streaming data, invoking ``callback`` if there is any.

        ``callback`` receives ``(handle, noOfSamples, startIndex, overflow,
        triggerAt, triggered, autoStop)``.
        """

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

        lpPs3000aReady = ps3000aStreamingReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps3000aGetStreamingLatestValues", handle),
            lpPs3000aReady,
            lambda: self._ps3000aGetStreamingLatestValues(handle, lpPs3000aReady, None),
        )

    def ps3000aNoOfStreamingValues(self, handle: c_int16) -> tuple[PICO_STATUS, int]:
        noOfValues = c_uint32(0)
        return (
            self._ps3000aNoOfStreamingValues(handle, byref(noOfValues)),
            noOfValues.value,
        )

    def ps3000aGetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggreatedSamples: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int]:
        maxDownSampleRatio = c_uint32(0)
        return (
            self._ps3000aGetMaxDownSampleRatio(
                handle,
                noOfUnaggreatedSamples,
                byref(maxDownSampleRatio),
                downSampleRatioMode,
                segmentIndex,
            ),
            maxDownSampleRatio.value,
        )

    def ps3000aGetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int, int]:
        """Read data into the registered buffers; returns sample count and overflow."""
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        return (
            self._ps3000aGetValues(
                handle,
                startIndex,
                byref(noOfSamples_),
                downSampleRatio,
                downSampleRatioMode,
                segmentIndex,
                byref(overflow),
            ),
            noOfSamples_.value,
            overflow.value,
        )

    def ps3000aGetValuesBulk(
        self,
        handle: c_int16,
        nosamples: int,
        fromSegment: int,
        toSegment: int,
        downsampleRatio: int,
        downsampleMode: PS3000A_RATIO_MODE,
    ):
        assert nosamples > 0
        assert fromSegment <= toSegment
        nosamples_ = c_uint32(nosamples)
        nsegments = (toSegment - fromSegment) + 1
        overflow = (c_int16 * nsegments)(0)
        return (
            self._ps3000aGetValuesBulk(
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

    def ps3000aGetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        segmentIndex: int,
        callback: Callable[[int, PICO_STATUS, int, int], None],
    ) -> PICO_STATUS:
        """Read data asynchronously.

        ``callback`` receives ``(handle, status, noOfSamples, overflow)``.
        """

        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: int | None
        ):
            callback(handle, PICO_STATUS(status), noOfSamples, overflow)

        lpDataReady = ps3000aDataReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps3000aGetValuesAsync", handle),
            lpDataReady,
            lambda: self._ps3000aGetValuesAsync(
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

    def ps3000aGetValuesOverlapped(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, c_uint32, c_int16]:
        """Set up a deferred read, performed when the next block completes.

        The driver writes the sample count and overflow flags later, so they are
        returned as ctypes objects; read their ``.value`` after the capture.
        """
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        # The driver keeps the pointers, so the outputs must outlive this call.
        status = self._with_callback(
            self._callback_key("ps3000aGetValuesOverlapped", handle),
            (noOfSamples_, overflow),
            lambda: self._ps3000aGetValuesOverlapped(
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

    def ps3000aGetValuesOverlappedBulk(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[PICO_STATUS, c_uint32, Any]:
        """Set up a deferred bulk read, performed when the next capture completes.

        The driver writes the sample count and per-segment overflow flags later,
        so they are returned as ctypes objects (a ``c_uint32`` and a ``c_int16``
        array); read them after the capture.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = (c_int16 * nsegments)()
        # The driver keeps the pointers, so the outputs must outlive this call.
        # Shares the slot with ps3000aGetValuesOverlapped: one deferred read.
        status = self._with_callback(
            self._callback_key("ps3000aGetValuesOverlapped", handle),
            (noOfSamples_, overflow),
            lambda: self._ps3000aGetValuesOverlappedBulk(
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

    def ps3000aGetTriggerInfoBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[PS3000A_TRIGGER_INFO]]:
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        triggerInfo = (PS3000A_TRIGGER_INFO * nsegments)()
        return (
            self._ps3000aGetTriggerInfoBulk(
                handle, triggerInfo, fromSegmentIndex, toSegmentIndex
            ),
            list(triggerInfo),
        )

    def ps3000aStop(self, handle: c_int16) -> PICO_STATUS:
        return self._ps3000aStop(handle)

    def ps3000aHoldOff(
        self, handle: c_int16, holdoff: int, type: PS3000A_HOLDOFF_TYPE
    ) -> PICO_STATUS:
        return self._ps3000aHoldOff(handle, holdoff, type)

    def ps3000aGetChannelInformation(
        self,
        handle: c_int16,
        info: PS3000A_CHANNEL_INFO,
        probe: int,
        channels: PS3000A_CHANNEL,
    ) -> tuple[PICO_STATUS, list[PS3000A_RANGE]]:
        ranges = (c_int32 * PS3000A_RANGE.PS3000A_MAX_RANGES)()
        length = c_int32(len(ranges))
        status = self._ps3000aGetChannelInformation(
            handle, info, probe, ranges, byref(length), channels
        )
        return status, [PS3000A_RANGE(r) for r in ranges[: length.value]]

    def ps3000aEnumerateUnits(self) -> tuple[PICO_STATUS, int, list[str]]:
        """Return the number of units found and their serial numbers."""
        count = c_int16(0)
        serials = create_string_buffer(_ENUMERATE_BUFFER_SIZE)
        serialLth = c_int16(_ENUMERATE_BUFFER_SIZE)
        status = self._ps3000aEnumerateUnits(byref(count), serials, byref(serialLth))
        serialstr = serials.value.decode("utf-8")
        return status, count.value, [s for s in serialstr.split(",") if s]

    def ps3000aPingUnit(self, handle: c_int16) -> PICO_STATUS:
        return self._ps3000aPingUnit(handle)

    def ps3000aMaximumValue(self, handle: c_int16):
        value = c_int16(0)
        return self._ps3000aMaximumValue(handle, byref(value)), value.value

    def ps3000aMinimumValue(self, handle: c_int16):
        value = c_int16(0)
        return self._ps3000aMinimumValue(handle, byref(value)), value.value

    def ps3000aGetAnalogueOffset(
        self, handle: c_int16, range: PS3000A_RANGE, coupling: PS3000A_COUPLING
    ):
        minv = c_float(0)
        maxv = c_float(0)
        return (
            self._ps3000aGetAnalogueOffset(
                handle, range, coupling, byref(maxv), byref(minv)
            ),
            minv.value,
            maxv.value,
        )

    def ps3000aGetMaxSegments(self, handle: c_int16):
        value = c_uint32(0)
        return self._ps3000aGetMaxSegments(handle, byref(value)), value.value

    def ps3000aChangePowerSource(self, handle: c_int16, source: PICO_STATUS):
        return self._ps3000aChangePowerSource(handle, source)

    def ps3000aCurrentPowerSource(self, handle: c_int16) -> PICO_STATUS:
        """Return the power source as status, e.g., ``PICO_POWER_SUPPLY_CONNECTED``."""
        return self._ps3000aCurrentPowerSource(handle)

    def ps3000aQueryOutputEdgeDetect(self, handle: c_int16) -> tuple[PICO_STATUS, bool]:
        state = c_int16(0)
        return self._ps3000aQueryOutputEdgeDetect(
            handle, byref(state)
        ), state.value != 0

    def ps3000aSetOutputEdgeDetect(self, handle: c_int16, state: bool) -> PICO_STATUS:
        return self._ps3000aSetOutputEdgeDetect(handle, 1 if state else 0)

    def ps3000aGetScalingValues(
        self, handle: c_int16, nChannels: int
    ) -> tuple[PICO_STATUS, list[PS3000A_SCALING_FACTORS_VALUES]]:
        scalingValues = (PS3000A_SCALING_FACTORS_VALUES * nChannels)()
        return (
            self._ps3000aGetScalingValues(handle, scalingValues, nChannels),
            list(scalingValues),
        )

    def ps3000aCheckForUpdate(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, list[PICO_FIRMWARE_INFO], bool]:
        """Return the firmware infos and whether any update is required."""
        firmwareInfos = (PICO_FIRMWARE_INFO * _MAX_FIRMWARE_INFOS)()
        nFirmwareInfos = c_int16(_MAX_FIRMWARE_INFOS)
        updatesRequired = c_uint16(0)
        status = self._ps3000aCheckForUpdate(
            handle, firmwareInfos, byref(nFirmwareInfos), byref(updatesRequired)
        )
        return (
            status,
            list(firmwareInfos[: nFirmwareInfos.value]),
            updatesRequired.value != 0,
        )

    def ps3000aStartFirmwareUpdate(
        self, handle: c_int16, progress: Callable[[int, int], None] | None
    ) -> PICO_STATUS:
        """Update the firmware; ``progress`` receives ``(handle, percent)``."""
        cb = PicoUpdateFirmwareProgress()  # NULL; ctypes rejects None here
        if progress is not None:

            def cbwrapper(handle: int, percent: int):
                progress(handle, percent)

            cb = PicoUpdateFirmwareProgress(cbwrapper)
        return self._with_callback(
            self._callback_key("ps3000aStartFirmwareUpdate", handle),
            cb,
            lambda: self._ps3000aStartFirmwareUpdate(handle, cb),
        )


__all__ = (
    "PS3000A_BANDWIDTH_LIMITER",
    "PS3000A_CHANNEL",
    "PS3000A_CHANNEL_BUFFER_INDEX",
    "PS3000A_CHANNEL_INFO",
    "PS3000A_COUPLING",
    "PS3000A_DIGITAL_CHANNEL",
    "PS3000A_DIGITAL_CHANNEL_DIRECTIONS",
    "PS3000A_DIGITAL_DIRECTION",
    "PS3000A_DIGITAL_PORT",
    "PS3000A_ETS_MODE",
    "PS3000A_EXTRA_OPERATIONS",
    "PS3000A_EXT_MAX_VALUE",
    "PS3000A_EXT_MIN_VALUE",
    "PS3000A_GAUSSIAN_MAX_FREQUENCY",
    "PS3000A_HALF_SINE_MAX_FREQUENCY",
    "PS3000A_HOLDOFF_TYPE",
    "PS3000A_INDEX_MODE",
    "PS3000A_MAX_ANALOGUE_OFFSET_500MV_2V",
    "PS3000A_MAX_ANALOGUE_OFFSET_50MV_200MV",
    "PS3000A_MAX_ANALOGUE_OFFSET_5V_20V",
    "PS3000A_MAX_LOGIC_LEVEL",
    "PS3000A_MAX_OVERSAMPLE",
    "PS3000A_MAX_SIG_GEN_BUFFER_SIZE",
    "PS3000A_MAX_SIG_GEN_FREQ",
    "PS3000A_MAX_SWEEPS_SHOTS",
    "PS3000A_MIN_ANALOGUE_OFFSET_500MV_2V",
    "PS3000A_MIN_ANALOGUE_OFFSET_50MV_200MV",
    "PS3000A_MIN_ANALOGUE_OFFSET_5V_20V",
    "PS3000A_MIN_DWELL_COUNT",
    "PS3000A_MIN_FREQUENCY",
    "PS3000A_MIN_LOGIC_LEVEL",
    "PS3000A_MIN_SIG_GEN_BUFFER_SIZE",
    "PS3000A_MIN_SIG_GEN_FREQ",
    "PS3000A_PRBS_MAX_FREQUENCY",
    "PS3000A_PRBS_MIN_FREQUENCY",
    "PS3000A_PULSE_WIDTH_TYPE",
    "PS3000A_PWQ_CONDITIONS",
    "PS3000A_PWQ_CONDITIONS_V2",
    "PS3000A_RAMP_MAX_FREQUENCY",
    "PS3000A_RANGE",
    "PS3000A_RATIO_MODE",
    "PS3000A_SCALING_FACTORS_VALUES",
    "PS3000A_SHOT_SWEEP_TRIGGER_CONTINUOUS_RUN",
    "PS3000A_SIGGEN_TRIG_SOURCE",
    "PS3000A_SIGGEN_TRIG_TYPE",
    "PS3000A_SINC_MAX_FREQUENCY",
    "PS3000A_SINE_MAX_FREQUENCY",
    "PS3000A_SQUARE_MAX_FREQUENCY",
    "PS3000A_SWEEP_TYPE",
    "PS3000A_THRESHOLD_DIRECTION",
    "PS3000A_THRESHOLD_MODE",
    "PS3000A_TIME_UNITS",
    "PS3000A_TRIANGLE_MAX_FREQUENCY",
    "PS3000A_TRIGGER_CHANNEL_PROPERTIES",
    "PS3000A_TRIGGER_CONDITIONS",
    "PS3000A_TRIGGER_CONDITIONS_V2",
    "PS3000A_TRIGGER_INFO",
    "PS3000A_TRIGGER_STATE",
    "PS3000A_WAVE_TYPE",
    "PS3204A_MAX_ETS_CYCLES",
    "PS3204A_MAX_INTERLEAVE",
    "PS3204MSO_MAX_INTERLEAVE",
    "PS3205A_MAX_ETS_CYCLES",
    "PS3205A_MAX_INTERLEAVE",
    "PS3205MSO_MAX_INTERLEAVE",
    "PS3206A_MAX_ETS_CYCLES",
    "PS3206A_MAX_INTERLEAVE",
    "PS3206B_MAX_SIG_GEN_BUFFER_SIZE",
    "PS3206MSO_MAX_INTERLEAVE",
    "PS3207A_MAX_ETS_CYCLES",
    "PS3207A_MAX_INTERLEAVE",
    "PS3207B_MAX_SIG_GEN_BUFFER_SIZE",
    "PicoScope3000aWrapper",
    "ps3000aBlockReady",
    "ps3000aDataReady",
    "ps3000aStreamingReady",
)
