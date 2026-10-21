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
from enum import IntEnum, IntFlag
from typing import Annotated, Any, Self, final

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

PS3000A_MIN_SIG_GEN_FREQ = 0.0  # C: MIN_SIG_GEN_FREQ
PS3000A_MAX_SIG_GEN_FREQ = 20000000.0  # C: MAX_SIG_GEN_FREQ

PS3207B_MAX_SIG_GEN_BUFFER_SIZE = 32768
PS3206B_MAX_SIG_GEN_BUFFER_SIZE = 16384
PS3000A_MAX_SIG_GEN_BUFFER_SIZE = 8192  # C: MAX_SIG_GEN_BUFFER_SIZE
PS3000A_MIN_SIG_GEN_BUFFER_SIZE = 1  # C: MIN_SIG_GEN_BUFFER_SIZE
PS3000A_MIN_DWELL_COUNT = 3  # C: MIN_DWELL_COUNT
PS3000A_MAX_SWEEPS_SHOTS = (1 << 30) - 1  # C: MAX_SWEEPS_SHOTS

PS3000A_MAX_ANALOGUE_OFFSET_50MV_200MV = 0.250  # C: MAX_ANALOGUE_OFFSET_50MV_200MV
PS3000A_MIN_ANALOGUE_OFFSET_50MV_200MV = -0.250  # C: MIN_ANALOGUE_OFFSET_50MV_200MV
PS3000A_MAX_ANALOGUE_OFFSET_500MV_2V = 2.500  # C: MAX_ANALOGUE_OFFSET_500MV_2V
PS3000A_MIN_ANALOGUE_OFFSET_500MV_2V = -2.500  # C: MIN_ANALOGUE_OFFSET_500MV_2V
PS3000A_MAX_ANALOGUE_OFFSET_5V_20V = 20.0  # C: MAX_ANALOGUE_OFFSET_5V_20V
PS3000A_MIN_ANALOGUE_OFFSET_5V_20V = -20.0  # C: MIN_ANALOGUE_OFFSET_5V_20V

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


class PS3000A_RATIO_MODE(IntFlag):
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
class PS3000A_TRIGGER_CONDITIONS(CStruct):
    channelA: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelB: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelC: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelD: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    external: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    aux: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    pulseWidthQualifier: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]


@final
class PS3000A_TRIGGER_CONDITIONS_V2(CStruct):
    channelA: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelB: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelC: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelD: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    external: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    aux: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    pulseWidthQualifier: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    digital: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]


@final
class PS3000A_PWQ_CONDITIONS(CStruct):
    channelA: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelB: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelC: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelD: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    external: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    aux: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]


@final
class PS3000A_PWQ_CONDITIONS_V2(CStruct):
    channelA: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelB: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelC: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    channelD: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    external: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    aux: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]
    digital: Annotated[PS3000A_TRIGGER_STATE, PS3000A_TRIGGER_STATE_T]


@final
class PS3000A_DIGITAL_CHANNEL_DIRECTIONS(CStruct):
    channel: Annotated[PS3000A_DIGITAL_CHANNEL, PS3000A_DIGITAL_CHANNEL_T]
    direction: Annotated[PS3000A_DIGITAL_DIRECTION, PS3000A_DIGITAL_DIRECTION_T]


@final
class PS3000A_TRIGGER_CHANNEL_PROPERTIES(CStruct):
    thresholdUpper: Annotated[int, c_int16]
    thresholdUpperHysteresis: Annotated[int, c_uint16]
    thresholdLower: Annotated[int, c_int16]
    thresholdLowerHysteresis: Annotated[int, c_uint16]
    channel: Annotated[PS3000A_CHANNEL, PS3000A_CHANNEL_T]
    thresholdMode: Annotated[PS3000A_THRESHOLD_MODE, PS3000A_THRESHOLD_MODE_T]


@final
class PS3000A_TRIGGER_INFO(CStruct):
    status: Annotated[PICO_STATUS, PICO_STATUS_T]
    segmentIndex: Annotated[int, c_uint32]
    reserved0: Annotated[int, c_uint32]
    triggerTime: Annotated[int, c_int64]
    # Declared as int16_t.
    timeUnits: Annotated[PS3000A_TIME_UNITS, c_int16]
    reserved1: Annotated[int, c_int16]
    timeStampCounter: Annotated[int, c_uint64]


@final
class PS3000A_SCALING_FACTORS_VALUES(CStruct):
    # A PS3000A_CHANNEL or a PS3000A_DIGITAL_PORT (declared as PS3000A_CHANNEL).
    channelOrPort: Annotated[int, PS3000A_CHANNEL_T]
    range: Annotated[PS3000A_RANGE, PS3000A_RANGE_T]
    offset: Annotated[int, c_int16]
    scalingFactor: Annotated[float, c_double]


ps3000aBlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps3000aDataReady = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p
)

ps3000aStreamingReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)

# Size of the buffer receiving the comma separated serials of ps3000aEnumerateUnits.
_ENUMERATE_BUFFER_SIZE = 4096


class PicoScope3000aWrapper(PicoScopeWrapperBase):
    # TODO: Rename the parameters that differ from the C prototypes:
    # ChangePowerSource (source -> powerState), GetStreamingLatestValues
    # (callback -> lpPs3000aReady), GetValuesAsync (callback -> lpDataReady),
    # GetValuesBulk (nosamples, fromSegment, toSegment, downsampleRatio,
    # downsampleMode), MemorySegments (nsegments), RunBlock (preSamples,
    # postSamples, segment, callback -> noOfPreTriggerSamples,
    # noOfPostTriggerSamples, segmentIndex, lpReady), SetChannel (coupling,
    # analog_offset -> type, analogOffset), SetDataBuffer (channel ->
    # channelOrPort), SetNoOfCaptures (ncaptures) and SetSimpleTrigger
    # (autoTriggerMS -> autoTrigger_ms). Also restore the C order of oversample
    # in RunBlock, GetTimebase and GetTimebase2. RunStreaming keeps the guide's
    # maxPostTriggerSamples (header typo).
    _library_name = "ps3000a"

    def __init__(self, library_path: str | None = None) -> None:
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
            [c_int16, POINTER(PS3000A_DIGITAL_CHANNEL_DIRECTIONS.c_type), c_int16],
        )
        self._ps3000aSetPulseWidthDigitalPortProperties = self._bind(
            "ps3000aSetPulseWidthDigitalPortProperties",
            [c_int16, POINTER(PS3000A_DIGITAL_CHANNEL_DIRECTIONS.c_type), c_int16],
        )
        self._ps3000aSetTriggerChannelProperties = self._bind(
            "ps3000aSetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS3000A_TRIGGER_CHANNEL_PROPERTIES.c_type),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps3000aSetTriggerChannelConditions = self._bind(
            "ps3000aSetTriggerChannelConditions",
            [c_int16, POINTER(PS3000A_TRIGGER_CONDITIONS.c_type), c_int16],
        )
        self._ps3000aSetTriggerChannelConditionsV2 = self._bind(
            "ps3000aSetTriggerChannelConditionsV2",
            [c_int16, POINTER(PS3000A_TRIGGER_CONDITIONS_V2.c_type), c_int16],
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
                POINTER(PS3000A_PWQ_CONDITIONS.c_type),
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
                POINTER(PS3000A_PWQ_CONDITIONS_V2.c_type),
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
            [c_int16, POINTER(PS3000A_TRIGGER_INFO.c_type), c_uint32, c_uint32],
        )
        self._ps3000aStop = self._bind("ps3000aStop", [c_int16])
        # Does nothing and returns an undefined value (guide p64): unchecked.
        self._ps3000aHoldOff = self._bind_legacy(
            "ps3000aHoldOff", [c_int16, c_uint64, PS3000A_HOLDOFF_TYPE_T], PICO_STATUS_T
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
        # Pinging reports a changed power source of a responsive unit, or an
        # undervoltage supply (guide p74).
        self._ps3000aPingUnit = self._bind(
            "ps3000aPingUnit",
            [c_int16],
            info=POWER_SOURCE_STATUSES | {PICO_STATUS.PICO_POWER_SUPPLY_UNDERVOLTAGE},
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
            [c_int16, POINTER(PS3000A_SCALING_FACTORS_VALUES.c_type), c_int16],
        )
        self._ps3000aCheckForUpdate = self._bind(
            "ps3000aCheckForUpdate",
            [
                c_int16,
                POINTER(PICO_FIRMWARE_INFO.c_type),
                POINTER(c_int16),
                POINTER(c_uint16),
            ],
        )
        # A successful update (or one that was not needed) returns
        # PICO_FIRMWARE_UP_TO_DATE (psospa guide; same firmware update scheme).
        self._ps3000aStartFirmwareUpdate = self._bind(
            "ps3000aStartFirmwareUpdate",
            [c_int16, PicoUpdateFirmwareProgress],
            info={PICO_STATUS.PICO_FIRMWARE_UP_TO_DATE},
        )

    def ps3000aOpenUnit(self, serial: str | None) -> tuple[c_int16, PICO_STATUS]:
        """Open a unit; returns the handle and the (power source) status."""
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        status = self._ps3000aOpenUnit(byref(handle), ser)
        return handle, status

    def ps3000aOpenUnitAsync(self, serial: str | None) -> tuple[bool, PICO_STATUS]:
        """Start opening a unit.

        Returns whether the open was started and the (power source) status.
        """
        started = c_int16(0)
        ser = serial.encode() if serial is not None else None
        status = self._ps3000aOpenUnitAsync(byref(started), ser)
        return started.value == 1, status

    def ps3000aOpenUnitProgress(self) -> tuple[c_int16, int, bool, PICO_STATUS]:
        """Poll an asynchronous open.

        Returns the handle, the progress, whether the open is complete and the
        status, which reports the power source once the open has completed.
        """
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        status = self._ps3000aOpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return handle, progressPercent.value, complete.value != 0, status

    def ps3000aCloseUnit(self, handle: c_int16) -> None:
        self._ps3000aCloseUnit(handle)
        self._release_buffers(handle)

    def ps3000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO) -> str:
        # Generous for any info string; longer ones are truncated (NUL terminated).
        buf = create_string_buffer(4096)
        size = c_int16(0)
        self._ps3000aGetUnitInfo(handle, buf, len(buf), byref(size), info)
        return buf.value.decode("utf-8")

    def ps3000aFlashLed(self, handle: c_int16, start: int) -> None:
        """Flash the LED ``start`` times; ``-1`` flashes until stopped by ``0``."""
        self._ps3000aFlashLed(handle, start)

    def ps3000aMemorySegments(self, handle: c_int16, nsegments: int) -> int:
        assert nsegments > 0
        maxSamples = c_int32(0)
        self._ps3000aMemorySegments(handle, nsegments, byref(maxSamples))
        return maxSamples.value

    def ps3000aSetChannel(
        self,
        handle: c_int16,
        channel: PS3000A_CHANNEL,
        enabled: bool,
        coupling: PS3000A_COUPLING,
        range: PS3000A_RANGE,
        analog_offset: float,
    ) -> None:
        self._ps3000aSetChannel(
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
    ) -> None:
        self._ps3000aSetDigitalPort(handle, port, 1 if enabled else 0, logicLevel)

    def ps3000aSetBandwidthFilter(
        self,
        handle: c_int16,
        channel: PS3000A_CHANNEL,
        bandwidth: PS3000A_BANDWIDTH_LIMITER,
    ) -> None:
        self._ps3000aSetBandwidthFilter(handle, channel, bandwidth)

    def ps3000aSetNoOfCaptures(self, handle: c_int16, ncaptures: int) -> None:
        assert ncaptures > 0
        self._ps3000aSetNoOfCaptures(handle, ncaptures)

    def ps3000aGetTimebase(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        segmentIndex: int,
        oversample: int = 0,
    ) -> tuple[int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_int32(0)
        self._ps3000aGetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNanoseconds.value, maxSamples.value

    def ps3000aGetTimebase2(
        self,
        handle: c_int16,
        timebase: int,
        noSamples: int,
        segmentIndex: int,
        oversample: int = 0,
    ) -> tuple[float, int]:
        timeIntervalNS = c_float(0)
        maxSamples = c_int32(0)
        self._ps3000aGetTimebase2(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNS),
            oversample,
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNS.value, maxSamples.value

    def ps3000aSetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: InputValues,
        sweepType: PS3000A_SWEEP_TYPE,
        operation: PS3000A_EXTRA_OPERATIONS,
        indexMode: PS3000A_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS3000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS3000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """``arbitraryWaveform`` holds the int16 samples of the arbitrary waveform.

        It is a sequence of ints or a buffer of int16 (e.g. a numpy array with
        ``dtype=np.int16``), which is passed without copying.
        """
        waveform, arbitraryWaveformSize = input_argument(
            arbitraryWaveform, c_int16, "arbitraryWaveform"
        )
        self._ps3000aSetSigGenArbitrary(
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
    ) -> None:
        self._ps3000aSetSigGenBuiltIn(
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
    ) -> None:
        self._ps3000aSetSigGenBuiltInV2(
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
    ) -> None:
        self._ps3000aSetSigGenPropertiesArbitrary(
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
    ) -> None:
        self._ps3000aSetSigGenPropertiesBuiltIn(
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
    ) -> int:
        phase = c_uint32(0)
        self._ps3000aSigGenFrequencyToPhase(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return phase.value

    def ps3000aSigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[int, int, int, int]:
        """Return the AWG's minimum/maximum sample values and buffer sizes."""
        minValue = c_int16(0)
        maxValue = c_int16(0)
        minSize = c_uint32(0)
        maxSize = c_uint32(0)
        self._ps3000aSigGenArbitraryMinMaxValues(
            handle, byref(minValue), byref(maxValue), byref(minSize), byref(maxSize)
        )
        return minValue.value, maxValue.value, minSize.value, maxSize.value

    def ps3000aGetMaxEtsValues(self, handle: c_int16) -> tuple[int, int]:
        etsCycles = c_int16(0)
        etsInterleave = c_int16(0)
        self._ps3000aGetMaxEtsValues(handle, byref(etsCycles), byref(etsInterleave))
        return etsCycles.value, etsInterleave.value

    def ps3000aSigGenSoftwareControl(self, handle: c_int16, state: int) -> None:
        self._ps3000aSigGenSoftwareControl(handle, state)

    def ps3000aSetEts(
        self,
        handle: c_int16,
        mode: PS3000A_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> int:
        sampleTimePicoseconds = c_int32(0)
        self._ps3000aSetEts(
            handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
        )
        return sampleTimePicoseconds.value

    def ps3000aSetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PS3000A_CHANNEL,
        threshold: int,
        direction: PS3000A_THRESHOLD_DIRECTION,
        delay: int,
        autoTriggerMS: int,
    ) -> None:
        assert autoTriggerMS >= 0
        self._ps3000aSetSimpleTrigger(
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
    ) -> None:
        self._ps3000aSetTriggerDigitalPortProperties(
            handle,
            c_array(PS3000A_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def ps3000aSetPulseWidthDigitalPortProperties(
        self,
        handle: c_int16,
        directions: Sequence[PS3000A_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> None:
        self._ps3000aSetPulseWidthDigitalPortProperties(
            handle,
            c_array(PS3000A_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def ps3000aSetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS3000A_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> None:
        self._ps3000aSetTriggerChannelProperties(
            handle,
            c_array(PS3000A_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps3000aSetTriggerChannelConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PS3000A_TRIGGER_CONDITIONS],
    ) -> None:
        self._ps3000aSetTriggerChannelConditions(
            handle, c_array(PS3000A_TRIGGER_CONDITIONS, conditions), len(conditions)
        )

    def ps3000aSetTriggerChannelConditionsV2(
        self,
        handle: c_int16,
        conditions: Sequence[PS3000A_TRIGGER_CONDITIONS_V2],
    ) -> None:
        self._ps3000aSetTriggerChannelConditionsV2(
            handle, c_array(PS3000A_TRIGGER_CONDITIONS_V2, conditions), len(conditions)
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
    ) -> None:
        self._ps3000aSetTriggerChannelDirections(
            handle, channelA, channelB, channelC, channelD, ext, aux
        )

    def ps3000aSetTriggerDelay(self, handle: c_int16, delay: int) -> None:
        self._ps3000aSetTriggerDelay(handle, delay)

    def ps3000aSetPulseWidthQualifier(
        self,
        handle: c_int16,
        conditions: Sequence[PS3000A_PWQ_CONDITIONS],
        direction: PS3000A_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS3000A_PULSE_WIDTH_TYPE,
    ) -> None:
        self._ps3000aSetPulseWidthQualifier(
            handle,
            c_array(PS3000A_PWQ_CONDITIONS, conditions),
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
    ) -> None:
        self._ps3000aSetPulseWidthQualifierV2(
            handle,
            c_array(PS3000A_PWQ_CONDITIONS_V2, conditions),
            len(conditions),
            direction,
            lower,
            upper,
            type,
        )

    def ps3000aIsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        self._ps3000aIsTriggerOrPulseWidthQualifierEnabled(
            handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
        )
        return triggerEnabled.value != 0, pulseWidthQualifierEnabled.value != 0

    def ps3000aGetTriggerTimeOffset(self, handle: c_int16, segmentIndex: int) -> float:
        """Returns the trigger time offset of the segment in seconds."""
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS3000A_TIME_UNITS_T(0)
        self._ps3000aGetTriggerTimeOffset(
            handle, byref(timeUpper), byref(timeLower), byref(timeUnits), segmentIndex
        )
        return seconds(
            int64_from_halves(timeUpper.value, timeLower.value), timeUnits.value
        )

    def ps3000aGetTriggerTimeOffset64(
        self, handle: c_int16, segmentIndex: int
    ) -> float:
        """Returns the trigger time offset of the segment in seconds."""
        time = c_int64(0)
        timeUnits = PS3000A_TIME_UNITS_T(0)
        self._ps3000aGetTriggerTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return seconds(time.value, timeUnits.value)

    def ps3000aGetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> list[float]:
        """Returns the trigger time offsets of the segments in seconds.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        timesUpper = (c_uint32 * nsegments)()
        timesLower = (c_uint32 * nsegments)()
        timeUnits = (PS3000A_TIME_UNITS_T * nsegments)()
        self._ps3000aGetValuesTriggerTimeOffsetBulk(
            handle, timesUpper, timesLower, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return [
            seconds(int64_from_halves(upper, lower), units)
            for upper, lower, units in zip(
                timesUpper, timesLower, timeUnits, strict=True
            )
        ]

    def ps3000aGetValuesTriggerTimeOffsetBulk64(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> list[float]:
        """Returns the trigger time offsets of the segments in seconds.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * nsegments)()
        timeUnits = (PS3000A_TIME_UNITS_T * nsegments)()
        self._ps3000aGetValuesTriggerTimeOffsetBulk64(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return [
            seconds(time, units) for time, units in zip(times, timeUnits, strict=True)
        ]

    def ps3000aGetNoOfCaptures(self, handle: c_int16) -> int:
        captures = c_uint32()
        self._ps3000aGetNoOfCaptures(handle, byref(captures))
        return captures.value

    def ps3000aGetNoOfProcessedCaptures(self, handle: c_int16) -> int:
        captures = c_uint32()
        self._ps3000aGetNoOfProcessedCaptures(handle, byref(captures))
        return captures.value

    def ps3000aSetDataBuffer(
        self,
        handle: c_int16,
        channel: PS3000A_CHANNEL | PS3000A_DIGITAL_PORT,
        buffer: DataBuffer,
        bufferLth: int,
        segmentIndex: int,
        mode: PS3000A_RATIO_MODE,
    ) -> None:
        """Set the buffer the driver writes the samples of ``channel`` to.

        ``channel`` is an analog channel or a digital port (MSO models).
        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int16 elements (e.g. ``np.empty(bufferLth, np.int16)``), or None. The
        wrapper keeps it from being freed or resized until it is replaced (same
        channel, segment and mode, also by :meth:`ps3000aSetDataBuffers`), set to
        None or the unit is closed. A raw address (int or ``c_void_p``) is
        passed unchecked and must be kept valid by the caller.
        """
        if bufferLth < 0:
            raise ValueError("bufferLth must not be negative")
        arg = buffer_argument(buffer, c_int16, bufferLth, writable=True, name="buffer")
        self._ps3000aSetDataBuffer(handle, channel, arg, bufferLth, segmentIndex, mode)
        self._keep_buffer((handle.value, "data", channel, segmentIndex, mode), arg)

    def ps3000aSetDataBuffers(
        self,
        handle: c_int16,
        channelOrPort: PS3000A_CHANNEL | PS3000A_DIGITAL_PORT,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        bufferLth: int,
        segmentIndex: int,
        mode: PS3000A_RATIO_MODE,
    ) -> None:
        """Like :meth:`ps3000aSetDataBuffer`, with buffers for the maxima and minima."""
        if bufferLth < 0:
            raise ValueError("bufferLth must not be negative")
        argMax = buffer_argument(
            bufferMax, c_int16, bufferLth, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, c_int16, bufferLth, writable=True, name="bufferMin"
        )
        self._ps3000aSetDataBuffers(
            handle, channelOrPort, argMax, argMin, bufferLth, segmentIndex, mode
        )
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_buffer(
            (handle.value, "data", channelOrPort, segmentIndex, mode), both
        )

    def ps3000aSetUnscaledDataBuffers(
        self,
        handle: c_int16,
        channelOrPort: PS3000A_CHANNEL | PS3000A_DIGITAL_PORT,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        bufferLth: int,
        segmentIndex: int,
        mode: PS3000A_RATIO_MODE,
    ) -> None:
        """Like :meth:`ps3000aSetDataBuffers`, with buffers of int8 elements.

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
        self._ps3000aSetUnscaledDataBuffers(
            handle, channelOrPort, argMax, argMin, bufferLth, segmentIndex, mode
        )
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_buffer(
            (handle.value, "unscaled", channelOrPort, segmentIndex, mode), both
        )

    def ps3000aSetEtsTimeBuffer(
        self, handle: c_int16, buffer: DataBuffer, bufferLth: int
    ) -> None:
        """Set the buffer the driver writes the ETS sample times to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int64 elements, or None. The wrapper keeps it alive until it is
        replaced (also by :meth:`ps3000aSetEtsTimeBuffers`), set to None or the
        unit is closed. A raw address (int or ``c_void_p``) is passed unchecked
        and must be kept valid by the caller.
        """
        if bufferLth < 0:
            raise ValueError("bufferLth must not be negative")
        arg = buffer_argument(buffer, c_int64, bufferLth, writable=True, name="buffer")
        self._ps3000aSetEtsTimeBuffer(handle, arg, bufferLth)
        # TODO: SetEtsTimeBuffer and SetEtsTimeBuffers share this key, so setting
        # one releases the other's buffer. The guide doesn't say whether the
        # driver drops the other; if it keeps both, it writes into a released
        # buffer. Use separate keys (as AGENTS.md advises when in doubt).
        self._keep_buffer((handle.value, "ets"), arg)

    def ps3000aSetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: DataBuffer,
        timeLower: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Like :meth:`ps3000aSetEtsTimeBuffer`, with the times split in 32-bit halves.

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
        self._ps3000aSetEtsTimeBuffers(handle, argUpper, argLower, bufferLth)
        both = None if argUpper is None and argLower is None else (argUpper, argLower)
        self._keep_buffer((handle.value, "ets"), both)

    def ps3000aIsReady(self, handle: c_int16) -> bool:
        ready = c_int16(0)
        self._ps3000aIsReady(handle, byref(ready))
        return ready.value != 0

    def ps3000aRunBlock(
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
        lpReady = ps3000aBlockReady()  # NULL; ctypes rejects None here
        if callback is not None:

            def cbwrapper(handle: int, status: int, _: int | None) -> None:
                callback(handle, PICO_STATUS(status))

            lpReady = ps3000aBlockReady(cbwrapper)
        self._with_callback(
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
        return timeInd.value

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
    ) -> int:
        """Start streaming; returns the actual sample interval."""
        interval = c_uint32(sampleInterval)
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
        )
        return interval.value

    def ps3000aGetStreamingLatestValues(
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

        lpPs3000aReady = ps3000aStreamingReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps3000aGetStreamingLatestValues", handle),
            lpPs3000aReady,
            lambda: self._ps3000aGetStreamingLatestValues(handle, lpPs3000aReady, None),
        )

    def ps3000aNoOfStreamingValues(self, handle: c_int16) -> int:
        noOfValues = c_uint32(0)
        self._ps3000aNoOfStreamingValues(handle, byref(noOfValues))
        return noOfValues.value

    def ps3000aGetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggreatedSamples: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        segmentIndex: int,
    ) -> int:
        maxDownSampleRatio = c_uint32(0)
        self._ps3000aGetMaxDownSampleRatio(
            handle,
            noOfUnaggreatedSamples,
            byref(maxDownSampleRatio),
            downSampleRatioMode,
            segmentIndex,
        )
        return maxDownSampleRatio.value

    def ps3000aGetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[int, int]:
        """Read data into the registered buffers; returns sample count and overflow."""
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        self._ps3000aGetValues(
            handle,
            startIndex,
            byref(noOfSamples_),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return noOfSamples_.value, overflow.value

    def ps3000aGetValuesBulk(
        self,
        handle: c_int16,
        nosamples: int,
        fromSegment: int,
        toSegment: int,
        downsampleRatio: int,
        downsampleMode: PS3000A_RATIO_MODE,
    ) -> tuple[int, list[int]]:
        """Returns the number of samples and the overflow flags of each segment.

        The driver wraps around from the last segment to the first if
        ``toSegment < fromSegment``; the wrapper does not support this.
        """
        assert nosamples > 0
        assert fromSegment <= toSegment
        nosamples_ = c_uint32(nosamples)
        nsegments = (toSegment - fromSegment) + 1
        overflow = (c_int16 * nsegments)(0)
        self._ps3000aGetValuesBulk(
            handle,
            byref(nosamples_),
            fromSegment,
            toSegment,
            downsampleRatio,
            downsampleMode,
            overflow,
        )
        return nosamples_.value, [int(f) for f in overflow]

    def ps3000aGetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
        segmentIndex: int,
        callback: Callable[[int, PICO_STATUS, int, int], None],
    ) -> None:
        """Read data asynchronously.

        ``callback`` receives ``(handle, status, noOfSamples, overflow)``.
        """
        # TODO: The guide allows a ps3000aStreamingReady callback here for
        # streaming-mode data (the header declares lpDataReady as void*), but the
        # binding is typed ps3000aDataReady and always passes a block-mode thunk.
        # Bind it as c_void_p and offer the streaming callback (separate method or
        # parameter), or document this method as block-mode only.

        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: int | None
        ) -> None:
            callback(handle, PICO_STATUS(status), noOfSamples, overflow)

        lpDataReady = ps3000aDataReady(cbwrapper)
        self._with_callback(
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
    ) -> tuple[c_uint32, c_int16]:
        """Set up a deferred read, performed when the next block completes.

        The driver writes the sample count and overflow flags later, so they are
        returned as ctypes objects; read their ``.value`` after the capture.
        """
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        # The driver keeps the pointers, so the outputs must outlive this call.
        self._with_callback(
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
        return noOfSamples_, overflow

    def ps3000aGetValuesOverlappedBulk(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS3000A_RATIO_MODE,
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
        # Shares the slot with ps3000aGetValuesOverlapped: one deferred read.
        self._with_callback(
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
        return noOfSamples_, overflow

    def ps3000aGetTriggerInfoBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> list[PS3000A_TRIGGER_INFO]:
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        triggerInfo = (PS3000A_TRIGGER_INFO.c_type * nsegments)()
        self._ps3000aGetTriggerInfoBulk(
            handle, triggerInfo, fromSegmentIndex, toSegmentIndex
        )
        return PS3000A_TRIGGER_INFO.from_c_array(triggerInfo)

    def ps3000aStop(self, handle: c_int16) -> None:
        self._ps3000aStop(handle)

    def ps3000aHoldOff(
        self, handle: c_int16, holdoff: int, type: PS3000A_HOLDOFF_TYPE
    ) -> None:
        """Does nothing; for backward compatibility only (guide p64)."""
        self._ps3000aHoldOff(handle, holdoff, type)

    def ps3000aGetChannelInformation(
        self,
        handle: c_int16,
        info: PS3000A_CHANNEL_INFO,
        probe: int,
        channels: PS3000A_CHANNEL,
    ) -> list[PS3000A_RANGE]:
        ranges = (c_int32 * PS3000A_RANGE.PS3000A_MAX_RANGES)()
        length = c_int32(len(ranges))
        self._ps3000aGetChannelInformation(
            handle, info, probe, ranges, byref(length), channels
        )
        return [PS3000A_RANGE(r) for r in ranges[: length.value]]

    def ps3000aEnumerateUnits(self) -> list[str]:
        """Return the serial numbers of the units found (not opened yet)."""
        count = c_int16(0)
        serials = create_string_buffer(_ENUMERATE_BUFFER_SIZE)
        serialLth = c_int16(_ENUMERATE_BUFFER_SIZE)
        self._ps3000aEnumerateUnits(byref(count), serials, byref(serialLth))
        units = [s for s in serials.value.decode("utf-8").split(",") if s]
        assert len(units) == count.value
        return units

    def ps3000aPingUnit(self, handle: c_int16) -> PICO_STATUS:
        """Check the unit responds; returns the status, which may report the power source."""
        return self._ps3000aPingUnit(handle)

    def ps3000aMaximumValue(self, handle: c_int16) -> int:
        value = c_int16(0)
        self._ps3000aMaximumValue(handle, byref(value))
        return value.value

    def ps3000aMinimumValue(self, handle: c_int16) -> int:
        value = c_int16(0)
        self._ps3000aMinimumValue(handle, byref(value))
        return value.value

    def ps3000aGetAnalogueOffset(
        self, handle: c_int16, range: PS3000A_RANGE, coupling: PS3000A_COUPLING
    ) -> tuple[float, float]:
        """Return the maximum and minimum analogue offset (C argument order)."""
        maximumVoltage = c_float(0)
        minimumVoltage = c_float(0)
        self._ps3000aGetAnalogueOffset(
            handle, range, coupling, byref(maximumVoltage), byref(minimumVoltage)
        )
        return maximumVoltage.value, minimumVoltage.value

    def ps3000aGetMaxSegments(self, handle: c_int16) -> int:
        value = c_uint32(0)
        self._ps3000aGetMaxSegments(handle, byref(value))
        return value.value

    def ps3000aChangePowerSource(
        self, handle: c_int16, source: PICO_STATUS
    ) -> PICO_STATUS:
        """Acknowledge the power source; returns the status reporting the power state."""
        return self._ps3000aChangePowerSource(handle, source)

    def ps3000aCurrentPowerSource(self, handle: c_int16) -> PICO_STATUS:
        """Return the power source as status, e.g., ``PICO_POWER_SUPPLY_CONNECTED``."""
        return self._ps3000aCurrentPowerSource(handle)

    def ps3000aQueryOutputEdgeDetect(self, handle: c_int16) -> bool:
        state = c_int16(0)
        self._ps3000aQueryOutputEdgeDetect(handle, byref(state))
        return state.value != 0

    def ps3000aSetOutputEdgeDetect(self, handle: c_int16, state: bool) -> None:
        self._ps3000aSetOutputEdgeDetect(handle, 1 if state else 0)

    def ps3000aGetScalingValues(
        self, handle: c_int16, nChannels: int
    ) -> list[PS3000A_SCALING_FACTORS_VALUES]:
        scalingValues = (PS3000A_SCALING_FACTORS_VALUES.c_type * nChannels)()
        self._ps3000aGetScalingValues(handle, scalingValues, nChannels)
        return PS3000A_SCALING_FACTORS_VALUES.from_c_array(scalingValues)

    def ps3000aCheckForUpdate(
        self, handle: c_int16
    ) -> tuple[list[PICO_FIRMWARE_INFO], bool]:
        """Return the firmware infos and whether any update is required."""
        # The first call (NULL array) only queries the number of components, as
        # documented for ps6000a and psospa (the ps3000a guide lacks the function).
        nFirmwareInfos = c_int16(0)
        updatesRequired = c_uint16(0)
        self._ps3000aCheckForUpdate(
            handle, None, byref(nFirmwareInfos), byref(updatesRequired)
        )
        capacity = max(0, nFirmwareInfos.value)
        firmwareInfos = (PICO_FIRMWARE_INFO.c_type * capacity)()
        if capacity > 0:
            self._ps3000aCheckForUpdate(
                handle, firmwareInfos, byref(nFirmwareInfos), byref(updatesRequired)
            )
        n = max(0, min(nFirmwareInfos.value, capacity))
        return (
            PICO_FIRMWARE_INFO.from_c_array(firmwareInfos[:n]),
            updatesRequired.value != 0,
        )

    def ps3000aStartFirmwareUpdate(
        self, handle: c_int16, progress: Callable[[int, int], None] | None
    ) -> PICO_STATUS:
        """Update the firmware; ``progress`` receives ``(handle, percent)``.

        Returns the status, PICO_FIRMWARE_UP_TO_DATE once the firmware has been
        updated or did not need an update.
        """
        cb = PicoUpdateFirmwareProgress()  # NULL; ctypes rejects None here
        if progress is not None:

            def cbwrapper(handle: int, percent: int) -> None:
                progress(handle, percent)

            cb = PicoUpdateFirmwareProgress(cbwrapper)
        return self._with_callback(
            self._callback_key("ps3000aStartFirmwareUpdate", handle),
            cb,
            lambda: self._ps3000aStartFirmwareUpdate(handle, cb),
            accepted=lambda status: (
                status in (PICO_STATUS.PICO_OK, PICO_STATUS.PICO_FIRMWARE_UP_TO_DATE)
            ),
        )


@final
class PicoScope3000aDevice(PicoScopeDeviceBase[PicoScope3000aWrapper]):
    """An opened ps3000a unit; the functions of :class:`PicoScope3000aWrapper` with its handle.

    See :class:`~pycosdk.PicoScopeDeviceBase`.
    """

    _wrapper_type = PicoScope3000aWrapper

    @classmethod
    def ps3000aOpenUnit(cls, serial: str | None) -> tuple[Self, PICO_STATUS]:
        """Like :meth:`PicoScope3000aWrapper.ps3000aOpenUnit`, returning a device instead of the handle."""
        handle, status = cls.shared_wrapper().ps3000aOpenUnit(serial)
        return cls(handle), status

    @classmethod
    def ps3000aOpenUnitProgress(cls) -> tuple[Self | None, int, bool, PICO_STATUS]:
        """Like :meth:`PicoScope3000aWrapper.ps3000aOpenUnitProgress`, with a device instead of the handle once opened."""
        handle, progressPercent, complete, status = (
            cls.shared_wrapper().ps3000aOpenUnitProgress()
        )
        return cls(handle) if complete else None, progressPercent, complete, status

    ps3000aOpenUnitAsync = wrapper_function(PicoScope3000aWrapper.ps3000aOpenUnitAsync)
    ps3000aEnumerateUnits = wrapper_function(
        PicoScope3000aWrapper.ps3000aEnumerateUnits
    )

    ps3000aCloseUnit = handle_method(
        PicoScope3000aWrapper.ps3000aCloseUnit, closes=True
    )
    ps3000aGetUnitInfo = handle_method(PicoScope3000aWrapper.ps3000aGetUnitInfo)
    ps3000aFlashLed = handle_method(PicoScope3000aWrapper.ps3000aFlashLed)
    ps3000aMemorySegments = handle_method(PicoScope3000aWrapper.ps3000aMemorySegments)
    ps3000aSetChannel = handle_method(PicoScope3000aWrapper.ps3000aSetChannel)
    ps3000aSetDigitalPort = handle_method(PicoScope3000aWrapper.ps3000aSetDigitalPort)
    ps3000aSetBandwidthFilter = handle_method(
        PicoScope3000aWrapper.ps3000aSetBandwidthFilter
    )
    ps3000aSetNoOfCaptures = handle_method(PicoScope3000aWrapper.ps3000aSetNoOfCaptures)
    ps3000aGetTimebase = handle_method(PicoScope3000aWrapper.ps3000aGetTimebase)
    ps3000aGetTimebase2 = handle_method(PicoScope3000aWrapper.ps3000aGetTimebase2)
    ps3000aSetSigGenArbitrary = handle_method(
        PicoScope3000aWrapper.ps3000aSetSigGenArbitrary
    )
    ps3000aSetSigGenBuiltIn = handle_method(
        PicoScope3000aWrapper.ps3000aSetSigGenBuiltIn
    )
    ps3000aSetSigGenBuiltInV2 = handle_method(
        PicoScope3000aWrapper.ps3000aSetSigGenBuiltInV2
    )
    ps3000aSetSigGenPropertiesArbitrary = handle_method(
        PicoScope3000aWrapper.ps3000aSetSigGenPropertiesArbitrary
    )
    ps3000aSetSigGenPropertiesBuiltIn = handle_method(
        PicoScope3000aWrapper.ps3000aSetSigGenPropertiesBuiltIn
    )
    ps3000aSigGenFrequencyToPhase = handle_method(
        PicoScope3000aWrapper.ps3000aSigGenFrequencyToPhase
    )
    ps3000aSigGenArbitraryMinMaxValues = handle_method(
        PicoScope3000aWrapper.ps3000aSigGenArbitraryMinMaxValues
    )
    ps3000aGetMaxEtsValues = handle_method(PicoScope3000aWrapper.ps3000aGetMaxEtsValues)
    ps3000aSigGenSoftwareControl = handle_method(
        PicoScope3000aWrapper.ps3000aSigGenSoftwareControl
    )
    ps3000aSetEts = handle_method(PicoScope3000aWrapper.ps3000aSetEts)
    ps3000aSetSimpleTrigger = handle_method(
        PicoScope3000aWrapper.ps3000aSetSimpleTrigger
    )
    ps3000aSetTriggerDigitalPortProperties = handle_method(
        PicoScope3000aWrapper.ps3000aSetTriggerDigitalPortProperties
    )
    ps3000aSetPulseWidthDigitalPortProperties = handle_method(
        PicoScope3000aWrapper.ps3000aSetPulseWidthDigitalPortProperties
    )
    ps3000aSetTriggerChannelProperties = handle_method(
        PicoScope3000aWrapper.ps3000aSetTriggerChannelProperties
    )
    ps3000aSetTriggerChannelConditions = handle_method(
        PicoScope3000aWrapper.ps3000aSetTriggerChannelConditions
    )
    ps3000aSetTriggerChannelConditionsV2 = handle_method(
        PicoScope3000aWrapper.ps3000aSetTriggerChannelConditionsV2
    )
    ps3000aSetTriggerChannelDirections = handle_method(
        PicoScope3000aWrapper.ps3000aSetTriggerChannelDirections
    )
    ps3000aSetTriggerDelay = handle_method(PicoScope3000aWrapper.ps3000aSetTriggerDelay)
    ps3000aSetPulseWidthQualifier = handle_method(
        PicoScope3000aWrapper.ps3000aSetPulseWidthQualifier
    )
    ps3000aSetPulseWidthQualifierV2 = handle_method(
        PicoScope3000aWrapper.ps3000aSetPulseWidthQualifierV2
    )
    ps3000aIsTriggerOrPulseWidthQualifierEnabled = handle_method(
        PicoScope3000aWrapper.ps3000aIsTriggerOrPulseWidthQualifierEnabled
    )
    ps3000aGetTriggerTimeOffset = handle_method(
        PicoScope3000aWrapper.ps3000aGetTriggerTimeOffset
    )
    ps3000aGetTriggerTimeOffset64 = handle_method(
        PicoScope3000aWrapper.ps3000aGetTriggerTimeOffset64
    )
    ps3000aGetValuesTriggerTimeOffsetBulk = handle_method(
        PicoScope3000aWrapper.ps3000aGetValuesTriggerTimeOffsetBulk
    )
    ps3000aGetValuesTriggerTimeOffsetBulk64 = handle_method(
        PicoScope3000aWrapper.ps3000aGetValuesTriggerTimeOffsetBulk64
    )
    ps3000aGetNoOfCaptures = handle_method(PicoScope3000aWrapper.ps3000aGetNoOfCaptures)
    ps3000aGetNoOfProcessedCaptures = handle_method(
        PicoScope3000aWrapper.ps3000aGetNoOfProcessedCaptures
    )
    ps3000aSetDataBuffer = handle_method(PicoScope3000aWrapper.ps3000aSetDataBuffer)
    ps3000aSetDataBuffers = handle_method(PicoScope3000aWrapper.ps3000aSetDataBuffers)
    ps3000aSetUnscaledDataBuffers = handle_method(
        PicoScope3000aWrapper.ps3000aSetUnscaledDataBuffers
    )
    ps3000aSetEtsTimeBuffer = handle_method(
        PicoScope3000aWrapper.ps3000aSetEtsTimeBuffer
    )
    ps3000aSetEtsTimeBuffers = handle_method(
        PicoScope3000aWrapper.ps3000aSetEtsTimeBuffers
    )
    ps3000aIsReady = handle_method(PicoScope3000aWrapper.ps3000aIsReady)
    ps3000aRunBlock = handle_method(PicoScope3000aWrapper.ps3000aRunBlock)
    ps3000aRunStreaming = handle_method(PicoScope3000aWrapper.ps3000aRunStreaming)
    ps3000aGetStreamingLatestValues = handle_method(
        PicoScope3000aWrapper.ps3000aGetStreamingLatestValues
    )
    ps3000aNoOfStreamingValues = handle_method(
        PicoScope3000aWrapper.ps3000aNoOfStreamingValues
    )
    ps3000aGetMaxDownSampleRatio = handle_method(
        PicoScope3000aWrapper.ps3000aGetMaxDownSampleRatio
    )
    ps3000aGetValues = handle_method(PicoScope3000aWrapper.ps3000aGetValues)
    ps3000aGetValuesBulk = handle_method(PicoScope3000aWrapper.ps3000aGetValuesBulk)
    ps3000aGetValuesAsync = handle_method(PicoScope3000aWrapper.ps3000aGetValuesAsync)
    ps3000aGetValuesOverlapped = handle_method(
        PicoScope3000aWrapper.ps3000aGetValuesOverlapped
    )
    ps3000aGetValuesOverlappedBulk = handle_method(
        PicoScope3000aWrapper.ps3000aGetValuesOverlappedBulk
    )
    ps3000aGetTriggerInfoBulk = handle_method(
        PicoScope3000aWrapper.ps3000aGetTriggerInfoBulk
    )
    ps3000aStop = handle_method(PicoScope3000aWrapper.ps3000aStop)
    ps3000aHoldOff = handle_method(PicoScope3000aWrapper.ps3000aHoldOff)
    ps3000aGetChannelInformation = handle_method(
        PicoScope3000aWrapper.ps3000aGetChannelInformation
    )
    ps3000aPingUnit = handle_method(PicoScope3000aWrapper.ps3000aPingUnit)
    ps3000aMaximumValue = handle_method(PicoScope3000aWrapper.ps3000aMaximumValue)
    ps3000aMinimumValue = handle_method(PicoScope3000aWrapper.ps3000aMinimumValue)
    ps3000aGetAnalogueOffset = handle_method(
        PicoScope3000aWrapper.ps3000aGetAnalogueOffset
    )
    ps3000aGetMaxSegments = handle_method(PicoScope3000aWrapper.ps3000aGetMaxSegments)
    ps3000aChangePowerSource = handle_method(
        PicoScope3000aWrapper.ps3000aChangePowerSource
    )
    ps3000aCurrentPowerSource = handle_method(
        PicoScope3000aWrapper.ps3000aCurrentPowerSource
    )
    ps3000aQueryOutputEdgeDetect = handle_method(
        PicoScope3000aWrapper.ps3000aQueryOutputEdgeDetect
    )
    ps3000aSetOutputEdgeDetect = handle_method(
        PicoScope3000aWrapper.ps3000aSetOutputEdgeDetect
    )
    ps3000aGetScalingValues = handle_method(
        PicoScope3000aWrapper.ps3000aGetScalingValues
    )
    ps3000aCheckForUpdate = handle_method(PicoScope3000aWrapper.ps3000aCheckForUpdate)
    ps3000aStartFirmwareUpdate = handle_method(
        PicoScope3000aWrapper.ps3000aStartFirmwareUpdate
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
    "PicoScope3000aDevice",
    "ps3000aBlockReady",
    "ps3000aDataReady",
    "ps3000aStreamingReady",
)
