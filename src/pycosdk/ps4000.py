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
    c_uint64,
    c_void_p,
    create_string_buffer,
)
from enum import IntEnum, IntFlag
from typing import Annotated, Self, final

from ._base import (
    CALLBACK_FUNCTYPE,
    POWER_SOURCE_STATUSES,
    PicoScopeWrapperBase,
    int64_from_halves,
    seconds,
)
from ._buffer import DataBuffer, InputValues, buffer_argument, input_argument
from ._device import PicoScopeDeviceBase, handle_method, wrapper_function
from ._struct import CStruct, c_array
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T

# Driver for the PicoScope 4000 Series (not the 4000A, see ps4000a). Several
# names are unprefixed in ps4000Api.h (e.g. SWEEP_TYPE, UP, P_NONE,
# MAX_SIG_GEN_BUFFER_SIZE); like the ps5000 module, they get a PS4000_ prefix
# here. The C name is noted where it differs.

PS4000_MAX_OVERSAMPLE_12BIT = 16
PS4000_MAX_OVERSAMPLE_8BIT = 256

PS4XXX_MAX_ETS_CYCLES = 400
PS4XXX_MAX_INTERLEAVE = 80

# Samples are always scaled to 16 bits, even without oversampling.
PS4262_MAX_VALUE = 32767
PS4262_MIN_VALUE = -32767

PS4000_MAX_VALUE = 32764
PS4000_MIN_VALUE = -32764
PS4000_LOST_DATA = -32768

PS4000_EXT_MAX_VALUE = 32767
PS4000_EXT_MIN_VALUE = -32767

PS4000_MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215  # C: MAX_PULSE_WIDTH_QUALIFIER_COUNT
PS4000_MAX_DELAY_COUNT = 8388607  # C: MAX_DELAY_COUNT

PS4000_MIN_SIG_GEN_FREQ = 0.0  # C: MIN_SIG_GEN_FREQ
PS4000_MAX_SIG_GEN_FREQ = 100000.0  # C: MAX_SIG_GEN_FREQ
PS4000_MAX_SIG_GEN_FREQ_4262 = 20000.0  # C: MAX_SIG_GEN_FREQ_4262

# Applicable to all variants with a signal generator.
PS4000_MIN_SIG_GEN_BUFFER_SIZE = 1  # C: MIN_SIG_GEN_BUFFER_SIZE

# Values for the PS4226 and PS4227.
PS4000_MAX_SIG_GEN_BUFFER_SIZE = 8192  # C: MAX_SIG_GEN_BUFFER_SIZE
PS4000_MIN_DWELL_COUNT = 10  # C: MIN_DWELL_COUNT

PS4262_MAX_WAVEFORM_BUFFER_SIZE = 4096
PS4262_MIN_DWELL_COUNT = 3

PS4000_MAX_SWEEPS_SHOTS = (1 << 30) - 1  # C: MAX_SWEEPS_SHOTS


class PS4000_CHANNEL_BUFFER_INDEX(IntEnum):
    PS4000_CHANNEL_A_MAX = 0
    PS4000_CHANNEL_A_MIN = 1
    PS4000_CHANNEL_B_MAX = 2
    PS4000_CHANNEL_B_MIN = 3
    PS4000_CHANNEL_C_MAX = 4
    PS4000_CHANNEL_C_MIN = 5
    PS4000_CHANNEL_D_MAX = 6
    PS4000_CHANNEL_D_MIN = 7
    PS4000_MAX_CHANNEL_BUFFERS = 8


PS4000_CHANNEL_BUFFER_INDEX_T = c_int32


class PS4000_CHANNEL(IntEnum):
    PS4000_CHANNEL_A = 0
    PS4000_CHANNEL_B = 1
    PS4000_CHANNEL_C = 2
    PS4000_CHANNEL_D = 3
    PS4000_EXTERNAL = 4
    PS4000_MAX_CHANNELS = PS4000_EXTERNAL
    PS4000_TRIGGER_AUX = 5
    PS4000_MAX_TRIGGER_SOURCES = 6


PS4000_CHANNEL_T = c_int32


class PS4000_CHANNEL_FLAGS(IntFlag):
    """The per-channel bits of the ``overflow`` outputs (bit 0: channel A).

    No C counterpart: the header passes them as ``int16_t``; modelled after the
    shared ``PICO_CHANNEL_FLAGS``.
    """

    PS4000_CHANNEL_A_FLAGS = 1 << PS4000_CHANNEL.PS4000_CHANNEL_A
    PS4000_CHANNEL_B_FLAGS = 1 << PS4000_CHANNEL.PS4000_CHANNEL_B
    PS4000_CHANNEL_C_FLAGS = 1 << PS4000_CHANNEL.PS4000_CHANNEL_C
    PS4000_CHANNEL_D_FLAGS = 1 << PS4000_CHANNEL.PS4000_CHANNEL_D


class PS4000_RANGE(IntEnum):
    PS4000_10MV = 0
    PS4000_20MV = 1
    PS4000_50MV = 2
    PS4000_100MV = 3
    PS4000_200MV = 4
    PS4000_500MV = 5
    PS4000_1V = 6
    PS4000_2V = 7
    PS4000_5V = 8
    PS4000_10V = 9
    PS4000_20V = 10
    PS4000_50V = 11
    PS4000_100V = 12
    PS4000_MAX_RANGES = 13

    PS4000_RESISTANCE_100R = PS4000_MAX_RANGES
    PS4000_RESISTANCE_1K = 14
    PS4000_RESISTANCE_10K = 15
    PS4000_RESISTANCE_100K = 16
    PS4000_RESISTANCE_1M = 17
    PS4000_MAX_RESISTANCES = 18

    PS4000_ACCELEROMETER_10MV = PS4000_MAX_RESISTANCES
    PS4000_ACCELEROMETER_20MV = 19
    PS4000_ACCELEROMETER_50MV = 20
    PS4000_ACCELEROMETER_100MV = 21
    PS4000_ACCELEROMETER_200MV = 22
    PS4000_ACCELEROMETER_500MV = 23
    PS4000_ACCELEROMETER_1V = 24
    PS4000_ACCELEROMETER_2V = 25
    PS4000_ACCELEROMETER_5V = 26
    PS4000_ACCELEROMETER_10V = 27
    PS4000_ACCELEROMETER_20V = 28
    PS4000_ACCELEROMETER_50V = 29
    PS4000_ACCELEROMETER_100V = 30
    PS4000_MAX_ACCELEROMETER = 31

    PS4000_TEMPERATURE_UPTO_40 = PS4000_MAX_ACCELEROMETER
    PS4000_TEMPERATURE_UPTO_70 = 32
    PS4000_TEMPERATURE_UPTO_100 = 33
    PS4000_TEMPERATURE_UPTO_130 = 34
    PS4000_MAX_TEMPERATURES = 35

    PS4000_RESISTANCE_5K = PS4000_MAX_TEMPERATURES
    PS4000_RESISTANCE_25K = 36
    PS4000_RESISTANCE_50K = 37
    PS4000_MAX_EXTRA_RESISTANCES = 38


PS4000_RANGE_T = c_int32


class PS4000_PROBE(IntEnum):
    # C: unprefixed P_* members
    PS4000_P_NONE = 0
    PS4000_P_CURRENT_CLAMP_10A = 1
    PS4000_P_CURRENT_CLAMP_1000A = 2
    PS4000_P_TEMPERATURE_SENSOR = 3
    PS4000_P_CURRENT_MEASURING_DEVICE = 4
    PS4000_P_PRESSURE_SENSOR_50BAR = 5
    PS4000_P_PRESSURE_SENSOR_5BAR = 6
    PS4000_P_OPTICAL_SWITCH = 7
    PS4000_P_UNKNOWN = 8
    PS4000_P_MAX_PROBES = PS4000_P_UNKNOWN


PS4000_PROBE_T = c_int32


class PS4000_CHANNEL_INFO(IntEnum):
    # C: unprefixed CI_* members
    PS4000_CI_RANGES = 0
    PS4000_CI_RESISTANCES = 1
    PS4000_CI_ACCELEROMETER = 2
    PS4000_CI_PROBES = 3
    PS4000_CI_TEMPERATURES = 4


PS4000_CHANNEL_INFO_T = c_int32


class PS4000_ETS_MODE(IntEnum):
    PS4000_ETS_OFF = 0
    PS4000_ETS_FAST = 1
    PS4000_ETS_SLOW = 2
    PS4000_ETS_MODES_MAX = 3


PS4000_ETS_MODE_T = c_int32


class PS4000_TIME_UNITS(IntEnum):
    PS4000_FS = 0
    PS4000_PS = 1
    PS4000_NS = 2
    PS4000_US = 3
    PS4000_MS = 4
    PS4000_S = 5
    PS4000_MAX_TIME_UNITS = 6


PS4000_TIME_UNITS_T = c_int32


class PS4000_SWEEP_TYPE(IntEnum):
    # C: SWEEP_TYPE with UP, DOWN, UPDOWN, DOWNUP, MAX_SWEEP_TYPES
    PS4000_UP = 0
    PS4000_DOWN = 1
    PS4000_UPDOWN = 2
    PS4000_DOWNUP = 3
    PS4000_MAX_SWEEP_TYPES = 4


PS4000_SWEEP_TYPE_T = c_int32


class PS4000_OPERATION_TYPES(IntEnum):
    PS4000_OP_NONE = 0
    PS4000_WHITENOISE = 1
    PS4000_PRBS = 2


PS4000_OPERATION_TYPES_T = c_int32


class PS4000_WAVE_TYPE(IntEnum):
    # C: WAVE_TYPE
    PS4000_SINE = 0
    PS4000_SQUARE = 1
    PS4000_TRIANGLE = 2
    PS4000_RAMP_UP = 3
    PS4000_RAMP_DOWN = 4
    PS4000_SINC = 5
    PS4000_GAUSSIAN = 6
    PS4000_HALF_SINE = 7
    PS4000_DC_VOLTAGE = 8
    PS4000_WHITE_NOISE = 9
    PS4000_MAX_WAVE_TYPES = 10  # C: MAX_WAVE_TYPES


PS4000_WAVE_TYPE_T = c_int32


class PS4000_SIGGEN_TRIG_TYPE(IntEnum):
    # C: SIGGEN_TRIG_TYPE with SIGGEN_* members
    PS4000_SIGGEN_RISING = 0
    PS4000_SIGGEN_FALLING = 1
    PS4000_SIGGEN_GATE_HIGH = 2
    PS4000_SIGGEN_GATE_LOW = 3


PS4000_SIGGEN_TRIG_TYPE_T = c_int32


class PS4000_SIGGEN_TRIG_SOURCE(IntEnum):
    # C: SIGGEN_TRIG_SOURCE with SIGGEN_* members
    PS4000_SIGGEN_NONE = 0
    PS4000_SIGGEN_SCOPE_TRIG = 1
    PS4000_SIGGEN_AUX_IN = 2
    PS4000_SIGGEN_EXT_IN = 3
    PS4000_SIGGEN_SOFT_TRIG = 4


PS4000_SIGGEN_TRIG_SOURCE_T = c_int32


class PS4000_INDEX_MODE(IntEnum):
    # C: INDEX_MODE with SINGLE, DUAL, QUAD, MAX_INDEX_MODES
    PS4000_SINGLE = 0
    PS4000_DUAL = 1
    PS4000_QUAD = 2
    PS4000_MAX_INDEX_MODES = 3


PS4000_INDEX_MODE_T = c_int32


class PS4000_THRESHOLD_MODE(IntEnum):
    # C: THRESHOLD_MODE with LEVEL, WINDOW
    PS4000_LEVEL = 0
    PS4000_WINDOW = 1


PS4000_THRESHOLD_MODE_T = c_int32


class PS4000_THRESHOLD_DIRECTION(IntEnum):
    # C: THRESHOLD_DIRECTION with unprefixed members
    PS4000_ABOVE = 0
    PS4000_BELOW = 1
    PS4000_RISING = 2
    PS4000_FALLING = 3
    PS4000_RISING_OR_FALLING = 4
    PS4000_ABOVE_LOWER = 5
    PS4000_BELOW_LOWER = 6
    PS4000_RISING_LOWER = 7
    PS4000_FALLING_LOWER = 8
    PS4000_INSIDE = PS4000_ABOVE
    PS4000_OUTSIDE = PS4000_BELOW
    PS4000_ENTER = PS4000_RISING
    PS4000_EXIT = PS4000_FALLING
    PS4000_ENTER_OR_EXIT = PS4000_RISING_OR_FALLING
    PS4000_POSITIVE_RUNT = 9
    PS4000_NEGATIVE_RUNT = 10
    PS4000_NONE = PS4000_RISING


PS4000_THRESHOLD_DIRECTION_T = c_int32


class PS4000_TRIGGER_STATE(IntEnum):
    # C: TRIGGER_STATE with CONDITION_* members
    PS4000_CONDITION_DONT_CARE = 0
    PS4000_CONDITION_TRUE = 1
    PS4000_CONDITION_FALSE = 2
    PS4000_CONDITION_MAX = 3


PS4000_TRIGGER_STATE_T = c_int32


@final
class PS4000_TRIGGER_CONDITIONS(CStruct):
    # C: TRIGGER_CONDITIONS
    channelA: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    channelB: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    channelC: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    channelD: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    external: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    aux: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    pulseWidthQualifier: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]


@final
class PS4000_PWQ_CONDITIONS(CStruct):
    # C: PWQ_CONDITIONS
    channelA: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    channelB: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    channelC: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    channelD: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    external: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]
    aux: Annotated[PS4000_TRIGGER_STATE, PS4000_TRIGGER_STATE_T]


@final
class PS4000_TRIGGER_CHANNEL_PROPERTIES(CStruct):
    # C: TRIGGER_CHANNEL_PROPERTIES
    thresholdUpper: Annotated[int, c_int16]
    thresholdUpperHysteresis: Annotated[int, c_uint16]
    thresholdLower: Annotated[int, c_int16]
    thresholdLowerHysteresis: Annotated[int, c_uint16]
    channel: Annotated[PS4000_CHANNEL, PS4000_CHANNEL_T]
    thresholdMode: Annotated[PS4000_THRESHOLD_MODE, PS4000_THRESHOLD_MODE_T]


class PS4000_RATIO_MODE(IntFlag):
    # C: RATIO_MODE with RATIO_MODE_* members. Note AVERAGE is 2 here, unlike
    # PS5000_RATIO_MODE. GetValues documents the modes as combinable (guide
    # p43); the buffer setters reject a combination.
    PS4000_RATIO_MODE_NONE = 0
    PS4000_RATIO_MODE_AGGREGATE = 1
    PS4000_RATIO_MODE_AVERAGE = 2


PS4000_RATIO_MODE_T = c_int32


class PS4000_PULSE_WIDTH_TYPE(IntEnum):
    # C: PULSE_WIDTH_TYPE with PW_TYPE_* members
    PS4000_PW_TYPE_NONE = 0
    PS4000_PW_TYPE_LESS_THAN = 1
    PS4000_PW_TYPE_GREATER_THAN = 2
    PS4000_PW_TYPE_IN_RANGE = 3
    PS4000_PW_TYPE_OUT_OF_RANGE = 4


PS4000_PULSE_WIDTH_TYPE_T = c_int32


class PS4000_HOLDOFF_TYPE(IntEnum):
    PS4000_TIME = 0
    PS4000_MAX_HOLDOFF_TYPE = 1


PS4000_HOLDOFF_TYPE_T = c_int32


class PS4000_FREQUENCY_COUNTER_RANGE(IntEnum):
    # C: unprefixed FC_* members
    PS4000_FC_2K = 0
    PS4000_FC_20K = 1
    PS4000_FC_20 = 2
    PS4000_FC_200 = 3
    PS4000_FC_MAX = 4


PS4000_FREQUENCY_COUNTER_RANGE_T = c_int32


ps4000BlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps4000StreamingReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)

# Like ps5000DataReady, and unlike the newer drivers' DataReady, this one
# carries no status but the trigger information instead.
ps4000DataReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_int16, c_uint32, c_int16, c_void_p
)


class PicoScope4000Wrapper(PicoScopeWrapperBase):
    _library_name = "ps4000"

    def __init__(self, library_path: str | None = None) -> None:
        super().__init__(library_path)

        self._ps4000OpenUnit = self._bind("ps4000OpenUnit", [POINTER(c_int16)])
        # Another open in progress: nothing is started, the status output is 0
        # (guide pp59-60).
        self._ps4000OpenUnitAsync = self._bind(
            "ps4000OpenUnitAsync",
            [POINTER(c_int16)],
            info={PICO_STATUS.PICO_OPEN_OPERATION_IN_PROGRESS},
        )
        self._ps4000OpenUnitEx = self._bind(
            "ps4000OpenUnitEx", [POINTER(c_int16), c_char_p]
        )
        self._ps4000OpenUnitAsyncEx = self._bind(
            "ps4000OpenUnitAsyncEx",
            [POINTER(c_int16), c_char_p],
            info={PICO_STATUS.PICO_OPEN_OPERATION_IN_PROGRESS},
        )
        self._ps4000OpenUnitProgress = self._bind(
            "ps4000OpenUnitProgress",
            [POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps4000GetUnitInfo = self._bind(
            "ps4000GetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps4000FlashLed = self._bind("ps4000FlashLed", [c_int16, c_int16])
        self._ps4000IsLedFlashing = self._bind(
            "ps4000IsLedFlashing", [c_int16, POINTER(c_int16)]
        )
        self._ps4000CloseUnit = self._bind("ps4000CloseUnit", [c_int16])
        self._ps4000MemorySegments = self._bind(
            "ps4000MemorySegments", [c_int16, c_uint16, POINTER(c_int32)]
        )
        self._ps4000SetChannel = self._bind(
            "ps4000SetChannel",
            [c_int16, PS4000_CHANNEL_T, c_int16, c_int16, PS4000_RANGE_T],
        )
        self._ps4000SetNoOfCaptures = self._bind(
            "ps4000SetNoOfCaptures", [c_int16, c_uint16]
        )
        self._ps4000GetTimebase = self._bind(
            "ps4000GetTimebase",
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
        self._ps4000GetTimebase2 = self._bind(
            "ps4000GetTimebase2",
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
        self._ps4000SigGenOff = self._bind("ps4000SigGenOff", [c_int16])
        self._ps4000SetSigGenArbitrary = self._bind(
            "ps4000SetSigGenArbitrary",
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
                PS4000_SWEEP_TYPE_T,
                c_int16,
                PS4000_INDEX_MODE_T,
                c_uint32,
                c_uint32,
                PS4000_SIGGEN_TRIG_TYPE_T,
                PS4000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        # waveType and operationType are int16_t in the header, not the enums.
        self._ps4000SetSigGenBuiltIn = self._bind(
            "ps4000SetSigGenBuiltIn",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_float,
                c_float,
                c_float,
                c_float,
                PS4000_SWEEP_TYPE_T,
                c_int16,
                c_uint32,
                c_uint32,
                PS4000_SIGGEN_TRIG_TYPE_T,
                PS4000_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000SigGenFrequencyToPhase = self._bind(
            "ps4000SigGenFrequencyToPhase",
            [c_int16, c_double, PS4000_INDEX_MODE_T, c_uint32, POINTER(c_uint32)],
        )
        self._ps4000SigGenArbitraryMinMaxValues = self._bind(
            "ps4000SigGenArbitraryMinMaxValues",
            [
                c_int16,
                POINTER(c_int16),
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_uint32),
            ],
        )
        self._ps4000SigGenSoftwareControl = self._bind(
            "ps4000SigGenSoftwareControl", [c_int16, c_int16]
        )
        self._ps4000SetEts = self._bind(
            "ps4000SetEts",
            [c_int16, PS4000_ETS_MODE_T, c_int16, c_int16, POINTER(c_int32)],
        )
        self._ps4000SetSimpleTrigger = self._bind(
            "ps4000SetSimpleTrigger",
            [
                c_int16,
                c_int16,
                PS4000_CHANNEL_T,
                c_int16,
                PS4000_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_int16,
            ],
        )
        self._ps4000SetTriggerChannelProperties = self._bind(
            "ps4000SetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS4000_TRIGGER_CHANNEL_PROPERTIES.c_type),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps4000SetExtTriggerRange = self._bind(
            "ps4000SetExtTriggerRange", [c_int16, PS4000_RANGE_T]
        )
        self._ps4000SetTriggerChannelConditions = self._bind(
            "ps4000SetTriggerChannelConditions",
            [c_int16, POINTER(PS4000_TRIGGER_CONDITIONS.c_type), c_int16],
        )
        self._ps4000SetTriggerChannelDirections = self._bind(
            "ps4000SetTriggerChannelDirections",
            [
                c_int16,
                PS4000_THRESHOLD_DIRECTION_T,
                PS4000_THRESHOLD_DIRECTION_T,
                PS4000_THRESHOLD_DIRECTION_T,
                PS4000_THRESHOLD_DIRECTION_T,
                PS4000_THRESHOLD_DIRECTION_T,
                PS4000_THRESHOLD_DIRECTION_T,
            ],
        )
        self._ps4000SetTriggerDelay = self._bind(
            "ps4000SetTriggerDelay", [c_int16, c_uint32]
        )
        self._ps4000SetPulseWidthQualifier = self._bind(
            "ps4000SetPulseWidthQualifier",
            [
                c_int16,
                POINTER(PS4000_PWQ_CONDITIONS.c_type),
                c_int16,
                PS4000_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS4000_PULSE_WIDTH_TYPE_T,
            ],
        )
        self._ps4000IsTriggerOrPulseWidthQualifierEnabled = self._bind(
            "ps4000IsTriggerOrPulseWidthQualifierEnabled",
            [c_int16, POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps4000GetTriggerTimeOffset = self._bind(
            "ps4000GetTriggerTimeOffset",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS4000_TIME_UNITS_T),
                c_uint16,
            ],
        )
        self._ps4000GetTriggerChannelTimeOffset = self._bind(
            "ps4000GetTriggerChannelTimeOffset",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS4000_TIME_UNITS_T),
                c_uint16,
                PS4000_CHANNEL_T,
            ],
        )
        self._ps4000GetTriggerTimeOffset64 = self._bind(
            "ps4000GetTriggerTimeOffset64",
            [c_int16, POINTER(c_int64), POINTER(PS4000_TIME_UNITS_T), c_uint16],
        )
        self._ps4000GetTriggerChannelTimeOffset64 = self._bind(
            "ps4000GetTriggerChannelTimeOffset64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS4000_TIME_UNITS_T),
                c_uint16,
                PS4000_CHANNEL_T,
            ],
        )
        self._ps4000GetValuesTriggerTimeOffsetBulk = self._bind(
            "ps4000GetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS4000_TIME_UNITS_T),
                c_uint16,
                c_uint16,
            ],
        )
        self._ps4000GetValuesTriggerChannelTimeOffsetBulk = self._bind(
            "ps4000GetValuesTriggerChannelTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS4000_TIME_UNITS_T),
                c_uint16,
                c_uint16,
                PS4000_CHANNEL_T,
            ],
        )
        self._ps4000GetValuesTriggerTimeOffsetBulk64 = self._bind(
            "ps4000GetValuesTriggerTimeOffsetBulk64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS4000_TIME_UNITS_T),
                c_uint16,
                c_uint16,
            ],
        )
        self._ps4000GetValuesTriggerChannelTimeOffsetBulk64 = self._bind(
            "ps4000GetValuesTriggerChannelTimeOffsetBulk64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS4000_TIME_UNITS_T),
                c_uint16,
                c_uint16,
                PS4000_CHANNEL_T,
            ],
        )
        self._ps4000SetDataBufferBulk = self._bind(
            "ps4000SetDataBufferBulk",
            [c_int16, PS4000_CHANNEL_T, c_void_p, c_int32, c_uint16],
        )
        self._ps4000SetDataBuffers = self._bind(
            "ps4000SetDataBuffers",
            [c_int16, PS4000_CHANNEL_T, c_void_p, c_void_p, c_int32],
        )
        self._ps4000SetDataBufferWithMode = self._bind(
            "ps4000SetDataBufferWithMode",
            [c_int16, PS4000_CHANNEL_T, c_void_p, c_int32, PS4000_RATIO_MODE_T],
        )
        self._ps4000SetDataBuffersWithMode = self._bind(
            "ps4000SetDataBuffersWithMode",
            [
                c_int16,
                PS4000_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_int32,
                PS4000_RATIO_MODE_T,
            ],
        )
        self._ps4000SetDataBuffer = self._bind(
            "ps4000SetDataBuffer", [c_int16, PS4000_CHANNEL_T, c_void_p, c_int32]
        )
        self._ps4000SetEtsTimeBuffer = self._bind(
            "ps4000SetEtsTimeBuffer", [c_int16, c_void_p, c_int32]
        )
        self._ps4000SetEtsTimeBuffers = self._bind(
            "ps4000SetEtsTimeBuffers", [c_int16, c_void_p, c_void_p, c_int32]
        )
        self._ps4000RunBlock = self._bind(
            "ps4000RunBlock",
            [
                c_int16,
                c_int32,
                c_int32,
                c_uint32,
                c_int16,
                POINTER(c_int32),
                c_uint16,
                ps4000BlockReady,
                c_void_p,
            ],
        )
        self._ps4000RunStreaming = self._bind(
            "ps4000RunStreaming",
            [
                c_int16,
                POINTER(c_uint32),
                PS4000_TIME_UNITS_T,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint32,
                c_uint32,
            ],
        )
        # The downSampleRatioMode arguments here and below are int16_t in the
        # header, not RATIO_MODE.
        self._ps4000RunStreamingEx = self._bind(
            "ps4000RunStreamingEx",
            [
                c_int16,
                POINTER(c_uint32),
                PS4000_TIME_UNITS_T,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint32,
                c_int16,
                c_uint32,
            ],
        )
        self._ps4000IsReady = self._bind("ps4000IsReady", [c_int16, POINTER(c_int16)])
        self._ps4000GetStreamingLatestValues = self._bind(
            "ps4000GetStreamingLatestValues",
            [c_int16, ps4000StreamingReady, c_void_p],
            # PICO_BUSY: no new streaming data yet / previous call still being
            # processed. The caller is expected to simply poll again.
            info=(PICO_STATUS.PICO_BUSY,),
        )
        self._ps4000NoOfStreamingValues = self._bind(
            "ps4000NoOfStreamingValues", [c_int16, POINTER(c_uint32)]
        )
        self._ps4000GetMaxDownSampleRatio = self._bind(
            "ps4000GetMaxDownSampleRatio",
            [c_int16, c_uint32, POINTER(c_uint32), c_int16, c_uint16],
        )
        self._ps4000GetValues = self._bind(
            "ps4000GetValues",
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
        self._ps4000GetValuesBulk = self._bind(
            "ps4000GetValuesBulk",
            [c_int16, POINTER(c_uint32), c_uint16, c_uint16, POINTER(c_int16)],
        )
        self._ps4000GetValuesAsync = self._bind(
            "ps4000GetValuesAsync",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint16,
                # Declared as void * in the header; a ps4000DataReady is passed.
                c_void_p,
                c_void_p,
            ],
        )
        self._ps4000Stop = self._bind("ps4000Stop", [c_int16])
        self._ps4000SetProbe = self._bind(
            "ps4000SetProbe", [c_int16, PS4000_PROBE_T, PS4000_RANGE_T]
        )
        self._ps4000HoldOff = self._bind(
            "ps4000HoldOff", [c_int16, c_uint64, PS4000_HOLDOFF_TYPE_T]
        )
        self._ps4000GetProbe = self._bind(
            "ps4000GetProbe", [c_int16, POINTER(PS4000_PROBE_T)]
        )
        self._ps4000GetChannelInformation = self._bind(
            "ps4000GetChannelInformation",
            [
                c_int16,
                PS4000_CHANNEL_INFO_T,
                c_int32,
                POINTER(c_int32),
                POINTER(c_int32),
                c_int32,
            ],
        )
        self._ps4000SetFrequencyCounter = self._bind(
            "ps4000SetFrequencyCounter",
            [
                c_int16,
                PS4000_CHANNEL_T,
                c_int16,
                PS4000_FREQUENCY_COUNTER_RANGE_T,
                c_int16,
                c_int16,
            ],
        )
        self._ps4000EnumerateUnits = self._bind(
            "ps4000EnumerateUnits",
            [POINTER(c_int16), c_char_p, POINTER(c_int16)],
            # Finding no units is a valid enumeration result, not a failure.
            info=(PICO_STATUS.PICO_NOT_FOUND,),
        )
        # A responding unit may report its power source instead of PICO_OK
        # (guide p63).
        self._ps4000PingUnit = self._bind(
            "ps4000PingUnit", [c_int16], info=POWER_SOURCE_STATUSES
        )
        self._ps4000SetBwFilter = self._bind(
            "ps4000SetBwFilter", [c_int16, PS4000_CHANNEL_T, c_int16]
        )
        self._ps4000TriggerWithinPreTriggerSamples = self._bind(
            "ps4000TriggerWithinPreTriggerSamples", [c_int16, c_int16]
        )
        self._ps4000GetNoOfCaptures = self._bind(
            "ps4000GetNoOfCaptures", [c_int16, POINTER(c_uint16)]
        )

    def ps4000OpenUnit(self) -> c_int16:
        """Open the first unit found."""
        handle = c_int16(0)
        self._ps4000OpenUnit(byref(handle))
        return handle

    def ps4000OpenUnitAsync(self) -> tuple[bool, PICO_STATUS]:
        """Start opening the first unit found; returns whether the operation
        started and the status.

        If another open operation is in progress, nothing is started and the
        status is PICO_OPEN_OPERATION_IN_PROGRESS.
        """
        status = c_int16(0)
        result = self._ps4000OpenUnitAsync(byref(status))
        return status.value != 0, result

    def ps4000OpenUnitEx(self, serial: str) -> c_int16:
        """Open the unit with the serial number ``serial``."""
        handle = c_int16(0)
        self._ps4000OpenUnitEx(byref(handle), serial.encode())
        return handle

    def ps4000OpenUnitAsyncEx(self, serial: str) -> tuple[bool, PICO_STATUS]:
        """Like :meth:`ps4000OpenUnitAsync`, for the unit with the serial number
        ``serial``."""
        status = c_int16(0)
        result = self._ps4000OpenUnitAsyncEx(byref(status), serial.encode())
        return status.value != 0, result

    def ps4000OpenUnitProgress(self) -> tuple[c_int16, int, bool]:
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        self._ps4000OpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return handle, progressPercent.value, complete.value != 0

    def ps4000GetUnitInfo(self, handle: c_int16, info: PICO_INFO) -> str:
        # Generous for any info string; longer ones are truncated (NUL terminated).
        string = create_string_buffer(4096)
        requiredSize = c_int16(0)
        self._ps4000GetUnitInfo(handle, string, len(string), byref(requiredSize), info)
        return string.value.decode("utf-8")

    def ps4000FlashLed(self, handle: c_int16, start: int) -> None:
        """Flash the LED ``start`` times; < 0 flashes indefinitely, 0 stops.

        RunBlock and RunStreaming cancel the flashing (guide p29).
        """
        self._ps4000FlashLed(handle, start)

    def ps4000IsLedFlashing(self, handle: c_int16) -> bool:
        status = c_int16(0)
        self._ps4000IsLedFlashing(handle, byref(status))
        return status.value != 0

    def ps4000CloseUnit(self, handle: c_int16) -> None:
        self._ps4000CloseUnit(handle)
        self._release_buffers(handle)

    def ps4000MemorySegments(self, handle: c_int16, nSegments: int) -> int:
        assert nSegments > 0
        nMaxSamples = c_int32(0)
        self._ps4000MemorySegments(handle, nSegments, byref(nMaxSamples))
        return nMaxSamples.value

    def ps4000SetChannel(
        self,
        handle: c_int16,
        channel: PS4000_CHANNEL,
        enabled: bool,
        dc: bool,
        range: PS4000_RANGE,
    ) -> None:
        """``dc`` selects DC coupling, otherwise AC."""
        self._ps4000SetChannel(
            handle, channel, 1 if enabled else 0, 1 if dc else 0, range
        )

    def ps4000SetNoOfCaptures(self, handle: c_int16, nCaptures: int) -> None:
        assert nCaptures > 0
        self._ps4000SetNoOfCaptures(handle, nCaptures)

    def ps4000GetTimebase(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        oversample: int,
        segmentIndex: int,
    ) -> tuple[int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_int32(0)
        self._ps4000GetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNanoseconds.value, maxSamples.value

    def ps4000GetTimebase2(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        oversample: int,
        segmentIndex: int,
    ) -> tuple[float, int]:
        timeIntervalNanoseconds = c_float(0)
        maxSamples = c_int32(0)
        self._ps4000GetTimebase2(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNanoseconds.value, maxSamples.value

    def ps4000SigGenOff(self, handle: c_int16) -> None:
        self._ps4000SigGenOff(handle)

    def ps4000SetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: InputValues,
        sweepType: PS4000_SWEEP_TYPE,
        operationType: PS4000_OPERATION_TYPES,
        indexMode: PS4000_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS4000_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """``arbitraryWaveform`` holds the int16 arbitrary waveform samples.

        It is a sequence of ints or a buffer of int16 (e.g. a numpy array with
        ``dtype=np.int16``), which is passed without copying. The samples range
        from 0 to 4095 and up to 8192 of them are allowed on the PicoScope 4226
        and 4227, from -32768 to 32767 and up to 4096 on the 4262 (guide p86).
        """
        waveform, arbitraryWaveformSize = input_argument(
            arbitraryWaveform, c_int16, "arbitraryWaveform"
        )
        self._ps4000SetSigGenArbitrary(
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
            operationType,
            indexMode,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps4000SetSigGenBuiltIn(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS4000_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS4000_SWEEP_TYPE,
        operationType: PS4000_OPERATION_TYPES,
        shots: int,
        sweeps: int,
        triggerType: PS4000_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps4000SetSigGenBuiltIn(
            handle,
            offsetVoltage,
            pkToPk,
            waveType,
            startFrequency,
            stopFrequency,
            increment,
            dwellTime,
            sweepType,
            operationType,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps4000SigGenFrequencyToPhase(
        self,
        handle: c_int16,
        frequency: float,
        indexMode: PS4000_INDEX_MODE,
        bufferLength: int,
    ) -> int:
        phase = c_uint32(0)
        self._ps4000SigGenFrequencyToPhase(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return phase.value

    def ps4000SigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[int, int, int, int]:
        minArbitraryWaveformValue = c_int16(0)
        maxArbitraryWaveformValue = c_int16(0)
        minArbitraryWaveformSize = c_uint32(0)
        maxArbitraryWaveformSize = c_uint32(0)
        self._ps4000SigGenArbitraryMinMaxValues(
            handle,
            byref(minArbitraryWaveformValue),
            byref(maxArbitraryWaveformValue),
            byref(minArbitraryWaveformSize),
            byref(maxArbitraryWaveformSize),
        )
        return (
            minArbitraryWaveformValue.value,
            maxArbitraryWaveformValue.value,
            minArbitraryWaveformSize.value,
            maxArbitraryWaveformSize.value,
        )

    def ps4000SigGenSoftwareControl(self, handle: c_int16, state: bool) -> None:
        self._ps4000SigGenSoftwareControl(handle, 1 if state else 0)

    def ps4000SetEts(
        self,
        handle: c_int16,
        mode: PS4000_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> int:
        sampleTimePicoseconds = c_int32(0)
        self._ps4000SetEts(
            handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
        )
        return sampleTimePicoseconds.value

    def ps4000SetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PS4000_CHANNEL,
        threshold: int,
        direction: PS4000_THRESHOLD_DIRECTION,
        delay: int,
        autoTrigger_ms: int,
    ) -> None:
        assert 0 <= autoTrigger_ms <= 32767  # int16_t in C
        self._ps4000SetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTrigger_ms,
        )

    def ps4000SetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS4000_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> None:
        self._ps4000SetTriggerChannelProperties(
            handle,
            c_array(PS4000_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps4000SetExtTriggerRange(self, handle: c_int16, extRange: PS4000_RANGE) -> None:
        """PicoScope 4262 only: ``PS4000_500MV`` or ``PS4000_5V`` (guide p81)."""
        self._ps4000SetExtTriggerRange(handle, extRange)

    def ps4000SetTriggerChannelConditions(
        self, handle: c_int16, conditions: Sequence[PS4000_TRIGGER_CONDITIONS]
    ) -> None:
        self._ps4000SetTriggerChannelConditions(
            handle, c_array(PS4000_TRIGGER_CONDITIONS, conditions), len(conditions)
        )

    def ps4000SetTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: PS4000_THRESHOLD_DIRECTION,
        channelB: PS4000_THRESHOLD_DIRECTION,
        channelC: PS4000_THRESHOLD_DIRECTION,
        channelD: PS4000_THRESHOLD_DIRECTION,
        ext: PS4000_THRESHOLD_DIRECTION,
        aux: PS4000_THRESHOLD_DIRECTION,
    ) -> None:
        self._ps4000SetTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext, aux
        )

    def ps4000SetTriggerDelay(self, handle: c_int16, delay: int) -> None:
        self._ps4000SetTriggerDelay(handle, delay)

    def ps4000SetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS4000_PWQ_CONDITIONS],
        direction: PS4000_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS4000_PULSE_WIDTH_TYPE,
    ) -> None:
        self._ps4000SetPulseWidthQualifier(
            handle,
            c_array(PS4000_PWQ_CONDITIONS, conditions),
            len(conditions),
            direction,
            lower,
            upper,
            type,
        )

    def ps4000IsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        self._ps4000IsTriggerOrPulseWidthQualifierEnabled(
            handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
        )
        return triggerEnabled.value != 0, pulseWidthQualifierEnabled.value != 0

    def ps4000GetTriggerTimeOffset(self, handle: c_int16, segmentIndex: int) -> float:
        """Returns the trigger time offset of the segment in seconds."""
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS4000_TIME_UNITS_T(0)
        self._ps4000GetTriggerTimeOffset(
            handle, byref(timeUpper), byref(timeLower), byref(timeUnits), segmentIndex
        )
        return seconds(
            int64_from_halves(timeUpper.value, timeLower.value), timeUnits.value
        )

    def ps4000GetTriggerChannelTimeOffset(
        self, handle: c_int16, segmentIndex: int, channel: PS4000_CHANNEL
    ) -> float:
        """Like :meth:`ps4000GetTriggerTimeOffset`, for the trigger on ``channel``."""
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS4000_TIME_UNITS_T(0)
        self._ps4000GetTriggerChannelTimeOffset(
            handle,
            byref(timeUpper),
            byref(timeLower),
            byref(timeUnits),
            segmentIndex,
            channel,
        )
        return seconds(
            int64_from_halves(timeUpper.value, timeLower.value), timeUnits.value
        )

    def ps4000GetTriggerTimeOffset64(self, handle: c_int16, segmentIndex: int) -> float:
        """Returns the trigger time offset of the segment in seconds."""
        time = c_int64(0)
        timeUnits = PS4000_TIME_UNITS_T(0)
        self._ps4000GetTriggerTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return seconds(time.value, timeUnits.value)

    def ps4000GetTriggerChannelTimeOffset64(
        self, handle: c_int16, segmentIndex: int, channel: PS4000_CHANNEL
    ) -> float:
        """Like :meth:`ps4000GetTriggerTimeOffset64`, for the trigger on ``channel``."""
        time = c_int64(0)
        timeUnits = PS4000_TIME_UNITS_T(0)
        self._ps4000GetTriggerChannelTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex, channel
        )
        return seconds(time.value, timeUnits.value)

    def ps4000GetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> list[float]:
        """Returns the trigger time offsets of the segments in seconds.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nSegments = (toSegmentIndex - fromSegmentIndex) + 1
        timesUpper = (c_uint32 * nSegments)()
        timesLower = (c_uint32 * nSegments)()
        timeUnits = (PS4000_TIME_UNITS_T * nSegments)()
        self._ps4000GetValuesTriggerTimeOffsetBulk(
            handle, timesUpper, timesLower, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return [
            seconds(int64_from_halves(upper, lower), units)
            for upper, lower, units in zip(
                timesUpper, timesLower, timeUnits, strict=True
            )
        ]

    def ps4000GetValuesTriggerChannelTimeOffsetBulk(
        self,
        handle: c_int16,
        fromSegmentIndex: int,
        toSegmentIndex: int,
        channel: PS4000_CHANNEL,
    ) -> list[float]:
        """Like :meth:`ps4000GetValuesTriggerTimeOffsetBulk`, for the trigger on
        ``channel``.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nSegments = (toSegmentIndex - fromSegmentIndex) + 1
        timesUpper = (c_uint32 * nSegments)()
        timesLower = (c_uint32 * nSegments)()
        timeUnits = (PS4000_TIME_UNITS_T * nSegments)()
        self._ps4000GetValuesTriggerChannelTimeOffsetBulk(
            handle,
            timesUpper,
            timesLower,
            timeUnits,
            fromSegmentIndex,
            toSegmentIndex,
            channel,
        )
        return [
            seconds(int64_from_halves(upper, lower), units)
            for upper, lower, units in zip(
                timesUpper, timesLower, timeUnits, strict=True
            )
        ]

    def ps4000GetValuesTriggerTimeOffsetBulk64(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> list[float]:
        """Returns the trigger time offsets of the segments in seconds.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nSegments = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * nSegments)()
        timeUnits = (PS4000_TIME_UNITS_T * nSegments)()
        self._ps4000GetValuesTriggerTimeOffsetBulk64(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return [
            seconds(time, units) for time, units in zip(times, timeUnits, strict=True)
        ]

    def ps4000GetValuesTriggerChannelTimeOffsetBulk64(
        self,
        handle: c_int16,
        fromSegmentIndex: int,
        toSegmentIndex: int,
        channel: PS4000_CHANNEL,
    ) -> list[float]:
        """Like :meth:`ps4000GetValuesTriggerTimeOffsetBulk64`, for the trigger on
        ``channel``.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nSegments = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * nSegments)()
        timeUnits = (PS4000_TIME_UNITS_T * nSegments)()
        self._ps4000GetValuesTriggerChannelTimeOffsetBulk64(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex, channel
        )
        return [
            seconds(time, units) for time, units in zip(times, timeUnits, strict=True)
        ]

    def ps4000SetDataBufferBulk(
        self,
        handle: c_int16,
        channel: PS4000_CHANNEL,
        buffer: DataBuffer,
        bufferLth: int,
        waveform: int,
    ) -> None:
        """Like :meth:`ps4000SetDataBuffer`, for one ``waveform`` in rapid block mode.

        ``waveform`` must be less than the number of captures, so call
        :meth:`ps4000SetNoOfCaptures` first (guide p74). The wrapper keeps one
        buffer per channel and waveform.
        """
        arg = buffer_argument(buffer, c_int16, bufferLth, writable=True, name="buffer")
        self._ps4000SetDataBufferBulk(handle, channel, arg, bufferLth, waveform)
        self._keep_buffer((handle.value, "bulk", channel, waveform), arg)

    def ps4000SetDataBuffers(
        self,
        handle: c_int16,
        channel: PS4000_CHANNEL,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Like :meth:`ps4000SetDataBuffer`, with buffers for the maxima and minima."""
        argMax = buffer_argument(
            bufferMax, c_int16, bufferLth, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, c_int16, bufferLth, writable=True, name="bufferMin"
        )
        self._ps4000SetDataBuffers(handle, channel, argMax, argMin, bufferLth)
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_buffer((handle.value, "data", channel), both)

    def ps4000SetDataBufferWithMode(
        self,
        handle: c_int16,
        channel: PS4000_CHANNEL,
        buffer: DataBuffer,
        bufferLth: int,
        mode: PS4000_RATIO_MODE,
    ) -> None:
        """Like :meth:`ps4000SetDataBuffer`, for the downsampling ``mode``.

        The wrapper keeps one buffer per channel and mode, separately from the
        buffers set without a mode.
        """
        # The driver has separate slots for PS4000_RATIO_MODE_AVERAGE and for the
        # other modes, the latter shared with SetDataBuffer(s) (seen in
        # libps4000.so); a separate key per mode only keeps buffers longer.
        arg = buffer_argument(buffer, c_int16, bufferLth, writable=True, name="buffer")
        self._ps4000SetDataBufferWithMode(handle, channel, arg, bufferLth, mode)
        self._keep_buffer((handle.value, "mode", channel, mode), arg)

    def ps4000SetDataBuffersWithMode(
        self,
        handle: c_int16,
        channel: PS4000_CHANNEL,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        bufferLth: int,
        mode: PS4000_RATIO_MODE,
    ) -> None:
        """Like :meth:`ps4000SetDataBufferWithMode`, with buffers for the maxima
        and minima."""
        argMax = buffer_argument(
            bufferMax, c_int16, bufferLth, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, c_int16, bufferLth, writable=True, name="bufferMin"
        )
        self._ps4000SetDataBuffersWithMode(
            handle, channel, argMax, argMin, bufferLth, mode
        )
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_buffer((handle.value, "mode", channel, mode), both)

    def ps4000SetDataBuffer(
        self,
        handle: c_int16,
        channel: PS4000_CHANNEL,
        buffer: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Set the buffer the driver writes the samples of ``channel`` to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int16 elements (e.g. ``np.empty(bufferLth, np.int16)``), or None. The
        wrapper keeps it from being freed or resized until it is replaced (also
        by :meth:`ps4000SetDataBuffers`), set to None or the unit is closed. A
        raw address (int or ``c_void_p``) is passed unchecked and must be kept
        valid by the caller.
        """
        arg = buffer_argument(buffer, c_int16, bufferLth, writable=True, name="buffer")
        self._ps4000SetDataBuffer(handle, channel, arg, bufferLth)
        self._keep_buffer((handle.value, "data", channel), arg)

    def ps4000SetEtsTimeBuffer(
        self, handle: c_int16, buffer: DataBuffer, bufferLth: int
    ) -> None:
        """Set the buffer the driver writes the ETS sample times to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int64 elements, or None. The wrapper keeps it from being freed or
        resized until it is replaced (also by :meth:`ps4000SetEtsTimeBuffers`),
        set to None or the unit is closed. A raw address (int or ``c_void_p``)
        is passed unchecked and must be kept valid by the caller.
        """
        arg = buffer_argument(buffer, c_int64, bufferLth, writable=True, name="buffer")
        self._ps4000SetEtsTimeBuffer(handle, arg, bufferLth)
        # Both ETS setters share the key: the driver keeps either the int64
        # buffer or the pair and clears the other (seen in libps4000.so).
        self._keep_buffer((handle.value, "ets"), arg)

    def ps4000SetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: DataBuffer,
        timeLower: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Like :meth:`ps4000SetEtsTimeBuffer`, with uint32 buffers for the upper
        and lower 32 bits of the times."""
        argUpper = buffer_argument(
            timeUpper, c_uint32, bufferLth, writable=True, name="timeUpper"
        )
        argLower = buffer_argument(
            timeLower, c_uint32, bufferLth, writable=True, name="timeLower"
        )
        self._ps4000SetEtsTimeBuffers(handle, argUpper, argLower, bufferLth)
        both = None if argUpper is None and argLower is None else (argUpper, argLower)
        self._keep_buffer((handle.value, "ets"), both)

    def ps4000RunBlock(
        self,
        handle: c_int16,
        noOfPreTriggerSamples: int,
        noOfPostTriggerSamples: int,
        timebase: int,
        oversample: int,
        segmentIndex: int,
        lpReady: Callable[[int, PICO_STATUS], None] | None,
    ) -> int:
        """``lpReady(handle, status)`` is called when the block is ready.

        Returns the time in ms the scope will spend collecting samples.
        """
        assert noOfPreTriggerSamples >= 0
        assert noOfPostTriggerSamples >= 0
        timeIndisposedMs = c_int32(0)
        cfunc = ps4000BlockReady()  # NULL; ctypes rejects None here
        if lpReady is not None:
            callback = lpReady

            def cbwrapper(handle: int, status: int, _: c_void_p) -> None:
                callback(handle, PICO_STATUS(status))

            cfunc = ps4000BlockReady(cbwrapper)
        self._with_callback(
            self._callback_key("ps4000RunBlock", handle),
            cfunc,
            lambda: self._ps4000RunBlock(
                handle,
                noOfPreTriggerSamples,
                noOfPostTriggerSamples,
                timebase,
                oversample,
                byref(timeIndisposedMs),
                segmentIndex,
                cfunc,
                None,
            ),
        )
        return timeIndisposedMs.value

    def ps4000RunStreaming(
        self,
        handle: c_int16,
        sampleInterval: int,
        sampleIntervalTimeUnits: PS4000_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostPreTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        overviewBufferSize: int,
    ) -> int:
        """Returns the actual sample interval; see :meth:`ps4000RunStreamingEx`
        for a downsampling mode."""
        interval = c_uint32(sampleInterval)
        self._ps4000RunStreaming(
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

    def ps4000RunStreamingEx(
        self,
        handle: c_int16,
        sampleInterval: int,
        sampleIntervalTimeUnits: PS4000_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostPreTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        downSampleRatioMode: PS4000_RATIO_MODE,
        overviewBufferSize: int,
    ) -> int:
        """Returns the actual sample interval."""
        interval = c_uint32(sampleInterval)
        self._ps4000RunStreamingEx(
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
        return interval.value

    def ps4000IsReady(self, handle: c_int16) -> bool:
        ready = c_int16(0)
        self._ps4000IsReady(handle, byref(ready))
        return ready.value != 0

    def ps4000GetStreamingLatestValues(
        self,
        handle: c_int16,
        lpPs4000Ready: Callable[
            [int, int, int, PS4000_CHANNEL_FLAGS, int, bool, bool], None
        ],
    ) -> PICO_STATUS:
        """``lpPs4000Ready(handle, noOfSamples, startIndex, overflow, triggerAt,
        triggered, autoStop)`` is called when new data has been copied.

        Returns PICO_OK, or PICO_BUSY if there is no new data yet (poll again).
        """
        callback = lpPs4000Ready

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
                PS4000_CHANNEL_FLAGS(overflow),
                triggerAt,
                triggered != 0,
                autoStop != 0,
            )

        cfunc = ps4000StreamingReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps4000GetStreamingLatestValues", handle),
            cfunc,
            lambda: self._ps4000GetStreamingLatestValues(handle, cfunc, None),
        )

    def ps4000NoOfStreamingValues(self, handle: c_int16) -> int:
        noOfValues = c_uint32(0)
        self._ps4000NoOfStreamingValues(handle, byref(noOfValues))
        return noOfValues.value

    def ps4000GetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggreatedSamples: int,
        downSampleRatioMode: PS4000_RATIO_MODE,
        segmentIndex: int,
    ) -> int:
        maxDownSampleRatio = c_uint32(0)
        self._ps4000GetMaxDownSampleRatio(
            handle,
            noOfUnaggreatedSamples,
            byref(maxDownSampleRatio),
            downSampleRatioMode,
            segmentIndex,
        )
        return maxDownSampleRatio.value

    def ps4000GetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS4000_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[int, PS4000_CHANNEL_FLAGS]:
        """Returns the number of samples retrieved and the overflowed channels."""
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        self._ps4000GetValues(
            handle,
            startIndex,
            byref(noOfSamples_),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return noOfSamples_.value, PS4000_CHANNEL_FLAGS(overflow.value)

    def ps4000GetValuesBulk(
        self,
        handle: c_int16,
        noOfSamples: int,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[int, list[PS4000_CHANNEL_FLAGS]]:
        """Returns the number of samples per segment and the overflowed channels
        of each segment. There are no downsampling parameters.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert noOfSamples > 0
        assert fromSegmentIndex <= toSegmentIndex
        noOfSamples_ = c_uint32(noOfSamples)
        nSegments = (toSegmentIndex - fromSegmentIndex) + 1
        overflow = (c_int16 * nSegments)()
        self._ps4000GetValuesBulk(
            handle, byref(noOfSamples_), fromSegmentIndex, toSegmentIndex, overflow
        )
        return noOfSamples_.value, [PS4000_CHANNEL_FLAGS(f) for f in overflow]

    def ps4000GetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS4000_RATIO_MODE,
        segmentIndex: int,
        lpDataReady: Callable[[int, int, PS4000_CHANNEL_FLAGS, int, bool], None],
    ) -> None:
        """``lpDataReady(handle, noOfSamples, overflow, triggerAt, triggered)`` is
        called when the data has been retrieved."""
        # TODO: The guide (p44) names ps4000StreamingReady as the callback type
        # (the header declares lpDataReady as void*), but pp22 and 27 name
        # ps4000DataReady, which is what this method passes. Offer the streaming
        # callback too, or document this method as block-mode only.
        callback = lpDataReady

        def cbwrapper(
            handle: int,
            noOfSamples: int,
            overflow: int,
            triggerAt: int,
            triggered: int,
            _: c_void_p,
        ) -> None:
            callback(
                handle,
                noOfSamples,
                PS4000_CHANNEL_FLAGS(overflow),
                triggerAt,
                triggered != 0,
            )

        cfunc = ps4000DataReady(cbwrapper)
        self._with_callback(
            self._callback_key("ps4000GetValuesAsync", handle),
            cfunc,
            lambda: self._ps4000GetValuesAsync(
                handle,
                startIndex,
                noOfSamples,
                downSampleRatio,
                downSampleRatioMode,
                segmentIndex,
                cfunc,
                None,
            ),
        )

    def ps4000Stop(self, handle: c_int16) -> None:
        self._ps4000Stop(handle)

    def ps4000SetProbe(
        self, handle: c_int16, probe: PS4000_PROBE, range: PS4000_RANGE
    ) -> None:
        self._ps4000SetProbe(handle, probe, range)

    def ps4000HoldOff(
        self, handle: c_int16, holdoff: int, type: PS4000_HOLDOFF_TYPE
    ) -> None:
        """Not supported by the driver yet, reserved for future use (guide p52)."""
        self._ps4000HoldOff(handle, holdoff, type)

    def ps4000GetProbe(self, handle: c_int16) -> PS4000_PROBE:
        probe = PS4000_PROBE_T(0)
        self._ps4000GetProbe(handle, byref(probe))
        return PS4000_PROBE(probe.value)

    def ps4000GetChannelInformation(
        self,
        handle: c_int16,
        info: PS4000_CHANNEL_INFO,
        probe: int,
        channels: PS4000_CHANNEL,
    ) -> list[PS4000_RANGE | PS4000_PROBE]:
        """Returns the ranges of the kind ``info`` available on ``channels``, or
        the probes for ``PS4000_CI_PROBES``.

        ``probe`` is not used and must be 0 (guide p30).
        """
        # The first call (NULL array) only queries the number of ranges.
        length = c_int32(0)
        self._ps4000GetChannelInformation(
            handle, info, probe, None, byref(length), channels
        )
        capacity = length.value
        if capacity <= 0:
            return []
        ranges = (c_int32 * capacity)()
        self._ps4000GetChannelInformation(
            handle, info, probe, ranges, byref(length), channels
        )
        n = min(length.value, capacity)
        if info == PS4000_CHANNEL_INFO.PS4000_CI_PROBES:
            return [PS4000_PROBE(r) for r in ranges[:n]]
        return [PS4000_RANGE(r) for r in ranges[:n]]

    def ps4000SetFrequencyCounter(
        self,
        handle: c_int16,
        channel: PS4000_CHANNEL,
        enabled: bool,
        range: PS4000_FREQUENCY_COUNTER_RANGE,
        thresholdMajor: int,
        thresholdMinor: int,
    ) -> None:
        self._ps4000SetFrequencyCounter(
            handle,
            channel,
            1 if enabled else 0,
            range,
            thresholdMajor,
            thresholdMinor,
        )

    def ps4000EnumerateUnits(self) -> list[str]:
        """Returns the serial numbers of the units found (not opened yet)."""
        count = c_int16(0)
        serials = create_string_buffer(4096)
        serialLth = c_int16(len(serials))
        self._ps4000EnumerateUnits(byref(count), serials, byref(serialLth))
        units = [s for s in serials.value.decode("utf-8").split(",") if s]
        assert len(units) == count.value
        return units

    def ps4000PingUnit(self, handle: c_int16) -> PICO_STATUS:
        """Returns the status, which tells the power source if not PICO_OK."""
        return self._ps4000PingUnit(handle)

    def ps4000SetBwFilter(
        self, handle: c_int16, channel: PS4000_CHANNEL, enable: bool
    ) -> None:
        self._ps4000SetBwFilter(handle, channel, 1 if enable else 0)

    def ps4000TriggerWithinPreTriggerSamples(self, handle: c_int16, state: int) -> None:
        """Undocumented; like the later drivers, presumably 0 disables and 1 arms."""
        self._ps4000TriggerWithinPreTriggerSamples(handle, state)

    def ps4000GetNoOfCaptures(self, handle: c_int16) -> int:
        nCaptures = c_uint16(0)
        self._ps4000GetNoOfCaptures(handle, byref(nCaptures))
        return nCaptures.value


@final
class PicoScope4000Device(PicoScopeDeviceBase[PicoScope4000Wrapper]):
    """An opened ps4000 unit; the functions of :class:`PicoScope4000Wrapper` with its handle.

    See :class:`~pycosdk.PicoScopeDeviceBase`.
    """

    _wrapper_type = PicoScope4000Wrapper

    @classmethod
    def ps4000OpenUnit(cls) -> Self:
        """Like :meth:`PicoScope4000Wrapper.ps4000OpenUnit`, returning a device instead of the handle."""
        return cls(cls.shared_wrapper().ps4000OpenUnit())

    @classmethod
    def ps4000OpenUnitEx(cls, serial: str) -> Self:
        """Like :meth:`PicoScope4000Wrapper.ps4000OpenUnitEx`, returning a device instead of the handle."""
        return cls(cls.shared_wrapper().ps4000OpenUnitEx(serial))

    @classmethod
    def ps4000OpenUnitProgress(cls) -> tuple[Self | None, int, bool]:
        """Like :meth:`PicoScope4000Wrapper.ps4000OpenUnitProgress`, with a device instead of the handle once opened."""
        handle, progressPercent, complete = (
            cls.shared_wrapper().ps4000OpenUnitProgress()
        )
        return cls(handle) if complete else None, progressPercent, complete

    ps4000OpenUnitAsync = wrapper_function(PicoScope4000Wrapper.ps4000OpenUnitAsync)
    ps4000OpenUnitAsyncEx = wrapper_function(PicoScope4000Wrapper.ps4000OpenUnitAsyncEx)
    ps4000EnumerateUnits = wrapper_function(PicoScope4000Wrapper.ps4000EnumerateUnits)

    ps4000GetUnitInfo = handle_method(PicoScope4000Wrapper.ps4000GetUnitInfo)
    ps4000FlashLed = handle_method(PicoScope4000Wrapper.ps4000FlashLed)
    ps4000IsLedFlashing = handle_method(PicoScope4000Wrapper.ps4000IsLedFlashing)
    ps4000CloseUnit = handle_method(PicoScope4000Wrapper.ps4000CloseUnit, closes=True)
    ps4000MemorySegments = handle_method(PicoScope4000Wrapper.ps4000MemorySegments)
    ps4000SetChannel = handle_method(PicoScope4000Wrapper.ps4000SetChannel)
    ps4000SetNoOfCaptures = handle_method(PicoScope4000Wrapper.ps4000SetNoOfCaptures)
    ps4000GetTimebase = handle_method(PicoScope4000Wrapper.ps4000GetTimebase)
    ps4000GetTimebase2 = handle_method(PicoScope4000Wrapper.ps4000GetTimebase2)
    ps4000SigGenOff = handle_method(PicoScope4000Wrapper.ps4000SigGenOff)
    ps4000SetSigGenArbitrary = handle_method(
        PicoScope4000Wrapper.ps4000SetSigGenArbitrary
    )
    ps4000SetSigGenBuiltIn = handle_method(PicoScope4000Wrapper.ps4000SetSigGenBuiltIn)
    ps4000SigGenFrequencyToPhase = handle_method(
        PicoScope4000Wrapper.ps4000SigGenFrequencyToPhase
    )
    ps4000SigGenArbitraryMinMaxValues = handle_method(
        PicoScope4000Wrapper.ps4000SigGenArbitraryMinMaxValues
    )
    ps4000SigGenSoftwareControl = handle_method(
        PicoScope4000Wrapper.ps4000SigGenSoftwareControl
    )
    ps4000SetEts = handle_method(PicoScope4000Wrapper.ps4000SetEts)
    ps4000SetSimpleTrigger = handle_method(PicoScope4000Wrapper.ps4000SetSimpleTrigger)
    ps4000SetTriggerChannelProperties = handle_method(
        PicoScope4000Wrapper.ps4000SetTriggerChannelProperties
    )
    ps4000SetExtTriggerRange = handle_method(
        PicoScope4000Wrapper.ps4000SetExtTriggerRange
    )
    ps4000SetTriggerChannelConditions = handle_method(
        PicoScope4000Wrapper.ps4000SetTriggerChannelConditions
    )
    ps4000SetTriggerChannelDirections = handle_method(
        PicoScope4000Wrapper.ps4000SetTriggerChannelDirections
    )
    ps4000SetTriggerDelay = handle_method(PicoScope4000Wrapper.ps4000SetTriggerDelay)
    ps4000SetPulseWidthQualifier = handle_method(
        PicoScope4000Wrapper.ps4000SetPulseWidthQualifier
    )
    ps4000IsTriggerOrPulseWidthQualifierEnabled = handle_method(
        PicoScope4000Wrapper.ps4000IsTriggerOrPulseWidthQualifierEnabled
    )
    ps4000GetTriggerTimeOffset = handle_method(
        PicoScope4000Wrapper.ps4000GetTriggerTimeOffset
    )
    ps4000GetTriggerChannelTimeOffset = handle_method(
        PicoScope4000Wrapper.ps4000GetTriggerChannelTimeOffset
    )
    ps4000GetTriggerTimeOffset64 = handle_method(
        PicoScope4000Wrapper.ps4000GetTriggerTimeOffset64
    )
    ps4000GetTriggerChannelTimeOffset64 = handle_method(
        PicoScope4000Wrapper.ps4000GetTriggerChannelTimeOffset64
    )
    ps4000GetValuesTriggerTimeOffsetBulk = handle_method(
        PicoScope4000Wrapper.ps4000GetValuesTriggerTimeOffsetBulk
    )
    ps4000GetValuesTriggerChannelTimeOffsetBulk = handle_method(
        PicoScope4000Wrapper.ps4000GetValuesTriggerChannelTimeOffsetBulk
    )
    ps4000GetValuesTriggerTimeOffsetBulk64 = handle_method(
        PicoScope4000Wrapper.ps4000GetValuesTriggerTimeOffsetBulk64
    )
    ps4000GetValuesTriggerChannelTimeOffsetBulk64 = handle_method(
        PicoScope4000Wrapper.ps4000GetValuesTriggerChannelTimeOffsetBulk64
    )
    ps4000SetDataBufferBulk = handle_method(
        PicoScope4000Wrapper.ps4000SetDataBufferBulk
    )
    ps4000SetDataBuffers = handle_method(PicoScope4000Wrapper.ps4000SetDataBuffers)
    ps4000SetDataBufferWithMode = handle_method(
        PicoScope4000Wrapper.ps4000SetDataBufferWithMode
    )
    ps4000SetDataBuffersWithMode = handle_method(
        PicoScope4000Wrapper.ps4000SetDataBuffersWithMode
    )
    ps4000SetDataBuffer = handle_method(PicoScope4000Wrapper.ps4000SetDataBuffer)
    ps4000SetEtsTimeBuffer = handle_method(PicoScope4000Wrapper.ps4000SetEtsTimeBuffer)
    ps4000SetEtsTimeBuffers = handle_method(
        PicoScope4000Wrapper.ps4000SetEtsTimeBuffers
    )
    ps4000RunBlock = handle_method(PicoScope4000Wrapper.ps4000RunBlock)
    ps4000RunStreaming = handle_method(PicoScope4000Wrapper.ps4000RunStreaming)
    ps4000RunStreamingEx = handle_method(PicoScope4000Wrapper.ps4000RunStreamingEx)
    ps4000IsReady = handle_method(PicoScope4000Wrapper.ps4000IsReady)
    ps4000GetStreamingLatestValues = handle_method(
        PicoScope4000Wrapper.ps4000GetStreamingLatestValues
    )
    ps4000NoOfStreamingValues = handle_method(
        PicoScope4000Wrapper.ps4000NoOfStreamingValues
    )
    ps4000GetMaxDownSampleRatio = handle_method(
        PicoScope4000Wrapper.ps4000GetMaxDownSampleRatio
    )
    ps4000GetValues = handle_method(PicoScope4000Wrapper.ps4000GetValues)
    ps4000GetValuesBulk = handle_method(PicoScope4000Wrapper.ps4000GetValuesBulk)
    ps4000GetValuesAsync = handle_method(PicoScope4000Wrapper.ps4000GetValuesAsync)
    ps4000Stop = handle_method(PicoScope4000Wrapper.ps4000Stop)
    ps4000SetProbe = handle_method(PicoScope4000Wrapper.ps4000SetProbe)
    ps4000HoldOff = handle_method(PicoScope4000Wrapper.ps4000HoldOff)
    ps4000GetProbe = handle_method(PicoScope4000Wrapper.ps4000GetProbe)
    ps4000GetChannelInformation = handle_method(
        PicoScope4000Wrapper.ps4000GetChannelInformation
    )
    ps4000SetFrequencyCounter = handle_method(
        PicoScope4000Wrapper.ps4000SetFrequencyCounter
    )
    ps4000PingUnit = handle_method(PicoScope4000Wrapper.ps4000PingUnit)
    ps4000SetBwFilter = handle_method(PicoScope4000Wrapper.ps4000SetBwFilter)
    ps4000TriggerWithinPreTriggerSamples = handle_method(
        PicoScope4000Wrapper.ps4000TriggerWithinPreTriggerSamples
    )
    ps4000GetNoOfCaptures = handle_method(PicoScope4000Wrapper.ps4000GetNoOfCaptures)


__all__ = (
    "PS4000_CHANNEL",
    "PS4000_CHANNEL_BUFFER_INDEX",
    "PS4000_CHANNEL_FLAGS",
    "PS4000_CHANNEL_INFO",
    "PS4000_ETS_MODE",
    "PS4000_EXT_MAX_VALUE",
    "PS4000_EXT_MIN_VALUE",
    "PS4000_FREQUENCY_COUNTER_RANGE",
    "PS4000_HOLDOFF_TYPE",
    "PS4000_INDEX_MODE",
    "PS4000_LOST_DATA",
    "PS4000_MAX_DELAY_COUNT",
    "PS4000_MAX_OVERSAMPLE_12BIT",
    "PS4000_MAX_OVERSAMPLE_8BIT",
    "PS4000_MAX_PULSE_WIDTH_QUALIFIER_COUNT",
    "PS4000_MAX_SIG_GEN_BUFFER_SIZE",
    "PS4000_MAX_SIG_GEN_FREQ",
    "PS4000_MAX_SIG_GEN_FREQ_4262",
    "PS4000_MAX_SWEEPS_SHOTS",
    "PS4000_MAX_VALUE",
    "PS4000_MIN_DWELL_COUNT",
    "PS4000_MIN_SIG_GEN_BUFFER_SIZE",
    "PS4000_MIN_SIG_GEN_FREQ",
    "PS4000_MIN_VALUE",
    "PS4000_OPERATION_TYPES",
    "PS4000_PROBE",
    "PS4000_PULSE_WIDTH_TYPE",
    "PS4000_PWQ_CONDITIONS",
    "PS4000_RANGE",
    "PS4000_RATIO_MODE",
    "PS4000_SIGGEN_TRIG_SOURCE",
    "PS4000_SIGGEN_TRIG_TYPE",
    "PS4000_SWEEP_TYPE",
    "PS4000_THRESHOLD_DIRECTION",
    "PS4000_THRESHOLD_MODE",
    "PS4000_TIME_UNITS",
    "PS4000_TRIGGER_CHANNEL_PROPERTIES",
    "PS4000_TRIGGER_CONDITIONS",
    "PS4000_TRIGGER_STATE",
    "PS4000_WAVE_TYPE",
    "PS4262_MAX_VALUE",
    "PS4262_MAX_WAVEFORM_BUFFER_SIZE",
    "PS4262_MIN_DWELL_COUNT",
    "PS4262_MIN_VALUE",
    "PS4XXX_MAX_ETS_CYCLES",
    "PS4XXX_MAX_INTERLEAVE",
    "PicoScope4000Wrapper",
    "PicoScope4000Device",
    "ps4000BlockReady",
    "ps4000DataReady",
    "ps4000StreamingReady",
)
