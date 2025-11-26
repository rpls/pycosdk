import sys
from ctypes import (
    CFUNCTYPE,
    POINTER,
    LibraryLoader,
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
from ctypes.util import find_library
from enum import IntEnum
from typing import Callable, final

from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T

PS6000_MAX_OVERSAMPLE_8BIT = 256

PS6000_MAX_VALUE = 32512
PS6000_MIN_VALUE = -32512

MAX_PULSE_WIDTH_QUALIFIER_COUNT = 16777215

MAX_SIG_GEN_BUFFER_SIZE = 16384
PS640X_C_D_MAX_SIG_GEN_BUFFER_SIZE = 65536

MIN_SIG_GEN_BUFFER_SIZE = 1
MIN_DWELL_COUNT = 3
MAX_SWEEPS_SHOTS = (1 << 30) - 1

MAX_WAVEFORMS_PER_SECOND = 1000000

MAX_ANALOGUE_OFFSET_50MV_200MV = 0.500
MIN_ANALOGUE_OFFSET_50MV_200MV = -0.500
MAX_ANALOGUE_OFFSET_500MV_2V = 2.500
MIN_ANALOGUE_OFFSET_500MV_2V = -2.500
MAX_ANALOGUE_OFFSET_5V_20V = 20.0
MIN_ANALOGUE_OFFSET_5V_20V = -20.0

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


ps6000BlockReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps6000StreamingReady = CFUNCTYPE(
    None, c_int16, c_uint32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)

ps6000DataReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p)


class PicoScope6000Wrapper:
    def __init__(self, library_path: str | None = None):
        if library_path is None:
            library_path = find_library("ps6000")
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

        self._ps6000OpenUnit = getattr(self.lib, "ps6000OpenUnit")
        self._ps6000OpenUnit.resType = PICO_STATUS_T
        self._ps6000OpenUnit.argTypes = [POINTER(c_int16), c_char_p]

        self._ps6000OpenUnitAsync = getattr(self.lib, "ps6000OpenUnitAsync")
        self._ps6000OpenUnitAsync.resType = PICO_STATUS_T
        self._ps6000OpenUnitAsync.argTypes = [POINTER(c_int16), c_char_p]

        self._ps6000OpenUnitProgress = getattr(self.lib, "ps6000OpenUnitProgress")
        self._ps6000OpenUnitProgress.resType = PICO_STATUS_T
        self._ps6000OpenUnitProgress.argTypes = [
            POINTER(c_int16),
            POINTER(c_int16),
            POINTER(c_int16),
        ]

        self._ps6000GetUnitInfo = getattr(self.lib, "ps6000GetUnitInfo")
        self._ps6000GetUnitInfo.resType = PICO_STATUS_T
        self._ps6000GetUnitInfo.argTypes = [
            c_int16,
            c_char_p,
            c_int16,
            POINTER(c_int16),
            PICO_INFO_T,
        ]

        self._ps6000FlashLed = getattr(self.lib, "ps6000FlashLed")
        self._ps6000FlashLed.resType = PICO_STATUS_T
        self._ps6000FlashLed.argTypes = [c_int16, c_int16]

        self._ps6000CloseUnit = getattr(self.lib, "ps6000CloseUnit")
        self._ps6000CloseUnit.resType = PICO_STATUS_T
        self._ps6000CloseUnit.argTypes = [
            c_int16,
        ]

        self._ps6000MemorySegments = getattr(self.lib, "ps6000MemorySegments")
        self._ps6000MemorySegments.resType = PICO_STATUS_T
        self._ps6000MemorySegments.argTypes = [c_int16, c_uint32, POINTER(c_uint32)]

        self._ps6000SetChannel = getattr(self.lib, "ps6000SetChannel")
        self._ps6000SetChannel.resType = PICO_STATUS_T
        self._ps6000SetChannel.argTypes = [
            c_int16,
            PS6000_CHANNEL_T,
            c_int16,
            PS6000_COUPLING_T,
            PS6000_RANGE_T,
            c_float,
            PS6000_BANDWIDTH_LIMITER_T,
        ]

        self._ps6000GetTimebase = getattr(self.lib, "ps6000GetTimebase")
        self._ps6000GetTimebase.resType = PICO_STATUS_T
        self._ps6000GetTimebase.argTypes = [
            c_int16,
            c_uint32,
            c_uint32,
            POINTER(c_int32),
            c_int16,
            POINTER(c_uint32),
            c_uint32,
        ]

        self._ps6000GetTimebase2 = getattr(self.lib, "ps6000GetTimebase2")
        self._ps6000GetTimebase2.resType = PICO_STATUS_T
        self._ps6000GetTimebase2.argTypes = [
            c_int16,
            c_uint32,
            c_uint32,
            POINTER(c_float),
            c_int16,
            POINTER(c_uint32),
            c_uint32,
        ]

        self._ps6000SetSigGenArbitrary = getattr(self.lib, "ps6000SetSigGenArbitrary")
        self._ps6000SetSigGenArbitrary.resType = PICO_STATUS_T
        self._ps6000SetSigGenArbitrary.argTypes = [
            c_int16,
            c_int32,
            c_uint32,
            c_uint32,
            c_uint32,
            c_uint32,
            c_uint32,
            c_void_p,
            c_int32,
            c_int32,
            c_int32,
            c_int32,
            c_uint32,
            c_uint32,
            c_int32,
            c_int32,
            c_int16,
        ]

        self._ps6000SetSigGenBuiltIn = getattr(self.lib, "ps6000SetSigGenBuiltIn")
        self._ps6000SetSigGenBuiltIn.resType = PICO_STATUS_T
        self._ps6000SetSigGenBuiltIn.argTypes = [
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
        ]

        self._ps6000SetSigGenBuiltInV2 = getattr(self.lib, "ps6000SetSigGenBuiltInV2")
        self._ps6000SetSigGenBuiltInV2.resType = PICO_STATUS_T
        self._ps6000SetSigGenBuiltInV2.argTypes = [
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
        ]

        self._ps6000SetSigGenPropertiesArbitrary = getattr(
            self.lib, "ps6000SetSigGenPropertiesArbitrary"
        )
        self._ps6000SetSigGenPropertiesArbitrary.resType = PICO_STATUS_T
        self._ps6000SetSigGenPropertiesArbitrary.argTypes = [
            c_int16,
            c_int32,
            c_uint32,
            c_uint32,
            c_uint32,
            c_uint32,
            c_uint32,
            c_int32,
            c_uint32,
            c_uint32,
            c_int32,
            c_int32,
            c_int16,
        ]

        self._ps6000SetSigGenPropertiesBuiltIn = getattr(
            self.lib, "ps6000SetSigGenPropertiesBuiltIn"
        )
        self._ps6000SetSigGenPropertiesBuiltIn.resType = PICO_STATUS_T
        self._ps6000SetSigGenPropertiesBuiltIn.argTypes = [
            c_int16,
            c_int32,
            c_uint32,
            c_double,
            c_double,
            c_double,
            c_double,
            c_int32,
            c_uint32,
            c_uint32,
            c_int32,
            c_int32,
            c_int16,
        ]

        self._ps6000SigGenFrequencyToPhase = getattr(
            self.lib, "ps6000SigGenFrequencyToPhase"
        )
        self._ps6000SigGenFrequencyToPhase.resType = PICO_STATUS_T
        self._ps6000SigGenFrequencyToPhase.argTypes = [
            c_int16,
            c_double,
            PS6000_INDEX_MODE_T,
            c_uint32,
            POINTER(c_uint32),
        ]

        self._ps6000SigGenArbitraryMinMaxValues = getattr(
            self.lib, "ps6000SigGenArbitraryMinMaxValues"
        )
        self._ps6000SigGenArbitraryMinMaxValues.resType = PICO_STATUS_T
        self._ps6000SigGenArbitraryMinMaxValues.argTypes = [
            c_int16,
            POINTER(c_int16),
            POINTER(c_int16),
            POINTER(c_uint32),
            POINTER(c_uint32),
        ]

        self._ps6000SigGenSoftwareControl = getattr(
            self.lib, "ps6000SigGenSoftwareControl"
        )
        self._ps6000SigGenSoftwareControl.resType = PICO_STATUS_T
        self._ps6000SigGenSoftwareControl.argTypes = [c_int16, c_int16]

        self._ps6000SetSimpleTrigger = getattr(self.lib, "ps6000SetSimpleTrigger")
        self._ps6000SetSimpleTrigger.resType = PICO_STATUS_T
        self._ps6000SetSimpleTrigger.argTypes = [
            c_int16,
            c_int16,
            PS6000_CHANNEL_T,
            c_int16,
            PS6000_THRESHOLD_DIRECTION_T,
            c_uint32,
            c_int16,
        ]

        self._ps6000SetEts = getattr(self.lib, "ps6000SetEts")
        self._ps6000SetEts.resType = PICO_STATUS_T
        self._ps6000SetEts.argTypes = [
            c_int16,
            PS6000_ETS_MODE_T,
            c_int16,
            c_int16,
            POINTER(c_int32),
        ]

        self._ps6000SetTriggerChannelProperties = getattr(
            self.lib, "ps6000SetTriggerChannelProperties"
        )
        self._ps6000SetTriggerChannelProperties.resType = PICO_STATUS_T
        self._ps6000SetTriggerChannelProperties.argTypes = [
            c_int16,
            POINTER(PS6000_TRIGGER_CHANNEL_PROPERTIES),
            c_int16,
            c_int16,
            c_uint32,
        ]

        self._ps6000SetTriggerChannelConditions = getattr(
            self.lib, "ps6000SetTriggerChannelConditions"
        )
        self._ps6000SetTriggerChannelConditions.resType = PICO_STATUS_T
        self._ps6000SetTriggerChannelConditions.argTypes = [
            c_int16,
            POINTER(PS6000_TRIGGER_CONDITIONS),
            c_int16,
        ]

        self._ps6000SetTriggerChannelDirections = getattr(
            self.lib, "ps6000SetTriggerChannelDirections"
        )
        self._ps6000SetTriggerChannelDirections.resType = PICO_STATUS_T
        self._ps6000SetTriggerChannelDirections.argTypes = [
            c_int16,
            PS6000_THRESHOLD_DIRECTION_T,
            PS6000_THRESHOLD_DIRECTION_T,
            PS6000_THRESHOLD_DIRECTION_T,
            PS6000_THRESHOLD_DIRECTION_T,
            PS6000_THRESHOLD_DIRECTION_T,
            PS6000_THRESHOLD_DIRECTION_T,
        ]

        self._ps6000SetTriggerDelay = getattr(self.lib, "ps6000SetTriggerDelay")
        self._ps6000SetTriggerDelay.resType = PICO_STATUS_T
        self._ps6000SetTriggerDelay.argTypes = [c_int16, c_uint32]

        self._ps6000SetPulseWidthQualifier = getattr(
            self.lib, "ps6000SetPulseWidthQualifier"
        )
        self._ps6000SetPulseWidthQualifier.resType = PICO_STATUS_T
        self._ps6000SetPulseWidthQualifier.argTypes = [
            c_int16,
            POINTER(PS6000_PWQ_CONDITIONS),
            c_int16,
            PS6000_THRESHOLD_DIRECTION_T,
            c_uint32,
            c_uint32,
            PS6000_PULSE_WIDTH_TYPE_T,
        ]

        self._ps6000IsTriggerOrPulseWidthQualifierEnabled = getattr(
            self.lib, "ps6000IsTriggerOrPulseWidthQualifierEnabled"
        )
        self._ps6000IsTriggerOrPulseWidthQualifierEnabled.resType = PICO_STATUS_T
        self._ps6000IsTriggerOrPulseWidthQualifierEnabled.argTypes = [
            c_int16,
            POINTER(c_int16),
            POINTER(c_int16),
        ]

        self._ps6000GetTriggerTimeOffset = getattr(
            self.lib, "ps6000GetTriggerTimeOffset"
        )
        self._ps6000GetTriggerTimeOffset.resType = PICO_STATUS_T
        self._ps6000GetTriggerTimeOffset.argTypes = [
            c_int16,
            POINTER(c_uint32),
            POINTER(c_uint32),
            POINTER(PS6000_TIME_UNITS_T),
            c_uint32,
        ]

        self._ps6000GetTriggerTimeOffset64 = getattr(
            self.lib, "ps6000GetTriggerTimeOffset64"
        )
        self._ps6000GetTriggerTimeOffset64.resType = PICO_STATUS_T
        self._ps6000GetTriggerTimeOffset64.argTypes = [
            c_int16,
            POINTER(c_int64),
            POINTER(PS6000_TIME_UNITS_T),
            c_uint32,
        ]

        self._ps6000GetValuesTriggerTimeOffsetBulk = getattr(
            self.lib, "ps6000GetValuesTriggerTimeOffsetBulk"
        )
        self._ps6000GetValuesTriggerTimeOffsetBulk.resType = PICO_STATUS_T
        self._ps6000GetValuesTriggerTimeOffsetBulk.argTypes = [
            c_int16,
            POINTER(c_uint32),
            POINTER(c_uint32),
            POINTER(PS6000_TIME_UNITS_T),
            c_uint32,
            c_uint32,
        ]

        self._ps6000GetValuesTriggerTimeOffsetBulk64 = getattr(
            self.lib, "ps6000GetValuesTriggerTimeOffsetBulk64"
        )
        self._ps6000GetValuesTriggerTimeOffsetBulk64.resType = PICO_STATUS_T
        self._ps6000GetValuesTriggerTimeOffsetBulk64.argTypes = [
            c_int16,
            POINTER(c_int64),
            POINTER(PS6000_TIME_UNITS_T),
            c_uint32,
            c_uint32,
        ]

        self._ps6000SetDataBuffers = getattr(self.lib, "ps6000SetDataBuffers")
        self._ps6000SetDataBuffers.resType = PICO_STATUS_T
        self._ps6000SetDataBuffers.argTypes = [
            c_int16,
            PS6000_CHANNEL_T,
            POINTER(c_int16),
            POINTER(c_int16),
            c_uint32,
            PS6000_RATIO_MODE_T,
        ]

        self._ps6000SetDataBuffer = getattr(self.lib, "ps6000SetDataBuffer")
        self._ps6000SetDataBuffer.resType = PICO_STATUS_T
        self._ps6000SetDataBuffer.argTypes = [
            c_int16,
            PS6000_CHANNEL_T,
            POINTER(c_int16),
            c_uint32,
            PS6000_RATIO_MODE_T,
        ]

        self._ps6000SetDataBufferBulk = getattr(self.lib, "ps6000SetDataBufferBulk")
        self._ps6000SetDataBufferBulk.resType = PICO_STATUS_T
        self._ps6000SetDataBufferBulk.argTypes = [
            c_int16,
            PS6000_CHANNEL_T,
            POINTER(c_int16),
            c_uint32,
            c_uint32,
            PS6000_RATIO_MODE_T,
        ]

        self._ps6000SetDataBuffersBulk = getattr(self.lib, "ps6000SetDataBuffersBulk")
        self._ps6000SetDataBuffersBulk.resType = PICO_STATUS_T
        self._ps6000SetDataBuffersBulk.argTypes = [
            c_int16,
            PS6000_CHANNEL_T,
            POINTER(c_int16),
            POINTER(c_int16),
            c_uint32,
            c_uint32,
            PS6000_RATIO_MODE_T,
        ]

        self._ps6000SetEtsTimeBuffer = getattr(self.lib, "ps6000SetEtsTimeBuffer")
        self._ps6000SetEtsTimeBuffer.resType = PICO_STATUS_T
        self._ps6000SetEtsTimeBuffer.argTypes = [c_int16, POINTER(c_int64), c_uint32]

        self._ps6000SetEtsTimeBuffers = getattr(self.lib, "ps6000SetEtsTimeBuffers")
        self._ps6000SetEtsTimeBuffers.resType = PICO_STATUS_T
        self._ps6000SetEtsTimeBuffers.argTypes = [
            c_int16,
            POINTER(c_uint32),
            POINTER(c_uint32),
            c_uint32,
        ]

        self._ps6000RunBlock = getattr(self.lib, "ps6000RunBlock")
        self._ps6000RunBlock.resType = PICO_STATUS_T
        self._ps6000RunBlock.argTypes = [
            c_int16,
            c_uint32,
            c_uint32,
            c_uint32,
            c_int16,
            POINTER(c_int32),
            c_uint32,
            ps6000BlockReady,
            c_void_p,
        ]

        self._ps6000IsReady = getattr(self.lib, "ps6000IsReady")
        self._ps6000IsReady.resType = PICO_STATUS_T
        self._ps6000IsReady.argTypes = [c_int16, POINTER(c_int16)]

        self._ps6000RunStreaming = getattr(self.lib, "ps6000RunStreaming")
        self._ps6000RunStreaming.resType = PICO_STATUS_T
        self._ps6000RunStreaming.argTypes = [
            c_int16,
            POINTER(c_uint32),
            PS6000_TIME_UNITS_T,
            c_uint32,
            c_uint32,
            c_int16,
            c_uint32,
            PS6000_RATIO_MODE_T,
            c_uint32,
        ]

        self._ps6000GetStreamingLatestValues = getattr(
            self.lib, "ps6000GetStreamingLatestValues"
        )
        self._ps6000GetStreamingLatestValues.resType = PICO_STATUS_T
        self._ps6000GetStreamingLatestValues.argTypes = [
            c_int16,
            ps6000StreamingReady,
            c_void_p,
        ]

        self._ps6000NoOfStreamingValues = getattr(self.lib, "ps6000NoOfStreamingValues")
        self._ps6000NoOfStreamingValues.resType = PICO_STATUS_T
        self._ps6000NoOfStreamingValues.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps6000GetMaxDownSampleRatio = getattr(
            self.lib, "ps6000GetMaxDownSampleRatio"
        )
        self._ps6000GetMaxDownSampleRatio.resType = PICO_STATUS_T
        self._ps6000GetMaxDownSampleRatio.argTypes = [
            c_int16,
            c_uint32,
            POINTER(c_uint32),
            PS6000_RATIO_MODE_T,
            c_uint32,
        ]

        self._ps6000GetValues = getattr(self.lib, "ps6000GetValues")
        self._ps6000GetValues.resType = PICO_STATUS_T
        self._ps6000GetValues.argTypes = [
            c_int16,
            c_uint32,
            POINTER(c_uint32),
            c_uint32,
            PS6000_RATIO_MODE_T,
            c_uint32,
            POINTER(c_int16),
        ]

        self._ps6000GetValuesBulk = getattr(self.lib, "ps6000GetValuesBulk")
        self._ps6000GetValuesBulk.resType = PICO_STATUS_T
        self._ps6000GetValuesBulk.argTypes = [
            c_int16,
            POINTER(c_uint32),
            c_uint32,
            c_uint32,
            c_uint32,
            PS6000_RATIO_MODE_T,
            POINTER(c_int16),
        ]

        self._ps6000GetValuesAsync = getattr(self.lib, "ps6000GetValuesAsync")
        self._ps6000GetValuesAsync.resType = PICO_STATUS_T
        self._ps6000GetValuesAsync.argTypes = [
            c_int16,
            c_uint32,
            c_uint32,
            c_uint32,
            PS6000_RATIO_MODE_T,
            c_uint32,
            ps6000DataReady,
            c_void_p,
        ]

        self._ps6000GetValuesOverlapped = getattr(self.lib, "ps6000GetValuesOverlapped")
        self._ps6000GetValuesOverlapped.resType = PICO_STATUS_T
        self._ps6000GetValuesOverlapped.argTypes = [
            c_int16,
            c_uint32,
            POINTER(c_uint32),
            c_uint32,
            PS6000_RATIO_MODE_T,
            c_uint32,
            POINTER(c_int16),
        ]

        self._ps6000GetValuesOverlappedBulk = getattr(
            self.lib, "ps6000GetValuesOverlappedBulk"
        )
        self._ps6000GetValuesOverlappedBulk.resType = PICO_STATUS_T
        self._ps6000GetValuesOverlappedBulk.argTypes = [
            c_int16,
            c_uint32,
            POINTER(c_uint32),
            c_uint32,
            PS6000_RATIO_MODE_T,
            c_uint32,
            c_uint32,
            POINTER(c_int16),
        ]

        self._ps6000GetValuesBulkAsyc = getattr(self.lib, "ps6000GetValuesBulkAsyc")
        self._ps6000GetValuesBulkAsyc.resType = PICO_STATUS_T
        self._ps6000GetValuesBulkAsyc.argTypes = [
            c_int16,
            c_uint32,
            POINTER(c_uint32),
            c_uint32,
            PS6000_RATIO_MODE_T,
            c_uint32,
            c_uint32,
            POINTER(c_int16),
        ]

        self._ps6000GetNoOfCaptures = getattr(self.lib, "ps6000GetNoOfCaptures")
        self._ps6000GetNoOfCaptures.resType = PICO_STATUS_T
        self._ps6000GetNoOfCaptures.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps6000GetNoOfProcessedCaptures = getattr(
            self.lib, "ps6000GetNoOfProcessedCaptures"
        )
        self._ps6000GetNoOfProcessedCaptures.resType = PICO_STATUS_T
        self._ps6000GetNoOfProcessedCaptures.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps6000Stop = getattr(self.lib, "ps6000Stop")
        self._ps6000Stop.resType = PICO_STATUS_T
        self._ps6000Stop.argTypes = [
            c_int16,
        ]

        self._ps6000SetNoOfCaptures = getattr(self.lib, "ps6000SetNoOfCaptures")
        self._ps6000SetNoOfCaptures.resType = PICO_STATUS_T
        self._ps6000SetNoOfCaptures.argTypes = [c_int16, c_uint32]

        self._ps6000SetWaveformLimiter = getattr(self.lib, "ps6000SetWaveformLimiter")
        self._ps6000SetWaveformLimiter.resType = PICO_STATUS_T
        self._ps6000SetWaveformLimiter.argTypes = [c_int16, c_uint32]

        self._ps6000EnumerateUnits = getattr(self.lib, "ps6000EnumerateUnits")
        self._ps6000EnumerateUnits.resType = PICO_STATUS_T
        self._ps6000EnumerateUnits.argTypes = [
            POINTER(c_int16),
            c_char_p,
            POINTER(c_int16),
        ]

        self._ps6000SetExternalClock = getattr(self.lib, "ps6000SetExternalClock")
        self._ps6000SetExternalClock.resType = PICO_STATUS_T
        self._ps6000SetExternalClock.argTypes = [
            c_int16,
            PS6000_EXTERNAL_FREQUENCY_T,
            c_int16,
        ]

        self._ps6000PingUnit = getattr(self.lib, "ps6000PingUnit")
        self._ps6000PingUnit.resType = PICO_STATUS_T
        self._ps6000PingUnit.argTypes = [
            c_int16,
        ]

        self._ps6000GetAnalogueOffset = getattr(self.lib, "ps6000GetAnalogueOffset")
        self._ps6000GetAnalogueOffset.resType = PICO_STATUS_T
        self._ps6000GetAnalogueOffset.argTypes = [
            c_int16,
            PS6000_RANGE_T,
            PS6000_COUPLING_T,
            POINTER(c_float),
            POINTER(c_float),
        ]

        self._ps6000GetTriggerInfoBulk = getattr(self.lib, "ps6000GetTriggerInfoBulk")
        self._ps6000GetTriggerInfoBulk.resType = PICO_STATUS_T
        self._ps6000GetTriggerInfoBulk.argTypes = [
            c_int16,
            c_void_p,
            c_uint32,
            c_uint32,
        ]

    def ps6000OpenUnit(self, serial: str | None):
        handle = c_int16(0)
        ser = c_char_p(serial.encode()) if serial is not None else 0
        return (
            PICO_STATUS(self._ps6000OpenUnit(byref(handle), ser)),
            handle,
        )

    def ps6000CloseUnit(self, handle: c_int16):
        return PICO_STATUS(self._ps6000CloseUnit(handle))

    def ps6000GetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._ps6000GetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return PICO_STATUS(status), infostr

    def ps6000MemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_uint32(0)
        return (
            PICO_STATUS(
                self._ps6000MemorySegments(handle, nsegments, byref(maxSamples))
            ),
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
        return PICO_STATUS(
            self._ps6000SetChannel(
                handle,
                channel,
                1 if enabled else 0,
                coupling,
                range,
                c_float(analog_offset),
                bandwidth,
            )
        )

    def ps6000SetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return PICO_STATUS(self._ps6000SetNoOfCaptures(handle, ncaptures))

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
            PICO_STATUS(
                self._ps6000GetTimebase2(
                    handle,
                    timebase,
                    noSamples,
                    byref(timeIntervalNS),
                    oversample,
                    byref(maxSamples),
                    segmentIndex,
                )
            ),
            timeIntervalNS.value,
            maxSamples.value,
        )

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
        return PICO_STATUS(
            self._ps6000SetSimpleTrigger(
                handle,
                1 if enable else 0,
                source,
                threshold,
                direction,
                delay,
                autoTriggerMS,
            )
        )

    def ps6000SetTriggerDelay(self, handle: c_int16, delay: int):
        return PICO_STATUS(self._ps6000SetTriggerDelay(handle, delay))

    def ps6000GetNoOfCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            PICO_STATUS(self._ps6000GetNoOfCaptures(handle, byref(captures))),
            captures.value,
        )

    def ps6000GetNoOfProcessedCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            PICO_STATUS(self._ps6000GetNoOfProcessedCaptures(handle, byref(captures))),
            captures.value,
        )

    def ps6000SetDataBuffer(
        self,
        handle: c_int16,
        channel: PS6000_CHANNEL,
        buffer: c_void_p,
        bufferLth: int,
        mode: PS6000_RATIO_MODE,
    ):
        return PICO_STATUS(
            self._ps6000SetDataBuffer(handle, channel, buffer, bufferLth, mode)
        )

    def ps6000SetDataBufferBulk(
        self,
        handle: c_int16,
        channel: PS6000_CHANNEL,
        buffer: c_void_p,
        bufferLth: int,
        waveform: int,
        mode: PS6000_RATIO_MODE,
    ):
        return PICO_STATUS(
            self._ps6000SetDataBufferBulk(
                handle, channel, buffer, bufferLth, waveform, mode
            )
        )

    def ps6000IsReady(self, handle: c_int16):
        ready = c_int16(0)
        return PICO_STATUS(self._ps6000IsReady(handle, byref(ready))), ready.value == 1

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
        lpReady = None
        if callback is not None:

            def cbwrapper(handle: c_int16, status: PICO_STATUS_T, _: c_void_p):
                callback(handle, PICO_STATUS(status))

            lpReady = ps6000BlockReady(cbwrapper)
        return (
            PICO_STATUS(
                self._ps6000RunBlock(
                    handle,
                    preSamples,
                    postSamples,
                    timebase,
                    oversample,
                    byref(timeInd),
                    segment,
                    lpReady,
                    None,
                )
            ),
            timeInd.value,
        )

    def ps6000GetAnalogueOffset(
        self, handle: c_int16, range: PS6000_RANGE, coupling: PS6000_COUPLING
    ):
        minv = c_float(0)
        maxv = c_float(0)
        return (
            PICO_STATUS(
                self._ps6000GetAnalogueOffset(
                    handle, range, coupling, byref(maxv), byref(minv)
                )
            ),
            minv.value,
            maxv.value,
        )

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
            PICO_STATUS(
                self._ps6000GetValuesBulk(
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
        status = PICO_STATUS(
            self._ps6000GetValuesTriggerTimeOffsetBulk64(
                handle, times, units, fromSegment, toSegment
            )
        )
        unitmap = {
            PS6000_TIME_UNITS.PS6000_FS: 1e-15,
            PS6000_TIME_UNITS.PS6000_PS: 1e-12,
            PS6000_TIME_UNITS.PS6000_NS: 1e-9,
            PS6000_TIME_UNITS.PS6000_US: 1e-6,
            PS6000_TIME_UNITS.PS6000_MS: 1e-3,
            PS6000_TIME_UNITS.PS6000_S: 1.0,
        }
        times_sec = [t * unitmap[PS6000_TIME_UNITS(u)] for t, u in zip(times, units)]
        return status, times_sec
