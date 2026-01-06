from ctypes import (
    Structure,
    c_double,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_void_p,
)
from typing import final

from .connectprobe import (
    PICO_CONNECT_PROBE_RANGE_T,
    PICO_CONNECT_PROBE_T,
    PICO_PROBE_RANGE_INFO_T,
)
from .deviceenums import (
    PICO_BANDWIDTH_LIMITER_FLAGS_T,
    PICO_BANDWIDTH_LIMITER_T,
    PICO_CHANNEL_T,
    PICO_COUPLING_T,
    PICO_DATA_TYPE_T,
    PICO_DIGITAL_DIRECTION_T,
    PICO_DIGITAL_PORT_T,
    PICO_LED_SELECT_T,
    PICO_LED_STATE_T,
    PICO_PORT_DIGITAL_CHANNEL_T,
    PICO_RATIO_MODE_T,
    PICO_READ_SELECTION_T,
    PICO_THRESHOLD_DIRECTION_T,
    PICO_THRESHOLD_MODE_T,
    PICO_TIME_UNITS_T,
    PICO_TRIGGER_STATE_T,
    PICO_USB_POWER_DELIVERY_DEVICE_TYPE_T,
)
from .status import PICO_STATUS_T


@final
class PICO_TRIGGER_INFO(Structure):
    _pack_ = 1
    _fields_ = [
        ("status", PICO_STATUS_T),
        ("segmentIndex", c_uint64),
        ("triggerIndex", c_uint64),
        ("triggerTime", c_double),
        ("timeUnits", PICO_TIME_UNITS_T),
        ("missedTriggers", c_uint64),
        ("timeStampCounter", c_uint64),
    ]


@final
class PICO_TRIGGER_CHANNEL_PROPERTIES(Structure):
    _pack_ = 1
    _fields_ = [
        ("thresholdUpper", c_int16),
        ("thresholdUpperHysteresis", c_uint16),
        ("thresholdLower", c_int16),
        ("thresholdLowerHysteresis", c_uint16),
        ("channel", PICO_CHANNEL_T),
    ]


@final
class PICO_CONDITION(Structure):
    _pack_ = 1
    _fields_ = [
        ("source", PICO_CHANNEL_T),
        ("condition", PICO_TRIGGER_STATE_T),
    ]


@final
class PICO_DIRECTION(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel", PICO_CHANNEL_T),
        ("direction", PICO_THRESHOLD_DIRECTION_T),
        ("thresholdMode", PICO_THRESHOLD_MODE_T),
    ]


@final
class PICO_USER_PROBE_INTERACTIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("connected_", c_uint16),
        ("channel_", PICO_CHANNEL_T),
        ("enabled_", c_uint16),
        ("probeName_", PICO_CONNECT_PROBE_T),
        ("requiresPower_", c_uint8),
        ("isPowered_", c_uint8),
        ("status_", PICO_STATUS_T),
        ("probeOff_", PICO_CONNECT_PROBE_RANGE_T),
        ("rangeFirst_", PICO_CONNECT_PROBE_RANGE_T),
        ("rangeLast_", PICO_CONNECT_PROBE_RANGE_T),
        ("rangeCurrent_", PICO_CONNECT_PROBE_RANGE_T),
        ("couplingFirst_", PICO_COUPLING_T),
        ("couplingLast_", PICO_COUPLING_T),
        ("couplingCurrent_", PICO_COUPLING_T),
        ("filterFlags_", PICO_BANDWIDTH_LIMITER_FLAGS_T),
        ("filterCurrent_", PICO_BANDWIDTH_LIMITER_FLAGS_T),
        ("defaultFilter_", PICO_BANDWIDTH_LIMITER_T),
    ]


@final
class PICO_DATA_BUFFERS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel_", PICO_CHANNEL_T),
        ("waveform_", c_uint64),
        ("downSampleRatioMode_", PICO_RATIO_MODE_T),
        ("read_", PICO_READ_SELECTION_T),
        ("bufferMax_", c_void_p),
        ("bufferMin_", c_void_p),
        ("dataType_", PICO_DATA_TYPE_T),
        ("nDistributionPoints_", c_uint32),
    ]


@final
class PICO_STREAMING_DATA_INFO(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel_", PICO_CHANNEL_T),
        ("mode_", PICO_RATIO_MODE_T),
        ("type_", PICO_DATA_TYPE_T),
        ("noOfSamples_", c_int32),
        ("bufferIndex_", c_uint64),
        ("startIndex_", c_int32),
        ("overflow_", c_int16),
    ]


@final
class PICO_STREAMING_DATA_TRIGGER_INFO(Structure):
    _pack_ = 1
    _fields_ = [
        ("triggerAt_", c_uint64),
        ("triggered_", c_int16),
        ("autoStop_", c_int16),
    ]


@final
class PICO_SCALING_FACTORS_VALUES(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel", PICO_CHANNEL_T),
        ("range", PICO_CONNECT_PROBE_RANGE_T),
        ("offset", c_int16),
        ("scalingFactor", c_double),
    ]


@final
class PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel", PICO_CHANNEL_T),
        ("rangeMin", c_int64),
        ("rangeMax", c_int64),
        ("rangeType", PICO_PROBE_RANGE_INFO_T),
        ("offset", c_int16),
        ("scalingFactor", c_double),
    ]


@final
class PROBE_APP(Structure):
    _pack_ = 1
    _fields_ = [
        ("id_", c_int32),
        ("appMajorVersion_", c_int32),
        ("appMinorVersion_", c_int32),
    ]


@final
class PICO_DIGITAL_CHANNEL_DIRECTIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel", PICO_PORT_DIGITAL_CHANNEL_T),
        ("direction", PICO_DIGITAL_DIRECTION_T),
    ]


@final
class PICO_DIGITAL_PORT_INTERACTIONS(Structure):
    _pack_ = 1
    _fields_ = [
        ("connected_", c_uint16),
        ("channel_", PICO_CHANNEL_T),
        ("digitalPortName_", PICO_DIGITAL_PORT_T),
        ("status_", PICO_STATUS_T),
        ("serial_[DIGITAL_PORT_SERIAL_LENGTH]", c_int8),
        ("calibrationDate_[DIGITAL_PORT_CALIBRATION_DATE_LENGTH]", c_int8),
    ]


@final
class PICO_CHANNEL_OVERVOLTAGE_TRIPPED(Structure):
    _pack_ = 1
    _fields_ = [
        ("channel_", PICO_CHANNEL_T),
        ("tripped_", c_uint8),
    ]


@final
class PICO_USB_POWER_DELIVERY(Structure):
    _pack_ = 1
    _fields_ = [
        ("valid_", c_uint8),
        ("busVoltagemV_", c_uint32),
        ("rpCurrentLimitmA_", c_uint32),
        ("partnerConnected_", c_uint8),
        ("ccPolarity_", c_uint8),
        ("attachedDevice_", PICO_USB_POWER_DELIVERY_DEVICE_TYPE_T),
        ("contractExists_", c_uint8),
        ("currentPdo_", c_uint32),
        ("currentRdo_", c_uint32),
    ]


@final
class PICO_USB_POWER_DETAILS(Structure):
    _pack_ = 1
    _fields_ = [
        ("powerErrorLikely_", c_uint8),
        ("dataPort_", PICO_USB_POWER_DELIVERY),
        ("powerPort_", PICO_USB_POWER_DELIVERY),
    ]


@final
class PICO_LED_COLOUR_PROPERTIES(Structure):
    _pack_ = 1
    _fields_ = [
        ("led_", PICO_LED_SELECT_T),
        ("hue_", c_uint16),
        ("saturation_", c_uint8),
    ]


@final
class PICO_LED_STATE_PROPERTIES(Structure):
    _pack_ = 1
    _fields_ = [
        ("led_", PICO_LED_SELECT_T),
        ("state_", PICO_LED_STATE_T),
    ]


__all__ = (
    "PICO_TRIGGER_INFO",
    "PICO_TRIGGER_CHANNEL_PROPERTIES",
    "PICO_CONDITION",
    "PICO_DIRECTION",
    "PICO_USER_PROBE_INTERACTIONS",
    "PICO_DATA_BUFFERS",
    "PICO_STREAMING_DATA_INFO",
    "PICO_STREAMING_DATA_TRIGGER_INFO",
    "PICO_SCALING_FACTORS_VALUES",
    "PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES",
    "PROBE_APP",
    "PICO_DIGITAL_CHANNEL_DIRECTIONS",
    "PICO_DIGITAL_PORT_INTERACTIONS",
    "PICO_CHANNEL_OVERVOLTAGE_TRIPPED",
    "PICO_USB_POWER_DELIVERY",
    "PICO_USB_POWER_DETAILS",
    "PICO_LED_COLOUR_PROPERTIES",
    "PICO_LED_STATE_PROPERTIES",
)
