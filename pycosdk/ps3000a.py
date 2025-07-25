from ctypes import (
    CFUNCTYPE,
    POINTER,
    LibraryLoader,
    Structure,
    c_char_p,
    c_float,
    c_int,
    c_int16,
    c_int32,
    c_int8,
    c_uint16,
    c_uint32,
    c_double,
    c_uint64,
    c_int64,
    c_void_p,
    byref,
    create_string_buffer,
)
from ctypes.util import find_library
from typing import Callable
from enum import IntEnum
import sys

from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T

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

MIN_SIG_GEN_FREQ = 0.0
MAX_SIG_GEN_FREQ = 20000000.0

PS3207B_MAX_SIG_GEN_BUFFER_SIZE = 32768
PS3206B_MAX_SIG_GEN_BUFFER_SIZE = 16384
MAX_SIG_GEN_BUFFER_SIZE = 8192
MIN_SIG_GEN_BUFFER_SIZE = 1
MIN_DWELL_COUNT = 3
MAX_SWEEPS_SHOTS = (1 << 30) - 1

MAX_ANALOGUE_OFFSET_50MV_200MV = 0.250
MIN_ANALOGUE_OFFSET_50MV_200MV = -0.250
MAX_ANALOGUE_OFFSET_500MV_2V = 2.500
MIN_ANALOGUE_OFFSET_500MV_2V = -2.500
MAX_ANALOGUE_OFFSET_5V_20V = 20.0
MIN_ANALOGUE_OFFSET_5V_20V = -20.0

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
    PS3000A_ES_OFF = 1
    PS3000A_WHITENOISE = 2
    PS3000A_PRBS = 3


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


class PS3000A_DIGITAL_CHANNEL_DIRECTIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel", PS3000A_DIGITAL_CHANNEL_T),
        ("direction", PS3000A_DIGITAL_DIRECTION_T),
    ]


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


class PS3000A_SCALING_FACTORS_VALUES(Structure):
    _pack_ = 1
    _fields_ = [
        ("channelOrPort", PS3000A_CHANNEL_T),
        ("range", PS3000A_RANGE_T),
        ("offset", c_int16),
        ("scalingFactor", c_double),
    ]


ps3000aBlockReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps3000aDataReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p)

ps3000aStreamingReady = CFUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)


class PicoScope3000aWrapper:
    def __init__(self, library_path: str | None = None):
        if library_path is None:
            library_path = find_library("ps6000a")
        if library_path is None:
            raise Exception("Library not found")

        if sys.platform == "win32":
            from ctypes import WinDLL

            loadercls = WinDLL
        else:
            from ctypes import CDLL

            loadercls = CDLL
        loader = LibraryLoader(loadercls)
        self.lib = loader[library_path]

        self._ps3000aOpenUnit = getattr(self.lib, "ps3000aOpenUnit")
        self._ps3000aOpenUnit.resType = PICO_STATUS_T
        self._ps3000aOpenUnit.argTypes = [POINTER(c_int16), c_char_p]

        self._ps3000aGetUnitInfo = getattr(self.lib, "ps3000aGetUnitInfo")
        self._ps3000aGetUnitInfo.resType = PICO_STATUS_T
        self._ps3000aGetUnitInfo.argTypes = [
            c_int16,
            c_char_p,
            c_int16,
            c_void_p,
            PICO_INFO_T,
        ]

        self._ps3000aCloseUnit = getattr(self.lib, "ps3000aCloseUnit")
        self._ps3000aCloseUnit.resType = PICO_STATUS_T
        self._ps3000aCloseUnit.argTypes = [c_int16]

        self._ps3000aMemorySegments = getattr(self.lib, "ps3000aMemorySegments")
        self._ps3000aMemorySegments.resType = PICO_STATUS_T
        self._ps3000aMemorySegments.argTypes = [c_int16, c_uint32, POINTER(c_uint32)]

        self._ps3000aSetChannel = getattr(self.lib, "ps3000aSetChannel")
        self._ps3000aSetChannel.resType = PICO_STATUS_T
        self._ps3000aSetChannel.argTypes = [
            c_int16,
            PS3000A_CHANNEL_T,
            c_int16,
            PS3000A_COUPLING_T,
            PS3000A_RANGE_T,
            c_float,
        ]

        self._ps3000aSetDigitalPort = getattr(self.lib, "ps3000aSetDigitalPort")
        self._ps3000aSetDigitalPort.resType = PICO_STATUS_T
        self._ps3000aSetDigitalPort.argTypes = [
            c_int16,
            PS3000A_DIGITAL_PORT_T,
            c_int16,
            c_int16,
        ]

        self._ps3000aSetBandwidthFilter = getattr(self.lib, "ps3000aSetBandwidthFilter")
        self._ps3000aSetBandwidthFilter.resType = PICO_STATUS_T
        self._ps3000aSetBandwidthFilter.argTypes = [
            c_int16,
            PS3000A_CHANNEL_T,
            PS3000A_BANDWIDTH_LIMITER_T,
        ]

        self._ps3000aSetNoOfCaptures = getattr(self.lib, "ps3000aSetNoOfCaptures")
        self._ps3000aSetNoOfCaptures.resType = PICO_STATUS_T
        self._ps3000aSetNoOfCaptures.argTypes = [c_int16, c_uint32]

        self._ps3000aGetTimebase2 = getattr(self.lib, "ps3000aGetTimebase2")
        self._ps3000aGetTimebase2.resType = PICO_STATUS_T
        self._ps3000aGetTimebase2.argTypes = [
            c_int16,
            c_uint32,
            c_int32,
            POINTER(c_float),
            c_int16,
            POINTER(c_uint32),
            c_uint32,
        ]

        self._ps3000aSetSimpleTrigger = getattr(self.lib, "ps3000aSetSimpleTrigger")
        self._ps3000aSetSimpleTrigger.resType = PICO_STATUS_T
        self._ps3000aSetSimpleTrigger.argTypes = [
            c_int16,
            c_int16,
            PS3000A_CHANNEL_T,
            c_int16,
            PS3000A_THRESHOLD_DIRECTION_T,
            c_uint32,
            c_int16,
        ]

        self._ps3000aSetTriggerDelay = getattr(self.lib, "ps3000aSetTriggerDelay")
        self._ps3000aSetTriggerDelay.resType = PICO_STATUS_T
        self._ps3000aSetTriggerDelay.argTypes = [c_int16, c_uint32]

        self._ps3000aGetNoOfCaptures = getattr(self.lib, "ps3000aGetNoOfCaptures")
        self._ps3000aGetNoOfCaptures.resType = PICO_STATUS_T
        self._ps3000aGetNoOfCaptures.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps3000aGetNoOfProcessedCaptures = getattr(
            self.lib, "ps3000aGetNoOfProcessedCaptures"
        )
        self._ps3000aGetNoOfProcessedCaptures.resType = PICO_STATUS_T
        self._ps3000aGetNoOfProcessedCaptures.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps3000aSetDataBuffer = getattr(self.lib, "ps3000aSetDataBuffer")
        self._ps3000aSetDataBuffer.resType = PICO_STATUS_T
        self._ps3000aSetDataBuffer.argTypes = [
            c_int16,
            c_int32,
            POINTER(c_int16),
            c_int32,
            c_uint32,
            PS3000A_RATIO_MODE_T,
        ]

        self._ps3000aSetDataBuffers = getattr(self.lib, "ps3000aSetDataBuffers")
        self._ps3000aSetDataBuffers.resType = PICO_STATUS_T
        self._ps3000aSetDataBuffers.argTypes = [
            c_int16,
            c_int32,
            POINTER(c_int16),
            POINTER(c_int16),
            c_int32,
            c_uint32,
            PS3000A_RATIO_MODE_T,
        ]

        self._ps3000aIsReady = getattr(self.lib, "ps3000aIsReady")
        self._ps3000aIsReady.resType = PICO_STATUS_T
        self._ps3000aIsReady.argTypes = [c_int16, POINTER(c_int16)]

        self._ps3000aRunBlock = getattr(self.lib, "ps3000aRunBlock")
        self._ps3000aRunBlock.resType = PICO_STATUS_T
        self._ps3000aRunBlock.argTypes = [
            c_int16,
            c_int32,
            c_int32,
            c_uint32,
            c_int16,
            POINTER(c_int32),
            c_uint32,
            ps3000aBlockReady,
            c_void_p,
        ]

        self._ps3000aGetValues = getattr(self.lib, "ps3000aGetValues")
        self._ps3000aGetValues.resType = PICO_STATUS_T
        self._ps3000aGetValues.argTypes = [
            c_int16,
            c_uint32,
            POINTER(c_uint32),
            c_uint32,
            PS3000A_RATIO_MODE_T,
            c_uint32,
            POINTER(c_int16),
        ]

        self._ps3000aGetValuesBulk = getattr(self.lib, "ps3000aGetValuesBulk")
        self._ps3000aGetValuesBulk.resType = PICO_STATUS_T
        self._ps3000aGetValuesBulk.argTypes = [
            c_int16,
            POINTER(c_uint32),
            c_uint32,
            c_uint32,
            c_uint32,
            PS3000A_RATIO_MODE_T,
            POINTER(c_int16),
        ]

        self._ps3000aStop = getattr(self.lib, "ps3000aStop")
        self._ps3000aStop.resType = PICO_STATUS_T
        self._ps3000aStop.argTypes = [c_int16]

        self._ps3000aHoldOff = getattr(self.lib, "ps3000aHoldOff")
        self._ps3000aHoldOff.resType = PICO_STATUS_T
        self._ps3000aHoldOff.argTypes = [c_int16, c_uint64, PS3000A_HOLDOFF_TYPE_T]

        self._ps3000aGetChannelInformation = getattr(
            self.lib, "ps3000aGetChannelInformation"
        )
        self._ps3000aGetChannelInformation.resType = PICO_STATUS_T
        self._ps3000aGetChannelInformation.argTypes = [
            c_int16,
            PS3000A_CHANNEL_INFO_T,
            c_int32,
            POINTER(c_int32),
            POINTER(c_int32),
            c_int32,
        ]

        self._ps3000aEnumerateUnits = getattr(self.lib, "ps3000aEnumerateUnits")
        self._ps3000aEnumerateUnits.resType = PICO_STATUS_T
        self._ps3000aEnumerateUnits.argTypes = [
            POINTER(c_int16),
            c_char_p,
            POINTER(c_int16),
        ]

        self._ps3000aPingUnit = getattr(self.lib, "ps3000aPingUnit")
        self._ps3000aPingUnit.resType = PICO_STATUS_T
        self._ps3000aPingUnit.argTypes = [c_int16]

        self._ps3000aMaximumValue = getattr(self.lib, "ps3000aMaximumValue")
        self._ps3000aMaximumValue.resType = PICO_STATUS_T
        self._ps3000aMaximumValue.argTypes = [c_int16, POINTER(c_int16)]

        self._ps3000aMinimumValue = getattr(self.lib, "ps3000aMinimumValue")
        self._ps3000aMinimumValue.resType = PICO_STATUS_T
        self._ps3000aMinimumValue.argTypes = [c_int16, POINTER(c_int16)]

        self._ps3000aGetAnalogueOffset = getattr(self.lib, "ps3000aGetAnalogueOffset")
        self._ps3000aGetAnalogueOffset.resType = PICO_STATUS_T
        self._ps3000aGetAnalogueOffset.argTypes = [
            c_int16,
            PS3000A_RANGE_T,
            PS3000A_COUPLING_T,
            POINTER(c_float),
            POINTER(c_float),
        ]

        self._ps3000aGetMaxSegments = getattr(self.lib, "ps3000aGetMaxSegments")
        self._ps3000aGetMaxSegments.resType = PICO_STATUS_T
        self._ps3000aGetMaxSegments.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps3000aChangePowerSource = getattr(self.lib, "ps3000aChangePowerSource")
        self._ps3000aChangePowerSource.resType = PICO_STATUS_T
        self._ps3000aChangePowerSource.argTypes = [c_int16, PICO_STATUS_T]

        self._ps3000aCurrentPowerSource = getattr(self.lib, "ps3000aCurrentPowerSource")
        self._ps3000aCurrentPowerSource.resType = PICO_STATUS_T
        self._ps3000aCurrentPowerSource.argTypes = [c_int16]

    def ps3000aOpenUnit(self, serial: str | None):
        handle = c_int16(0)
        ser = c_char_p(serial.encode()) if serial is not None else 0
        return (
            PICO_STATUS(self._ps3000aOpenUnit(byref(handle), ser)),
            handle,
        )

    def ps3000aCloseUnit(self, handle: c_int16):
        return PICO_STATUS(self._ps3000aCloseUnit(handle))

    def ps3000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._ps3000aGetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return PICO_STATUS(status), infostr

    def ps3000aMemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_uint32(0)
        return (
            PICO_STATUS(
                self._ps3000aMemorySegments(handle, nsegments, byref(maxSamples))
            ),
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
        return PICO_STATUS(
            self._ps3000aSetChannel(
                handle,
                channel,
                1 if enabled else 0,
                coupling,
                range,
                c_float(analog_offset),
            )
        )

    def ps3000aSetBandwidthFilter(
        self,
        handle: c_int16,
        channel: PS3000A_CHANNEL,
        bandwidth: PS3000A_BANDWIDTH_LIMITER,
    ):
        return PICO_STATUS(self._ps3000aSetBandwidthFilter(handle, channel, bandwidth))

    def ps3000aSetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return PICO_STATUS(self._ps3000aSetNoOfCaptures(handle, ncaptures))

    def ps3000aGetTimebase2(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ):
        timeIntervalNS = c_float(0)
        maxSamples = c_int32(0)
        return (
            PICO_STATUS(
                self._ps3000aGetTimebase2(
                    handle,
                    timebase,
                    noSamples,
                    byref(timeIntervalNS),
                    0,  # oversample not used
                    byref(maxSamples),
                    segmentIndex,
                )
            ),
            timeIntervalNS.value,
            maxSamples.value,
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
        return PICO_STATUS(
            self._ps3000aSetSimpleTrigger(
                handle,
                1 if enable else 0,
                source,
                threshold,
                direction,
                delay,
                autoTriggerUS,
            )
        )

    def ps3000aSetTriggerDelay(self, handle: c_int16, delay: int):
        return PICO_STATUS(self._ps3000aSetTriggerDelay(handle, delay))

    def ps3000aGetNoOfCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            PICO_STATUS(self._ps3000aGetNoOfCaptures(handle, byref(captures))),
            captures.value,
        )

    def ps3000aGetNoOfProcessedCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            PICO_STATUS(self._ps3000aGetNoOfProcessedCaptures(handle, byref(captures))),
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
        return PICO_STATUS(
            self._ps3000aSetDataBuffer(
                handle, channel, buffer, bufferLth, segmentIndex, mode
            )
        )

    def ps3000aIsReady(self, handle: c_int16):
        ready = c_int16(0)
        return PICO_STATUS(self._ps3000aIsReady(handle, byref(ready))), ready.value == 1

    def ps3000aRunBlock(
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
        timeInd = c_uint32(0)
        lpReady = None
        if callback is not None:

            def cbwrapper(handle: c_int16, status: PICO_STATUS_T, _: c_void_p):
                callback(handle, PICO_STATUS(status))

            lpReady = ps3000aBlockReady(cbwrapper)
        return (
            PICO_STATUS(
                self._ps3000aRunBlock(
                    handle,
                    preSamples,
                    postSamples,
                    timebase,
                    0,
                    byref(timeInd),
                    segment,
                    lpReady,
                    None,
                )
            ),
            timeInd.value,
        )

    def ps3000aGetMaxSegments(self, handle: c_int16):
        value = c_uint32(0)
        return (
            PICO_STATUS(self._ps3000aGetMaxSegments(handle, byref(value))),
            value.value,
        )

    def ps3000aMinimumValue(self, handle: c_int16):
        value = c_int16(0)
        return PICO_STATUS(self._ps3000aMinimumValue(handle, byref(value))), value.value

    def ps3000aMaximumValue(self, handle: c_int16):
        value = c_int16(0)
        return PICO_STATUS(self._ps3000aMaximumValue(handle, byref(value))), value.value

    def ps3000aGetAnalogueOffset(
        self, handle: c_int16, range: PS3000A_RANGE, coupling: PS3000A_COUPLING
    ):
        minv = c_float(0)
        maxv = c_float(0)
        return (
            PICO_STATUS(
                self._ps3000aGetAnalogueOffset(
                    handle, range, coupling, byref(minv), byref(maxv)
                )
            ),
            minv.value,
            maxv.value,
        )

    def ps3000aChangePowerSource(self, handle: c_int16, source: PICO_STATUS):
        return PICO_STATUS(self._ps3000aChangePowerSource(handle, source))

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
        nosamples_ = c_uint64(nosamples)
        nsegments = (toSegment - fromSegment) + 1
        overflow = (c_int16 * nsegments)(0)
        return (
            PICO_STATUS(
                self._ps3000aGetValuesBulk(
                    handle,
                    byref(nosamples_),
                    fromSegment,
                    toSegment,
                    downsampleRatio,
                    downsampleMode,
                    overflow,
                )
            ),
            nosamples_.value,
            [int(f) for f in overflow],
        )
