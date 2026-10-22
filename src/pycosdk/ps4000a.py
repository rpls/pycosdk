# pyright: reportAny=false, reportUnannotatedClassAttribute=false
from collections.abc import Callable, Sequence
from ctypes import (
    POINTER,
    Array,
    byref,
    c_char_p,
    c_double,
    c_float,
    c_int16,
    c_int32,
    c_int64,
    c_uint8,
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
from .exceptions import StatusException
from .connectprobe import (
    PICO_CONNECT_PROBE,
    PICO_CONNECT_PROBE_RANGE,
    PICO_CONNECT_PROBE_RANGE_T,
    PICO_CONNECT_PROBE_T,
)
from .status import (
    PICO_INFO,
    PICO_INFO_T,
    PICO_STATUS,
    PICO_STATUS_T,
    PICO_STRING_VALUE,
    PICO_STRING_VALUE_T,
)
from .version import PICO_FIRMWARE_INFO

# Driver for the PicoScope 4000A Series (4444, 4824, 4824A, 4224A, 4424A, ...).
# MAX_PULSE_WIDTH_QUALIFIER_COUNT and MAX_DELAY_COUNT are unprefixed in
# ps4000aApi.h and get a PS4000A_ prefix here.

PS4000A_EXT_MAX_VALUE = 32767
PS4000A_EXT_MIN_VALUE = -32767

PS4000A_MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215  # C: MAX_PULSE_WIDTH_QUALIFIER_COUNT
PS4000A_MAX_DELAY_COUNT = 8388607  # C: MAX_DELAY_COUNT

PS4000A_MAX_SIG_GEN_BUFFER_SIZE = 16384

PS4000A_MIN_SIG_GEN_BUFFER_SIZE = 10
PS4000A_MIN_DWELL_COUNT = 10
PS4000A_MAX_SWEEPS_SHOTS = (1 << 30) - 1
PS4000A_AWG_DAC_FREQUENCY = 80e6
PS4000A_AWG_PHASE_ACCUMULATOR = 4294967296.0

PS4000A_MAX_ANALOGUE_OFFSET_50MV_200MV = 0.250
PS4000A_MIN_ANALOGUE_OFFSET_50MV_200MV = -0.250
PS4000A_MAX_ANALOGUE_OFFSET_500MV_2V = 2.500
PS4000A_MIN_ANALOGUE_OFFSET_500MV_2V = -2.500
PS4000A_MAX_ANALOGUE_OFFSET_5V_20V = 20.0
PS4000A_MIN_ANALOGUE_OFFSET_5V_20V = -20.0
PS4000A_MAX_ANALOGUE_OFFSET_10V_50V = 25.0
PS4000A_MIN_ANALOGUE_OFFSET_10V_50V = -25.0


# Upper limit for the buffers of GetString and DeviceMetaData, which grow while
# the driver reports them as too small.
_MAX_STRING_SIZE = 1 << 24


class PS4000A_DEVICE_RESOLUTION(IntEnum):
    PS4000A_DR_8BIT = 0
    PS4000A_DR_12BIT = 1
    PS4000A_DR_14BIT = 2
    PS4000A_DR_15BIT = 3
    PS4000A_DR_16BIT = 4


PS4000A_DEVICE_RESOLUTION_T = c_int32


class PS4000A_EXTRA_OPERATIONS(IntEnum):
    PS4000A_ES_OFF = 0
    PS4000A_WHITENOISE = 1
    PS4000A_PRBS = 2


PS4000A_EXTRA_OPERATIONS_T = c_int32


class PS4000A_BANDWIDTH_LIMITER_FLAGS(IntFlag):
    PS4000A_BW_FULL_FLAG = 1 << 0
    PS4000A_BW_20KHZ_FLAG = 1 << 1
    PS4000A_BW_100KHZ_FLAG = 1 << 2
    PS4000A_BW_1MHZ_FLAG = 1 << 3


PS4000A_BANDWIDTH_LIMITER_FLAGS_T = c_int32


class PS4000A_BANDWIDTH_LIMITER(IntEnum):
    PS4000A_BW_FULL = 0
    PS4000A_BW_20KHZ = 1
    PS4000A_BW_100KHZ = 2  # default when a current clamp is detected
    PS4000A_BW_1MHZ = 3  # default for 14 bits


PS4000A_BANDWIDTH_LIMITER_T = c_int32


class PS4000A_COUPLING(IntEnum):
    PS4000A_AC = 0
    PS4000A_DC = 1


PS4000A_COUPLING_T = c_int32


class PS4000A_CHANNEL(IntEnum):
    PS4000A_CHANNEL_A = 0
    PS4000A_CHANNEL_B = 1
    PS4000A_CHANNEL_C = 2
    PS4000A_CHANNEL_D = 3
    PS4000A_MAX_4_CHANNELS = 4
    PS4000A_CHANNEL_E = PS4000A_MAX_4_CHANNELS
    PS4000A_CHANNEL_F = 5
    PS4000A_CHANNEL_G = 6
    PS4000A_CHANNEL_H = 7
    PS4000A_EXTERNAL = 8
    PS4000A_MAX_CHANNELS = PS4000A_EXTERNAL
    PS4000A_TRIGGER_AUX = 9
    PS4000A_MAX_TRIGGER_SOURCES = 10
    PS4000A_PULSE_WIDTH_SOURCE = 0x10000000


PS4000A_CHANNEL_T = c_int32


class PS4000A_CHANNEL_BUFFER_INDEX(IntEnum):
    PS4000A_CHANNEL_A_MAX = 0
    PS4000A_CHANNEL_A_MIN = 1
    PS4000A_CHANNEL_B_MAX = 2
    PS4000A_CHANNEL_B_MIN = 3
    PS4000A_CHANNEL_C_MAX = 4
    PS4000A_CHANNEL_C_MIN = 5
    PS4000A_CHANNEL_D_MAX = 6
    PS4000A_CHANNEL_D_MIN = 7
    PS4000A_CHANNEL_E_MAX = 8
    PS4000A_CHANNEL_E_MIN = 9
    PS4000A_CHANNEL_F_MAX = 10
    PS4000A_CHANNEL_F_MIN = 11
    PS4000A_CHANNEL_G_MAX = 12
    PS4000A_CHANNEL_G_MIN = 13
    PS4000A_CHANNEL_H_MAX = 14
    PS4000A_CHANNEL_H_MIN = 15
    PS4000A_MAX_CHANNEL_BUFFERS = 16


PS4000A_CHANNEL_BUFFER_INDEX_T = c_int32


class PS4000A_RANGE(IntEnum):
    """The voltage ranges; equal to the ``PICO_X1_PROBE_*`` values of
    ``PICO_CONNECT_PROBE_RANGE``, which the functions take."""

    PS4000A_10MV = 0
    PS4000A_20MV = 1
    PS4000A_50MV = 2
    PS4000A_100MV = 3
    PS4000A_200MV = 4
    PS4000A_500MV = 5
    PS4000A_1V = 6
    PS4000A_2V = 7
    PS4000A_5V = 8
    PS4000A_10V = 9
    PS4000A_20V = 10
    PS4000A_50V = 11
    PS4000A_100V = 12
    PS4000A_200V = 13
    PS4000A_MAX_RANGES = 14


PS4000A_RANGE_T = c_int32


class PS4000A_RESISTANCE_RANGE(IntEnum):
    """The resistance ranges; equal to the ``PICO_PS4000A_RESISTANCE_*`` values of
    ``PICO_CONNECT_PROBE_RANGE``, which the functions take."""

    PS4000A_RESISTANCE_315K = 0x00000200
    PS4000A_RESISTANCE_1100K = 0x00000201
    PS4000A_RESISTANCE_10M = 0x00000202
    PS4000A_MAX_RESISTANCE_RANGES = 3
    PS4000A_RESISTANCE_ADCV = 0x10000000


PS4000A_RESISTANCE_RANGE_T = c_int32


class PS4000A_ETS_MODE(IntEnum):
    PS4000A_ETS_OFF = 0
    PS4000A_ETS_FAST = 1
    PS4000A_ETS_SLOW = 2
    PS4000A_ETS_MODES_MAX = 3


PS4000A_ETS_MODE_T = c_int32


class PS4000A_TIME_UNITS(IntEnum):
    PS4000A_FS = 0
    PS4000A_PS = 1
    PS4000A_NS = 2
    PS4000A_US = 3
    PS4000A_MS = 4
    PS4000A_S = 5
    PS4000A_MAX_TIME_UNITS = 6


PS4000A_TIME_UNITS_T = c_int32


class PS4000A_SWEEP_TYPE(IntEnum):
    PS4000A_UP = 0
    PS4000A_DOWN = 1
    PS4000A_UPDOWN = 2
    PS4000A_DOWNUP = 3
    PS4000A_MAX_SWEEP_TYPES = 4


PS4000A_SWEEP_TYPE_T = c_int32


class PS4000A_WAVE_TYPE(IntEnum):
    PS4000A_SINE = 0
    PS4000A_SQUARE = 1
    PS4000A_TRIANGLE = 2
    PS4000A_RAMP_UP = 3
    PS4000A_RAMP_DOWN = 4
    PS4000A_SINC = 5
    PS4000A_GAUSSIAN = 6
    PS4000A_HALF_SINE = 7
    PS4000A_DC_VOLTAGE = 8
    PS4000A_WHITE_NOISE = 9
    PS4000A_MAX_WAVE_TYPES = 10


PS4000A_WAVE_TYPE_T = c_int32


class PS4000A_PIN_STATES(IntEnum):
    PS4000A_CAL_PINS_OFF = 0
    PS4000A_GND_SIGNAL = 1
    PS4000A_SIGNAL_SIGNAL = 2


PS4000A_PIN_STATES_T = c_int32


PS4000A_SINE_MAX_FREQUENCY = 1000000.0
PS4000A_SQUARE_MAX_FREQUENCY = 1000000.0
PS4000A_TRIANGLE_MAX_FREQUENCY = 1000000.0
PS4000A_SINC_MAX_FREQUENCY = 1000000.0
PS4000A_RAMP_MAX_FREQUENCY = 1000000.0
PS4000A_HALF_SINE_MAX_FREQUENCY = 1000000.0
PS4000A_GAUSSIAN_MAX_FREQUENCY = 1000000.0
PS4000A_MIN_FREQUENCY = 0.03


class PS4000A_CHANNEL_LED(IntEnum):
    PS4000A_CHANNEL_LED_OFF = 0
    PS4000A_CHANNEL_LED_RED = 1
    PS4000A_CHANNEL_LED_GREEN = 2


PS4000A_CHANNEL_LED_T = c_int32


class PS4000A_PROBE_LED_POSITION(IntFlag):
    PS4000A_UPPER_LEFT_LED = 0x01
    PS4000A_LOWER_LEFT_LED = 0x02
    PS4000A_UPPER_RIGHT_LED = 0x04
    PS4000A_LOWER_RIGHT_LED = 0x08
    PS4000A_MIDDLE_LEFT_LED = 0x10
    PS4000A_MIDDLE_RIGHT_LED = 0x20

    PS4000A_RIGHT_LEDS = (
        PS4000A_UPPER_RIGHT_LED | PS4000A_LOWER_RIGHT_LED | PS4000A_MIDDLE_RIGHT_LED
    )
    PS4000A_LEFT_LEDS = (
        PS4000A_UPPER_LEFT_LED | PS4000A_LOWER_LEFT_LED | PS4000A_MIDDLE_LEFT_LED
    )

    PS4000A_UPPER_LEDS = PS4000A_UPPER_RIGHT_LED | PS4000A_UPPER_LEFT_LED
    PS4000A_LOWER_LEDS = PS4000A_LOWER_RIGHT_LED | PS4000A_LOWER_LEFT_LED
    PS4000A_MIDDLE_LEDS = PS4000A_MIDDLE_RIGHT_LED | PS4000A_MIDDLE_LEFT_LED

    PS4000A_ALL_LEDS = (
        PS4000A_UPPER_LEFT_LED
        | PS4000A_LOWER_LEFT_LED
        | PS4000A_UPPER_RIGHT_LED
        | PS4000A_LOWER_RIGHT_LED
        | PS4000A_MIDDLE_LEFT_LED
        | PS4000A_MIDDLE_RIGHT_LED
    )


PS4000A_PROBE_LED_POSITION_T = c_int32


class PS4000A_META_TYPE(IntEnum):
    PS4000A_MT_UNIT_INFO = 0
    PS4000A_MT_DEVICE_CAPABILITY = 1
    PS4000A_MT_DEVICE_SETTINGS = 2
    PS4000A_MT_SIGNAL_GENERATOR_SETTINGS = 3


PS4000A_META_TYPE_T = c_int32


class PS4000A_META_OPERATION(IntEnum):
    PS4000A_MO_READ = 0
    PS4000A_MO_WRITE = 1


PS4000A_META_OPERATION_T = c_int32


class PS4000A_META_FORMAT(IntEnum):
    PS4000A_MF_COMMA_SEPARATED = 0
    PS4000A_MF_XML = 1


PS4000A_META_FORMAT_T = c_int32


class PS4000A_SIGGEN_TRIG_TYPE(IntEnum):
    PS4000A_SIGGEN_RISING = 0
    PS4000A_SIGGEN_FALLING = 1
    PS4000A_SIGGEN_GATE_HIGH = 2
    PS4000A_SIGGEN_GATE_LOW = 3


PS4000A_SIGGEN_TRIG_TYPE_T = c_int32


class PS4000A_SIGGEN_TRIG_SOURCE(IntEnum):
    PS4000A_SIGGEN_NONE = 0
    PS4000A_SIGGEN_SCOPE_TRIG = 1
    PS4000A_SIGGEN_AUX_IN = 2
    PS4000A_SIGGEN_EXT_IN = 3
    PS4000A_SIGGEN_SOFT_TRIG = 4


PS4000A_SIGGEN_TRIG_SOURCE_T = c_int32


class PS4000A_INDEX_MODE(IntEnum):
    PS4000A_SINGLE = 0
    PS4000A_DUAL = 1
    PS4000A_QUAD = 2
    PS4000A_MAX_INDEX_MODES = 3


PS4000A_INDEX_MODE_T = c_int32


class PS4000A_THRESHOLD_MODE(IntEnum):
    PS4000A_LEVEL = 0
    PS4000A_WINDOW = 1


PS4000A_THRESHOLD_MODE_T = c_int32


class PS4000A_THRESHOLD_DIRECTION(IntEnum):
    PS4000A_ABOVE = 0
    PS4000A_BELOW = 1
    PS4000A_RISING = 2
    PS4000A_FALLING = 3
    PS4000A_RISING_OR_FALLING = 4
    PS4000A_ABOVE_LOWER = 5
    PS4000A_BELOW_LOWER = 6
    PS4000A_RISING_LOWER = 7
    PS4000A_FALLING_LOWER = 8
    PS4000A_INSIDE = PS4000A_ABOVE
    PS4000A_OUTSIDE = PS4000A_BELOW
    PS4000A_ENTER = PS4000A_RISING
    PS4000A_EXIT = PS4000A_FALLING
    PS4000A_ENTER_OR_EXIT = PS4000A_RISING_OR_FALLING
    PS4000A_POSITIVE_RUNT = 9
    PS4000A_NEGATIVE_RUNT = 10
    PS4000A_NONE = PS4000A_RISING


PS4000A_THRESHOLD_DIRECTION_T = c_int32


class PS4000A_TRIGGER_STATE(IntEnum):
    PS4000A_CONDITION_DONT_CARE = 0
    PS4000A_CONDITION_TRUE = 1
    PS4000A_CONDITION_FALSE = 2
    PS4000A_CONDITION_MAX = 3


PS4000A_TRIGGER_STATE_T = c_int32


class PS4000A_SENSOR_STATE(IntEnum):
    PS4000A_CONNECT_STATE_FLOATING = 0
    PS4000A_SENSOR_STATE_CONNECTED = 1


PS4000A_SENSOR_STATE_T = c_int32


class PS4000A_FREQUENCY_COUNTER_RANGE(IntEnum):
    PS4000A_FC_2K = 0
    PS4000A_FC_20K = 1
    PS4000A_FC_20 = 2
    PS4000A_FC_200 = 3
    PS4000A_FC_MAX = 4


PS4000A_FREQUENCY_COUNTER_RANGE_T = c_int32


class PS4000A_ACCELEROMETER_AXIS(IntEnum):
    PS4000A_AXIS_X = 0
    PS4000A_AXIS_Y = 1
    PS4000A_AXIS_Z = 2


PS4000A_ACCELEROMETER_AXIS_T = c_int32


class PS4000A_CHANNEL_FLAGS(IntFlag):
    PS4000A_CHANNEL_A_FLAGS = 1
    PS4000A_CHANNEL_B_FLAGS = 2
    PS4000A_CHANNEL_C_FLAGS = 4
    PS4000A_CHANNEL_D_FLAGS = 8
    PS4000A_CHANNEL_E_FLAGS = 16
    PS4000A_CHANNEL_F_FLAGS = 32
    PS4000A_CHANNEL_G_FLAGS = 64
    PS4000A_CHANNEL_H_FLAGS = 128


PS4000A_CHANNEL_FLAGS_T = c_int32


@final
class PS4000A_CHANNEL_LED_SETTING(CStruct):
    channel: Annotated[PS4000A_CHANNEL, PS4000A_CHANNEL_T]
    state: Annotated[PS4000A_CHANNEL_LED, PS4000A_CHANNEL_LED_T]


@final
class PS4000A_PROBE_LED_COLOUR(CStruct):
    red: Annotated[int, c_uint8]
    green: Annotated[int, c_uint8]
    blue: Annotated[int, c_uint8]


@final
class PS4000A_PROBE_CHANNEL_LED_SETTING(CStruct):
    channel: Annotated[PS4000A_CHANNEL, PS4000A_CHANNEL_T]
    position: Annotated[PS4000A_PROBE_LED_POSITION, PS4000A_PROBE_LED_POSITION_T]
    rgb: PS4000A_PROBE_LED_COLOUR


@final
class PS4000A_DIRECTION(CStruct):
    channel: Annotated[PS4000A_CHANNEL, PS4000A_CHANNEL_T]
    direction: Annotated[PS4000A_THRESHOLD_DIRECTION, PS4000A_THRESHOLD_DIRECTION_T]


@final
class PS4000A_CONDITION(CStruct):
    source: Annotated[PS4000A_CHANNEL, PS4000A_CHANNEL_T]
    condition: Annotated[PS4000A_TRIGGER_STATE, PS4000A_TRIGGER_STATE_T]


class PS4000A_CONDITIONS_INFO(IntFlag):
    PS4000A_CLEAR = 0x00000001
    PS4000A_ADD = 0x00000002


PS4000A_CONDITIONS_INFO_T = c_int32


@final
class PS4000A_TRIGGER_CHANNEL_PROPERTIES(CStruct):
    thresholdUpper: Annotated[int, c_int16]
    thresholdUpperHysteresis: Annotated[int, c_uint16]
    thresholdLower: Annotated[int, c_int16]
    thresholdLowerHysteresis: Annotated[int, c_uint16]
    channel: Annotated[PS4000A_CHANNEL, PS4000A_CHANNEL_T]
    thresholdMode: Annotated[PS4000A_THRESHOLD_MODE, PS4000A_THRESHOLD_MODE_T]


@final
class PS4000A_CONNECT_DETECT(CStruct):
    channel: Annotated[PS4000A_CHANNEL, PS4000A_CHANNEL_T]
    state: Annotated[PS4000A_SENSOR_STATE, PS4000A_SENSOR_STATE_T] = (
        PS4000A_SENSOR_STATE.PS4000A_CONNECT_STATE_FLOATING
    )


@final
class PS4000A_USER_PROBE_INTERACTIONS(CStruct):
    connected: Annotated[bool, c_uint16]
    channel: Annotated[PS4000A_CHANNEL, PS4000A_CHANNEL_T]
    enabled: Annotated[bool, c_uint16]
    probeName: Annotated[PICO_CONNECT_PROBE, PICO_CONNECT_PROBE_T]
    requiresPower_: Annotated[bool, c_uint8]
    isPowered_: Annotated[bool, c_uint8]
    status_: Annotated[PICO_STATUS, PICO_STATUS_T]
    probeOff: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    rangeFirst_: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    rangeLast_: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    rangeCurrent_: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    couplingFirst_: Annotated[PS4000A_COUPLING, PS4000A_COUPLING_T]
    couplingLast_: Annotated[PS4000A_COUPLING, PS4000A_COUPLING_T]
    couplingCurrent_: Annotated[PS4000A_COUPLING, PS4000A_COUPLING_T]
    filterFlags_: Annotated[
        PS4000A_BANDWIDTH_LIMITER_FLAGS, PS4000A_BANDWIDTH_LIMITER_FLAGS_T
    ]
    filterCurrent_: Annotated[
        PS4000A_BANDWIDTH_LIMITER_FLAGS, PS4000A_BANDWIDTH_LIMITER_FLAGS_T
    ]
    defaultFilter_: Annotated[PS4000A_BANDWIDTH_LIMITER, PS4000A_BANDWIDTH_LIMITER_T]


class PS4000A_RATIO_MODE(IntFlag):
    PS4000A_RATIO_MODE_NONE = 0
    PS4000A_RATIO_MODE_AGGREGATE = 1
    PS4000A_RATIO_MODE_DECIMATE = 2
    PS4000A_RATIO_MODE_AVERAGE = 4
    PS4000A_RATIO_MODE_DISTRIBUTION = 8


PS4000A_RATIO_MODE_T = c_int32


class PS4000A_PULSE_WIDTH_TYPE(IntEnum):
    PS4000A_PW_TYPE_NONE = 0
    PS4000A_PW_TYPE_LESS_THAN = 1
    PS4000A_PW_TYPE_GREATER_THAN = 2
    PS4000A_PW_TYPE_IN_RANGE = 3
    PS4000A_PW_TYPE_OUT_OF_RANGE = 4


PS4000A_PULSE_WIDTH_TYPE_T = c_int32


class PS4000A_CHANNEL_INFO(IntEnum):
    PS4000A_CI_RANGES = 0
    PS4000A_CI_RESISTANCES = 1


PS4000A_CHANNEL_INFO_T = c_int32


ps4000aBlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps4000aStreamingReady = CALLBACK_FUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)

ps4000aDataReady = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p
)

# Like the shared PicoProbeInteractions, but with the driver's own struct.
ps4000aProbeInteractions = CALLBACK_FUNCTYPE(
    None,
    c_int16,
    PICO_STATUS_T,
    POINTER(PS4000A_USER_PROBE_INTERACTIONS.c_type),
    c_uint32,
)


class PicoScope4000aWrapper(PicoScopeWrapperBase):
    _library_name = "ps4000a"

    def __init__(self, library_path: str | None = None) -> None:
        super().__init__(library_path)

        # The power source statuses report how the device is powered: a 4444
        # without its DC supply, a 4824 on a USB 2.0 port (guide pp70-76).
        # The async opens start nothing if another open is in progress.
        self._ps4000aOpenUnitWithResolution = self._bind(
            "ps4000aOpenUnitWithResolution",
            [POINTER(c_int16), c_char_p, PS4000A_DEVICE_RESOLUTION_T],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps4000aOpenUnit = self._bind(
            "ps4000aOpenUnit",
            [POINTER(c_int16), c_char_p],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps4000aOpenUnitAsyncWithResolution = self._bind(
            "ps4000aOpenUnitAsyncWithResolution",
            [POINTER(c_int16), c_char_p, PS4000A_DEVICE_RESOLUTION_T],
            info=POWER_SOURCE_STATUSES | {PICO_STATUS.PICO_OPEN_OPERATION_IN_PROGRESS},
        )
        self._ps4000aOpenUnitAsync = self._bind(
            "ps4000aOpenUnitAsync",
            [POINTER(c_int16), c_char_p],
            info=POWER_SOURCE_STATUSES | {PICO_STATUS.PICO_OPEN_OPERATION_IN_PROGRESS},
        )
        self._ps4000aOpenUnitProgress = self._bind(
            "ps4000aOpenUnitProgress",
            [POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps4000aGetUnitInfo = self._bind(
            "ps4000aGetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps4000aGetAccessoryInfo = self._bind(
            "ps4000aGetAccessoryInfo",
            [
                c_int16,
                PS4000A_CHANNEL_T,
                c_char_p,
                c_int16,
                POINTER(c_int16),
                PICO_INFO_T,
            ],
        )
        self._ps4000aFlashLed = self._bind("ps4000aFlashLed", [c_int16, c_int16])
        self._ps4000aSetChannelLed = self._bind(
            "ps4000aSetChannelLed",
            [c_int16, POINTER(PS4000A_CHANNEL_LED_SETTING.c_type), c_uint16],
        )
        self._ps4000aIsLedFlashing = self._bind(
            "ps4000aIsLedFlashing", [c_int16, POINTER(c_int16)]
        )
        self._ps4000aCloseUnit = self._bind("ps4000aCloseUnit", [c_int16])
        self._ps4000aMemorySegments = self._bind(
            "ps4000aMemorySegments", [c_int16, c_uint32, POINTER(c_int32)]
        )
        self._ps4000aSetChannel = self._bind(
            "ps4000aSetChannel",
            [
                c_int16,
                PS4000A_CHANNEL_T,
                c_int16,
                PS4000A_COUPLING_T,
                PICO_CONNECT_PROBE_RANGE_T,
                c_float,
            ],
        )
        self._ps4000aSetBandwidthFilter = self._bind(
            "ps4000aSetBandwidthFilter",
            [c_int16, PS4000A_CHANNEL_T, PS4000A_BANDWIDTH_LIMITER_T],
        )
        self._ps4000aApplyResistanceScaling = self._bind(
            "ps4000aApplyResistanceScaling",
            [
                c_int16,
                PS4000A_CHANNEL_T,
                PICO_CONNECT_PROBE_RANGE_T,
                c_void_p,
                c_void_p,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps4000aGetTimebase = self._bind(
            "ps4000aGetTimebase",
            [
                c_int16,
                c_uint32,
                c_int32,
                POINTER(c_int32),
                POINTER(c_int32),
                c_uint32,
            ],
        )
        self._ps4000aGetTimebase2 = self._bind(
            "ps4000aGetTimebase2",
            [
                c_int16,
                c_uint32,
                c_int32,
                POINTER(c_float),
                POINTER(c_int32),
                c_uint32,
            ],
        )
        self._ps4000aSetSigGenArbitrary = self._bind(
            "ps4000aSetSigGenArbitrary",
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
                PS4000A_SWEEP_TYPE_T,
                PS4000A_EXTRA_OPERATIONS_T,
                PS4000A_INDEX_MODE_T,
                c_uint32,
                c_uint32,
                PS4000A_SIGGEN_TRIG_TYPE_T,
                PS4000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000aSetSigGenArbitraryV2 = self._bind(
            "ps4000aSetSigGenArbitraryV2",
            [
                c_int16,
                c_int32,
                c_uint32,
                c_uint64,
                c_uint64,
                c_uint64,
                c_uint64,
                c_void_p,
                c_int32,
                PS4000A_SWEEP_TYPE_T,
                PS4000A_EXTRA_OPERATIONS_T,
                PS4000A_INDEX_MODE_T,
                c_uint64,
                c_uint64,
                PS4000A_SIGGEN_TRIG_TYPE_T,
                PS4000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000aSetSigGenBuiltIn = self._bind(
            "ps4000aSetSigGenBuiltIn",
            [
                c_int16,
                c_int32,
                c_uint32,
                PS4000A_WAVE_TYPE_T,
                c_double,
                c_double,
                c_double,
                c_double,
                PS4000A_SWEEP_TYPE_T,
                PS4000A_EXTRA_OPERATIONS_T,
                c_uint32,
                c_uint32,
                PS4000A_SIGGEN_TRIG_TYPE_T,
                PS4000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000aSetSigGenBuiltInV2 = self._bind(
            "ps4000aSetSigGenBuiltInV2",
            [
                c_int16,
                c_int32,
                c_uint32,
                PS4000A_WAVE_TYPE_T,
                c_double,
                c_double,
                c_double,
                c_double,
                PS4000A_SWEEP_TYPE_T,
                PS4000A_EXTRA_OPERATIONS_T,
                c_uint64,
                c_uint64,
                PS4000A_SIGGEN_TRIG_TYPE_T,
                PS4000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000aSetSigGenPropertiesArbitrary = self._bind(
            "ps4000aSetSigGenPropertiesArbitrary",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                c_uint32,
                PS4000A_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS4000A_SIGGEN_TRIG_TYPE_T,
                PS4000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000aSetSigGenPropertiesArbitraryV2 = self._bind(
            "ps4000aSetSigGenPropertiesArbitraryV2",
            [
                c_int16,
                c_uint64,
                c_uint64,
                c_uint64,
                c_uint64,
                PS4000A_SWEEP_TYPE_T,
                c_uint64,
                c_uint64,
                PS4000A_SIGGEN_TRIG_TYPE_T,
                PS4000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000aSetSigGenPropertiesBuiltIn = self._bind(
            "ps4000aSetSigGenPropertiesBuiltIn",
            [
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS4000A_SWEEP_TYPE_T,
                c_uint32,
                c_uint32,
                PS4000A_SIGGEN_TRIG_TYPE_T,
                PS4000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000aSetSigGenPropertiesBuiltInV2 = self._bind(
            "ps4000aSetSigGenPropertiesBuiltInV2",
            [
                c_int16,
                c_double,
                c_double,
                c_double,
                c_double,
                PS4000A_SWEEP_TYPE_T,
                c_uint64,
                c_uint64,
                PS4000A_SIGGEN_TRIG_TYPE_T,
                PS4000A_SIGGEN_TRIG_SOURCE_T,
                c_int16,
            ],
        )
        self._ps4000aSigGenFrequencyToPhase = self._bind(
            "ps4000aSigGenFrequencyToPhase",
            [c_int16, c_double, PS4000A_INDEX_MODE_T, c_uint32, POINTER(c_uint32)],
        )
        self._ps4000aSigGenFrequencyToPhaseV2 = self._bind(
            "ps4000aSigGenFrequencyToPhaseV2",
            [c_int16, c_double, PS4000A_INDEX_MODE_T, c_uint32, POINTER(c_uint64)],
        )
        self._ps4000aSigGenArbitraryMinMaxValues = self._bind(
            "ps4000aSigGenArbitraryMinMaxValues",
            [
                c_int16,
                POINTER(c_int16),
                POINTER(c_int16),
                POINTER(c_uint32),
                POINTER(c_uint32),
            ],
        )
        self._ps4000aSigGenSoftwareControl = self._bind(
            "ps4000aSigGenSoftwareControl", [c_int16, c_int16]
        )
        self._ps4000aSetEts = self._bind(
            "ps4000aSetEts",
            [c_int16, PS4000A_ETS_MODE_T, c_int16, c_int16, POINTER(c_int32)],
        )
        self._ps4000aSetTriggerChannelProperties = self._bind(
            "ps4000aSetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PS4000A_TRIGGER_CHANNEL_PROPERTIES.c_type),
                c_int16,
                c_int16,
                c_int32,
            ],
        )
        self._ps4000aSetTriggerChannelConditions = self._bind(
            "ps4000aSetTriggerChannelConditions",
            [
                c_int16,
                POINTER(PS4000A_CONDITION.c_type),
                c_int16,
                PS4000A_CONDITIONS_INFO_T,
            ],
        )
        self._ps4000aSetTriggerChannelDirections = self._bind(
            "ps4000aSetTriggerChannelDirections",
            [c_int16, POINTER(PS4000A_DIRECTION.c_type), c_int16],
        )
        self._ps4000aSetSimpleTrigger = self._bind(
            "ps4000aSetSimpleTrigger",
            [
                c_int16,
                c_int16,
                PS4000A_CHANNEL_T,
                c_int16,
                PS4000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_int16,
            ],
        )
        self._ps4000aSetTriggerDelay = self._bind(
            "ps4000aSetTriggerDelay", [c_int16, c_uint32]
        )
        self._ps4000aSetPulseWidthQualifierProperties = self._bind(
            "ps4000aSetPulseWidthQualifierProperties",
            [
                c_int16,
                PS4000A_THRESHOLD_DIRECTION_T,
                c_uint32,
                c_uint32,
                PS4000A_PULSE_WIDTH_TYPE_T,
            ],
        )
        self._ps4000aSetPulseWidthQualifierConditions = self._bind(
            "ps4000aSetPulseWidthQualifierConditions",
            [
                c_int16,
                POINTER(PS4000A_CONDITION.c_type),
                c_int16,
                PS4000A_CONDITIONS_INFO_T,
            ],
        )
        self._ps4000aIsTriggerOrPulseWidthQualifierEnabled = self._bind(
            "ps4000aIsTriggerOrPulseWidthQualifierEnabled",
            [c_int16, POINTER(c_int16), POINTER(c_int16)],
        )
        self._ps4000aGetTriggerTimeOffset = self._bind(
            "ps4000aGetTriggerTimeOffset",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS4000A_TIME_UNITS_T),
                c_uint32,
            ],
        )
        self._ps4000aGetTriggerTimeOffset64 = self._bind(
            "ps4000aGetTriggerTimeOffset64",
            [c_int16, POINTER(c_int64), POINTER(PS4000A_TIME_UNITS_T), c_uint32],
        )
        self._ps4000aGetValuesTriggerTimeOffsetBulk = self._bind(
            "ps4000aGetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_uint32),
                POINTER(c_uint32),
                POINTER(PS4000A_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps4000aGetValuesTriggerTimeOffsetBulk64 = self._bind(
            "ps4000aGetValuesTriggerTimeOffsetBulk64",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PS4000A_TIME_UNITS_T),
                c_uint32,
                c_uint32,
            ],
        )
        self._ps4000aSetDataBuffers = self._bind(
            "ps4000aSetDataBuffers",
            [
                c_int16,
                PS4000A_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_int32,
                c_uint32,
                PS4000A_RATIO_MODE_T,
            ],
        )
        self._ps4000aSetDataBuffer = self._bind(
            "ps4000aSetDataBuffer",
            [
                c_int16,
                PS4000A_CHANNEL_T,
                c_void_p,
                c_int32,
                c_uint32,
                PS4000A_RATIO_MODE_T,
            ],
        )
        self._ps4000aSetEtsTimeBuffer = self._bind(
            "ps4000aSetEtsTimeBuffer", [c_int16, c_void_p, c_int32]
        )
        self._ps4000aSetEtsTimeBuffers = self._bind(
            "ps4000aSetEtsTimeBuffers", [c_int16, c_void_p, c_void_p, c_int32]
        )
        self._ps4000aIsReady = self._bind("ps4000aIsReady", [c_int16, POINTER(c_int16)])
        self._ps4000aRunBlock = self._bind(
            "ps4000aRunBlock",
            [
                c_int16,
                c_int32,
                c_int32,
                c_uint32,
                POINTER(c_int32),
                c_uint32,
                ps4000aBlockReady,
                c_void_p,
            ],
        )
        self._ps4000aRunStreaming = self._bind(
            "ps4000aRunStreaming",
            [
                c_int16,
                POINTER(c_uint32),
                PS4000A_TIME_UNITS_T,
                c_uint32,
                c_uint32,
                c_int16,
                c_uint32,
                PS4000A_RATIO_MODE_T,
                c_uint32,
            ],
        )
        # PICO_BUSY: no new streaming data is available yet; poll again later.
        self._ps4000aGetStreamingLatestValues = self._bind(
            "ps4000aGetStreamingLatestValues",
            [c_int16, ps4000aStreamingReady, c_void_p],
            info=(PICO_STATUS.PICO_BUSY,),
        )
        self._ps4000aNoOfStreamingValues = self._bind(
            "ps4000aNoOfStreamingValues", [c_int16, POINTER(c_uint32)]
        )
        self._ps4000aGetMaxDownSampleRatio = self._bind(
            "ps4000aGetMaxDownSampleRatio",
            [c_int16, c_uint32, POINTER(c_uint32), PS4000A_RATIO_MODE_T, c_uint32],
        )
        self._ps4000aGetValues = self._bind(
            "ps4000aGetValues",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS4000A_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps4000aGetValuesAsync = self._bind(
            "ps4000aGetValuesAsync",
            [
                c_int16,
                c_uint32,
                c_uint32,
                c_uint32,
                PS4000A_RATIO_MODE_T,
                c_uint32,
                # Declared as void * in the header; a ps4000aDataReady is passed.
                c_void_p,
                c_void_p,
            ],
        )
        self._ps4000aGetValuesBulk = self._bind(
            "ps4000aGetValuesBulk",
            [
                c_int16,
                POINTER(c_uint32),
                c_uint32,
                c_uint32,
                c_uint32,
                PS4000A_RATIO_MODE_T,
                POINTER(c_int16),
            ],
        )
        self._ps4000aGetValuesOverlapped = self._bind(
            "ps4000aGetValuesOverlapped",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS4000A_RATIO_MODE_T,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps4000aGetValuesOverlappedBulk = self._bind(
            "ps4000aGetValuesOverlappedBulk",
            [
                c_int16,
                c_uint32,
                POINTER(c_uint32),
                c_uint32,
                PS4000A_RATIO_MODE_T,
                c_uint32,
                c_uint32,
                POINTER(c_int16),
            ],
        )
        self._ps4000aEnumerateUnits = self._bind(
            "ps4000aEnumerateUnits",
            [POINTER(c_int16), c_char_p, POINTER(c_int16)],
            # Finding no units is a valid enumeration result, not a failure.
            info=(PICO_STATUS.PICO_NOT_FOUND,),
        )
        self._ps4000aGetChannelInformation = self._bind(
            "ps4000aGetChannelInformation",
            [
                c_int16,
                PS4000A_CHANNEL_INFO_T,
                c_int32,
                POINTER(c_int32),
                POINTER(c_int32),
                c_int32,
            ],
        )
        self._ps4000aConnectDetect = self._bind(
            "ps4000aConnectDetect",
            [c_int16, POINTER(PS4000A_CONNECT_DETECT.c_type), c_int16],
        )
        self._ps4000aSetProbeInteractionCallback = self._bind(
            "ps4000aSetProbeInteractionCallback", [c_int16, ps4000aProbeInteractions]
        )
        self._ps4000aCalibrateProbe = self._bind(
            "ps4000aCalibrateProbe", [c_int16, PS4000A_CHANNEL_T, POINTER(c_int16)]
        )
        self._ps4000aSetProbeLedColour = self._bind(
            "ps4000aSetProbeLedColour",
            [c_int16, POINTER(PS4000A_PROBE_CHANNEL_LED_SETTING.c_type), c_uint16],
        )
        self._ps4000aRegisterProbeLedColour = self._bind(
            "ps4000aRegisterProbeLedColour",
            [
                c_int16,
                PICO_CONNECT_PROBE_T,
                POINTER(PS4000A_PROBE_CHANNEL_LED_SETTING.c_type),
                c_uint16,
            ],
        )
        self._ps4000aSetProbeLedDefaults = self._bind(
            "ps4000aSetProbeLedDefaults", [c_int16, c_int16]
        )
        self._ps4000aMaximumValue = self._bind(
            "ps4000aMaximumValue", [c_int16, POINTER(c_int16)]
        )
        self._ps4000aMinimumValue = self._bind(
            "ps4000aMinimumValue", [c_int16, POINTER(c_int16)]
        )
        self._ps4000aGetAnalogueOffset = self._bind(
            "ps4000aGetAnalogueOffset",
            [
                c_int16,
                PICO_CONNECT_PROBE_RANGE_T,
                PS4000A_COUPLING_T,
                POINTER(c_float),
                POINTER(c_float),
            ],
        )
        self._ps4000aGetMaxSegments = self._bind(
            "ps4000aGetMaxSegments", [c_int16, POINTER(c_uint32)]
        )
        # Changing or querying the power source reports the (new) power source.
        self._ps4000aChangePowerSource = self._bind(
            "ps4000aChangePowerSource",
            [c_int16, PICO_STATUS_T],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps4000aCurrentPowerSource = self._bind(
            "ps4000aCurrentPowerSource", [c_int16], info=POWER_SOURCE_STATUSES
        )
        self._ps4000aStop = self._bind("ps4000aStop", [c_int16])
        # A responding unit may report its power source instead of PICO_OK
        # (guide p77).
        self._ps4000aPingUnit = self._bind(
            "ps4000aPingUnit",
            [c_int16],
            info=POWER_SOURCE_STATUSES | {PICO_STATUS.PICO_POWER_SUPPLY_UNDERVOLTAGE},
        )
        self._ps4000aSetNoOfCaptures = self._bind(
            "ps4000aSetNoOfCaptures", [c_int16, c_uint32]
        )
        self._ps4000aGetNoOfCaptures = self._bind(
            "ps4000aGetNoOfCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps4000aGetNoOfProcessedCaptures = self._bind(
            "ps4000aGetNoOfProcessedCaptures", [c_int16, POINTER(c_uint32)]
        )
        self._ps4000aDeviceMetaData = self._bind(
            "ps4000aDeviceMetaData",
            [
                c_int16,
                c_char_p,
                POINTER(c_int32),
                PS4000A_META_TYPE_T,
                PS4000A_META_OPERATION_T,
                PS4000A_META_FORMAT_T,
            ],
        )
        self._ps4000aGetString = self._bind(
            "ps4000aGetString",
            [c_int16, PICO_STRING_VALUE_T, c_char_p, POINTER(c_int32)],
        )
        self._ps4000aGetCommonModeOverflow = self._bind(
            "ps4000aGetCommonModeOverflow", [c_int16, POINTER(c_uint16)]
        )
        self._ps4000aSetFrequencyCounter = self._bind(
            "ps4000aSetFrequencyCounter",
            [
                c_int16,
                PS4000A_CHANNEL_T,
                c_int16,
                PS4000A_FREQUENCY_COUNTER_RANGE_T,
                c_int16,
                c_int16,
            ],
        )
        self._ps4000aQueryOutputEdgeDetect = self._bind(
            "ps4000aQueryOutputEdgeDetect", [c_int16, POINTER(c_int16)]
        )
        self._ps4000aSetOutputEdgeDetect = self._bind(
            "ps4000aSetOutputEdgeDetect", [c_int16, c_int16]
        )
        # Changing the resolution re-evaluates the power source, like opening
        # the unit does (guide p89).
        self._ps4000aSetDeviceResolution = self._bind(
            "ps4000aSetDeviceResolution",
            [c_int16, PS4000A_DEVICE_RESOLUTION_T],
            info=POWER_SOURCE_STATUSES,
        )
        self._ps4000aGetDeviceResolution = self._bind(
            "ps4000aGetDeviceResolution",
            [c_int16, POINTER(PS4000A_DEVICE_RESOLUTION_T)],
        )
        self._ps4000aSetCalibrationPins = self._bind(
            "ps4000aSetCalibrationPins",
            [
                c_int16,
                PS4000A_PIN_STATES_T,
                PS4000A_WAVE_TYPE_T,
                c_double,
                c_uint32,
                c_uint32,
            ],
        )
        self._ps4000aNearestSampleIntervalStateless = self._bind(
            "ps4000aNearestSampleIntervalStateless",
            [
                c_int16,
                PS4000A_CHANNEL_FLAGS_T,
                c_double,
                PS4000A_DEVICE_RESOLUTION_T,
                c_uint16,
                POINTER(c_uint32),
                POINTER(c_double),
            ],
        )
        self._ps4000aGetMinimumTimebaseStateless = self._bind(
            "ps4000aGetMinimumTimebaseStateless",
            [
                c_int16,
                PS4000A_CHANNEL_FLAGS_T,
                POINTER(c_uint32),
                POINTER(c_double),
                PS4000A_DEVICE_RESOLUTION_T,
            ],
        )
        self._ps4000aCheckForUpdate = self._bind(
            "ps4000aCheckForUpdate",
            [
                c_int16,
                POINTER(PICO_FIRMWARE_INFO.c_type),
                POINTER(c_int16),
                POINTER(c_uint16),
            ],
        )
        # A successful update (or one that was not needed) returns
        # PICO_FIRMWARE_UP_TO_DATE (guide p119).
        self._ps4000aStartFirmwareUpdate = self._bind(
            "ps4000aStartFirmwareUpdate",
            [c_int16, PicoUpdateFirmwareProgress],
            info={PICO_STATUS.PICO_FIRMWARE_UP_TO_DATE},
        )
        self._ps4000aSetAccelerometerProbeAxis = self._bind(
            "ps4000aSetAccelerometerProbeAxis",
            [c_int16, PS4000A_CHANNEL_T, PS4000A_ACCELEROMETER_AXIS_T],
        )
        self._ps4000aSetAccelerometerCalibrationMode = self._bind(
            "ps4000aSetAccelerometerCalibrationMode",
            [c_int16, PS4000A_CHANNEL_T, c_int16],
        )
        self._ps4000aFetchAccelerometerCalibrationStatistics = self._bind(
            "ps4000aFetchAccelerometerCalibrationStatistics",
            [
                c_int16,
                PS4000A_CHANNEL_T,
                POINTER(c_float),
                POINTER(c_float),
                POINTER(c_float),
                POINTER(c_uint16),
            ],
        )
        self._ps4000aGetMaximumProbeValue = self._bind(
            "ps4000aGetMaximumProbeValue",
            [c_int16, PS4000A_CHANNEL_T, PICO_CONNECT_PROBE_RANGE_T, POINTER(c_int16)],
        )

    def ps4000aOpenUnitWithResolution(
        self, serial: str | None, resolution: PS4000A_DEVICE_RESOLUTION
    ) -> tuple[c_int16, PICO_STATUS]:
        """Returns the handle and the status, which tells the power source if
        not PICO_OK."""
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        status = self._ps4000aOpenUnitWithResolution(byref(handle), ser, resolution)
        return handle, status

    def ps4000aOpenUnit(self, serial: str | None) -> tuple[c_int16, PICO_STATUS]:
        """Returns the handle and the status, which tells the power source if
        not PICO_OK."""
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        status = self._ps4000aOpenUnit(byref(handle), ser)
        return handle, status

    def ps4000aOpenUnitAsyncWithResolution(
        self, serial: str | None, resolution: PS4000A_DEVICE_RESOLUTION
    ) -> tuple[bool, PICO_STATUS]:
        """Start opening a unit; returns whether the operation started and the
        status, which tells the power source if not PICO_OK.

        If another open operation is in progress, nothing is started and the
        status is PICO_OPEN_OPERATION_IN_PROGRESS.
        """
        status = c_int16(0)
        ser = serial.encode() if serial is not None else None
        result = self._ps4000aOpenUnitAsyncWithResolution(
            byref(status), ser, resolution
        )
        return status.value != 0, result

    def ps4000aOpenUnitAsync(self, serial: str | None) -> tuple[bool, PICO_STATUS]:
        """Start opening a unit; returns whether the operation started and the
        status, which tells the power source if not PICO_OK.

        If another open operation is in progress, nothing is started and the
        status is PICO_OPEN_OPERATION_IN_PROGRESS.
        """
        status = c_int16(0)
        ser = serial.encode() if serial is not None else None
        result = self._ps4000aOpenUnitAsync(byref(status), ser)
        return status.value != 0, result

    def ps4000aOpenUnitProgress(self) -> tuple[c_int16, int, bool, PICO_STATUS]:
        """Returns the handle, the progress, whether the open is complete and
        the status, which tells the power source if not PICO_OK."""
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        status = self._ps4000aOpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return handle, progressPercent.value, complete.value != 0, status

    def ps4000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO) -> str:
        # Generous for any info string; longer ones are truncated (NUL terminated).
        string = create_string_buffer(4096)
        requiredSize = c_int16(0)
        self._ps4000aGetUnitInfo(handle, string, len(string), byref(requiredSize), info)
        return string.value.decode("utf-8")

    def ps4000aGetAccessoryInfo(
        self, handle: c_int16, channel: PS4000A_CHANNEL, info: PICO_INFO
    ) -> str:
        """Returns information about the accessory (probe) on ``channel``.

        Needs a probe interaction callback, see
        :meth:`ps4000aSetProbeInteractionCallback`.
        """
        # Generous for any info string; longer ones are truncated (NUL terminated).
        string = create_string_buffer(4096)
        requiredSize = c_int16(0)
        self._ps4000aGetAccessoryInfo(
            handle, channel, string, len(string), byref(requiredSize), info
        )
        return string.value.decode("utf-8")

    def ps4000aFlashLed(self, handle: c_int16, start: int) -> None:
        """Flash the LED ``start`` times; < 0 flashes indefinitely, 0 stops.

        RunBlock and RunStreaming cancel the flashing (guide p34).
        """
        self._ps4000aFlashLed(handle, start)

    def ps4000aSetChannelLed(
        self, handle: c_int16, ledStates: Sequence[PS4000A_CHANNEL_LED_SETTING]
    ) -> None:
        self._ps4000aSetChannelLed(
            handle, c_array(PS4000A_CHANNEL_LED_SETTING, ledStates), len(ledStates)
        )

    def ps4000aIsLedFlashing(self, handle: c_int16) -> bool:
        status = c_int16(0)
        self._ps4000aIsLedFlashing(handle, byref(status))
        return status.value != 0

    def ps4000aCloseUnit(self, handle: c_int16) -> None:
        self._ps4000aCloseUnit(handle)
        self._release_buffers(handle)

    def ps4000aMemorySegments(self, handle: c_int16, nSegments: int) -> int:
        """Returns the samples per segment, shared by the enabled channels: half
        of it per channel with 2, a quarter with 3-4 and an eighth with 5-8
        enabled channels (guide p66)."""
        assert nSegments > 0
        nMaxSamples = c_int32(0)
        self._ps4000aMemorySegments(handle, nSegments, byref(nMaxSamples))
        return nMaxSamples.value

    def ps4000aSetChannel(
        self,
        handle: c_int16,
        channel: PS4000A_CHANNEL,
        enabled: bool,
        type: PS4000A_COUPLING,
        range: PICO_CONNECT_PROBE_RANGE | int,
        analogOffset: float,
    ) -> None:
        """``type`` is the coupling, ``analogOffset`` in volts.

        ``range`` is a ``PICO_CONNECT_PROBE_RANGE``; ``PS4000A_RANGE`` values
        equal its ``PICO_X1_PROBE_*`` ranges. Per the header, a resistance range
        may be ORed with ``PS4000A_RESISTANCE_ADCV``.
        """
        self._ps4000aSetChannel(
            handle, channel, 1 if enabled else 0, type, range, analogOffset
        )

    def ps4000aSetBandwidthFilter(
        self,
        handle: c_int16,
        channel: PS4000A_CHANNEL,
        bandwidth: PS4000A_BANDWIDTH_LIMITER,
    ) -> None:
        self._ps4000aSetBandwidthFilter(handle, channel, bandwidth)

    def ps4000aApplyResistanceScaling(
        self,
        handle: c_int16,
        channel: PS4000A_CHANNEL,
        range: PICO_CONNECT_PROBE_RANGE | int,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        buffertLth: int,
    ) -> PS4000A_CHANNEL_FLAGS:
        """Scale the int16 samples in ``bufferMax`` and ``bufferMin`` for the
        resistance ``range``; returns the overflow bits.

        Undocumented: the guide doesn't cover it, so the in-place scaling of
        both buffers is inferred from the header.
        """
        argMax = buffer_argument(
            bufferMax, c_int16, buffertLth, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, c_int16, buffertLth, writable=True, name="bufferMin"
        )
        overflow = c_int16(0)
        self._ps4000aApplyResistanceScaling(
            handle, channel, range, argMax, argMin, buffertLth, byref(overflow)
        )
        return PS4000A_CHANNEL_FLAGS(overflow.value)

    def ps4000aGetTimebase(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ) -> tuple[int, int]:
        timeIntervalNanoseconds = c_int32(0)
        maxSamples = c_int32(0)
        self._ps4000aGetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNanoseconds.value, maxSamples.value

    def ps4000aGetTimebase2(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ) -> tuple[float, int]:
        timeIntervalNanoseconds = c_float(0)
        maxSamples = c_int32(0)
        self._ps4000aGetTimebase2(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNanoseconds),
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNanoseconds.value, maxSamples.value

    def ps4000aSetSigGenArbitrary(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: InputValues,
        sweepType: PS4000A_SWEEP_TYPE,
        operation: PS4000A_EXTRA_OPERATIONS,
        indexMode: PS4000A_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS4000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """``arbitraryWaveform`` holds the int16 arbitrary waveform samples.

        It is a sequence of ints or a buffer of int16 (e.g. a numpy array with
        ``dtype=np.int16``), which is passed without copying.
        """
        waveform, arbitraryWaveformSize = input_argument(
            arbitraryWaveform, c_int16, "arbitraryWaveform"
        )
        self._ps4000aSetSigGenArbitrary(
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

    def ps4000aSetSigGenArbitraryV2(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        arbitraryWaveform: InputValues,
        sweepType: PS4000A_SWEEP_TYPE,
        operation: PS4000A_EXTRA_OPERATIONS,
        indexMode: PS4000A_INDEX_MODE,
        shots: int,
        sweeps: int,
        triggerType: PS4000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """Like :meth:`ps4000aSetSigGenArbitrary`, with 64-bit phases, dwell
        count, shots and sweeps."""
        waveform, arbitraryWaveformSize = input_argument(
            arbitraryWaveform, c_int16, "arbitraryWaveform"
        )
        self._ps4000aSetSigGenArbitraryV2(
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

    def ps4000aSetSigGenBuiltIn(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS4000A_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS4000A_SWEEP_TYPE,
        operation: PS4000A_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS4000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps4000aSetSigGenBuiltIn(
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

    def ps4000aSetSigGenBuiltInV2(
        self,
        handle: c_int16,
        offsetVoltage: int,
        pkToPk: int,
        waveType: PS4000A_WAVE_TYPE,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS4000A_SWEEP_TYPE,
        operation: PS4000A_EXTRA_OPERATIONS,
        shots: int,
        sweeps: int,
        triggerType: PS4000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """Like :meth:`ps4000aSetSigGenBuiltIn`, with 64-bit shots and sweeps."""
        self._ps4000aSetSigGenBuiltInV2(
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

    def ps4000aSetSigGenPropertiesArbitrary(
        self,
        handle: c_int16,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PS4000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS4000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps4000aSetSigGenPropertiesArbitrary(
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

    def ps4000aSetSigGenPropertiesArbitraryV2(
        self,
        handle: c_int16,
        startDeltaPhase: int,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PS4000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS4000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """Like :meth:`ps4000aSetSigGenPropertiesArbitrary`, with 64-bit phases,
        dwell count, shots and sweeps."""
        self._ps4000aSetSigGenPropertiesArbitraryV2(
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

    def ps4000aSetSigGenPropertiesBuiltIn(
        self,
        handle: c_int16,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS4000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS4000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        self._ps4000aSetSigGenPropertiesBuiltIn(
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

    def ps4000aSetSigGenPropertiesBuiltInV2(
        self,
        handle: c_int16,
        startFrequency: float,
        stopFrequency: float,
        increment: float,
        dwellTime: float,
        sweepType: PS4000A_SWEEP_TYPE,
        shots: int,
        sweeps: int,
        triggerType: PS4000A_SIGGEN_TRIG_TYPE,
        triggerSource: PS4000A_SIGGEN_TRIG_SOURCE,
        extInThreshold: int,
    ) -> None:
        """Like :meth:`ps4000aSetSigGenPropertiesBuiltIn`, with 64-bit shots and
        sweeps."""
        self._ps4000aSetSigGenPropertiesBuiltInV2(
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

    def ps4000aSigGenFrequencyToPhase(
        self,
        handle: c_int16,
        frequency: float,
        indexMode: PS4000A_INDEX_MODE,
        bufferLength: int,
    ) -> int:
        phase = c_uint32(0)
        self._ps4000aSigGenFrequencyToPhase(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return phase.value

    def ps4000aSigGenFrequencyToPhaseV2(
        self,
        handle: c_int16,
        frequency: float,
        indexMode: PS4000A_INDEX_MODE,
        bufferLength: int,
    ) -> int:
        """Like :meth:`ps4000aSigGenFrequencyToPhase`, with a 64-bit phase."""
        phase = c_uint64(0)
        self._ps4000aSigGenFrequencyToPhaseV2(
            handle, frequency, indexMode, bufferLength, byref(phase)
        )
        return phase.value

    def ps4000aSigGenArbitraryMinMaxValues(
        self, handle: c_int16
    ) -> tuple[int, int, int, int]:
        minArbitraryWaveformValue = c_int16(0)
        maxArbitraryWaveformValue = c_int16(0)
        minArbitraryWaveformSize = c_uint32(0)
        maxArbitraryWaveformSize = c_uint32(0)
        self._ps4000aSigGenArbitraryMinMaxValues(
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

    def ps4000aSigGenSoftwareControl(self, handle: c_int16, state: int) -> None:
        self._ps4000aSigGenSoftwareControl(handle, state)

    def ps4000aSetEts(
        self,
        handle: c_int16,
        mode: PS4000A_ETS_MODE,
        etsCycles: int,
        etsInterleave: int,
    ) -> int:
        """Not implemented by the driver, returns PICO_ETS_NOT_SUPPORTED (guide p90)."""
        sampleTimePicoseconds = c_int32(0)
        self._ps4000aSetEts(
            handle, mode, etsCycles, etsInterleave, byref(sampleTimePicoseconds)
        )
        return sampleTimePicoseconds.value

    def ps4000aSetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PS4000A_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMilliseconds: int,
    ) -> None:
        self._ps4000aSetTriggerChannelProperties(
            handle,
            c_array(PS4000A_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            1 if auxOutputEnable else 0,
            autoTriggerMilliseconds,
        )

    def ps4000aSetTriggerChannelConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PS4000A_CONDITION],
        info: PS4000A_CONDITIONS_INFO,
    ) -> None:
        self._ps4000aSetTriggerChannelConditions(
            handle, c_array(PS4000A_CONDITION, conditions), len(conditions), info
        )

    def ps4000aSetTriggerChannelDirections(
        self, handle: c_int16, directions: Sequence[PS4000A_DIRECTION]
    ) -> None:
        self._ps4000aSetTriggerChannelDirections(
            handle, c_array(PS4000A_DIRECTION, directions), len(directions)
        )

    def ps4000aSetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PS4000A_CHANNEL,
        threshold: int,
        direction: PS4000A_THRESHOLD_DIRECTION,
        delay: int,
        autoTrigger_ms: int,
    ) -> None:
        assert 0 <= autoTrigger_ms <= 32767  # int16_t in C
        self._ps4000aSetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTrigger_ms,
        )

    def ps4000aSetTriggerDelay(self, handle: c_int16, delay: int) -> None:
        self._ps4000aSetTriggerDelay(handle, delay)

    def ps4000aSetPulseWidthQualifierProperties(
        self,
        handle: c_int16,
        direction: PS4000A_THRESHOLD_DIRECTION,
        lower: int,
        upper: int,
        type: PS4000A_PULSE_WIDTH_TYPE,
    ) -> None:
        self._ps4000aSetPulseWidthQualifierProperties(
            handle, direction, lower, upper, type
        )

    def ps4000aSetPulseWidthQualifierConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PS4000A_CONDITION],
        info: PS4000A_CONDITIONS_INFO,
    ) -> None:
        self._ps4000aSetPulseWidthQualifierConditions(
            handle, c_array(PS4000A_CONDITION, conditions), len(conditions), info
        )

    def ps4000aIsTriggerOrPulseWidthQualifierEnabled(
        self, handle: c_int16
    ) -> tuple[bool, bool]:
        triggerEnabled = c_int16(0)
        pulseWidthQualifierEnabled = c_int16(0)
        self._ps4000aIsTriggerOrPulseWidthQualifierEnabled(
            handle, byref(triggerEnabled), byref(pulseWidthQualifierEnabled)
        )
        return triggerEnabled.value != 0, pulseWidthQualifierEnabled.value != 0

    def ps4000aGetTriggerTimeOffset(self, handle: c_int16, segmentIndex: int) -> float:
        """Returns the trigger time offset of the segment in seconds."""
        timeUpper = c_uint32(0)
        timeLower = c_uint32(0)
        timeUnits = PS4000A_TIME_UNITS_T(0)
        self._ps4000aGetTriggerTimeOffset(
            handle, byref(timeUpper), byref(timeLower), byref(timeUnits), segmentIndex
        )
        return seconds(
            int64_from_halves(timeUpper.value, timeLower.value), timeUnits.value
        )

    def ps4000aGetTriggerTimeOffset64(
        self, handle: c_int16, segmentIndex: int
    ) -> float:
        """Returns the trigger time offset of the segment in seconds."""
        time = c_int64(0)
        timeUnits = PS4000A_TIME_UNITS_T(0)
        self._ps4000aGetTriggerTimeOffset64(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return seconds(time.value, timeUnits.value)

    def ps4000aGetValuesTriggerTimeOffsetBulk(
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
        timeUnits = (PS4000A_TIME_UNITS_T * nSegments)()
        self._ps4000aGetValuesTriggerTimeOffsetBulk(
            handle, timesUpper, timesLower, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return [
            seconds(int64_from_halves(upper, lower), units)
            for upper, lower, units in zip(
                timesUpper, timesLower, timeUnits, strict=True
            )
        ]

    def ps4000aGetValuesTriggerTimeOffsetBulk64(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> list[float]:
        """Returns the trigger time offsets of the segments in seconds.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nSegments = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * nSegments)()
        timeUnits = (PS4000A_TIME_UNITS_T * nSegments)()
        self._ps4000aGetValuesTriggerTimeOffsetBulk64(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return [
            seconds(time, units) for time, units in zip(times, timeUnits, strict=True)
        ]

    def ps4000aSetDataBuffers(
        self,
        handle: c_int16,
        channel: PS4000A_CHANNEL,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        bufferLth: int,
        segmentIndex: int,
        mode: PS4000A_RATIO_MODE,
    ) -> None:
        """Like :meth:`ps4000aSetDataBuffer`, with buffers for the maxima and minima.

        With ``bufferMax`` None, the driver writes non-aggregated values to
        ``bufferMin`` (guide p88).
        """
        argMax = buffer_argument(
            bufferMax, c_int16, bufferLth, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, c_int16, bufferLth, writable=True, name="bufferMin"
        )
        self._ps4000aSetDataBuffers(
            handle, channel, argMax, argMin, bufferLth, segmentIndex, mode
        )
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_buffer((handle.value, "data", channel, segmentIndex, mode), both)

    def ps4000aSetDataBuffer(
        self,
        handle: c_int16,
        channel: PS4000A_CHANNEL,
        buffer: DataBuffer,
        bufferLth: int,
        segmentIndex: int,
        mode: PS4000A_RATIO_MODE,
    ) -> None:
        """Set the buffer the driver writes the samples of ``channel`` to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int16 elements (e.g. ``np.empty(bufferLth, np.int16)``), or None. The
        wrapper keeps it from being freed or resized until it is replaced (per
        channel, segment and mode, also by :meth:`ps4000aSetDataBuffers`), set
        to None or the unit is closed. A raw address (int or ``c_void_p``) is
        passed unchecked and must be kept valid by the caller.
        """
        arg = buffer_argument(buffer, c_int16, bufferLth, writable=True, name="buffer")
        self._ps4000aSetDataBuffer(handle, channel, arg, bufferLth, segmentIndex, mode)
        self._keep_buffer((handle.value, "data", channel, segmentIndex, mode), arg)

    def ps4000aSetEtsTimeBuffer(
        self, handle: c_int16, buffer: DataBuffer, bufferLth: int
    ) -> None:
        """Set the buffer the driver writes the ETS sample times to.

        The driver does not implement ETS and returns PICO_ETS_NOT_SUPPORTED
        (guide p91).

        ``buffer`` is a writable, C-contiguous buffer of at least ``bufferLth``
        int64 elements, or None. The wrapper keeps it from being freed or
        resized until it is replaced, set to None or the unit is closed. A raw
        address (int or ``c_void_p``) is passed unchecked and must be kept valid
        by the caller.
        """
        arg = buffer_argument(buffer, c_int64, bufferLth, writable=True, name="buffer")
        self._ps4000aSetEtsTimeBuffer(handle, arg, bufferLth)
        self._keep_buffer((handle.value, "ets"), arg)

    def ps4000aSetEtsTimeBuffers(
        self,
        handle: c_int16,
        timeUpper: DataBuffer,
        timeLower: DataBuffer,
        bufferLth: int,
    ) -> None:
        """Like :meth:`ps4000aSetEtsTimeBuffer`, with uint32 buffers for the upper
        and lower 32 bits of the times.

        The wrapper keeps these separately from the buffer of
        :meth:`ps4000aSetEtsTimeBuffer`.
        """
        argUpper = buffer_argument(
            timeUpper, c_uint32, bufferLth, writable=True, name="timeUpper"
        )
        argLower = buffer_argument(
            timeLower, c_uint32, bufferLth, writable=True, name="timeLower"
        )
        self._ps4000aSetEtsTimeBuffers(handle, argUpper, argLower, bufferLth)
        both = None if argUpper is None and argLower is None else (argUpper, argLower)
        self._keep_buffer((handle.value, "ets32"), both)

    def ps4000aIsReady(self, handle: c_int16) -> bool:
        ready = c_int16(0)
        self._ps4000aIsReady(handle, byref(ready))
        return ready.value != 0

    def ps4000aRunBlock(
        self,
        handle: c_int16,
        noOfPreTriggerSamples: int,
        noOfPostTriggerSamples: int,
        timebase: int,
        segmentIndex: int,
        lpReady: Callable[[int, PICO_STATUS], None] | None,
    ) -> int:
        """``lpReady(handle, status)`` is called when the block is ready.

        Returns the time in ms the scope will spend collecting samples.
        """
        assert noOfPreTriggerSamples >= 0
        assert noOfPostTriggerSamples >= 0
        timeIndisposedMs = c_int32(0)
        cfunc = ps4000aBlockReady()  # NULL; ctypes rejects None here
        if lpReady is not None:
            callback = lpReady

            def cbwrapper(handle: int, status: int, _: c_void_p) -> None:
                callback(handle, PICO_STATUS(status))

            cfunc = ps4000aBlockReady(cbwrapper)
        self._with_callback(
            self._callback_key("ps4000aRunBlock", handle),
            cfunc,
            lambda: self._ps4000aRunBlock(
                handle,
                noOfPreTriggerSamples,
                noOfPostTriggerSamples,
                timebase,
                byref(timeIndisposedMs),
                segmentIndex,
                cfunc,
                None,
            ),
        )
        return timeIndisposedMs.value

    def ps4000aRunStreaming(
        self,
        handle: c_int16,
        sampleInterval: int,
        sampleIntervalTimeUnits: PS4000A_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        downSampleRatioMode: PS4000A_RATIO_MODE,
        overviewBufferSize: int,
    ) -> int:
        """Returns the actual sample interval chosen by the driver."""
        interval = c_uint32(sampleInterval)
        self._ps4000aRunStreaming(
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

    def ps4000aGetStreamingLatestValues(
        self,
        handle: c_int16,
        lpPs4000aReady: Callable[
            [int, int, int, PS4000A_CHANNEL_FLAGS, int, bool, bool], None
        ],
    ) -> PICO_STATUS:
        """``lpPs4000aReady(handle, noOfSamples, startIndex, overflow, triggerAt,
        triggered, autoStop)`` is called when new data has been copied.

        Returns PICO_OK, or PICO_BUSY if there is no new data yet (poll again).
        """
        callback = lpPs4000aReady

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
                PS4000A_CHANNEL_FLAGS(overflow),
                triggerAt,
                triggered != 0,
                autoStop != 0,
            )

        cfunc = ps4000aStreamingReady(cbwrapper)
        return self._with_callback(
            self._callback_key("ps4000aGetStreamingLatestValues", handle),
            cfunc,
            lambda: self._ps4000aGetStreamingLatestValues(handle, cfunc, None),
        )

    def ps4000aNoOfStreamingValues(self, handle: c_int16) -> int:
        noOfValues = c_uint32(0)
        self._ps4000aNoOfStreamingValues(handle, byref(noOfValues))
        return noOfValues.value

    def ps4000aGetMaxDownSampleRatio(
        self,
        handle: c_int16,
        noOfUnaggregatedSamples: int,
        downSampleRatioMode: PS4000A_RATIO_MODE,
        segmentIndex: int,
    ) -> int:
        maxDownSampleRatio = c_uint32(0)
        self._ps4000aGetMaxDownSampleRatio(
            handle,
            noOfUnaggregatedSamples,
            byref(maxDownSampleRatio),
            downSampleRatioMode,
            segmentIndex,
        )
        return maxDownSampleRatio.value

    def ps4000aGetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS4000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[int, PS4000A_CHANNEL_FLAGS]:
        """Returns the number of samples retrieved and the overflowed channels."""
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        self._ps4000aGetValues(
            handle,
            startIndex,
            byref(noOfSamples_),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return noOfSamples_.value, PS4000A_CHANNEL_FLAGS(overflow.value)

    def ps4000aGetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS4000A_RATIO_MODE,
        segmentIndex: int,
        lpDataReady: Callable[[int, PICO_STATUS, int, PS4000A_CHANNEL_FLAGS], None],
    ) -> None:
        """``lpDataReady(handle, status, noOfSamples, overflow)`` is called when
        the data has been retrieved."""
        # TODO: The guide (p53) names ps4000aStreamingReady as the callback type
        # (the header declares lpDataReady as void*), but pp23 and 122 name
        # ps4000aDataReady, which is what this method passes. Offer the streaming
        # callback too, or document this method as block-mode only.
        callback = lpDataReady

        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: c_void_p
        ) -> None:
            callback(
                handle,
                PICO_STATUS(status),
                noOfSamples,
                PS4000A_CHANNEL_FLAGS(overflow),
            )

        cfunc = ps4000aDataReady(cbwrapper)
        self._with_callback(
            self._callback_key("ps4000aGetValuesAsync", handle),
            cfunc,
            lambda: self._ps4000aGetValuesAsync(
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

    def ps4000aGetValuesBulk(
        self,
        handle: c_int16,
        noOfSamples: int,
        fromSegmentIndex: int,
        toSegmentIndex: int,
        downSampleRatio: int,
        downSampleRatioMode: PS4000A_RATIO_MODE,
    ) -> tuple[int, list[PS4000A_CHANNEL_FLAGS]]:
        """Returns the number of samples and the overflowed channels of each
        segment.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert noOfSamples > 0
        assert fromSegmentIndex <= toSegmentIndex
        noOfSamples_ = c_uint32(noOfSamples)
        nSegments = (toSegmentIndex - fromSegmentIndex) + 1
        overflow = (c_int16 * nSegments)()
        self._ps4000aGetValuesBulk(
            handle,
            byref(noOfSamples_),
            fromSegmentIndex,
            toSegmentIndex,
            downSampleRatio,
            downSampleRatioMode,
            overflow,
        )
        return noOfSamples_.value, [PS4000A_CHANNEL_FLAGS(f) for f in overflow]

    def ps4000aGetValuesOverlapped(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS4000A_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[c_uint32, c_int16]:
        """Set up a data retrieval that is performed during the next run.

        The driver writes the number of samples and the overflow bits after
        the capture, so the returned ctypes objects are only valid then (read
        their ``.value``). They are kept alive by the wrapper until replaced.
        """
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = c_int16(0)
        self._with_callback(
            self._callback_key("ps4000aGetValuesOverlapped", handle),
            (noOfSamples_, overflow),
            lambda: self._ps4000aGetValuesOverlapped(
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

    def ps4000aGetValuesOverlappedBulk(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PS4000A_RATIO_MODE,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[c_uint32, Array[c_int16]]:
        """Bulk variant of :meth:`ps4000aGetValuesOverlapped`.

        The returned ctypes objects (sample count and per-segment overflow
        bits) are filled in by the driver after the capture.
        """
        assert fromSegmentIndex <= toSegmentIndex
        noOfSamples_ = c_uint32(noOfSamples)
        overflow = (c_int16 * (toSegmentIndex - fromSegmentIndex + 1))()
        self._with_callback(
            self._callback_key("ps4000aGetValuesOverlappedBulk", handle),
            (noOfSamples_, overflow),
            lambda: self._ps4000aGetValuesOverlappedBulk(
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

    def ps4000aEnumerateUnits(self) -> list[str]:
        """Returns the serial numbers of the units found (not opened yet)."""
        count = c_int16(0)
        serials = create_string_buffer(4096)
        serialLth = c_int16(len(serials))
        self._ps4000aEnumerateUnits(byref(count), serials, byref(serialLth))
        units = [s for s in serials.value.decode("utf-8").split(",") if s]
        assert len(units) == count.value
        return units

    def ps4000aGetChannelInformation(
        self,
        handle: c_int16,
        info: PS4000A_CHANNEL_INFO,
        probe: int,
        channels: PS4000A_CHANNEL,
    ) -> list[PICO_CONNECT_PROBE_RANGE | int]:
        """Returns the ranges of the kind ``info`` available on ``channels``.

        Values without a ``PICO_CONNECT_PROBE_RANGE`` member (e.g. with the
        ``PS4000A_RESISTANCE_ADCV`` flag) are returned as ints.

        ``probe`` is not used and must be 0 (guide p36).
        """
        # The first call (NULL array) only queries the number of ranges.
        length = c_int32(0)
        self._ps4000aGetChannelInformation(
            handle, info, probe, None, byref(length), channels
        )
        capacity = length.value
        if capacity <= 0:
            return []
        ranges = (c_int32 * capacity)()
        self._ps4000aGetChannelInformation(
            handle, info, probe, ranges, byref(length), channels
        )
        n = min(length.value, capacity)
        known = PICO_CONNECT_PROBE_RANGE._value2member_map_
        return [PICO_CONNECT_PROBE_RANGE(r) if r in known else r for r in ranges[:n]]

    def ps4000aConnectDetect(
        self, handle: c_int16, sensor: Sequence[PS4000A_CONNECT_DETECT]
    ) -> list[PS4000A_CONNECT_DETECT]:
        """Returns ``sensor`` with the detected state of each channel.

        Undocumented: the guide doesn't cover it, so the array is assumed to be
        in/out (channels in, states out), as the header suggests.
        """
        arr = c_array(PS4000A_CONNECT_DETECT, sensor)
        self._ps4000aConnectDetect(handle, arr, len(sensor))
        return PS4000A_CONNECT_DETECT.from_c_array(arr) if arr is not None else []

    def ps4000aSetProbeInteractionCallback(
        self,
        handle: c_int16,
        callback: Callable[
            [int, PICO_STATUS, list[PS4000A_USER_PROBE_INTERACTIONS]], None
        ]
        | None,
    ) -> None:
        """``callback(handle, status, probes)`` is called on probe changes.

        ``probes`` are copies, valid beyond the callback. Register it right after
        opening the unit (and handling its power status), before any
        :meth:`ps4000aSetChannel` (guide pp95, 129).
        """
        cfunc = ps4000aProbeInteractions()  # NULL; ctypes rejects None here
        if callback is not None:
            user = callback

            def cbwrapper(handle: int, status: int, probes: Any, nProbes: int) -> None:
                # TODO: A value without an enum member (e.g. a new probe in
                # probeName) makes from_c raise; ctypes prints and drops the
                # exception, so the event never reaches the user callback. Same
                # in ps6000a: convert unknown enum values to int.
                copies = (
                    [
                        PS4000A_USER_PROBE_INTERACTIONS.from_c(probes[i])
                        for i in range(nProbes)
                    ]
                    if probes
                    else []
                )
                user(handle, PICO_STATUS(status), copies)

            cfunc = ps4000aProbeInteractions(cbwrapper)
        self._with_callback(
            self._callback_key("ps4000aSetProbeInteractionCallback", handle),
            cfunc,
            lambda: self._ps4000aSetProbeInteractionCallback(handle, cfunc),
        )

    def ps4000aCalibrateProbe(self, handle: c_int16, channel: PS4000A_CHANNEL) -> bool:
        """Returns ``checkCalibrationRequired``; undocumented, inferred from the
        header."""
        checkCalibrationRequired = c_int16(0)
        self._ps4000aCalibrateProbe(handle, channel, byref(checkCalibrationRequired))
        return checkCalibrationRequired.value != 0

    def ps4000aSetProbeLedColour(
        self, handle: c_int16, settings: Sequence[PS4000A_PROBE_CHANNEL_LED_SETTING]
    ) -> None:
        self._ps4000aSetProbeLedColour(
            handle, c_array(PS4000A_PROBE_CHANNEL_LED_SETTING, settings), len(settings)
        )

    def ps4000aRegisterProbeLedColour(
        self,
        handle: c_int16,
        probe: PICO_CONNECT_PROBE,
        settings: Sequence[PS4000A_PROBE_CHANNEL_LED_SETTING],
    ) -> None:
        self._ps4000aRegisterProbeLedColour(
            handle,
            probe,
            c_array(PS4000A_PROBE_CHANNEL_LED_SETTING, settings),
            len(settings),
        )

    def ps4000aSetProbeLedDefaults(self, handle: c_int16, enabled: bool) -> None:
        self._ps4000aSetProbeLedDefaults(handle, 1 if enabled else 0)

    def ps4000aMaximumValue(self, handle: c_int16) -> int:
        value = c_int16(0)
        self._ps4000aMaximumValue(handle, byref(value))
        return value.value

    def ps4000aMinimumValue(self, handle: c_int16) -> int:
        value = c_int16(0)
        self._ps4000aMinimumValue(handle, byref(value))
        return value.value

    def ps4000aGetAnalogueOffset(
        self,
        handle: c_int16,
        range: PICO_CONNECT_PROBE_RANGE | int,
        coupling: PS4000A_COUPLING,
    ) -> tuple[float, float]:
        """Returns the maximum and the minimum analogue offset (in C order)."""
        maximumOffset = c_float(0)
        minimumOffset = c_float(0)
        self._ps4000aGetAnalogueOffset(
            handle, range, coupling, byref(maximumOffset), byref(minimumOffset)
        )
        return maximumOffset.value, minimumOffset.value

    def ps4000aGetMaxSegments(self, handle: c_int16) -> int:
        maxSegments = c_uint32(0)
        self._ps4000aGetMaxSegments(handle, byref(maxSegments))
        return maxSegments.value

    def ps4000aChangePowerSource(
        self, handle: c_int16, powerState: PICO_STATUS
    ) -> PICO_STATUS:
        """Returns the status, which tells the power source if not PICO_OK."""
        return self._ps4000aChangePowerSource(handle, powerState)

    def ps4000aCurrentPowerSource(self, handle: c_int16) -> PICO_STATUS:
        """Returns the power source: ``PICO_POWER_SUPPLY_CONNECTED`` or
        ``..._NOT_CONNECTED`` on a 4444, PICO_OK or
        ``PICO_USB3_0_DEVICE_NON_USB3_0_PORT`` on the others (guide p32)."""
        return self._ps4000aCurrentPowerSource(handle)

    def ps4000aStop(self, handle: c_int16) -> None:
        self._ps4000aStop(handle)

    def ps4000aPingUnit(self, handle: c_int16) -> PICO_STATUS:
        """Returns the status, which tells the power source if not PICO_OK."""
        return self._ps4000aPingUnit(handle)

    def ps4000aSetNoOfCaptures(self, handle: c_int16, nCaptures: int) -> None:
        assert nCaptures > 0
        self._ps4000aSetNoOfCaptures(handle, nCaptures)

    def ps4000aGetNoOfCaptures(self, handle: c_int16) -> int:
        nCaptures = c_uint32(0)
        self._ps4000aGetNoOfCaptures(handle, byref(nCaptures))
        return nCaptures.value

    def ps4000aGetNoOfProcessedCaptures(self, handle: c_int16) -> int:
        nProcessedCaptures = c_uint32(0)
        self._ps4000aGetNoOfProcessedCaptures(handle, byref(nProcessedCaptures))
        return nProcessedCaptures.value

    def ps4000aDeviceMetaData(
        self,
        handle: c_int16,
        settings: str | None,
        type: PS4000A_META_TYPE,
        operation: PS4000A_META_OPERATION,
        format: PS4000A_META_FORMAT,
    ) -> str:
        """Read (``settings`` None) or write (``settings``) the device meta data;
        returns the settings read, or an empty string when writing.

        Undocumented: the guide doesn't cover it, so the direction of
        ``settings`` (by ``operation``) and the length semantics are inferred
        from the header.
        """
        if operation == PS4000A_META_OPERATION.PS4000A_MO_WRITE:
            assert settings is not None
            data = create_string_buffer(settings.encode())
            nSettingsLength = c_int32(len(data) - 1)  # without the NUL
            self._ps4000aDeviceMetaData(
                handle, data, byref(nSettingsLength), type, operation, format
            )
            return ""
        size = 65536
        while True:
            buf = create_string_buffer(size)
            nSettingsLength = c_int32(size)
            try:
                self._ps4000aDeviceMetaData(
                    handle, buf, byref(nSettingsLength), type, operation, format
                )
            except StatusException as e:
                tooSmall = e.status == PICO_STATUS.PICO_STRING_BUFFER_TO_SMALL
                if not tooSmall or size >= _MAX_STRING_SIZE:
                    raise
            else:
                if nSettingsLength.value <= size:
                    return buf.value.decode("utf-8")
            # Too small: retry with the reported length, or twice the size.
            size = max(nSettingsLength.value + 1, 2 * size)

    def ps4000aGetString(self, handle: c_int16, stringValue: PICO_STRING_VALUE) -> str:
        """Undocumented: the guide doesn't cover it, so the length semantics are
        inferred from the header."""
        size = 4096
        while True:
            string = create_string_buffer(size)
            stringLength = c_int32(size)
            try:
                self._ps4000aGetString(handle, stringValue, string, byref(stringLength))
            except StatusException as e:
                tooSmall = e.status == PICO_STATUS.PICO_STRING_BUFFER_TO_SMALL
                if not tooSmall or size >= _MAX_STRING_SIZE:
                    raise
            else:
                if stringLength.value <= size:
                    return string.value.decode("utf-8")
            # Too small: retry with the reported length, or twice the size.
            size = max(stringLength.value + 1, 2 * size)

    def ps4000aGetCommonModeOverflow(self, handle: c_int16) -> PS4000A_CHANNEL_FLAGS:
        """Returns the channels whose common-mode voltage range was exceeded."""
        overflow = c_uint16(0)
        self._ps4000aGetCommonModeOverflow(handle, byref(overflow))
        return PS4000A_CHANNEL_FLAGS(overflow.value)

    def ps4000aSetFrequencyCounter(
        self,
        handle: c_int16,
        channel: PS4000A_CHANNEL,
        enabled: bool,
        range: PS4000A_FREQUENCY_COUNTER_RANGE,
        thresholdMajor: int,
        thresholdMinor: int,
    ) -> None:
        self._ps4000aSetFrequencyCounter(
            handle,
            channel,
            1 if enabled else 0,
            range,
            thresholdMajor,
            thresholdMinor,
        )

    def ps4000aQueryOutputEdgeDetect(self, handle: c_int16) -> bool:
        state = c_int16(0)
        self._ps4000aQueryOutputEdgeDetect(handle, byref(state))
        return state.value != 0

    def ps4000aSetOutputEdgeDetect(self, handle: c_int16, state: bool) -> None:
        self._ps4000aSetOutputEdgeDetect(handle, 1 if state else 0)

    def ps4000aSetDeviceResolution(
        self, handle: c_int16, resolution: PS4000A_DEVICE_RESOLUTION
    ) -> PICO_STATUS:
        """Returns the status, which tells the power source if not PICO_OK.

        Call :meth:`ps4000aSetChannel` afterwards (guide p89).
        """
        return self._ps4000aSetDeviceResolution(handle, resolution)

    def ps4000aGetDeviceResolution(self, handle: c_int16) -> PS4000A_DEVICE_RESOLUTION:
        resolution = PS4000A_DEVICE_RESOLUTION_T(0)
        self._ps4000aGetDeviceResolution(handle, byref(resolution))
        return PS4000A_DEVICE_RESOLUTION(resolution.value)

    def ps4000aSetCalibrationPins(
        self,
        handle: c_int16,
        pinStates: PS4000A_PIN_STATES,
        waveType: PS4000A_WAVE_TYPE,
        frequency: float,
        amplitude: int,
        offset: int,
    ) -> None:
        """PicoScope 4444 only. ``frequency`` in Hz, ``amplitude`` and ``offset``
        in µV.

        ``offset`` may be negative (guide p84) although the header declares it
        ``uint32_t``; it is passed as two's complement.
        """
        self._ps4000aSetCalibrationPins(
            handle, pinStates, waveType, frequency, amplitude, offset & 0xFFFFFFFF
        )

    def ps4000aNearestSampleIntervalStateless(
        self,
        handle: c_int16,
        enabledChannelOrPortFlags: PS4000A_CHANNEL_FLAGS,
        timeIntervalRequested: float,
        resolution: PS4000A_DEVICE_RESOLUTION,
        useEts: bool,
    ) -> tuple[int, float]:
        """``timeIntervalRequested`` and the returned interval are in seconds."""
        timebase = c_uint32(0)
        timeIntervalAvailable = c_double(0)
        self._ps4000aNearestSampleIntervalStateless(
            handle,
            enabledChannelOrPortFlags,
            timeIntervalRequested,
            resolution,
            1 if useEts else 0,
            byref(timebase),
            byref(timeIntervalAvailable),
        )
        return timebase.value, timeIntervalAvailable.value

    def ps4000aGetMinimumTimebaseStateless(
        self,
        handle: c_int16,
        enabledChannelOrPortFlags: PS4000A_CHANNEL_FLAGS,
        resolution: PS4000A_DEVICE_RESOLUTION,
    ) -> tuple[int, float]:
        """Returns the minimum timebase and its interval in seconds."""
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        self._ps4000aGetMinimumTimebaseStateless(
            handle,
            enabledChannelOrPortFlags,
            byref(timebase),
            byref(timeInterval),
            resolution,
        )
        return timebase.value, timeInterval.value

    def ps4000aCheckForUpdate(
        self, handle: c_int16
    ) -> tuple[list[PICO_FIRMWARE_INFO], bool]:
        """Returns the firmware infos, and whether updates are required."""
        # The first call (NULL array) only queries the number of infos.
        nFirmwareInfos = c_int16(0)
        updatesRequired = c_uint16(0)
        self._ps4000aCheckForUpdate(
            handle, None, byref(nFirmwareInfos), byref(updatesRequired)
        )
        capacity = max(0, nFirmwareInfos.value)
        firmwareInfos = (PICO_FIRMWARE_INFO.c_type * capacity)()
        if capacity > 0:
            self._ps4000aCheckForUpdate(
                handle, firmwareInfos, byref(nFirmwareInfos), byref(updatesRequired)
            )
        count = max(0, min(nFirmwareInfos.value, capacity))
        return (
            PICO_FIRMWARE_INFO.from_c_array(firmwareInfos[:count]),
            updatesRequired.value != 0,
        )

    def ps4000aStartFirmwareUpdate(
        self, handle: c_int16, progress: Callable[[int, int], None] | None
    ) -> PICO_STATUS:
        """``progress(handle, progressPercent)`` reports the update progress.

        Returns the status, PICO_FIRMWARE_UP_TO_DATE once the firmware has been
        updated or did not need an update.
        """
        cfunc = PicoUpdateFirmwareProgress()  # NULL; ctypes rejects None here
        if progress is not None:
            callback = progress

            def cbwrapper(handle: int, progressPercent: int) -> None:
                callback(handle, progressPercent)

            cfunc = PicoUpdateFirmwareProgress(cbwrapper)
        return self._with_callback(
            self._callback_key("ps4000aStartFirmwareUpdate", handle),
            cfunc,
            lambda: self._ps4000aStartFirmwareUpdate(handle, cfunc),
            accepted=lambda status: (
                status in (PICO_STATUS.PICO_OK, PICO_STATUS.PICO_FIRMWARE_UP_TO_DATE)
            ),
        )

    def ps4000aSetAccelerometerProbeAxis(
        self,
        handle: c_int16,
        channel: PS4000A_CHANNEL,
        axis: PS4000A_ACCELEROMETER_AXIS,
    ) -> None:
        self._ps4000aSetAccelerometerProbeAxis(handle, channel, axis)

    def ps4000aSetAccelerometerCalibrationMode(
        self, handle: c_int16, channel: PS4000A_CHANNEL, enableCalibration: bool
    ) -> None:
        self._ps4000aSetAccelerometerCalibrationMode(
            handle, channel, 1 if enableCalibration else 0
        )

    def ps4000aFetchAccelerometerCalibrationStatistics(
        self, handle: c_int16, channel: PS4000A_CHANNEL
    ) -> tuple[float, float, float, int]:
        """Returns the mean, minimum, maximum and the number of samples."""
        mean = c_float(0)
        min = c_float(0)
        max = c_float(0)
        count = c_uint16(0)
        self._ps4000aFetchAccelerometerCalibrationStatistics(
            handle, channel, byref(mean), byref(min), byref(max), byref(count)
        )
        return mean.value, min.value, max.value, count.value

    def ps4000aGetMaximumProbeValue(
        self,
        handle: c_int16,
        channel: PS4000A_CHANNEL,
        range: PICO_CONNECT_PROBE_RANGE | int,
    ) -> int:
        """Returns the maximum sample value of the probe on ``channel`` at ``range``.

        Needs a probe interaction callback, see
        :meth:`ps4000aSetProbeInteractionCallback`.
        """
        value = c_int16(0)
        self._ps4000aGetMaximumProbeValue(handle, channel, range, byref(value))
        return value.value


@final
class PicoScope4000aDevice(PicoScopeDeviceBase[PicoScope4000aWrapper]):
    """An opened ps4000a unit; the functions of :class:`PicoScope4000aWrapper` with its handle.

    See :class:`~pycosdk.PicoScopeDeviceBase`.
    """

    _wrapper_type = PicoScope4000aWrapper

    @classmethod
    def ps4000aOpenUnitWithResolution(
        cls, serial: str | None, resolution: PS4000A_DEVICE_RESOLUTION
    ) -> tuple[Self, PICO_STATUS]:
        """Like :meth:`PicoScope4000aWrapper.ps4000aOpenUnitWithResolution`, returning a device instead of the handle."""
        handle, status = cls.shared_wrapper().ps4000aOpenUnitWithResolution(
            serial, resolution
        )
        return cls(handle), status

    @classmethod
    def ps4000aOpenUnit(cls, serial: str | None) -> tuple[Self, PICO_STATUS]:
        """Like :meth:`PicoScope4000aWrapper.ps4000aOpenUnit`, returning a device instead of the handle."""
        handle, status = cls.shared_wrapper().ps4000aOpenUnit(serial)
        return cls(handle), status

    @classmethod
    def ps4000aOpenUnitProgress(cls) -> tuple[Self | None, int, bool, PICO_STATUS]:
        """Like :meth:`PicoScope4000aWrapper.ps4000aOpenUnitProgress`, with a device instead of the handle once opened."""
        handle, progressPercent, complete, status = (
            cls.shared_wrapper().ps4000aOpenUnitProgress()
        )
        return cls(handle) if complete else None, progressPercent, complete, status

    ps4000aOpenUnitAsyncWithResolution = wrapper_function(
        PicoScope4000aWrapper.ps4000aOpenUnitAsyncWithResolution
    )
    ps4000aOpenUnitAsync = wrapper_function(PicoScope4000aWrapper.ps4000aOpenUnitAsync)
    ps4000aEnumerateUnits = wrapper_function(
        PicoScope4000aWrapper.ps4000aEnumerateUnits
    )

    ps4000aGetUnitInfo = handle_method(PicoScope4000aWrapper.ps4000aGetUnitInfo)
    ps4000aGetAccessoryInfo = handle_method(
        PicoScope4000aWrapper.ps4000aGetAccessoryInfo
    )
    ps4000aFlashLed = handle_method(PicoScope4000aWrapper.ps4000aFlashLed)
    ps4000aSetChannelLed = handle_method(PicoScope4000aWrapper.ps4000aSetChannelLed)
    ps4000aIsLedFlashing = handle_method(PicoScope4000aWrapper.ps4000aIsLedFlashing)
    ps4000aCloseUnit = handle_method(
        PicoScope4000aWrapper.ps4000aCloseUnit, closes=True
    )
    ps4000aMemorySegments = handle_method(PicoScope4000aWrapper.ps4000aMemorySegments)
    ps4000aSetChannel = handle_method(PicoScope4000aWrapper.ps4000aSetChannel)
    ps4000aSetBandwidthFilter = handle_method(
        PicoScope4000aWrapper.ps4000aSetBandwidthFilter
    )
    ps4000aApplyResistanceScaling = handle_method(
        PicoScope4000aWrapper.ps4000aApplyResistanceScaling
    )
    ps4000aGetTimebase = handle_method(PicoScope4000aWrapper.ps4000aGetTimebase)
    ps4000aGetTimebase2 = handle_method(PicoScope4000aWrapper.ps4000aGetTimebase2)
    ps4000aSetSigGenArbitrary = handle_method(
        PicoScope4000aWrapper.ps4000aSetSigGenArbitrary
    )
    ps4000aSetSigGenArbitraryV2 = handle_method(
        PicoScope4000aWrapper.ps4000aSetSigGenArbitraryV2
    )
    ps4000aSetSigGenBuiltIn = handle_method(
        PicoScope4000aWrapper.ps4000aSetSigGenBuiltIn
    )
    ps4000aSetSigGenBuiltInV2 = handle_method(
        PicoScope4000aWrapper.ps4000aSetSigGenBuiltInV2
    )
    ps4000aSetSigGenPropertiesArbitrary = handle_method(
        PicoScope4000aWrapper.ps4000aSetSigGenPropertiesArbitrary
    )
    ps4000aSetSigGenPropertiesArbitraryV2 = handle_method(
        PicoScope4000aWrapper.ps4000aSetSigGenPropertiesArbitraryV2
    )
    ps4000aSetSigGenPropertiesBuiltIn = handle_method(
        PicoScope4000aWrapper.ps4000aSetSigGenPropertiesBuiltIn
    )
    ps4000aSetSigGenPropertiesBuiltInV2 = handle_method(
        PicoScope4000aWrapper.ps4000aSetSigGenPropertiesBuiltInV2
    )
    ps4000aSigGenFrequencyToPhase = handle_method(
        PicoScope4000aWrapper.ps4000aSigGenFrequencyToPhase
    )
    ps4000aSigGenFrequencyToPhaseV2 = handle_method(
        PicoScope4000aWrapper.ps4000aSigGenFrequencyToPhaseV2
    )
    ps4000aSigGenArbitraryMinMaxValues = handle_method(
        PicoScope4000aWrapper.ps4000aSigGenArbitraryMinMaxValues
    )
    ps4000aSigGenSoftwareControl = handle_method(
        PicoScope4000aWrapper.ps4000aSigGenSoftwareControl
    )
    ps4000aSetEts = handle_method(PicoScope4000aWrapper.ps4000aSetEts)
    ps4000aSetTriggerChannelProperties = handle_method(
        PicoScope4000aWrapper.ps4000aSetTriggerChannelProperties
    )
    ps4000aSetTriggerChannelConditions = handle_method(
        PicoScope4000aWrapper.ps4000aSetTriggerChannelConditions
    )
    ps4000aSetTriggerChannelDirections = handle_method(
        PicoScope4000aWrapper.ps4000aSetTriggerChannelDirections
    )
    ps4000aSetSimpleTrigger = handle_method(
        PicoScope4000aWrapper.ps4000aSetSimpleTrigger
    )
    ps4000aSetTriggerDelay = handle_method(PicoScope4000aWrapper.ps4000aSetTriggerDelay)
    ps4000aSetPulseWidthQualifierProperties = handle_method(
        PicoScope4000aWrapper.ps4000aSetPulseWidthQualifierProperties
    )
    ps4000aSetPulseWidthQualifierConditions = handle_method(
        PicoScope4000aWrapper.ps4000aSetPulseWidthQualifierConditions
    )
    ps4000aIsTriggerOrPulseWidthQualifierEnabled = handle_method(
        PicoScope4000aWrapper.ps4000aIsTriggerOrPulseWidthQualifierEnabled
    )
    ps4000aGetTriggerTimeOffset = handle_method(
        PicoScope4000aWrapper.ps4000aGetTriggerTimeOffset
    )
    ps4000aGetTriggerTimeOffset64 = handle_method(
        PicoScope4000aWrapper.ps4000aGetTriggerTimeOffset64
    )
    ps4000aGetValuesTriggerTimeOffsetBulk = handle_method(
        PicoScope4000aWrapper.ps4000aGetValuesTriggerTimeOffsetBulk
    )
    ps4000aGetValuesTriggerTimeOffsetBulk64 = handle_method(
        PicoScope4000aWrapper.ps4000aGetValuesTriggerTimeOffsetBulk64
    )
    ps4000aSetDataBuffers = handle_method(PicoScope4000aWrapper.ps4000aSetDataBuffers)
    ps4000aSetDataBuffer = handle_method(PicoScope4000aWrapper.ps4000aSetDataBuffer)
    ps4000aSetEtsTimeBuffer = handle_method(
        PicoScope4000aWrapper.ps4000aSetEtsTimeBuffer
    )
    ps4000aSetEtsTimeBuffers = handle_method(
        PicoScope4000aWrapper.ps4000aSetEtsTimeBuffers
    )
    ps4000aIsReady = handle_method(PicoScope4000aWrapper.ps4000aIsReady)
    ps4000aRunBlock = handle_method(PicoScope4000aWrapper.ps4000aRunBlock)
    ps4000aRunStreaming = handle_method(PicoScope4000aWrapper.ps4000aRunStreaming)
    ps4000aGetStreamingLatestValues = handle_method(
        PicoScope4000aWrapper.ps4000aGetStreamingLatestValues
    )
    ps4000aNoOfStreamingValues = handle_method(
        PicoScope4000aWrapper.ps4000aNoOfStreamingValues
    )
    ps4000aGetMaxDownSampleRatio = handle_method(
        PicoScope4000aWrapper.ps4000aGetMaxDownSampleRatio
    )
    ps4000aGetValues = handle_method(PicoScope4000aWrapper.ps4000aGetValues)
    ps4000aGetValuesAsync = handle_method(PicoScope4000aWrapper.ps4000aGetValuesAsync)
    ps4000aGetValuesBulk = handle_method(PicoScope4000aWrapper.ps4000aGetValuesBulk)
    ps4000aGetValuesOverlapped = handle_method(
        PicoScope4000aWrapper.ps4000aGetValuesOverlapped
    )
    ps4000aGetValuesOverlappedBulk = handle_method(
        PicoScope4000aWrapper.ps4000aGetValuesOverlappedBulk
    )
    ps4000aGetChannelInformation = handle_method(
        PicoScope4000aWrapper.ps4000aGetChannelInformation
    )
    ps4000aConnectDetect = handle_method(PicoScope4000aWrapper.ps4000aConnectDetect)
    ps4000aSetProbeInteractionCallback = handle_method(
        PicoScope4000aWrapper.ps4000aSetProbeInteractionCallback
    )
    ps4000aCalibrateProbe = handle_method(PicoScope4000aWrapper.ps4000aCalibrateProbe)
    ps4000aSetProbeLedColour = handle_method(
        PicoScope4000aWrapper.ps4000aSetProbeLedColour
    )
    ps4000aRegisterProbeLedColour = handle_method(
        PicoScope4000aWrapper.ps4000aRegisterProbeLedColour
    )
    ps4000aSetProbeLedDefaults = handle_method(
        PicoScope4000aWrapper.ps4000aSetProbeLedDefaults
    )
    ps4000aMaximumValue = handle_method(PicoScope4000aWrapper.ps4000aMaximumValue)
    ps4000aMinimumValue = handle_method(PicoScope4000aWrapper.ps4000aMinimumValue)
    ps4000aGetAnalogueOffset = handle_method(
        PicoScope4000aWrapper.ps4000aGetAnalogueOffset
    )
    ps4000aGetMaxSegments = handle_method(PicoScope4000aWrapper.ps4000aGetMaxSegments)
    ps4000aChangePowerSource = handle_method(
        PicoScope4000aWrapper.ps4000aChangePowerSource
    )
    ps4000aCurrentPowerSource = handle_method(
        PicoScope4000aWrapper.ps4000aCurrentPowerSource
    )
    ps4000aStop = handle_method(PicoScope4000aWrapper.ps4000aStop)
    ps4000aPingUnit = handle_method(PicoScope4000aWrapper.ps4000aPingUnit)
    ps4000aSetNoOfCaptures = handle_method(PicoScope4000aWrapper.ps4000aSetNoOfCaptures)
    ps4000aGetNoOfCaptures = handle_method(PicoScope4000aWrapper.ps4000aGetNoOfCaptures)
    ps4000aGetNoOfProcessedCaptures = handle_method(
        PicoScope4000aWrapper.ps4000aGetNoOfProcessedCaptures
    )
    ps4000aDeviceMetaData = handle_method(PicoScope4000aWrapper.ps4000aDeviceMetaData)
    ps4000aGetString = handle_method(PicoScope4000aWrapper.ps4000aGetString)
    ps4000aGetCommonModeOverflow = handle_method(
        PicoScope4000aWrapper.ps4000aGetCommonModeOverflow
    )
    ps4000aSetFrequencyCounter = handle_method(
        PicoScope4000aWrapper.ps4000aSetFrequencyCounter
    )
    ps4000aQueryOutputEdgeDetect = handle_method(
        PicoScope4000aWrapper.ps4000aQueryOutputEdgeDetect
    )
    ps4000aSetOutputEdgeDetect = handle_method(
        PicoScope4000aWrapper.ps4000aSetOutputEdgeDetect
    )
    ps4000aSetDeviceResolution = handle_method(
        PicoScope4000aWrapper.ps4000aSetDeviceResolution
    )
    ps4000aGetDeviceResolution = handle_method(
        PicoScope4000aWrapper.ps4000aGetDeviceResolution
    )
    ps4000aSetCalibrationPins = handle_method(
        PicoScope4000aWrapper.ps4000aSetCalibrationPins
    )
    ps4000aNearestSampleIntervalStateless = handle_method(
        PicoScope4000aWrapper.ps4000aNearestSampleIntervalStateless
    )
    ps4000aGetMinimumTimebaseStateless = handle_method(
        PicoScope4000aWrapper.ps4000aGetMinimumTimebaseStateless
    )
    ps4000aCheckForUpdate = handle_method(PicoScope4000aWrapper.ps4000aCheckForUpdate)
    ps4000aStartFirmwareUpdate = handle_method(
        PicoScope4000aWrapper.ps4000aStartFirmwareUpdate
    )
    ps4000aSetAccelerometerProbeAxis = handle_method(
        PicoScope4000aWrapper.ps4000aSetAccelerometerProbeAxis
    )
    ps4000aSetAccelerometerCalibrationMode = handle_method(
        PicoScope4000aWrapper.ps4000aSetAccelerometerCalibrationMode
    )
    ps4000aFetchAccelerometerCalibrationStatistics = handle_method(
        PicoScope4000aWrapper.ps4000aFetchAccelerometerCalibrationStatistics
    )
    ps4000aGetMaximumProbeValue = handle_method(
        PicoScope4000aWrapper.ps4000aGetMaximumProbeValue
    )


__all__ = (
    "PS4000A_ACCELEROMETER_AXIS",
    "PS4000A_AWG_DAC_FREQUENCY",
    "PS4000A_AWG_PHASE_ACCUMULATOR",
    "PS4000A_BANDWIDTH_LIMITER",
    "PS4000A_BANDWIDTH_LIMITER_FLAGS",
    "PS4000A_CHANNEL",
    "PS4000A_CHANNEL_BUFFER_INDEX",
    "PS4000A_CHANNEL_FLAGS",
    "PS4000A_CHANNEL_INFO",
    "PS4000A_CHANNEL_LED",
    "PS4000A_CHANNEL_LED_SETTING",
    "PS4000A_CONDITION",
    "PS4000A_CONDITIONS_INFO",
    "PS4000A_CONNECT_DETECT",
    "PS4000A_COUPLING",
    "PS4000A_DEVICE_RESOLUTION",
    "PS4000A_DIRECTION",
    "PS4000A_ETS_MODE",
    "PS4000A_EXTRA_OPERATIONS",
    "PS4000A_EXT_MAX_VALUE",
    "PS4000A_EXT_MIN_VALUE",
    "PS4000A_FREQUENCY_COUNTER_RANGE",
    "PS4000A_GAUSSIAN_MAX_FREQUENCY",
    "PS4000A_HALF_SINE_MAX_FREQUENCY",
    "PS4000A_INDEX_MODE",
    "PS4000A_MAX_ANALOGUE_OFFSET_10V_50V",
    "PS4000A_MAX_ANALOGUE_OFFSET_500MV_2V",
    "PS4000A_MAX_ANALOGUE_OFFSET_50MV_200MV",
    "PS4000A_MAX_ANALOGUE_OFFSET_5V_20V",
    "PS4000A_MAX_DELAY_COUNT",
    "PS4000A_MAX_PULSE_WIDTH_QUALIFIER_COUNT",
    "PS4000A_MAX_SIG_GEN_BUFFER_SIZE",
    "PS4000A_MAX_SWEEPS_SHOTS",
    "PS4000A_META_FORMAT",
    "PS4000A_META_OPERATION",
    "PS4000A_META_TYPE",
    "PS4000A_MIN_ANALOGUE_OFFSET_10V_50V",
    "PS4000A_MIN_ANALOGUE_OFFSET_500MV_2V",
    "PS4000A_MIN_ANALOGUE_OFFSET_50MV_200MV",
    "PS4000A_MIN_ANALOGUE_OFFSET_5V_20V",
    "PS4000A_MIN_DWELL_COUNT",
    "PS4000A_MIN_FREQUENCY",
    "PS4000A_MIN_SIG_GEN_BUFFER_SIZE",
    "PS4000A_PIN_STATES",
    "PS4000A_PROBE_CHANNEL_LED_SETTING",
    "PS4000A_PROBE_LED_COLOUR",
    "PS4000A_PROBE_LED_POSITION",
    "PS4000A_PULSE_WIDTH_TYPE",
    "PS4000A_RAMP_MAX_FREQUENCY",
    "PS4000A_RANGE",
    "PS4000A_RATIO_MODE",
    "PS4000A_RESISTANCE_RANGE",
    "PS4000A_SENSOR_STATE",
    "PS4000A_SIGGEN_TRIG_SOURCE",
    "PS4000A_SIGGEN_TRIG_TYPE",
    "PS4000A_SINC_MAX_FREQUENCY",
    "PS4000A_SINE_MAX_FREQUENCY",
    "PS4000A_SQUARE_MAX_FREQUENCY",
    "PS4000A_SWEEP_TYPE",
    "PS4000A_THRESHOLD_DIRECTION",
    "PS4000A_THRESHOLD_MODE",
    "PS4000A_TIME_UNITS",
    "PS4000A_TRIANGLE_MAX_FREQUENCY",
    "PS4000A_TRIGGER_CHANNEL_PROPERTIES",
    "PS4000A_TRIGGER_STATE",
    "PS4000A_USER_PROBE_INTERACTIONS",
    "PS4000A_WAVE_TYPE",
    "PicoScope4000aWrapper",
    "PicoScope4000aDevice",
    "ps4000aBlockReady",
    "ps4000aDataReady",
    "ps4000aProbeInteractions",
    "ps4000aStreamingReady",
)
