# pyright: reportAny=false, reportUnannotatedClassAttribute=false
from collections.abc import Callable, Sequence
from ctypes import (
    POINTER,
    byref,
    c_char_p,
    c_double,
    c_float,
    c_int8,
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
from typing import Annotated, Any, Self, final

from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase
from ._buffer import DataBuffer, InputValues, buffer_argument, input_argument
from ._device import PicoScopeDeviceBase, handle_method, wrapper_function
from ._struct import CStruct, c_array
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T

PS2000A_MAX_ETS_CYCLES = 500  # C: MAX_ETS_CYCLES
PS2000A_MAX_INTERLEAVE = 40  # C: MAX_INTERLEAVE

PS2208_MAX_ETS_CYCLES = 500
PS2208_MAX_INTERLEAVE = 20

PS2207_MAX_ETS_CYCLES = 500
PS2207_MAX_INTERLEAVE = 20

PS2206_MAX_ETS_CYCLES = 250
PS2206_MAX_INTERLEAVE = 10

PS2000A_EXT_MAX_VALUE = 32767
PS2000A_EXT_MIN_VALUE = -32767

PS2000A_MAX_LOGIC_LEVEL = 32767
PS2000A_MIN_LOGIC_LEVEL = -32767

PS2000A_MIN_SIG_GEN_FREQ = 0.0  # C: MIN_SIG_GEN_FREQ
PS2000A_MAX_SIG_GEN_FREQ = 20000000.0  # C: MAX_SIG_GEN_FREQ

PS2000A_MAX_SIG_GEN_BUFFER_SIZE = 8192
PS2000A_MIN_SIG_GEN_BUFFER_SIZE = 1
PS2000A_MIN_DWELL_COUNT = 3
PS2000A_MAX_SWEEPS_SHOTS = (1 << 30) - 1

PS2000A_MAX_ANALOGUE_OFFSET_50MV_200MV = 0.250
PS2000A_MIN_ANALOGUE_OFFSET_50MV_200MV = -0.250
PS2000A_MAX_ANALOGUE_OFFSET_500MV_2V = 2.500
PS2000A_MIN_ANALOGUE_OFFSET_500MV_2V = -2.500
PS2000A_MAX_ANALOGUE_OFFSET_5V_20V = 20.0
PS2000A_MIN_ANALOGUE_OFFSET_5V_20V = -20.0

PS2000A_SHOT_SWEEP_TRIGGER_CONTINUOUS_RUN = 0xFFFFFFFF

PS2000A_CHANNEL_BUFFER_INDEX_T = c_int32


class PS2000A_CHANNEL_BUFFER_INDEX(IntEnum):
    PS2000A_CHANNEL_A_MAX = 0
    PS2000A_CHANNEL_A_MIN = 1
    PS2000A_CHANNEL_B_MAX = 2
    PS2000A_CHANNEL_B_MIN = 3
    PS2000A_CHANNEL_C_MAX = 4
    PS2000A_CHANNEL_C_MIN = 5
    PS2000A_CHANNEL_D_MAX = 6
    PS2000A_CHANNEL_D_MIN = 7
    PS2000A_MAX_CHANNEL_BUFFERS = 8


PS2000A_CHANNEL_T = c_int32


class PS2000A_CHANNEL(IntEnum):
    PS2000A_CHANNEL_A = 0
    PS2000A_CHANNEL_B = 1
    PS2000A_CHANNEL_C = 2
    PS2000A_CHANNEL_D = 3
    PS2000A_EXTERNAL = 4
    PS2000A_MAX_CHANNELS = PS2000A_EXTERNAL
    PS2000A_TRIGGER_AUX = 5
    PS2000A_MAX_TRIGGER_SOURCES = 6


PS2000A_TRIGGER_OPERAND_T = c_int32


class PS2000A_TRIGGER_OPERAND(IntEnum):
    PS2000A_OPERAND_NONE = 0
    PS2000A_OPERAND_OR = 1
    PS2000A_OPERAND_AND = 2
    PS2000A_OPERAND_THEN = 3


PS2000A_DIGITAL_PORT_T = c_int32


class PS2000A_DIGITAL_PORT(IntEnum):
    PS2000A_DIGITAL_PORT0 = 0x80
    PS2000A_DIGITAL_PORT1 = 0x81
    PS2000A_DIGITAL_PORT2 = 0x82
    PS2000A_DIGITAL_PORT3 = 0x83
    PS2000A_MAX_DIGITAL_PORTS = (PS2000A_DIGITAL_PORT3 - PS2000A_DIGITAL_PORT0) + 1


PS2000A_DIGITAL_CHANNEL_T = c_int32


class PS2000A_DIGITAL_CHANNEL(IntEnum):
    PS2000A_DIGITAL_CHANNEL_0 = 0
    PS2000A_DIGITAL_CHANNEL_1 = 1
    PS2000A_DIGITAL_CHANNEL_2 = 2
    PS2000A_DIGITAL_CHANNEL_3 = 3
    PS2000A_DIGITAL_CHANNEL_4 = 4
    PS2000A_DIGITAL_CHANNEL_5 = 5
    PS2000A_DIGITAL_CHANNEL_6 = 6
    PS2000A_DIGITAL_CHANNEL_7 = 7
    PS2000A_DIGITAL_CHANNEL_8 = 8
    PS2000A_DIGITAL_CHANNEL_9 = 9
    PS2000A_DIGITAL_CHANNEL_10 = 10
    PS2000A_DIGITAL_CHANNEL_11 = 11
    PS2000A_DIGITAL_CHANNEL_12 = 12
    PS2000A_DIGITAL_CHANNEL_13 = 13
    PS2000A_DIGITAL_CHANNEL_14 = 14
    PS2000A_DIGITAL_CHANNEL_15 = 15
    PS2000A_DIGITAL_CHANNEL_16 = 16
    PS2000A_DIGITAL_CHANNEL_17 = 17
    PS2000A_DIGITAL_CHANNEL_18 = 18
    PS2000A_DIGITAL_CHANNEL_19 = 19
    PS2000A_DIGITAL_CHANNEL_20 = 20
    PS2000A_DIGITAL_CHANNEL_21 = 21
    PS2000A_DIGITAL_CHANNEL_22 = 22
    PS2000A_DIGITAL_CHANNEL_23 = 23
    PS2000A_DIGITAL_CHANNEL_24 = 24
    PS2000A_DIGITAL_CHANNEL_25 = 25
    PS2000A_DIGITAL_CHANNEL_26 = 26
    PS2000A_DIGITAL_CHANNEL_27 = 27
    PS2000A_DIGITAL_CHANNEL_28 = 28
    PS2000A_DIGITAL_CHANNEL_29 = 29
    PS2000A_DIGITAL_CHANNEL_30 = 30
    PS2000A_DIGITAL_CHANNEL_31 = 31
    PS2000A_MAX_DIGITAL_CHANNELS = 32


PS2000A_RANGE_T = c_int32


class PS2000A_RANGE(IntEnum):
    PS2000A_10MV = 0
    PS2000A_20MV = 1
    PS2000A_50MV = 2
    PS2000A_100MV = 3
    PS2000A_200MV = 4
    PS2000A_500MV = 5
    PS2000A_1V = 6
    PS2000A_2V = 7
    PS2000A_5V = 8
    PS2000A_10V = 9
    PS2000A_20V = 10
    PS2000A_50V = 11
    PS2000A_MAX_RANGES = 12


PS2000A_COUPLING_T = c_int32


class PS2000A_COUPLING(IntEnum):
    PS2000A_AC = 0
    PS2000A_DC = 1


PS2000A_CHANNEL_INFO_T = c_int32


class PS2000A_CHANNEL_INFO(IntEnum):
    PS2000A_CI_RANGES = 0


PS2000A_ETS_MODE_T = c_int32


class PS2000A_ETS_MODE(IntEnum):
    PS2000A_ETS_OFF = 0
    PS2000A_ETS_FAST = 1
    PS2000A_ETS_SLOW = 2
    PS2000A_ETS_MODES_MAX = 3


PS2000A_TIME_UNITS_T = c_int32


class PS2000A_TIME_UNITS(IntEnum):
    PS2000A_FS = 0
    PS2000A_PS = 1
    PS2000A_NS = 2
    PS2000A_US = 3
    PS2000A_MS = 4
    PS2000A_S = 5
    PS2000A_MAX_TIME_UNITS = 6


PS2000A_SWEEP_TYPE_T = c_int32


class PS2000A_SWEEP_TYPE(IntEnum):
    PS2000A_UP = 0
    PS2000A_DOWN = 1
    PS2000A_UPDOWN = 2
    PS2000A_DOWNUP = 3
    PS2000A_MAX_SWEEP_TYPES = 4


PS2000A_WAVE_TYPE_T = c_int32


class PS2000A_WAVE_TYPE(IntEnum):
    PS2000A_SINE = 0
    PS2000A_SQUARE = 1
    PS2000A_TRIANGLE = 2
    PS2000A_RAMP_UP = 3
    PS2000A_RAMP_DOWN = 4
    PS2000A_SINC = 5
    PS2000A_GAUSSIAN = 6
    PS2000A_HALF_SINE = 7
    PS2000A_DC_VOLTAGE = 8
    PS2000A_MAX_WAVE_TYPES = 9


PS2000A_EXTRA_OPERATIONS_T = c_int32


class PS2000A_EXTRA_OPERATIONS(IntEnum):
    PS2000A_ES_OFF = 0
    PS2000A_WHITENOISE = 1
    PS2000A_PRBS = 2


PS2000A_CAPTURE_STATE_T = c_int32


class PS2000A_CAPTURE_STATE(IntEnum):
    PS2000A_CAPTURE_STATE_NONE = 0
    PS2000A_CAPTURE_STATE_IDLE = 1
    PS2000A_CAPTURE_STATE_PRE_TRIGGER = 2
    PS2000A_CAPTURE_STATE_WAIT_FOR_TRIGGER = 3
    PS2000A_CAPTURE_STATE_POST_TRIGGER = 4


PS2000A_SINE_MAX_FREQUENCY = 1000000.0
PS2000A_SQUARE_MAX_FREQUENCY = 1000000.0
PS2000A_TRIANGLE_MAX_FREQUENCY = 1000000.0
PS2000A_SINC_MAX_FREQUENCY = 1000000.0
PS2000A_RAMP_MAX_FREQUENCY = 1000000.0
PS2000A_HALF_SINE_MAX_FREQUENCY = 1000000.0
PS2000A_GAUSSIAN_MAX_FREQUENCY = 1000000.0
PS2000A_PRBS_MAX_FREQUENCY = 1000000.0
PS2000A_PRBS_MIN_FREQUENCY = 0.03
PS2000A_MIN_FREQUENCY = 0.03

PS2000A_SIGGEN_TRIG_TYPE_T = c_int32


class PS2000A_SIGGEN_TRIG_TYPE(IntEnum):
    PS2000A_SIGGEN_RISING = 0
    PS2000A_SIGGEN_FALLING = 1
    PS2000A_SIGGEN_GATE_HIGH = 2
    PS2000A_SIGGEN_GATE_LOW = 3


PS2000A_SIGGEN_TRIG_SOURCE_T = c_int32


class PS2000A_SIGGEN_TRIG_SOURCE(IntEnum):
    PS2000A_SIGGEN_NONE = 0
    PS2000A_SIGGEN_SCOPE_TRIG = 1
    PS2000A_SIGGEN_AUX_IN = 2
    PS2000A_SIGGEN_EXT_IN = 3
    PS2000A_SIGGEN_SOFT_TRIG = 4


PS2000A_INDEX_MODE_T = c_int32


class PS2000A_INDEX_MODE(IntEnum):
    PS2000A_SINGLE = 0
    PS2000A_DUAL = 1
    PS2000A_QUAD = 2
    PS2000A_MAX_INDEX_MODES = 3


PS2000A_THRESHOLD_MODE_T = c_int32


class PS2000A_THRESHOLD_MODE(IntEnum):
    PS2000A_LEVEL = 0
    PS2000A_WINDOW = 1


PS2000A_THRESHOLD_DIRECTION_T = c_int32


class PS2000A_THRESHOLD_DIRECTION(IntEnum):
    PS2000A_ABOVE = 0
    PS2000A_BELOW = 1
    PS2000A_RISING = 2
    PS2000A_FALLING = 3
    PS2000A_RISING_OR_FALLING = 4
    PS2000A_ABOVE_LOWER = 5
    PS2000A_BELOW_LOWER = 6
    PS2000A_RISING_LOWER = 7
    PS2000A_FALLING_LOWER = 8
    PS2000A_INSIDE = PS2000A_ABOVE
    PS2000A_OUTSIDE = PS2000A_BELOW
    PS2000A_ENTER = PS2000A_RISING
    PS2000A_EXIT = PS2000A_FALLING
    PS2000A_ENTER_OR_EXIT = PS2000A_RISING_OR_FALLING
    PS2000A_POSITIVE_RUNT = 9
    PS2000A_NEGATIVE_RUNT = 10
    PS2000A_NONE = PS2000A_RISING


PS2000A_DIGITAL_DIRECTION_T = c_int32


class PS2000A_DIGITAL_DIRECTION(IntEnum):
    PS2000A_DIGITAL_DONT_CARE = 0
    PS2000A_DIGITAL_DIRECTION_LOW = 1
    PS2000A_DIGITAL_DIRECTION_HIGH = 2
    PS2000A_DIGITAL_DIRECTION_RISING = 3
    PS2000A_DIGITAL_DIRECTION_FALLING = 4
    PS2000A_DIGITAL_DIRECTION_RISING_OR_FALLING = 5
    PS2000A_DIGITAL_MAX_DIRECTION = 6


PS2000A_TRIGGER_STATE_T = c_int32


class PS2000A_TRIGGER_STATE(IntEnum):
    PS2000A_CONDITION_DONT_CARE = 0
    PS2000A_CONDITION_TRUE = 1
    PS2000A_CONDITION_FALSE = 2
    PS2000A_CONDITION_MAX = 3


@final
class PS2000A_TRIGGER_CONDITIONS(CStruct):
    channelA: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    channelB: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    channelC: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    channelD: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    external: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    aux: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    pulseWidthQualifier: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    digital: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]


@final
class PS2000A_PWQ_CONDITIONS(CStruct):
    channelA: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    channelB: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    channelC: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    channelD: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    external: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    aux: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]
    digital: Annotated[PS2000A_TRIGGER_STATE, PS2000A_TRIGGER_STATE_T]


@final
class PS2000A_DIGITAL_CHANNEL_DIRECTIONS(CStruct):
    channel: Annotated[PS2000A_DIGITAL_CHANNEL, PS2000A_DIGITAL_CHANNEL_T]
    direction: Annotated[PS2000A_DIGITAL_DIRECTION, PS2000A_DIGITAL_DIRECTION_T]


@final
class PS2000A_TRIGGER_CHANNEL_PROPERTIES(CStruct):
    thresholdUpper: Annotated[int, c_int16]
    thresholdUpperHysteresis: Annotated[int, c_uint16]
    thresholdLower: Annotated[int, c_int16]
    thresholdLowerHysteresis: Annotated[int, c_uint16]
    channel: Annotated[PS2000A_CHANNEL, PS2000A_CHANNEL_T]
    thresholdMode: Annotated[PS2000A_THRESHOLD_MODE, PS2000A_THRESHOLD_MODE_T]


PS2000A_RATIO_MODE_T = c_int32


class PS2000A_RATIO_MODE(IntEnum):
    PS2000A_RATIO_MODE_NONE = 0
    PS2000A_RATIO_MODE_AGGREGATE = 1
    PS2000A_RATIO_MODE_DECIMATE = 2
    PS2000A_RATIO_MODE_AVERAGE = 4


PS2000A_PULSE_WIDTH_TYPE_T = c_int32


class PS2000A_PULSE_WIDTH_TYPE(IntEnum):
    PS2000A_PW_TYPE_NONE = 0
    PS2000A_PW_TYPE_LESS_THAN = 1
    PS2000A_PW_TYPE_GREATER_THAN = 2
    PS2000A_PW_TYPE_IN_RANGE = 3
    PS2000A_PW_TYPE_OUT_OF_RANGE = 4


PS2000A_HOLDOFF_TYPE_T = c_int32


class PS2000A_HOLDOFF_TYPE(IntEnum):
    PS2000A_TIME = 0
    PS2000A_MAX_HOLDOFF_TYPE = 1


@final
class PS2000A_SCALING_FACTORS_VALUES(CStruct):
    # A PS2000A_CHANNEL or a PS2000A_DIGITAL_PORT (declared as PS2000A_CHANNEL).
    channelOrPort: Annotated[int, PS2000A_CHANNEL_T]
    range: Annotated[PS2000A_RANGE, PS2000A_RANGE_T]
    offset: Annotated[int, c_int16]
    scalingFactor: Annotated[float, c_double]


ps2000aBlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps2000aStreamingReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)

ps2000aDataReady = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p
)

# Size of the buffer receiving the comma separated serials of ps2000aEnumerateUnits.
_ENUMERATE_BUFFER_SIZE = 4096


class PicoScope2000aWrapper(PicoScopeWrapperBase):
    _library_name = "ps2000a"

    def __init__(self, library_path: str | None = None) -> None:
        super().__init__(library_path)

        # The 2000A series is USB bus powered: the driver reports no power source
        # statuses (and has no ChangePowerSource), so opening has no info statuses.
        self._ps2000aOpenUnit = self._bind(
            "ps2000aOpenUnit", [POINTER(c_int16), c_char_p]
        )
        self._ps2000aOpenUnitAsync = self._bind(
            "ps2000aOpenUnitAsync", [POINTER(c_int16), c_char_p]
        )
        self._ps2000aOpenUnitProgress = self._bind(
            "ps2000aOpenUnitProgress",
            [POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps2000aGetUnitInfo = self._bind(
            "ps2000aGetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps2000aFlashLed = self._bind("ps2000aFlashLed", [c_int16, c_int16])
        self._ps2000aCloseUnit = self._bind("ps2000aCloseUnit", [c_int16])
        self._ps2000aMemorySegments = self._bind(
            "ps2000aMemorySegments", [c_int16, c_uint32, POINTER(c_int32)]
        )
        self._ps2000aSetChannel = self._bind(
            "ps2000aSetChannel",
            [
                c_int16,
                PS2000A_CHANNEL_T,
                c_int16,
                PS2000A_COUPLING_T,
                PS2000A_RANGE_T,
                c_float,
            ],
        )
        self._ps2000aSetDigitalPort = self._bind(
            "ps2000aSetDigitalPort",
            [c_int16, PS2000A_DIGITAL_PORT_T, c_int16, c_int16],
        )
        self._ps2000aSetNoOfCaptures = self._bind(
            "ps2000aSetNoOfCaptures", [c_int16, c_uint32]
        )
        self._ps2000aGetTimebase = self._bind(
            "ps2000aGetTimebase",
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
        self._ps2000aGetTimebase2 = self._bind(
            "ps2000aGetTimebase2",
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
        self._ps2000aSetSigGenArbitrary = self._bind(
            "ps2000aSetSigGenArbitrary",
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
                PS2000A_SWEEP_TYPE_T,
                PS2000A_EXTRA_OPERATIONS_T,
                PS2000A_INDEX_MODE_T,
                c_uint32,
                c_uint32,
                PS2000A_SIGGEN_TRIG_TYPE_T,
                PS2000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps2000aSetSigGenBuiltIn = self._bind(
            "ps2000aSetSigGenBuiltIn",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_float,
                c_float,
                c_float,
                c_float,
                PS2000A_SWEEP_TYPE_T,
                PS2000A_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS2000A_SIGGEN_TRIG_TYPE_T,
                PS2000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps2000aSetSigGenBuiltInV2 = self._bind(
            "ps2000aSetSigGenBuiltInV2",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS2000A_SWEEP_TYPE_T,
                PS2000A_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS2000A_SIGGEN_TRIG_TYPE_T,
                PS2000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps2000aSetSigGenPropertiesArbitrary = self._bind(
            "ps2000aSetSigGenPropertiesArbitrary",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                PS2000A_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS2000A_SIGGEN_TRIG_TYPE_T,
                PS2000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps2000aSetSigGenPropertiesBuiltIn = self._bind(
            "ps2000aSetSigGenPropertiesBuiltIn",
            [
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS2000A_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS2000A_SIGGEN_TRIG_TYPE_T,
                PS2000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps2000aSigGenFrequencyToPhase = self._bind(
            "ps2000aSigGenFrequencyToPhase",
            [c_int16, c_double, PS2000A_INDEX_MODE_T, c_uint32, POINTER(c_uint32)],
        )
        self._ps2000aSigGenArbitraryMinMaxValues = self._bind(
            "ps2000aSigGenArbitraryMinMaxValues",
            [
                c_int16,
                POINTER(c_int16),
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_uint32),
            ],
        )
        self._ps2000aGetMaxEtsValues = self._bind(
            "ps2000aGetMaxEtsValues", [c_int16, POINTER(c_int16), POINTER(c_int16)]
        )
        self._ps2000aSigGenSoftwareControl = self._bind(
            "ps2000aSigGenSoftwareControl", [c_int16, c_int16]
        )
        self._ps2000aSetEts = self._bind(
            "ps2000aSetEts",
            [c_int16, PS2000A_ETS_MODE_T, c_int16, c_int16, POINTER(c_int32)],
        )
        self._ps2000aSetSimpleTrigger = self._bind(
            "ps2000aSetSimpleTrigger",
            [
                c_int16,
                c_int16,
                PS2000A_CHANNEL_T,
                c_int16,
                PS2000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_int16,
            ],
        )
        self._ps2000aSetTriggerDigitalPortProperties = self._bind(
            "ps2000aSetTriggerDigitalPortProperties",
            [c_int16, POINTER(PS2000A_DIGITAL_CHANNEL_DIRECTIONS.c_type), c_int16],
        )
        self._ps2000aSetDigitalAnalogTriggerOperand = self._bind(
            "ps2000aSetDigitalAnalogTriggerOperand",
            [c_int16, PS2000A_TRIGGER_OPERAND_T],
        )
        self._ps2000aSetPulseWidthDigitalPortProperties = self._bind(
            "ps2000aSetPulseWidthDigitalPortProperties",
            [c_int16, POINTER(PS2000A_DIGITAL_CHANNEL_DIRECTIONS.c_type), c_int16],
        )
        self._ps2000aSetTriggerChannelProperties = self._bind(
            "ps2000aSetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS2000A_TRIGGER_CHANNEL_PROPERTIES.c_type),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps2000aSetTriggerChannelConditions = self._bind(
            "ps2000aSetTriggerChannelConditions",
            [c_int16, POINTER(PS2000A_TRIGGER_CONDITIONS.c_type), c_int16],
        )
        self._ps2000aSetTriggerChannelDirections = self._bind(
            "ps2000aSetTriggerChannelDirections",
            [
                c_int16,
                PS2000A_THRESHOLD_DIRECTION_T,
                PS2000A_THRESHOLD_DIRECTION_T,
                PS2000A_THRESHOLD_DIRECTION_T,
                PS2000A_THRESHOLD_DIRECTION_T,
                PS2000A_THRESHOLD_DIRECTION_T,
                PS2000A_THRESHOLD_DIRECTION_T,
            ],
        )
        self._ps2000aSetTriggerDelay = self._bind(
            "ps2000aSetTriggerDelay", [c_int16, c_uint32]
        )
        self._ps2000aSetPulseWidthQualifier = self._bind(
            "ps2000aSetPulseWidthQualifier",
            [
                c_int16,
                POINTER(PS2000A_PWQ_CONDITIONS.c_type),
                c_int16,
                PS2000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS2000A_PULSE_WIDTH_TYPE_T,
            ],
        )
        self._ps2000aIsTriggerOrPulseWidthQualifierEnabled = self._bind(
            "ps2000aIsTriggerOrPulseWidthQualifierEnabled",
            [c_int16, POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps2000aGetTriggerTimeOffset = self._bind(
            "ps2000aGetTriggerTimeOffset",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS2000A_TIME_UNITS_T),
                c_uint32,
            ],
        )
        self._ps2000aGetTriggerTimeOffset64 = self._bind(
            "ps2000aGetTriggerTimeOffset64",
            [c_int16, POINTER(c_int64), POINTER(PS2000A_TIME_UNITS_T), c_uint32],
        )
        self._ps2000aGetValuesTriggerTimeOffsetBulk = self._bind(
            "ps2000aGetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS2000A_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps2000aGetValuesTriggerTimeOffsetBulk64 = self._bind(
            "ps2000aGetValuesTriggerTimeOffsetBulk64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS2000A_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps2000aGetNoOfCaptures = self._bind(
            "ps2000aGetNoOfCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps2000aGetNoOfProcessedCaptures = self._bind(
            "ps2000aGetNoOfProcessedCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps2000aSetDataBuffer = self._bind(
            "ps2000aSetDataBuffer",
            [
                c_int16,
                c_int32,
                c_void_p,
                c_int32,
                c_uint32,
                PS2000A_RATIO_MODE_T,
            ],
        )
        self._ps2000aSetDataBuffers = self._bind(
            "ps2000aSetDataBuffers",
            [
                c_int16,
                c_int32,
                c_void_p,
                c_void_p,
                c_int32,
                c_uint32,
                PS2000A_RATIO_MODE_T,
            ],
        )
        self._ps2000aSetUnscaledDataBuffers = self._bind(
            "ps2000aSetUnscaledDataBuffers",
            [
                c_int16,
                PS2000A_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_int32,
                c_uint32,
                PS2000A_RATIO_MODE_T,
            ],
        )
        self._ps2000aSetEtsTimeBuffer = self._bind(
            "ps2000aSetEtsTimeBuffer", [c_int16, c_void_p, c_int32]
        )
        self._ps2000aSetEtsTimeBuffers = self._bind(
            "ps2000aSetEtsTimeBuffers", [c_int16, c_void_p, c_void_p, c_int32]
        )
        self._ps2000aIsReady = self._bind("ps2000aIsReady", [c_int16, POINTER(c_int16)])
        self._ps2000aRunBlock = self._bind(
            "ps2000aRunBlock",
            [
                c_int16,
                c_int32,
                c_int32,
                c_uint32,
                c_int16,
                POINTER(c_int32),
                c_uint32,
                ps2000aBlockReady,
                c_void_p,
            ],
        )
        self._ps2000aRunStreaming = self._bind(
            "ps2000aRunStreaming",
            [
                c_int16,
                POINTER(c_uint32),
                PS2000A_TIME_UNITS_T,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint32,
                PS2000A_RATIO_MODE_T,
                c_uint32,
            ],
        )
        # PICO_BUSY: the driver has no new data to hand over yet; poll again.
        self._ps2000aGetStreamingLatestValues = self._bind(
            "ps2000aGetStreamingLatestValues",
            [c_int16, ps2000aStreamingReady, c_void_p],
            info=(PICO_STATUS.PICO_BUSY,),
        )
        self._ps2000aNoOfStreamingValues = self._bind(
            "ps2000aNoOfStreamingValues", [c_int16, POINTER(c_uint32)]
        )
        self._ps2000aGetMaxDownSampleRatio = self._bind(
            "ps2000aGetMaxDownSampleRatio",
            [c_int16, c_uint32, POINTER(c_uint32), PS2000A_RATIO_MODE_T, c_uint32],
        )
        self._ps2000aGetValues = self._bind(
            "ps2000aGetValues",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS2000A_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps2000aGetValuesBulk = self._bind(
            "ps2000aGetValuesBulk",
            [
                c_int16,
                POINTER(c_uint32),
                c_uint32,
                c_uint32,
                c_uint32,
                PS2000A_RATIO_MODE_T,
                POINTER(c_int16),
            ],
        )
        # Declared with a void pointer for lpDataReady; it is a ps2000aDataReady.
        self._ps2000aGetValuesAsync = self._bind(
            "ps2000aGetValuesAsync",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                PS2000A_RATIO_MODE_T,
                c_uint32,
                ps2000aDataReady,
                c_void_p,
            ],
        )
        self._ps2000aGetValuesOverlapped = self._bind(
            "ps2000aGetValuesOverlapped",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS2000A_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps2000aGetValuesOverlappedBulk = self._bind(
            "ps2000aGetValuesOverlappedBulk",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS2000A_RATIO_MODE_T,
                c_uint32,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps2000aStop = self._bind("ps2000aStop", [c_int16])
        self._ps2000aHoldOff = self._bind(
            "ps2000aHoldOff", [c_int16, c_uint64, PS2000A_HOLDOFF_TYPE_T]
        )
        self._ps2000aGetChannelInformation = self._bind(
            "ps2000aGetChannelInformation",
            [
                c_int16,
                PS2000A_CHANNEL_INFO_T,
                c_int32,
                POINTER(c_int32),
                POINTER(c_int32),
                c_int32,
            ],
        )
        # Finding no units is not a failure of the enumeration.
        self._ps2000aEnumerateUnits = self._bind(
            "ps2000aEnumerateUnits",
            [POINTER(c_int16), c_char_p, POINTER(c_int16)],
            info=(PICO_STATUS.PICO_NOT_FOUND,),
        )
        self._ps2000aPingUnit = self._bind("ps2000aPingUnit", [c_int16])
        self._ps2000aMaximumValue = self._bind(
            "ps2000aMaximumValue", [c_int16, POINTER(c_int16)]
        )
        self._ps2000aMinimumValue = self._bind(
            "ps2000aMinimumValue", [c_int16, POINTER(c_int16)]
        )
        self._ps2000aGetAnalogueOffset = self._bind(
            "ps2000aGetAnalogueOffset",
            [
                c_int16,
                PS2000A_RANGE_T,
                PS2000A_COUPLING_T,
                POINTER(c_float),
                POINTER(c_float),
            ],
        )
        self._ps2000aGetMaxSegments = self._bind(
            "ps2000aGetMaxSegments", [c_int16, POINTER(c_uint32)]
        )
        self._ps2000aQueryOutputEdgeDetect = self._bind(
            "ps2000aQueryOutputEdgeDetect", [c_int16, POINTER(c_int16)]
        )
        self._ps2000aSetOutputEdgeDetect = self._bind(
            "ps2000aSetOutputEdgeDetect", [c_int16, c_int16]
        )
        self._ps2000aGetScalingValues = self._bind(
            "ps2000aGetScalingValues",
            [c_int16, POINTER(PS2000A_SCALING_FACTORS_VALUES.c_type), c_int16],
        )
        self._ps2000aGetCaptureState = self._bind(
            "ps2000aGetCaptureState", [c_int16, POINTER(PS2000A_CAPTURE_STATE_T)]
        )

    def ps2000aOpenUnit(self, serial: str | None) -> c_int16:
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        self._ps2000aOpenUnit(byref(handle), ser)
        return handle

    def ps2000aOpenUnitAsync(self, serial: str | None) -> bool:
        """Start opening a unit; returns whether the open was started."""
        status = c_int16(0)
        ser = serial.encode() if serial is not None else None
        self._ps2000aOpenUnitAsync(byref(status), ser)
        return status.value == 1

    def ps2000aOpenUnitProgress(self) -> tuple[c_int16, int, bool]:
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        self._ps2000aOpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return handle, progressPercent.value, complete.value != 0

    def ps2000aCloseUnit(self, handle: c_int16) -> None:
        self._ps2000aCloseUnit(handle)
        self._release_buffers(handle)

    def ps2000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO) -> str:
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        self._ps2000aGetUnitInfo(handle, buf, 255, byref(size), info)
        return buf.raw[: max(size.value - 1, 0)].decode("utf-8")

    def ps2000aFlashLed(self, handle: c_int16, start: int) -> None:
        """Flash the LED ``start`` times; ``-1`` flashes until stopped by ``0``."""
        self._ps2000aFlashLed(handle, start)

    def ps2000aMemorySegments(self, handle: c_int16, nsegments: int) -> int:
        assert nsegments > 0
        maxSamples = c_int32(0)
        self._ps2000aMemorySegments(handle, nsegments, byref(maxSamples))
        return maxSamples.value

    def ps2000aSetChannel(
        self,
        handle: c_int16,
        channel: PS2000A_CHANNEL,
        enabled: bool,
        coupling: PS2000A_COUPLING,
        range: PS2000A_RANGE,
        analog_offset: float,
    ) -> None:
        self._ps2000aSetChannel(
            handle,
            channel,
            1 if enabled else 0,
            coupling,
            range,
            analog_offset,
        )

    def ps2000aSetDigitalPort(
        self,
        handle: c_int16,
        port: PS2000A_DIGITAL_PORT,
        enabled: bool,
        logicLevel: int,
    ) -> None:
        self._ps2000aSetDigitalPort(handle, port, 1 if enabled else 0, logicLevel)

    def ps2000aSetNoOfCaptures(self, handle: c_int16, ncaptures: int) -> None:
        assert ncaptures > 0
        self._ps2000aSetNoOfCaptures(handle, ncaptures)

    def ps2000aGetTimebase(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        segmentIndex: int,
        oversample: int = 0,
    ) -> tuple[int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_int32(0)
        self._ps2000aGetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNanoseconds.value, maxSamples.value

    def ps2000aGetTimebase2(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        segmentIndex: int,
        oversample: int = 0,
    ) -> tuple[float, int]:
        timeIntervalNS = c_float(0)
        maxSamples = c_int32(0)
        self._ps2000aGetTimebase2(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNS),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNS.value, maxSamples.value

    def ps2000aSetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: InputValues,
        sweepType: PS2000A_SWEEP_TYPE,
        operation: PS2000A_EXTRA_OPERATIONS,
        indexMode: PS2000A_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS2000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS2000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """``arbitraryWaveform`` holds the int16 samples of the arbitrary waveform.

        It is a sequence of ints or a buffer of int16 (e.g. a numpy array with
        ``dtype=np.int16``), which is passed without copying.
        """
        waveform, arbitraryWaveformSize = input_argument(
            arbitraryWaveform, c_int16, "arbitraryWaveform"
        )
        self._ps2000aSetSigGenArbitrary(
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
            operation,
            indexMode,
            shots,
            sweeps,
            triggerType,
            triggerSource,
            extInThreshold,
        )

    def ps2000aSetSigGenBuiltIn(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS2000A_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS2000A_SWEEP_TYPE,
        operation: PS2000A_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS2000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS2000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps2000aSetSigGenBuiltIn(
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

    def ps2000aSetSigGenBuiltInV2(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS2000A_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS2000A_SWEEP_TYPE,
        operation: PS2000A_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS2000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS2000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps2000aSetSigGenBuiltInV2(
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

    def ps2000aSetSigGenPropertiesArbitrary(
        self,
        handle: c_int16,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PS2000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS2000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS2000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps2000aSetSigGenPropertiesArbitrary(
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

    def ps2000aSetSigGenPropertiesBuiltIn(
        self,
        handle: c_int16,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS2000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS2000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS2000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps2000aSetSigGenPropertiesBuiltIn(
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

    def ps2000aSigGenFrequencyToPhase(
        self,
        handle: c_int16,
        frequency: float,
        indexMode: PS2000A_INDEX_MODE,
        bufferLength: int,
    ) -> int:
        phase = c_uint32(0)
        self._ps2000aSigGenFrequencyToPhase(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return phase.value

    def ps2000aSigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[int, int, int, int]:
        """Return the AWG's minimum/maximum sample values and buffer sizes."""
        minValue = c_int16(0)
        maxValue = c_int16(0)
        minSize = c_uint32(0)
        maxSize = c_uint32(0)
        self._ps2000aSigGenArbitraryMinMaxValues(
            handle, byref(minValue), byref(maxValue), byref(minSize), byref(maxSize)
        )
        return minValue.value, maxValue.value, minSize.value, maxSize.value

    def ps2000aGetMaxEtsValues(self, handle: c_int16) -> tuple[int, int]:
        etsCycles = c_int16(0)
        etsInterleave = c_int16(0)
        self._ps2000aGetMaxEtsValues(handle, byref(etsCycles), byref(etsInterleave))
        return etsCycles.value, etsInterleave.value

    def ps2000aSigGenSoftwareControl(self, handle: c_int16, state: int) -> None:
        self._ps2000aSigGenSoftwareControl(handle, state)

    def ps2000aSetEts(
        self,
        handle: c_int16,
        mode: PS2000A_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> int:
        sampleTimePicoseconds = c_int32(0)
        self._ps2000aSetEts(
            handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
        )
        return sampleTimePicoseconds.value

    def ps2000aSetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PS2000A_CHANNEL,
        threshold: int,
        direction: PS2000A_THRESHOLD_DIRECTION,
        delay: int,
        autoTriggerMS: int,
    ) -> None:
        assert autoTriggerMS >= 0
        self._ps2000aSetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTriggerMS,
        )

    def ps2000aSetTriggerDigitalPortProperties(
        self,
        handle: c_int16,
        directions: Sequence[PS2000A_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> None:
        self._ps2000aSetTriggerDigitalPortProperties(
            handle,
            c_array(PS2000A_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def ps2000aSetDigitalAnalogTriggerOperand(
        self, handle: c_int16, operand: PS2000A_TRIGGER_OPERAND
    ) -> None:
        """Set how the analog and digital triggers of MSO models are combined."""
        self._ps2000aSetDigitalAnalogTriggerOperand(handle, operand)

    def ps2000aSetPulseWidthDigitalPortProperties(
        self,
        handle: c_int16,
        directions: Sequence[PS2000A_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> None:
        self._ps2000aSetPulseWidthDigitalPortProperties(
            handle,
            c_array(PS2000A_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def ps2000aSetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS2000A_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> None:
        self._ps2000aSetTriggerChannelProperties(
            handle,
            c_array(PS2000A_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps2000aSetTriggerChannelConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PS2000A_TRIGGER_CONDITIONS],
    ) -> None:
        self._ps2000aSetTriggerChannelConditions(
            handle, c_array(PS2000A_TRIGGER_CONDITIONS, conditions), len(conditions)
        )

    def ps2000aSetTriggerChannelDirections(
        self,
        handle: c_int16,
        channelA: PS2000A_THRESHOLD_DIRECTION,
        channelB: PS2000A_THRESHOLD_DIRECTION,
        channelC: PS2000A_THRESHOLD_DIRECTION,
        channelD: PS2000A_THRESHOLD_DIRECTION,
        ext: PS2000A_THRESHOLD_DIRECTION,
        aux: PS2000A_THRESHOLD_DIRECTION,
    ) -> None:
        self._ps2000aSetTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext, aux
        )

    def ps2000aSetTriggerDelay(self, handle: c_int16, delay: int) -> None:
        self._ps2000aSetTriggerDelay(handle, delay)

    def ps2000aSetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS2000A_PWQ_CONDITIONS],
        direction: PS2000A_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS2000A_PULSE_WIDTH_TYPE,
    ) -> None:
        self._ps2000aSetPulseWidthQualifier(
            handle,
            c_array(PS2000A_PWQ_CONDITIONS, conditions),
            len(conditions),
            direction,
            lower,
            upper,
            type,
        )

    def ps2000aIsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        self._ps2000aIsTriggerOrPulseWidthQualifierEnabled(
            handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
        )
        return triggerEnabled.value != 0, pulseWidthQualifierEnabled.value != 0

    def ps2000aGetTriggerTimeOffset(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[int, int, PS2000A_TIME_UNITS]:
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS2000A_TIME_UNITS_T(0)
        self._ps2000aGetTriggerTimeOffset(
            handle, byref(timeUpper), byref(timeLower), byref(timeUnits), segmentIndex
        )
        return timeUpper.value, timeLower.value, PS2000A_TIME_UNITS(timeUnits.value)

    def ps2000aGetTriggerTimeOffset64(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[int, PS2000A_TIME_UNITS]:
        time = c_int64(0)
        timeUnits = PS2000A_TIME_UNITS_T(0)
        self._ps2000aGetTriggerTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return time.value, PS2000A_TIME_UNITS(timeUnits.value)

    def ps2000aGetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[list[int], list[int], list[PS2000A_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        timesUpper = (c_uint32 * nsegments)()
        timesLower = (c_uint32 * nsegments)()
        timeUnits = (PS2000A_TIME_UNITS_T * nsegments)()
        self._ps2000aGetValuesTriggerTimeOffsetBulk(
            handle, timesUpper, timesLower, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return (
            list(timesUpper),
            list(timesLower),
            [PS2000A_TIME_UNITS(u) for u in timeUnits],
        )

    def ps2000aGetValuesTriggerTimeOffsetBulk64(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[list[int], list[PS2000A_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * nsegments)()
        timeUnits = (PS2000A_TIME_UNITS_T * nsegments)()
        self._ps2000aGetValuesTriggerTimeOffsetBulk64(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return list(times), [PS2000A_TIME_UNITS(u) for u in timeUnits]

    def ps2000aGetNoOfCaptures(self, handle: c_int16) -> int:
        captures = c_uint32()
        self._ps2000aGetNoOfCaptures(handle, byref(captures))
        return captures.value

    def ps2000aGetNoOfProcessedCaptures(self, handle: c_int16) -> int:
        captures = c_uint32()
        self._ps2000aGetNoOfProcessedCaptures(handle, byref(captures))
        return captures.value

    def ps2000aSetDataBuffer(
        self,
        handle: c_int16,
        channelOrPort: PS2000A_CHANNEL | PS2000A_DIGITAL_PORT,
        buffer: DataBuffer,
        bufferLth: int,
        segmentIndex: int,
        mode: PS2000A_RATIO_MODE,
    ) -> None:
        """Set the buffer the driver writes the samples of ``channelOrPort`` to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int16 elements (e.g. ``np.empty(bufferLth, np.int16)``), or None. The
        wrapper keeps it from being freed or resized until it is replaced (same
        channel, segment and mode, also by :meth:`ps2000aSetDataBuffers`), set to
        None or the unit is closed. A raw address (int or ``c_void_p``) is
        passed unchecked and must be kept valid by the caller.
        """
        if bufferLth < 0:
            raise ValueError("bufferLth must not be negative")
        arg = buffer_argument(buffer, c_int16, bufferLth, writable=True, name="buffer")
        self._ps2000aSetDataBuffer(
            handle, channelOrPort, arg, bufferLth, segmentIndex, mode
        )
        self._keep_buffer(
            (handle.value, "data", channelOrPort, segmentIndex, mode), arg
        )

    def ps2000aSetDataBuffers(
        self,
        handle: c_int16,
        channelOrPort: PS2000A_CHANNEL | PS2000A_DIGITAL_PORT,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        bufferLth: int,
        segmentIndex: int,
        mode: PS2000A_RATIO_MODE,
    ) -> None:
        """Like :meth:`ps2000aSetDataBuffer`, with buffers for the maxima and minima."""
        if bufferLth < 0:
            raise ValueError("bufferLth must not be negative")
        argMax = buffer_argument(
            bufferMax, c_int16, bufferLth, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, c_int16, bufferLth, writable=True, name="bufferMin"
        )
        self._ps2000aSetDataBuffers(
            handle, channelOrPort, argMax, argMin, bufferLth, segmentIndex, mode
        )
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_buffer(
            (handle.value, "data", channelOrPort, segmentIndex, mode), both
        )

    def ps2000aSetUnscaledDataBuffers(
        self,
        handle: c_int16,
        channelOrPort: PS2000A_CHANNEL | PS2000A_DIGITAL_PORT,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        bufferLth: int,
        segmentIndex: int,
        mode: PS2000A_RATIO_MODE,
    ) -> None:
        """Like :meth:`ps2000aSetDataBuffers`, with buffers of int8 elements.

        The wrapper keeps them alive separately from the int16 buffers, until
        they are replaced by this function (same channel, segment and mode),
        set to None or the unit is closed.
        """
        if bufferLth < 0:
            raise ValueError("bufferLth must not be negative")
        argMax = buffer_argument(
            bufferMax, c_int8, bufferLth, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, c_int8, bufferLth, writable=True, name="bufferMin"
        )
        self._ps2000aSetUnscaledDataBuffers(
            handle, channelOrPort, argMax, argMin, bufferLth, segmentIndex, mode
        )
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_buffer(
            (handle.value, "unscaled", channelOrPort, segmentIndex, mode), both
        )

    def ps2000aSetEtsTimeBuffer(
        self, handle: c_int16, buffer: DataBuffer, bufferLth: int
    ) -> None:
        """Set the buffer the driver writes the ETS sample times to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int64 elements, or None. The wrapper keeps it alive until it is
        replaced (also by :meth:`ps2000aSetEtsTimeBuffers`), set to None or the
        unit is closed. A raw address (int or ``c_void_p``) is passed unchecked
        and must be kept valid by the caller.
        """
        if bufferLth < 0:
            raise ValueError("bufferLth must not be negative")
        arg = buffer_argument(buffer, c_int64, bufferLth, writable=True, name="buffer")
        self._ps2000aSetEtsTimeBuffer(handle, arg, bufferLth)
        self._keep_buffer((handle.value, "ets"), arg)

    def ps2000aSetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: DataBuffer,
        timeLower: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Like :meth:`ps2000aSetEtsTimeBuffer`, with the times split in 32-bit halves.

        ``timeUpper`` and ``timeLower`` hold at least ``bufferLth`` uint32
        elements each.
        """
        if bufferLth < 0:
            raise ValueError("bufferLth must not be negative")
        argUpper = buffer_argument(
            timeUpper, c_uint32, bufferLth, writable=True, name="timeUpper"
        )
        argLower = buffer_argument(
            timeLower, c_uint32, bufferLth, writable=True, name="timeLower"
        )
        self._ps2000aSetEtsTimeBuffers(handle, argUpper, argLower, bufferLth)
        both = None if argUpper is None and argLower is None else (argUpper, argLower)
        self._keep_buffer((handle.value, "ets"), both)

    def ps2000aIsReady(self, handle: c_int16) -> bool:
        ready = c_int16(0)
        self._ps2000aIsReady(handle, byref(ready))
        return ready.value == 1

    def ps2000aRunBlock(
        self,
        handle: c_int16,
        preSamples: int,
        postSamples: int,
        timebase: int,
        segment: int,
        callback: Callable[[int, PICO_STATUS], None] | None,
        oversample: int = 0,
    ) -> int:
        """Start a block capture; returns the time indisposed in milliseconds."""
        assert preSamples >= 0
        assert postSamples >= 0
        timeInd = c_int32(0)
        lpReady = ps2000aBlockReady()  # NULL; ctypes rejects None here
        if callback is not None:

            def cbwrapper(handle: int, status: int, _: int | None) -> None:
                callback(handle, PICO_STATUS(status))

            lpReady = ps2000aBlockReady(cbwrapper)
        self._with_callback(
            self._callback_key("ps2000aRunBlock", handle),
            lpReady,
            lambda: self._ps2000aRunBlock(
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
        return timeInd.value

    def ps2000aRunStreaming(
        self,
        handle: c_int16,
        sampleInterval: int,
        sampleIntervalTimeUnits: PS2000A_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        downSampleRatioMode: PS2000A_RATIO_MODE,
        overviewBufferSize: int,
    ) -> int:
        """Start streaming; returns the actual sample interval."""
        interval = c_uint32(sampleInterval)
        self._ps2000aRunStreaming(
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
        return interval.value

    def ps2000aGetStreamingLatestValues(
        self,
        handle: c_int16,
        callback: Callable[[int, int, int, int, int, bool, bool], None],
    ) -> PICO_STATUS:
        """Fetch new streaming data, invoking ``callback`` if there is any.

        ``callback`` receives ``(handle, noOfSamples, startIndex, overflow,
        triggerAt, triggered, autoStop)``. Returns the status: ``PICO_BUSY`` is
        informational (no new data yet, poll again), otherwise ``PICO_OK``.
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

        lpPs2000aReady = ps2000aStreamingReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps2000aGetStreamingLatestValues", handle),
            lpPs2000aReady,
            lambda: self._ps2000aGetStreamingLatestValues(handle, lpPs2000aReady, None),
        )

    def ps2000aNoOfStreamingValues(self, handle: c_int16) -> int:
        noOfValues = c_uint32(0)
        self._ps2000aNoOfStreamingValues(handle, byref(noOfValues))
        return noOfValues.value

    def ps2000aGetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggreatedSamples: int,
        downSampleRatioMode: PS2000A_RATIO_MODE,
        segmentIndex: int,
    ) -> int:
        maxDownSampleRatio = c_uint32(0)
        self._ps2000aGetMaxDownSampleRatio(
            handle,
            noOfUnaggreatedSamples,
            byref(maxDownSampleRatio),
            downSampleRatioMode,
            segmentIndex,
        )
        return maxDownSampleRatio.value

    def ps2000aGetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS2000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[int, int]:
        """Read data into the registered buffers; returns sample count and overflow."""
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        self._ps2000aGetValues(
            handle,
            startIndex,
            byref(noOfSamples_),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return noOfSamples_.value, overflow.value

    def ps2000aGetValuesBulk(
        self,
        handle: c_int16,
        nosamples: int,
        fromSegment: int,
        toSegment: int,
        downsampleRatio: int,
        downsampleMode: PS2000A_RATIO_MODE,
    ) -> tuple[int, list[int]]:
        assert nosamples > 0
        assert fromSegment <= toSegment
        nosamples_ = c_uint32(nosamples)
        nsegments = (toSegment - fromSegment) + 1
        overflow = (c_int16 * nsegments)(0)
        self._ps2000aGetValuesBulk(
            handle,
            byref(nosamples_),
            fromSegment,
            toSegment,
            downsampleRatio,
            downsampleMode,
            overflow,
        )
        return nosamples_.value, [int(f) for f in overflow]

    def ps2000aGetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS2000A_RATIO_MODE,
        segmentIndex: int,
        callback: Callable[[int, PICO_STATUS, int, int], None],
    ) -> None:
        """Read data asynchronously.

        ``callback`` receives ``(handle, status, noOfSamples, overflow)``.
        """

        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: int | None
        ) -> None:
            callback(handle, PICO_STATUS(status), noOfSamples, overflow)

        lpDataReady = ps2000aDataReady(cbwrapper)
        self._with_callback(
            self._callback_key("ps2000aGetValuesAsync", handle),
            lpDataReady,
            lambda: self._ps2000aGetValuesAsync(
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

    def ps2000aGetValuesOverlapped(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS2000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[c_uint32, c_int16]:
        """Set up a deferred read, performed when the next block completes.

        The driver writes the sample count and overflow flags later, so they are
        returned as ctypes objects; read their ``.value`` after the capture.
        """
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        # The driver keeps the pointers, so the outputs must outlive this call.
        self._with_callback(
            self._callback_key("ps2000aGetValuesOverlapped", handle),
            (noOfSamples_, overflow),
            lambda: self._ps2000aGetValuesOverlapped(
                handle,
                startIndex,
                byref(noOfSamples_),
                downSampleRatio,
                downSampleRatioMode,
                segmentIndex,
                byref(overflow),
            ),
        )
        return noOfSamples_, overflow

    def ps2000aGetValuesOverlappedBulk(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS2000A_RATIO_MODE,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[c_uint32, Any]:
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
        # Shares the slot with ps2000aGetValuesOverlapped: one deferred read.
        self._with_callback(
            self._callback_key("ps2000aGetValuesOverlapped", handle),
            (noOfSamples_, overflow),
            lambda: self._ps2000aGetValuesOverlappedBulk(
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
        return noOfSamples_, overflow

    def ps2000aStop(self, handle: c_int16) -> None:
        self._ps2000aStop(handle)

    def ps2000aHoldOff(
        self, handle: c_int16, holdoff: int, type: PS2000A_HOLDOFF_TYPE
    ) -> None:
        self._ps2000aHoldOff(handle, holdoff, type)

    def ps2000aGetChannelInformation(
        self,
        handle: c_int16,
        info: PS2000A_CHANNEL_INFO,
        probe: int,
        channels: PS2000A_CHANNEL,
    ) -> list[PS2000A_RANGE]:
        ranges = (c_int32 * PS2000A_RANGE.PS2000A_MAX_RANGES)()
        length = c_int32(len(ranges))
        self._ps2000aGetChannelInformation(
            handle, info, probe, ranges, byref(length), channels
        )
        return [PS2000A_RANGE(r) for r in ranges[: length.value]]

    def ps2000aEnumerateUnits(self) -> tuple[int, list[str]]:
        """Return the number of units found and their serial numbers."""
        count = c_int16(0)
        serials = create_string_buffer(_ENUMERATE_BUFFER_SIZE)
        serialLth = c_int16(_ENUMERATE_BUFFER_SIZE)
        self._ps2000aEnumerateUnits(byref(count), serials, byref(serialLth))
        serialstr = serials.value.decode("utf-8")
        return count.value, [s for s in serialstr.split(",") if s]

    def ps2000aPingUnit(self, handle: c_int16) -> None:
        self._ps2000aPingUnit(handle)

    def ps2000aMaximumValue(self, handle: c_int16) -> int:
        value = c_int16(0)
        self._ps2000aMaximumValue(handle, byref(value))
        return value.value

    def ps2000aMinimumValue(self, handle: c_int16) -> int:
        value = c_int16(0)
        self._ps2000aMinimumValue(handle, byref(value))
        return value.value

    def ps2000aGetAnalogueOffset(
        self, handle: c_int16, range: PS2000A_RANGE, coupling: PS2000A_COUPLING
    ) -> tuple[float, float]:
        """Return the maximum and minimum analogue offset (C argument order)."""
        maximumVoltage = c_float(0)
        minimumVoltage = c_float(0)
        self._ps2000aGetAnalogueOffset(
            handle, range, coupling, byref(maximumVoltage), byref(minimumVoltage)
        )
        return maximumVoltage.value, minimumVoltage.value

    def ps2000aGetMaxSegments(self, handle: c_int16) -> int:
        value = c_uint32(0)
        self._ps2000aGetMaxSegments(handle, byref(value))
        return value.value

    def ps2000aQueryOutputEdgeDetect(self, handle: c_int16) -> bool:
        state = c_int16(0)
        self._ps2000aQueryOutputEdgeDetect(handle, byref(state))
        return state.value != 0

    def ps2000aSetOutputEdgeDetect(self, handle: c_int16, state: bool) -> None:
        self._ps2000aSetOutputEdgeDetect(handle, 1 if state else 0)

    def ps2000aGetScalingValues(
        self, handle: c_int16, nChannels: int
    ) -> list[PS2000A_SCALING_FACTORS_VALUES]:
        scalingValues = (PS2000A_SCALING_FACTORS_VALUES.c_type * nChannels)()
        self._ps2000aGetScalingValues(handle, scalingValues, nChannels)
        return PS2000A_SCALING_FACTORS_VALUES.from_c_array(scalingValues)

    def ps2000aGetCaptureState(self, handle: c_int16) -> PS2000A_CAPTURE_STATE:
        captureState = PS2000A_CAPTURE_STATE_T(0)
        self._ps2000aGetCaptureState(handle, byref(captureState))
        return PS2000A_CAPTURE_STATE(captureState.value)


@final
class PicoScope2000aDevice(PicoScopeDeviceBase[PicoScope2000aWrapper]):
    """An opened ps2000a unit; the functions of :class:`PicoScope2000aWrapper` with its handle.

    See :class:`~pycosdk.PicoScopeDeviceBase`.
    """

    _wrapper_type = PicoScope2000aWrapper

    @classmethod
    def ps2000aOpenUnit(cls, serial: str | None) -> Self:
        """Like :meth:`PicoScope2000aWrapper.ps2000aOpenUnit`, returning a device instead of the handle."""
        return cls(cls.shared_wrapper().ps2000aOpenUnit(serial))

    @classmethod
    def ps2000aOpenUnitProgress(cls) -> tuple[Self | None, int, bool]:
        """Like :meth:`PicoScope2000aWrapper.ps2000aOpenUnitProgress`, with a device instead of the handle once opened."""
        handle, progressPercent, complete = (
            cls.shared_wrapper().ps2000aOpenUnitProgress()
        )
        return cls(handle) if complete else None, progressPercent, complete

    ps2000aOpenUnitAsync = wrapper_function(PicoScope2000aWrapper.ps2000aOpenUnitAsync)
    ps2000aEnumerateUnits = wrapper_function(
        PicoScope2000aWrapper.ps2000aEnumerateUnits
    )

    ps2000aCloseUnit = handle_method(
        PicoScope2000aWrapper.ps2000aCloseUnit, closes=True
    )
    ps2000aGetUnitInfo = handle_method(PicoScope2000aWrapper.ps2000aGetUnitInfo)
    ps2000aFlashLed = handle_method(PicoScope2000aWrapper.ps2000aFlashLed)
    ps2000aMemorySegments = handle_method(PicoScope2000aWrapper.ps2000aMemorySegments)
    ps2000aSetChannel = handle_method(PicoScope2000aWrapper.ps2000aSetChannel)
    ps2000aSetDigitalPort = handle_method(PicoScope2000aWrapper.ps2000aSetDigitalPort)
    ps2000aSetNoOfCaptures = handle_method(PicoScope2000aWrapper.ps2000aSetNoOfCaptures)
    ps2000aGetTimebase = handle_method(PicoScope2000aWrapper.ps2000aGetTimebase)
    ps2000aGetTimebase2 = handle_method(PicoScope2000aWrapper.ps2000aGetTimebase2)
    ps2000aSetSigGenArbitrary = handle_method(
        PicoScope2000aWrapper.ps2000aSetSigGenArbitrary
    )
    ps2000aSetSigGenBuiltIn = handle_method(
        PicoScope2000aWrapper.ps2000aSetSigGenBuiltIn
    )
    ps2000aSetSigGenBuiltInV2 = handle_method(
        PicoScope2000aWrapper.ps2000aSetSigGenBuiltInV2
    )
    ps2000aSetSigGenPropertiesArbitrary = handle_method(
        PicoScope2000aWrapper.ps2000aSetSigGenPropertiesArbitrary
    )
    ps2000aSetSigGenPropertiesBuiltIn = handle_method(
        PicoScope2000aWrapper.ps2000aSetSigGenPropertiesBuiltIn
    )
    ps2000aSigGenFrequencyToPhase = handle_method(
        PicoScope2000aWrapper.ps2000aSigGenFrequencyToPhase
    )
    ps2000aSigGenArbitraryMinMaxValues = handle_method(
        PicoScope2000aWrapper.ps2000aSigGenArbitraryMinMaxValues
    )
    ps2000aGetMaxEtsValues = handle_method(PicoScope2000aWrapper.ps2000aGetMaxEtsValues)
    ps2000aSigGenSoftwareControl = handle_method(
        PicoScope2000aWrapper.ps2000aSigGenSoftwareControl
    )
    ps2000aSetEts = handle_method(PicoScope2000aWrapper.ps2000aSetEts)
    ps2000aSetSimpleTrigger = handle_method(
        PicoScope2000aWrapper.ps2000aSetSimpleTrigger
    )
    ps2000aSetTriggerDigitalPortProperties = handle_method(
        PicoScope2000aWrapper.ps2000aSetTriggerDigitalPortProperties
    )
    ps2000aSetDigitalAnalogTriggerOperand = handle_method(
        PicoScope2000aWrapper.ps2000aSetDigitalAnalogTriggerOperand
    )
    ps2000aSetPulseWidthDigitalPortProperties = handle_method(
        PicoScope2000aWrapper.ps2000aSetPulseWidthDigitalPortProperties
    )
    ps2000aSetTriggerChannelProperties = handle_method(
        PicoScope2000aWrapper.ps2000aSetTriggerChannelProperties
    )
    ps2000aSetTriggerChannelConditions = handle_method(
        PicoScope2000aWrapper.ps2000aSetTriggerChannelConditions
    )
    ps2000aSetTriggerChannelDirections = handle_method(
        PicoScope2000aWrapper.ps2000aSetTriggerChannelDirections
    )
    ps2000aSetTriggerDelay = handle_method(PicoScope2000aWrapper.ps2000aSetTriggerDelay)
    ps2000aSetPulseWidthQualifier = handle_method(
        PicoScope2000aWrapper.ps2000aSetPulseWidthQualifier
    )
    ps2000aIsTriggerOrPulseWidthQualifierEnabled = handle_method(
        PicoScope2000aWrapper.ps2000aIsTriggerOrPulseWidthQualifierEnabled
    )
    ps2000aGetTriggerTimeOffset = handle_method(
        PicoScope2000aWrapper.ps2000aGetTriggerTimeOffset
    )
    ps2000aGetTriggerTimeOffset64 = handle_method(
        PicoScope2000aWrapper.ps2000aGetTriggerTimeOffset64
    )
    ps2000aGetValuesTriggerTimeOffsetBulk = handle_method(
        PicoScope2000aWrapper.ps2000aGetValuesTriggerTimeOffsetBulk
    )
    ps2000aGetValuesTriggerTimeOffsetBulk64 = handle_method(
        PicoScope2000aWrapper.ps2000aGetValuesTriggerTimeOffsetBulk64
    )
    ps2000aGetNoOfCaptures = handle_method(PicoScope2000aWrapper.ps2000aGetNoOfCaptures)
    ps2000aGetNoOfProcessedCaptures = handle_method(
        PicoScope2000aWrapper.ps2000aGetNoOfProcessedCaptures
    )
    ps2000aSetDataBuffer = handle_method(PicoScope2000aWrapper.ps2000aSetDataBuffer)
    ps2000aSetDataBuffers = handle_method(PicoScope2000aWrapper.ps2000aSetDataBuffers)
    ps2000aSetUnscaledDataBuffers = handle_method(
        PicoScope2000aWrapper.ps2000aSetUnscaledDataBuffers
    )
    ps2000aSetEtsTimeBuffer = handle_method(
        PicoScope2000aWrapper.ps2000aSetEtsTimeBuffer
    )
    ps2000aSetEtsTimeBuffers = handle_method(
        PicoScope2000aWrapper.ps2000aSetEtsTimeBuffers
    )
    ps2000aIsReady = handle_method(PicoScope2000aWrapper.ps2000aIsReady)
    ps2000aRunBlock = handle_method(PicoScope2000aWrapper.ps2000aRunBlock)
    ps2000aRunStreaming = handle_method(PicoScope2000aWrapper.ps2000aRunStreaming)
    ps2000aGetStreamingLatestValues = handle_method(
        PicoScope2000aWrapper.ps2000aGetStreamingLatestValues
    )
    ps2000aNoOfStreamingValues = handle_method(
        PicoScope2000aWrapper.ps2000aNoOfStreamingValues
    )
    ps2000aGetMaxDownSampleRatio = handle_method(
        PicoScope2000aWrapper.ps2000aGetMaxDownSampleRatio
    )
    ps2000aGetValues = handle_method(PicoScope2000aWrapper.ps2000aGetValues)
    ps2000aGetValuesBulk = handle_method(PicoScope2000aWrapper.ps2000aGetValuesBulk)
    ps2000aGetValuesAsync = handle_method(PicoScope2000aWrapper.ps2000aGetValuesAsync)
    ps2000aGetValuesOverlapped = handle_method(
        PicoScope2000aWrapper.ps2000aGetValuesOverlapped
    )
    ps2000aGetValuesOverlappedBulk = handle_method(
        PicoScope2000aWrapper.ps2000aGetValuesOverlappedBulk
    )
    ps2000aStop = handle_method(PicoScope2000aWrapper.ps2000aStop)
    ps2000aHoldOff = handle_method(PicoScope2000aWrapper.ps2000aHoldOff)
    ps2000aGetChannelInformation = handle_method(
        PicoScope2000aWrapper.ps2000aGetChannelInformation
    )
    ps2000aPingUnit = handle_method(PicoScope2000aWrapper.ps2000aPingUnit)
    ps2000aMaximumValue = handle_method(PicoScope2000aWrapper.ps2000aMaximumValue)
    ps2000aMinimumValue = handle_method(PicoScope2000aWrapper.ps2000aMinimumValue)
    ps2000aGetAnalogueOffset = handle_method(
        PicoScope2000aWrapper.ps2000aGetAnalogueOffset
    )
    ps2000aGetMaxSegments = handle_method(PicoScope2000aWrapper.ps2000aGetMaxSegments)
    ps2000aQueryOutputEdgeDetect = handle_method(
        PicoScope2000aWrapper.ps2000aQueryOutputEdgeDetect
    )
    ps2000aSetOutputEdgeDetect = handle_method(
        PicoScope2000aWrapper.ps2000aSetOutputEdgeDetect
    )
    ps2000aGetScalingValues = handle_method(
        PicoScope2000aWrapper.ps2000aGetScalingValues
    )
    ps2000aGetCaptureState = handle_method(PicoScope2000aWrapper.ps2000aGetCaptureState)


__all__ = (
    "PS2000A_CAPTURE_STATE",
    "PS2000A_CHANNEL",
    "PS2000A_CHANNEL_BUFFER_INDEX",
    "PS2000A_CHANNEL_INFO",
    "PS2000A_COUPLING",
    "PS2000A_DIGITAL_CHANNEL",
    "PS2000A_DIGITAL_CHANNEL_DIRECTIONS",
    "PS2000A_DIGITAL_DIRECTION",
    "PS2000A_DIGITAL_PORT",
    "PS2000A_ETS_MODE",
    "PS2000A_EXTRA_OPERATIONS",
    "PS2000A_EXT_MAX_VALUE",
    "PS2000A_EXT_MIN_VALUE",
    "PS2000A_GAUSSIAN_MAX_FREQUENCY",
    "PS2000A_HALF_SINE_MAX_FREQUENCY",
    "PS2000A_HOLDOFF_TYPE",
    "PS2000A_INDEX_MODE",
    "PS2000A_MAX_ANALOGUE_OFFSET_500MV_2V",
    "PS2000A_MAX_ANALOGUE_OFFSET_50MV_200MV",
    "PS2000A_MAX_ANALOGUE_OFFSET_5V_20V",
    "PS2000A_MAX_ETS_CYCLES",
    "PS2000A_MAX_INTERLEAVE",
    "PS2000A_MAX_LOGIC_LEVEL",
    "PS2000A_MAX_SIG_GEN_BUFFER_SIZE",
    "PS2000A_MAX_SIG_GEN_FREQ",
    "PS2000A_MAX_SWEEPS_SHOTS",
    "PS2000A_MIN_ANALOGUE_OFFSET_500MV_2V",
    "PS2000A_MIN_ANALOGUE_OFFSET_50MV_200MV",
    "PS2000A_MIN_ANALOGUE_OFFSET_5V_20V",
    "PS2000A_MIN_DWELL_COUNT",
    "PS2000A_MIN_FREQUENCY",
    "PS2000A_MIN_LOGIC_LEVEL",
    "PS2000A_MIN_SIG_GEN_BUFFER_SIZE",
    "PS2000A_MIN_SIG_GEN_FREQ",
    "PS2000A_PRBS_MAX_FREQUENCY",
    "PS2000A_PRBS_MIN_FREQUENCY",
    "PS2000A_PULSE_WIDTH_TYPE",
    "PS2000A_PWQ_CONDITIONS",
    "PS2000A_RAMP_MAX_FREQUENCY",
    "PS2000A_RANGE",
    "PS2000A_RATIO_MODE",
    "PS2000A_SCALING_FACTORS_VALUES",
    "PS2000A_SHOT_SWEEP_TRIGGER_CONTINUOUS_RUN",
    "PS2000A_SIGGEN_TRIG_SOURCE",
    "PS2000A_SIGGEN_TRIG_TYPE",
    "PS2000A_SINC_MAX_FREQUENCY",
    "PS2000A_SINE_MAX_FREQUENCY",
    "PS2000A_SQUARE_MAX_FREQUENCY",
    "PS2000A_SWEEP_TYPE",
    "PS2000A_THRESHOLD_DIRECTION",
    "PS2000A_THRESHOLD_MODE",
    "PS2000A_TIME_UNITS",
    "PS2000A_TRIANGLE_MAX_FREQUENCY",
    "PS2000A_TRIGGER_CHANNEL_PROPERTIES",
    "PS2000A_TRIGGER_CONDITIONS",
    "PS2000A_TRIGGER_OPERAND",
    "PS2000A_TRIGGER_STATE",
    "PS2000A_WAVE_TYPE",
    "PS2206_MAX_ETS_CYCLES",
    "PS2206_MAX_INTERLEAVE",
    "PS2207_MAX_ETS_CYCLES",
    "PS2207_MAX_INTERLEAVE",
    "PS2208_MAX_ETS_CYCLES",
    "PS2208_MAX_INTERLEAVE",
    "PicoScope2000aWrapper",
    "PicoScope2000aDevice",
    "ps2000aBlockReady",
    "ps2000aDataReady",
    "ps2000aStreamingReady",
)
