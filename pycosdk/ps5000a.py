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
from enum import IntEnum, IntFlag
from typing import Callable, final

from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T


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


class PS5000A_BANDWIDTH_LIMITER(IntEnum):
    PS5000A_BW_FULL = 0
    PS5000A_BW_20MHZ = 1


PS5000A_BANDWIDTH_LIMITER_T = c_int32


class PS5000A_COUPLING(IntEnum):
    PS5000A_AC = 0
    PS5000A_DC = 0


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


class PS5000A_TIME_UNITS(IntEnum):
    PS5000A_FS = 0
    PS5000A_PS = 1
    PS5000A_NS = 2
    PS5000A_US = 3
    PS5000A_MS = 4
    PS5000A_S = 5
    PS5000A_MAX_TIME_UNITS = 6


class PS5000A_SWEEP_TYPE(IntEnum):
    PS5000A_UP = 0
    PS5000A_DOWN = 1
    PS5000A_UPDOWN = 2
    PS5000A_DOWNUP = 3
    PS5000A_MAX_SWEEP_TYPES = 4


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


class PS5000A_CONDITIONS_INFO(IntEnum):
    PS5000A_CLEAR = 0x00000001
    PS5000A_ADD = 0x00000002


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


class PS5000A_SIGGEN_TRIG_SOURCE(IntEnum):
    PS5000A_SIGGEN_NONE = 0
    PS5000A_SIGGEN_SCOPE_TRIG = 1
    PS5000A_SIGGEN_AUX_IN = 2
    PS5000A_SIGGEN_EXT_IN = 3
    PS5000A_SIGGEN_SOFT_TRIG = 4


class PS5000A_INDEX_MODE(IntEnum):
    PS5000A_SINGLE = 0
    PS5000A_DUAL = 1
    PS5000A_QUAD = 2
    PS5000A_MAX_INDEX_MODES = 3


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
    _fields = [
        ("channelA", PS5000A_TRIGGER_STATE),
        ("channelB", PS5000A_TRIGGER_STATE),
        ("channelC", PS5000A_TRIGGER_STATE),
        ("channelD", PS5000A_TRIGGER_STATE),
        ("external", PS5000A_TRIGGER_STATE),
        ("aux", PS5000A_TRIGGER_STATE),
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


ps5000aBlockReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)

ps5000aDataReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_uint32, c_int16, c_void_p)

ps5000aStreamingReady = CFUNCTYPE(
    None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p
)


class PicoScope5000aWrapper:
    def __init__(self, library_path: str | None = None):
        if library_path is None:
            library_path = find_library("ps5000a")
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

        self._ps5000aOpenUnit = getattr(self.lib, "ps5000aOpenUnit")
        self._ps5000aOpenUnit.resType = PICO_STATUS_T
        self._ps5000aOpenUnit.argTypes = [
            POINTER(c_int16),
            c_char_p,
            PS5000A_DEVICE_RESOLUTION_T,
        ]

        self._ps5000aGetUnitInfo = getattr(self.lib, "ps5000aGetUnitInfo")
        self._ps5000aGetUnitInfo.resType = PICO_STATUS_T
        self._ps5000aGetUnitInfo.argTypes = [
            c_int16,
            c_char_p,
            c_int16,
            c_void_p,
            PICO_INFO_T,
        ]

        self._ps5000aCloseUnit = getattr(self.lib, "ps5000aCloseUnit")
        self._ps5000aCloseUnit.resType = PICO_STATUS_T
        self._ps5000aCloseUnit.argTypes = [c_int16]

        self._ps5000aMemorySegments = getattr(self.lib, "ps5000aMemorySegments")
        self._ps5000aMemorySegments.resType = PICO_STATUS_T
        self._ps5000aMemorySegments.argTypes = [c_int16, c_uint32, POINTER(c_uint32)]

        self._ps5000aSetChannel = getattr(self.lib, "ps5000aSetChannel")
        self._ps5000aSetChannel.resType = PICO_STATUS_T
        self._ps5000aSetChannel.argTypes = [
            c_int16,
            PS5000A_CHANNEL_T,
            c_int16,
            PS5000A_COUPLING_T,
            PS5000A_RANGE_T,
            c_float,
        ]

        self._ps5000aSetDigitalPort = getattr(self.lib, "ps5000aSetDigitalPort")
        self._ps5000aSetDigitalPort.resType = PICO_STATUS_T
        self._ps5000aSetDigitalPort.argTypes = [
            c_int16,
            PS5000A_CHANNEL_T,
            c_int16,
            c_int16,
        ]

        self._ps5000aSetBandwidthFilter = getattr(self.lib, "ps5000aSetBandwidthFilter")
        self._ps5000aSetBandwidthFilter.resType = PICO_STATUS_T
        self._ps5000aSetBandwidthFilter.argTypes = [
            c_int16,
            PS5000A_CHANNEL_T,
            PS5000A_BANDWIDTH_LIMITER_T,
        ]

        self._ps5000aSetNoOfCaptures = getattr(self.lib, "ps5000aSetNoOfCaptures")
        self._ps5000aSetNoOfCaptures.resType = PICO_STATUS_T
        self._ps5000aSetNoOfCaptures.argTypes = [c_int16, c_uint32]

        self._ps5000aGetTimebase2 = getattr(self.lib, "ps5000aGetTimebase2")
        self._ps5000aGetTimebase2.resType = PICO_STATUS_T
        self._ps5000aGetTimebase2.argTypes = [
            c_int16,
            c_uint32,
            c_int32,
            POINTER(c_float),
            POINTER(c_int32),
            c_uint32,
        ]

        self._ps5000aSetSimpleTrigger = getattr(self.lib, "ps5000aSetSimpleTrigger")
        self._ps5000aSetSimpleTrigger.resType = PICO_STATUS_T
        self._ps5000aSetSimpleTrigger.argTypes = [
            c_int16,
            c_int16,
            PS5000A_CHANNEL_T,
            c_int16,
            PS5000A_THRESHOLD_DIRECTION_T,
            c_uint32,
            c_int16,
        ]

        self._ps5000aSetTriggerDelay = getattr(self.lib, "ps5000aSetTriggerDelay")
        self._ps5000aSetTriggerDelay.resType = PICO_STATUS_T
        self._ps5000aSetTriggerDelay.argTypes = [c_int16, c_uint32]

        self._ps5000aGetNoOfCaptures = getattr(self.lib, "ps5000aGetNoOfCaptures")
        self._ps5000aGetNoOfCaptures.resType = PICO_STATUS_T
        self._ps5000aGetNoOfCaptures.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps5000aGetNoOfProcessedCaptures = getattr(
            self.lib, "ps5000aGetNoOfProcessedCaptures"
        )
        self._ps5000aGetNoOfProcessedCaptures.resType = PICO_STATUS_T
        self._ps5000aGetNoOfProcessedCaptures.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps5000aSetDataBuffer = getattr(self.lib, "ps5000aSetDataBuffer")
        self._ps5000aSetDataBuffer.resType = PICO_STATUS_T
        self._ps5000aSetDataBuffer.argTypes = [
            c_int16,
            PS5000A_CHANNEL_T,
            POINTER(c_int16),
            c_int32,
            c_uint32,
            PS5000A_RATIO_MODE_T,
        ]

        self._ps5000aSetDataBuffers = getattr(self.lib, "ps5000aSetDataBuffers")
        self._ps5000aSetDataBuffers.resType = PICO_STATUS_T
        self._ps5000aSetDataBuffers.argTypes = [
            c_int16,
            PS5000A_CHANNEL_T,
            POINTER(c_int16),
            POINTER(c_int16),
            c_int32,
            c_uint32,
            PS5000A_RATIO_MODE_T,
        ]

        self._ps5000aIsReady = getattr(self.lib, "ps5000aIsReady")
        self._ps5000aIsReady.resType = PICO_STATUS_T
        self._ps5000aIsReady.argTypes = [c_int16, POINTER(c_int16)]

        self._ps5000aRunBlock = getattr(self.lib, "ps5000aRunBlock")
        self._ps5000aRunBlock.resType = PICO_STATUS_T
        self._ps5000aRunBlock.argTypes = [
            c_int16,
            c_int32,
            c_int32,
            c_uint32,
            POINTER(c_int32),
            c_uint32,
            ps5000aBlockReady,
            c_void_p,
        ]

        self._ps5000aGetValues = getattr(self.lib, "ps5000aGetValues")
        self._ps5000aGetValues.resType = PICO_STATUS_T
        self._ps5000aGetValues.argTypes = [
            c_int16,
            c_uint32,
            POINTER(c_uint32),
            c_uint32,
            PS5000A_RATIO_MODE_T,
            c_uint32,
            POINTER(c_int16),
        ]

        self._ps5000aGetValuesBulk = getattr(self.lib, "ps5000aGetValuesBulk")
        self._ps5000aGetValuesBulk.resType = PICO_STATUS_T
        self._ps5000aGetValuesBulk.argTypes = [
            c_int16,
            POINTER(c_uint32),
            c_uint32,
            c_uint32,
            c_uint32,
            PS5000A_RATIO_MODE_T,
            POINTER(c_int16),
        ]

        self._ps5000aStop = getattr(self.lib, "ps5000aStop")
        self._ps5000aStop.resType = PICO_STATUS_T
        self._ps5000aStop.argTypes = [c_int16]

        self._ps5000aGetChannelInformation = getattr(
            self.lib, "ps5000aGetChannelInformation"
        )
        self._ps5000aGetChannelInformation.resType = PICO_STATUS_T
        self._ps5000aGetChannelInformation.argTypes = [
            c_int16,
            PS5000A_CHANNEL_INFO_T,
            c_int32,
            POINTER(c_int32),
            POINTER(c_int32),
            PS5000A_CHANNEL_T,
        ]

        self._ps5000aEnumerateUnits = getattr(self.lib, "ps5000aEnumerateUnits")
        self._ps5000aEnumerateUnits.resType = PICO_STATUS_T
        self._ps5000aEnumerateUnits.argTypes = [
            POINTER(c_int16),
            c_char_p,
            POINTER(c_int16),
        ]

        self._ps5000aPingUnit = getattr(self.lib, "ps5000aPingUnit")
        self._ps5000aPingUnit.resType = PICO_STATUS_T
        self._ps5000aPingUnit.argTypes = [c_int16]

        self._ps5000aMaximumValue = getattr(self.lib, "ps5000aMaximumValue")
        self._ps5000aMaximumValue.resType = PICO_STATUS_T
        self._ps5000aMaximumValue.argTypes = [c_int16, POINTER(c_int16)]

        self._ps5000aMinimumValue = getattr(self.lib, "ps5000aMinimumValue")
        self._ps5000aMinimumValue.resType = PICO_STATUS_T
        self._ps5000aMinimumValue.argTypes = [c_int16, POINTER(c_int16)]

        self._ps5000aGetAnalogueOffset = getattr(self.lib, "ps5000aGetAnalogueOffset")
        self._ps5000aGetAnalogueOffset.resType = PICO_STATUS_T
        self._ps5000aGetAnalogueOffset.argTypes = [
            c_int16,
            PS5000A_RANGE_T,
            PS5000A_COUPLING_T,
            POINTER(c_float),
            POINTER(c_float),
        ]

        self._ps5000aGetMaxSegments = getattr(self.lib, "ps5000aGetMaxSegments")
        self._ps5000aGetMaxSegments.resType = PICO_STATUS_T
        self._ps5000aGetMaxSegments.argTypes = [c_int16, POINTER(c_uint32)]

        self._ps5000aChangePowerSource = getattr(self.lib, "ps5000aChangePowerSource")
        self._ps5000aChangePowerSource.resType = PICO_STATUS_T
        self._ps5000aChangePowerSource.argTypes = [c_int16, PICO_STATUS_T]

        self._ps5000aCurrentPowerSource = getattr(self.lib, "ps5000aCurrentPowerSource")
        self._ps5000aCurrentPowerSource.resType = PICO_STATUS_T
        self._ps5000aCurrentPowerSource.argTypes = [c_int16]

    def ps5000aOpenUnit(
        self, serial: str | None, resolution: PS5000A_DEVICE_RESOLUTION
    ):
        handle = c_int16(0)
        ser = c_char_p(serial.encode()) if serial is not None else 0
        return (
            PICO_STATUS(self._ps5000aOpenUnit(byref(handle), ser, resolution)),
            handle,
        )

    def ps5000aCloseUnit(self, handle: c_int16):
        return PICO_STATUS(self._ps5000aCloseUnit(handle))

    def ps5000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._ps5000aGetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return PICO_STATUS(status), infostr

    def ps5000aMemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_int32(0)
        return (
            PICO_STATUS(
                self._ps5000aMemorySegments(handle, nsegments, byref(maxSamples))
            ),
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
        return PICO_STATUS(
            self._ps5000aSetChannel(
                handle,
                channel,
                1 if enabled else 0,
                coupling,
                range,
                c_float(analog_offset),
            )
        )

    def ps5000aSetBandwidthFilter(
        self,
        handle: c_int16,
        channel: PS5000A_CHANNEL,
        bandwidth: PS5000A_BANDWIDTH_LIMITER,
    ):
        return PICO_STATUS(self._ps5000aSetBandwidthFilter(handle, channel, bandwidth))

    def ps5000aSetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return PICO_STATUS(self._ps5000aSetNoOfCaptures(handle, ncaptures))

    def ps5000aGetTimebase2(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ):
        timeIntervalNS = c_float(0)
        maxSamples = c_int32(0)
        return (
            PICO_STATUS(
                self._ps5000aGetTimebase2(
                    handle,
                    timebase,
                    noSamples,
                    byref(timeIntervalNS),
                    byref(maxSamples),
                    segmentIndex,
                )
            ),
            timeIntervalNS.value,
            maxSamples.value,
        )

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
        return PICO_STATUS(
            self._ps5000aSetSimpleTrigger(
                handle,
                1 if enable else 0,
                source,
                threshold,
                direction,
                delay,
                autoTriggerMS,
            )
        )

    def ps5000aSetTriggerDelay(self, handle: c_int16, delay: int):
        return PICO_STATUS(self._ps5000aSetTriggerDelay(handle, delay))

    def ps5000aGetNoOfCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            PICO_STATUS(self._ps5000aGetNoOfCaptures(handle, byref(captures))),
            captures.value,
        )

    def ps5000aGetNoOfProcessedCaptures(self, handle: c_int16):
        captures = c_uint32()
        return (
            PICO_STATUS(self._ps5000aGetNoOfProcessedCaptures(handle, byref(captures))),
            captures.value,
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
        return PICO_STATUS(
            self._ps5000aSetDataBuffer(
                handle, channel, buffer, bufferLth, segmentIndex, mode
            )
        )

    def ps5000aIsReady(self, handle: c_int16):
        ready = c_int16(0)
        return PICO_STATUS(self._ps5000aIsReady(handle, byref(ready))), ready.value == 1

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
        lpReady = None
        if callback is not None:

            def cbwrapper(handle: c_int16, status: PICO_STATUS_T, _: c_void_p):
                callback(handle, PICO_STATUS(status))

            lpReady = ps5000aBlockReady(cbwrapper)
        return (
            PICO_STATUS(
                self._ps5000aRunBlock(
                    handle,
                    preSamples,
                    postSamples,
                    timebase,
                    byref(timeInd),
                    segment,
                    lpReady,
                    None,
                )
            ),
            timeInd.value,
        )

    def ps5000aGetMaxSegments(self, handle: c_int16):
        value = c_uint32(0)
        return (
            PICO_STATUS(self._ps5000aGetMaxSegments(handle, byref(value))),
            value.value,
        )

    def ps5000aMinimumValue(self, handle: c_int16):
        value = c_int16(0)
        return PICO_STATUS(self._ps5000aMinimumValue(handle, byref(value))), value.value

    def ps5000aMaximumValue(self, handle: c_int16):
        value = c_int16(0)
        return PICO_STATUS(self._ps5000aMaximumValue(handle, byref(value))), value.value

    def ps5000aGetAnalogueOffset(
        self, handle: c_int16, range: PS5000A_RANGE, coupling: PS5000A_COUPLING
    ):
        minv = c_float(0)
        maxv = c_float(0)
        return (
            PICO_STATUS(
                self._ps5000aGetAnalogueOffset(
                    handle, range, coupling, byref(maxv), byref(minv)
                )
            ),
            minv.value,
            maxv.value,
        )

    def ps5000aChangePowerSource(self, handle: c_int16, source: PICO_STATUS):
        return PICO_STATUS(self._ps5000aChangePowerSource(handle, source))

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
            PICO_STATUS(
                self._ps5000aGetValuesBulk(
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
