from ctypes import (
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
from enum import IntFlag
from typing import Annotated, final

from ._struct import CStruct
from .connectprobe import (
    PICO_CONNECT_PROBE,
    PICO_CONNECT_PROBE_RANGE,
    PICO_CONNECT_PROBE_RANGE_T,
    PICO_CONNECT_PROBE_T,
    PICO_PROBE_RANGE_INFO,
    PICO_PROBE_RANGE_INFO_T,
)
from .deviceenums import (
    PICO_BANDWIDTH_LIMITER,
    PICO_BANDWIDTH_LIMITER_FLAGS,
    PICO_BANDWIDTH_LIMITER_FLAGS_T,
    PICO_BANDWIDTH_LIMITER_T,
    PICO_CHANNEL,
    PICO_CHANNEL_T,
    PICO_COUPLING,
    PICO_COUPLING_T,
    PICO_DATA_TYPE,
    PICO_DATA_TYPE_T,
    PICO_DIGITAL_DIRECTION,
    PICO_DIGITAL_DIRECTION_T,
    PICO_DIGITAL_PORT,
    PICO_DIGITAL_PORT_T,
    PICO_LED_SELECT,
    PICO_LED_SELECT_T,
    PICO_LED_STATE,
    PICO_LED_STATE_T,
    PICO_PORT_DIGITAL_CHANNEL,
    PICO_PORT_DIGITAL_CHANNEL_T,
    PICO_RATIO_MODE,
    PICO_RATIO_MODE_T,
    PICO_READ_SELECTION,
    PICO_READ_SELECTION_T,
    PICO_THRESHOLD_DIRECTION,
    PICO_THRESHOLD_DIRECTION_T,
    PICO_THRESHOLD_MODE,
    PICO_THRESHOLD_MODE_T,
    PICO_TIME_UNITS,
    PICO_TIME_UNITS_T,
    PICO_TRIGGER_STATE,
    PICO_TRIGGER_STATE_T,
    PICO_USB_POWER_DELIVERY_DEVICE_TYPE,
    PICO_USB_POWER_DELIVERY_DEVICE_TYPE_T,
)
from .status import PICO_STATUS, PICO_STATUS_T

# The structs are typed dataclasses; their C structs are available as ``c_type``,
# see CStruct. All structs in PicoDeviceStructs.h are packed to 1 byte.

DIGITAL_PORT_SERIAL_LENGTH = 10
DIGITAL_PORT_CALIBRATION_DATE_LENGTH = 8


class PICO_TRIGGER_INFO_STATUS(IntFlag):
    """The statuses that ``PICO_TRIGGER_INFO.status`` ORs together.

    No C counterpart: the header declares the field as ``PICO_STATUS``. Other
    statuses are kept as unnamed values (still comparable with ``PICO_STATUS``).
    """

    PICO_OK = PICO_STATUS.PICO_OK
    PICO_DEVICE_TIME_STAMP_RESET = PICO_STATUS.PICO_DEVICE_TIME_STAMP_RESET
    PICO_TRIGGER_TIME_NOT_REQUESTED = PICO_STATUS.PICO_TRIGGER_TIME_NOT_REQUESTED
    PICO_TRIGGER_TIME_BUFFER_NOT_SET = PICO_STATUS.PICO_TRIGGER_TIME_BUFFER_NOT_SET
    PICO_TRIGGER_TIME_FAILED_TO_CALCULATE = (
        PICO_STATUS.PICO_TRIGGER_TIME_FAILED_TO_CALCULATE
    )


@final
class PICO_TRIGGER_INFO(CStruct):
    status: Annotated[PICO_TRIGGER_INFO_STATUS, PICO_STATUS_T]
    segmentIndex: Annotated[int, c_uint64]
    triggerIndex: Annotated[int, c_uint64]
    triggerTime: Annotated[float, c_double]
    timeUnits: Annotated[PICO_TIME_UNITS, PICO_TIME_UNITS_T]
    missedTriggers: Annotated[int, c_uint64]
    timeStampCounter: Annotated[int, c_uint64]


@final
class PICO_TRIGGER_CHANNEL_PROPERTIES(CStruct):
    thresholdUpper: Annotated[int, c_int16]
    thresholdUpperHysteresis: Annotated[int, c_uint16]
    thresholdLower: Annotated[int, c_int16]
    thresholdLowerHysteresis: Annotated[int, c_uint16]
    channel: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]


@final
class PICO_CONDITION(CStruct):
    source: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    condition: Annotated[PICO_TRIGGER_STATE, PICO_TRIGGER_STATE_T]


@final
class PICO_DIRECTION(CStruct):
    channel: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    direction: Annotated[PICO_THRESHOLD_DIRECTION, PICO_THRESHOLD_DIRECTION_T]
    thresholdMode: Annotated[PICO_THRESHOLD_MODE, PICO_THRESHOLD_MODE_T]


@final
class PICO_USER_PROBE_INTERACTIONS(CStruct):
    connected_: Annotated[bool, c_uint16]
    channel_: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    enabled_: Annotated[bool, c_uint16]
    probeName_: Annotated[PICO_CONNECT_PROBE, PICO_CONNECT_PROBE_T]
    requiresPower_: Annotated[bool, c_uint8]
    isPowered_: Annotated[bool, c_uint8]
    status_: Annotated[PICO_STATUS, PICO_STATUS_T]
    probeOff_: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    rangeFirst_: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    rangeLast_: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    rangeCurrent_: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    couplingFirst_: Annotated[PICO_COUPLING, PICO_COUPLING_T]
    couplingLast_: Annotated[PICO_COUPLING, PICO_COUPLING_T]
    couplingCurrent_: Annotated[PICO_COUPLING, PICO_COUPLING_T]
    filterFlags_: Annotated[
        PICO_BANDWIDTH_LIMITER_FLAGS, PICO_BANDWIDTH_LIMITER_FLAGS_T
    ]
    filterCurrent_: Annotated[
        PICO_BANDWIDTH_LIMITER_FLAGS, PICO_BANDWIDTH_LIMITER_FLAGS_T
    ]
    defaultFilter_: Annotated[PICO_BANDWIDTH_LIMITER, PICO_BANDWIDTH_LIMITER_T]


@final
class PICO_DATA_BUFFERS(CStruct):
    channel_: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    waveform_: Annotated[int, c_uint64]
    downSampleRatioMode_: Annotated[PICO_RATIO_MODE, PICO_RATIO_MODE_T]
    read_: Annotated[PICO_READ_SELECTION, PICO_READ_SELECTION_T]
    # Buffer addresses (e.g. numpy ``.ctypes.data``), None for NULL.
    bufferMax_: Annotated[int | None, c_void_p]
    bufferMin_: Annotated[int | None, c_void_p]
    dataType_: Annotated[PICO_DATA_TYPE, PICO_DATA_TYPE_T]
    nDistributionPoints_: Annotated[int, c_uint32]


@final
class PICO_STREAMING_DATA_INFO(CStruct):
    channel_: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    mode_: Annotated[PICO_RATIO_MODE, PICO_RATIO_MODE_T]
    type_: Annotated[PICO_DATA_TYPE, PICO_DATA_TYPE_T]
    # Written by the driver.
    noOfSamples_: Annotated[int, c_int32] = 0
    bufferIndex_: Annotated[int, c_uint64] = 0
    startIndex_: Annotated[int, c_int32] = 0
    overflow_: Annotated[int, c_int16] = 0


@final
class PICO_STREAMING_DATA_TRIGGER_INFO(CStruct):
    triggerAt_: Annotated[int, c_uint64]
    triggered_: Annotated[bool, c_int16]
    autoStop_: Annotated[bool, c_int16]


@final
class PICO_SCALING_FACTORS_VALUES(CStruct):
    channel: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    range: Annotated[PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T]
    offset: Annotated[int, c_int16]
    scalingFactor: Annotated[float, c_double]


@final
class PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES(CStruct):
    channel: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    rangeMin: Annotated[int, c_int64]
    rangeMax: Annotated[int, c_int64]
    rangeType: Annotated[PICO_PROBE_RANGE_INFO, PICO_PROBE_RANGE_INFO_T]
    offset: Annotated[int, c_int16]
    scalingFactor: Annotated[float, c_double]


@final
class PROBE_APP(CStruct):
    id_: Annotated[int, c_int32]
    appMajorVersion_: Annotated[int, c_int32]
    appMinorVersion_: Annotated[int, c_int32]


@final
class PICO_DIGITAL_CHANNEL_DIRECTIONS(CStruct):
    channel: Annotated[PICO_PORT_DIGITAL_CHANNEL, PICO_PORT_DIGITAL_CHANNEL_T]
    direction: Annotated[PICO_DIGITAL_DIRECTION, PICO_DIGITAL_DIRECTION_T]


@final
class PICO_DIGITAL_PORT_INTERACTIONS(CStruct):
    connected_: Annotated[bool, c_uint16]
    channel_: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    digitalPortName_: Annotated[PICO_DIGITAL_PORT, PICO_DIGITAL_PORT_T]
    status_: Annotated[PICO_STATUS, PICO_STATUS_T]
    serial_: Annotated[str, c_int8 * DIGITAL_PORT_SERIAL_LENGTH]
    calibrationDate_: Annotated[str, c_int8 * DIGITAL_PORT_CALIBRATION_DATE_LENGTH]


@final
class PICO_CHANNEL_OVERVOLTAGE_TRIPPED(CStruct):
    channel_: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
    tripped_: Annotated[bool, c_uint8]


@final
class PICO_USB_POWER_DELIVERY(CStruct):
    valid_: Annotated[bool, c_uint8]
    busVoltagemV_: Annotated[int, c_uint32]
    rpCurrentLimitmA_: Annotated[int, c_uint32]
    partnerConnected_: Annotated[int, c_uint8]
    ccPolarity_: Annotated[int, c_uint8]
    attachedDevice_: Annotated[
        PICO_USB_POWER_DELIVERY_DEVICE_TYPE, PICO_USB_POWER_DELIVERY_DEVICE_TYPE_T
    ]
    contractExists_: Annotated[bool, c_uint8]
    currentPdo_: Annotated[int, c_uint32]
    currentRdo_: Annotated[int, c_uint32]


@final
class PICO_USB_POWER_DETAILS(CStruct):
    powerErrorLikely_: Annotated[bool, c_uint8]
    dataPort_: PICO_USB_POWER_DELIVERY
    powerPort_: PICO_USB_POWER_DELIVERY


@final
class PICO_LED_COLOUR_PROPERTIES(CStruct):
    led_: Annotated[PICO_LED_SELECT, PICO_LED_SELECT_T]
    hue_: Annotated[int, c_uint16]
    saturation_: Annotated[int, c_uint8]


@final
class PICO_LED_STATE_PROPERTIES(CStruct):
    led_: Annotated[PICO_LED_SELECT, PICO_LED_SELECT_T]
    state_: Annotated[PICO_LED_STATE, PICO_LED_STATE_T]


__all__ = (
    "DIGITAL_PORT_CALIBRATION_DATE_LENGTH",
    "DIGITAL_PORT_SERIAL_LENGTH",
    "PICO_CHANNEL_OVERVOLTAGE_TRIPPED",
    "PICO_CONDITION",
    "PICO_DATA_BUFFERS",
    "PICO_DIGITAL_CHANNEL_DIRECTIONS",
    "PICO_DIGITAL_PORT_INTERACTIONS",
    "PICO_DIRECTION",
    "PICO_LED_COLOUR_PROPERTIES",
    "PICO_LED_STATE_PROPERTIES",
    "PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES",
    "PICO_SCALING_FACTORS_VALUES",
    "PICO_STREAMING_DATA_INFO",
    "PICO_STREAMING_DATA_TRIGGER_INFO",
    "PICO_TRIGGER_CHANNEL_PROPERTIES",
    "PICO_TRIGGER_INFO",
    "PICO_TRIGGER_INFO_STATUS",
    "PICO_USB_POWER_DELIVERY",
    "PICO_USB_POWER_DETAILS",
    "PICO_USER_PROBE_INTERACTIONS",
    "PROBE_APP",
)
