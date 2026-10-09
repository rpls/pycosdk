# pyright: reportAny=false, reportUnannotatedClassAttribute=false
from collections.abc import Callable, Sequence
from ctypes import (
    POINTER,
    Structure,
    byref,
    c_char_p,
    c_double,
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
from enum import IntEnum
from typing import TYPE_CHECKING, Any, final

from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase
from .callback import (
    PicoAWGOverrangeInteractions,
    PicoExternalReferenceInteractions,
    PicoProbeInteractions,
    PicoTemperatureSensorInteractions,
    PicoUpdateFirmwareProgress,
)
from .connectprobe import (
    PICO_CONNECT_PROBE,
    PICO_CONNECT_PROBE_RANGE,
    PICO_CONNECT_PROBE_RANGE_T,
    PICO_CONNECT_PROBE_T,
)
from .deviceenums import (
    PICO_ACTION,
    PICO_ACTION_T,
    PICO_AUTO_TRIGGER_STATUS,
    PICO_AUTO_TRIGGER_STATUS_T,
    PICO_AUXIO_MODE,
    PICO_AUXIO_MODE_T,
    PICO_BANDWIDTH_LIMITER,
    PICO_BANDWIDTH_LIMITER_T,
    PICO_CAL_TYPE,
    PICO_CAL_TYPE_T,
    PICO_CHANNEL,
    PICO_CHANNEL_FLAGS,
    PICO_CHANNEL_FLAGS_T,
    PICO_CHANNEL_T,
    PICO_CLOCK_REFERENCE,
    PICO_COUPLING,
    PICO_COUPLING_T,
    PICO_DATA_TYPE,
    PICO_DATA_TYPE_T,
    PICO_DEVICE_RESOLUTION,
    PICO_DEVICE_RESOLUTION_T,
    PICO_DIGITAL_PORT_HYSTERESIS,
    PICO_DIGITAL_PORT_HYSTERESIS_T,
    PICO_PULSE_WIDTH_TYPE,
    PICO_PULSE_WIDTH_TYPE_T,
    PICO_RATIO_MODE,
    PICO_RATIO_MODE_T,
    PICO_SCOPE_STATE,
    PICO_SCOPE_STATE_T,
    PICO_SIGGEN_FILTER_STATE,
    PICO_SIGGEN_FILTER_STATE_T,
    PICO_SIGGEN_PARAMETER,
    PICO_SIGGEN_PARAMETER_T,
    PICO_SIGGEN_TRIG_SOURCE,
    PICO_SIGGEN_TRIG_SOURCE_T,
    PICO_SIGGEN_TRIG_TYPE,
    PICO_SIGGEN_TRIG_TYPE_T,
    PICO_SWEEP_TYPE,
    PICO_SWEEP_TYPE_T,
    PICO_TEMPERATURE_REFERENCE,
    PICO_TEXT_FORMAT,
    PICO_TEXT_FORMAT_T,
    PICO_THRESHOLD_DIRECTION,
    PICO_THRESHOLD_DIRECTION_T,
    PICO_TIME_UNITS,
    PICO_TIME_UNITS_T,
    PICO_TRIGGER_WITHIN_PRE_TRIGGER,
    PICO_TRIGGER_WITHIN_PRE_TRIGGER_T,
    PICO_WAVE_TYPE,
    PICO_WAVE_TYPE_T,
)
from .devicestructs import (
    PICO_CHANNEL_OVERVOLTAGE_TRIPPED,
    PICO_CONDITION,
    PICO_DIGITAL_CHANNEL_DIRECTIONS,
    PICO_DIGITAL_PORT_INTERACTIONS,
    PICO_DIRECTION,
    PICO_SCALING_FACTORS_VALUES,
    PICO_STREAMING_DATA_INFO,
    PICO_STREAMING_DATA_TRIGGER_INFO,
    PICO_TRIGGER_CHANNEL_PROPERTIES,
    PICO_TRIGGER_INFO,
    PICO_USER_PROBE_INTERACTIONS,
)
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T
from .statusconfig import errstate
from .version import PICO_FIRMWARE_INFO

if TYPE_CHECKING:
    from ctypes import Array

    # Anything ctypes accepts for a PICO_POINTER sample buffer, e.g., a ctypes
    # array, a c_void_p, or an address such as numpy's ``arr.ctypes.data``.
    DataBuffer = c_void_p | int | Array[Any] | None


# Definitions from PicoDeviceDefinitionsExperimental.h


class PICO_PROBE_USER_ACTION(IntEnum):
    PICO_PROBE_BUTTON_PRESS = 0


PICO_PROBE_USER_ACTION_T = c_int32


class PICO_PROBE_BUTTON_PRESS_TYPE(IntEnum):
    PICO_PROBE_BUTTON_SHORT_DURATION_PRESS = 0
    PICO_PROBE_BUTTON_LONG_DURATION_PRESS = 1


PICO_PROBE_BUTTON_PRESS_TYPE_T = c_int32


@final
class PICO_PROBE_BUTTON_PRESS_PARAMETER(Structure):
    _pack_ = 1
    _fields_ = [
        ("buttonIndex", c_uint8),
        ("buttonPressType", PICO_PROBE_BUTTON_PRESS_TYPE_T),
    ]


ps6000aBlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)
ps6000aDataReady = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, c_uint64, c_int16, c_void_p
)
# Same signature as the generic PicoProbeInteractions.
ps6000aProbeInteractions = PicoProbeInteractions
ps6000aDigitalPortInteractions = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, POINTER(PICO_DIGITAL_PORT_INTERACTIONS), c_uint32
)
PicoProbeUserAction = CALLBACK_FUNCTYPE(
    None,
    c_int16,
    PICO_STATUS_T,
    PICO_CHANNEL_T,
    PICO_CONNECT_PROBE_T,
    PICO_PROBE_USER_ACTION_T,
    c_void_p,
    c_void_p,
)
# Former (misspelled) name, kept for backwards compatibility.
PicoExternalReferenceInterations = PicoExternalReferenceInteractions

# A USB 3.0 device connected to a USB 2.0 port is still opened successfully.
_OPEN_UNIT_INFO = frozenset({PICO_STATUS.PICO_USB3_0_DEVICE_NON_USB3_0_PORT})


def _array(ctype: Any, items: Sequence[Any]) -> Any:
    """Return ``items`` as ctypes array, or None (NULL) if there are none."""
    if len(items) == 0:
        return None
    return (ctype * len(items))(*items)


def _decode(buf: Any, size: int) -> str:
    """Decode a NUL terminated string of ``size`` bytes (including the NUL)."""
    return buf.raw[: max(size - 1, 0)].split(b"\0", 1)[0].decode("utf-8")


class PicoScope6000aWrapper(PicoScopeWrapperBase):
    _library_name = "ps6000a"

    def __init__(self, library_path: str | None = None):
        super().__init__(library_path)

        self._ps6000aOpenUnit = self._bind(
            "ps6000aOpenUnit",
            [POINTER(c_int16), c_char_p, PICO_DEVICE_RESOLUTION_T],
            info=_OPEN_UNIT_INFO,
        )
        self._ps6000aOpenUnitAsync = self._bind(
            "ps6000aOpenUnitAsync",
            [POINTER(c_int16), c_char_p, PICO_DEVICE_RESOLUTION_T],
            info=_OPEN_UNIT_INFO,
        )
        self._ps6000aOpenUnitProgress = self._bind(
            "ps6000aOpenUnitProgress",
            [POINTER(c_int16), POINTER(c_int16), POINTER(c_int16)],
            info=_OPEN_UNIT_INFO,
        )
        self._ps6000aGetUnitInfo = self._bind(
            "ps6000aGetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps6000aGetAccessoryInfo = self._bind(
            "ps6000aGetAccessoryInfo",
            [c_int16, PICO_CHANNEL_T, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._ps6000aCloseUnit = self._bind("ps6000aCloseUnit", [c_int16])
        self._ps6000aFlashLed = self._bind("ps6000aFlashLed", [c_int16, c_int16])
        self._ps6000aSetAuxIoMode = self._bind(
            "ps6000aSetAuxIoMode", [c_int16, PICO_AUXIO_MODE_T]
        )
        self._ps6000aSetTriggerHoldoffCounterBySamples = self._bind(
            "ps6000aSetTriggerHoldoffCounterBySamples", [c_int16, c_uint64]
        )
        self._ps6000aMemorySegments = self._bind(
            "ps6000aMemorySegments", [c_int16, c_uint64, POINTER(c_uint64)]
        )
        self._ps6000aMemorySegmentsBySamples = self._bind(
            "ps6000aMemorySegmentsBySamples", [c_int16, c_uint64, POINTER(c_uint64)]
        )
        self._ps6000aGetMaximumAvailableMemory = self._bind(
            "ps6000aGetMaximumAvailableMemory",
            [c_int16, POINTER(c_uint64), PICO_DEVICE_RESOLUTION_T],
        )
        self._ps6000aQueryMaxSegmentsBySamples = self._bind(
            "ps6000aQueryMaxSegmentsBySamples",
            [
                c_int16,
                c_uint64,
                c_uint32,
                POINTER(c_uint64),
                PICO_DEVICE_RESOLUTION_T,
            ],
        )
        self._ps6000aGetScopeState = self._bind(
            "ps6000aGetScopeState", [c_int16, POINTER(PICO_SCOPE_STATE_T)]
        )
        self._ps6000aSetChannelOn = self._bind(
            "ps6000aSetChannelOn",
            [
                c_int16,
                PICO_CHANNEL_T,
                PICO_COUPLING_T,
                PICO_CONNECT_PROBE_RANGE_T,
                c_double,
                PICO_BANDWIDTH_LIMITER_T,
            ],
        )
        self._ps6000aSetChannelOff = self._bind(
            "ps6000aSetChannelOff", [c_int16, PICO_CHANNEL_T]
        )
        self._ps6000aSetDigitalPortOn = self._bind(
            "ps6000aSetDigitalPortOn",
            [
                c_int16,
                PICO_CHANNEL_T,
                POINTER(c_int16),
                c_int16,
                PICO_DIGITAL_PORT_HYSTERESIS_T,
            ],
        )
        self._ps6000aSetDigitalPortOff = self._bind(
            "ps6000aSetDigitalPortOff", [c_int16, PICO_CHANNEL_T]
        )
        self._ps6000aGetTimebase = self._bind(
            "ps6000aGetTimebase",
            [
                c_int16,
                c_uint32,
                c_uint64,
                POINTER(c_double),
                POINTER(c_uint64),
                c_uint64,
            ],
        )
        self._ps6000aSigGenWaveform = self._bind(
            "ps6000aSigGenWaveform", [c_int16, PICO_WAVE_TYPE_T, c_void_p, c_uint64]
        )
        self._ps6000aSigGenRange = self._bind(
            "ps6000aSigGenRange", [c_int16, c_double, c_double]
        )
        self._ps6000aSigGenWaveformDutyCycle = self._bind(
            "ps6000aSigGenWaveformDutyCycle", [c_int16, c_double]
        )
        self._ps6000aSigGenTrigger = self._bind(
            "ps6000aSigGenTrigger",
            [
                c_int16,
                PICO_SIGGEN_TRIG_TYPE_T,
                PICO_SIGGEN_TRIG_SOURCE_T,
                c_uint64,
                c_uint64,
            ],
        )
        self._ps6000aSigGenFilter = self._bind(
            "ps6000aSigGenFilter", [c_int16, PICO_SIGGEN_FILTER_STATE_T]
        )
        self._ps6000aSigGenFrequency = self._bind(
            "ps6000aSigGenFrequency", [c_int16, c_double]
        )
        self._ps6000aSigGenFrequencySweep = self._bind(
            "ps6000aSigGenFrequencySweep",
            [c_int16, c_double, c_double, c_double, PICO_SWEEP_TYPE_T],
        )
        self._ps6000aSigGenPhase = self._bind("ps6000aSigGenPhase", [c_int16, c_uint64])
        self._ps6000aSigGenPhaseSweep = self._bind(
            "ps6000aSigGenPhaseSweep",
            [c_int16, c_uint64, c_uint64, c_uint64, PICO_SWEEP_TYPE_T],
        )
        self._ps6000aSigGenClockManual = self._bind(
            "ps6000aSigGenClockManual", [c_int16, c_double, c_uint64]
        )
        self._ps6000aSigGenSoftwareTriggerControl = self._bind(
            "ps6000aSigGenSoftwareTriggerControl", [c_int16, PICO_SIGGEN_TRIG_TYPE_T]
        )
        self._ps6000aSigGenApply = self._bind(
            "ps6000aSigGenApply",
            [
                c_int16,
                c_int16,
                c_int16,
                c_int16,
                c_int16,
                c_int16,
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
            ],
        )
        self._ps6000aSigGenLimits = self._bind(
            "ps6000aSigGenLimits",
            [
                c_int16,
                PICO_SIGGEN_PARAMETER_T,
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
            ],
        )
        self._ps6000aSigGenFrequencyLimits = self._bind(
            "ps6000aSigGenFrequencyLimits",
            [
                c_int16,
                PICO_WAVE_TYPE_T,
                POINTER(c_uint64),
                POINTER(c_double),
                c_int16,
                POINTER(c_double),
                POINTER(c_uint64),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
            ],
        )
        self._ps6000aSigGenPause = self._bind("ps6000aSigGenPause", [c_int16])
        self._ps6000aSigGenRestart = self._bind("ps6000aSigGenRestart", [c_int16])
        self._ps6000aSetSimpleTrigger = self._bind(
            "ps6000aSetSimpleTrigger",
            [
                c_int16,
                c_int16,
                PICO_CHANNEL_T,
                c_int16,
                PICO_THRESHOLD_DIRECTION_T,
                c_uint64,
                c_uint32,
            ],
        )
        self._ps6000aTriggerWithinPreTriggerSamples = self._bind(
            "ps6000aTriggerWithinPreTriggerSamples",
            [c_int16, PICO_TRIGGER_WITHIN_PRE_TRIGGER_T],
        )
        self._ps6000aSetTriggerChannelProperties = self._bind(
            "ps6000aSetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PICO_TRIGGER_CHANNEL_PROPERTIES),
                c_int16,
                c_int16,
                c_uint32,
            ],
        )
        self._ps6000aSetTriggerChannelConditions = self._bind(
            "ps6000aSetTriggerChannelConditions",
            [c_int16, POINTER(PICO_CONDITION), c_int16, PICO_ACTION_T],
        )
        self._ps6000aSetTriggerChannelDirections = self._bind(
            "ps6000aSetTriggerChannelDirections",
            [c_int16, POINTER(PICO_DIRECTION), c_int16],
        )
        self._ps6000aSetTriggerDelay = self._bind(
            "ps6000aSetTriggerDelay", [c_int16, c_uint64]
        )
        self._ps6000aSetPulseWidthQualifierProperties = self._bind(
            "ps6000aSetPulseWidthQualifierProperties",
            [c_int16, c_uint32, c_uint32, PICO_PULSE_WIDTH_TYPE_T],
        )
        self._ps6000aSetPulseWidthQualifierConditions = self._bind(
            "ps6000aSetPulseWidthQualifierConditions",
            [c_int16, POINTER(PICO_CONDITION), c_int16, PICO_ACTION_T],
        )
        self._ps6000aSetPulseWidthQualifierDirections = self._bind(
            "ps6000aSetPulseWidthQualifierDirections",
            [c_int16, POINTER(PICO_DIRECTION), c_int16],
        )
        self._ps6000aSetTriggerDigitalPortProperties = self._bind(
            "ps6000aSetTriggerDigitalPortProperties",
            [
                c_int16,
                PICO_CHANNEL_T,
                POINTER(PICO_DIGITAL_CHANNEL_DIRECTIONS),
                c_int16,
            ],
        )
        self._ps6000aSetPulseWidthDigitalPortProperties = self._bind(
            "ps6000aSetPulseWidthDigitalPortProperties",
            [
                c_int16,
                PICO_CHANNEL_T,
                POINTER(PICO_DIGITAL_CHANNEL_DIRECTIONS),
                c_int16,
            ],
        )
        self._ps6000aGetTriggerTimeOffset = self._bind(
            "ps6000aGetTriggerTimeOffset",
            [c_int16, POINTER(c_int64), POINTER(PICO_TIME_UNITS_T), c_uint64],
        )
        self._ps6000aGetValuesTriggerTimeOffsetBulk = self._bind(
            "ps6000aGetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PICO_TIME_UNITS_T),
                c_uint64,
                c_uint64,
            ],
        )
        self._ps6000aSetDataBuffer = self._bind(
            "ps6000aSetDataBuffer",
            [
                c_int16,
                PICO_CHANNEL_T,
                c_void_p,
                c_int32,
                PICO_DATA_TYPE_T,
                c_uint64,
                PICO_RATIO_MODE_T,
                PICO_ACTION_T,
            ],
        )
        self._ps6000aSetDataBuffers = self._bind(
            "ps6000aSetDataBuffers",
            [
                c_int16,
                PICO_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_int32,
                PICO_DATA_TYPE_T,
                c_uint64,
                PICO_RATIO_MODE_T,
                PICO_ACTION_T,
            ],
        )
        self._ps6000aRunBlock = self._bind(
            "ps6000aRunBlock",
            [
                c_int16,
                c_uint64,
                c_uint64,
                c_uint32,
                POINTER(c_double),
                c_uint64,
                ps6000aBlockReady,
                c_void_p,
            ],
        )
        self._ps6000aIsReady = self._bind("ps6000aIsReady", [c_int16, POINTER(c_int16)])
        self._ps6000aRunStreaming = self._bind(
            "ps6000aRunStreaming",
            [
                c_int16,
                POINTER(c_double),
                PICO_TIME_UNITS_T,
                c_uint64,
                c_uint64,
                c_int16,
                c_uint64,
                PICO_RATIO_MODE_T,
            ],
        )
        self._ps6000aGetStreamingLatestValues = self._bind(
            "ps6000aGetStreamingLatestValues",
            [
                c_int16,
                POINTER(PICO_STREAMING_DATA_INFO),
                c_uint64,
                POINTER(PICO_STREAMING_DATA_TRIGGER_INFO),
            ],
            # Not an error: the driver has data pending and needs new buffers
            # (set with ps6000aSetDataBuffer(s)) before it can continue.
            info={PICO_STATUS.PICO_WAITING_FOR_DATA_BUFFERS},
        )
        self._ps6000aNoOfStreamingValues = self._bind(
            "ps6000aNoOfStreamingValues", [c_int16, POINTER(c_uint64)]
        )
        self._ps6000aGetValues = self._bind(
            "ps6000aGetValues",
            [
                c_int16,
                c_uint64,
                POINTER(c_uint64),
                c_uint64,
                PICO_RATIO_MODE_T,
                c_uint64,
                POINTER(c_int16),
            ],
        )
        self._ps6000aGetValuesBulk = self._bind(
            "ps6000aGetValuesBulk",
            [
                c_int16,
                c_uint64,
                POINTER(c_uint64),
                c_uint64,
                c_uint64,
                c_uint64,
                PICO_RATIO_MODE_T,
                POINTER(c_int16),
            ],
        )
        # lpDataReady is declared as PICO_POINTER, but is a ps6000aDataReady.
        self._ps6000aGetValuesAsync = self._bind(
            "ps6000aGetValuesAsync",
            [
                c_int16,
                c_uint64,
                c_uint64,
                c_uint64,
                PICO_RATIO_MODE_T,
                c_uint64,
                ps6000aDataReady,
                c_void_p,
            ],
        )
        self._ps6000aGetValuesBulkAsync = self._bind(
            "ps6000aGetValuesBulkAsync",
            [
                c_int16,
                c_uint64,
                c_uint64,
                c_uint64,
                c_uint64,
                c_uint64,
                PICO_RATIO_MODE_T,
                ps6000aDataReady,
                c_void_p,
            ],
        )
        self._ps6000aGetValuesOverlapped = self._bind(
            "ps6000aGetValuesOverlapped",
            [
                c_int16,
                c_uint64,
                POINTER(c_uint64),
                c_uint64,
                PICO_RATIO_MODE_T,
                c_uint64,
                c_uint64,
                POINTER(c_int16),
            ],
        )
        self._ps6000aStopUsingGetValuesOverlapped = self._bind(
            "ps6000aStopUsingGetValuesOverlapped", [c_int16]
        )
        self._ps6000aGetNoOfCaptures = self._bind(
            "ps6000aGetNoOfCaptures", [c_int16, POINTER(c_uint64)]
        )
        self._ps6000aGetNoOfProcessedCaptures = self._bind(
            "ps6000aGetNoOfProcessedCaptures", [c_int16, POINTER(c_uint64)]
        )
        self._ps6000aStop = self._bind("ps6000aStop", [c_int16])
        self._ps6000aSetNoOfCaptures = self._bind(
            "ps6000aSetNoOfCaptures", [c_int16, c_uint64]
        )
        self._ps6000aGetTriggerInfo = self._bind(
            "ps6000aGetTriggerInfo",
            [c_int16, POINTER(PICO_TRIGGER_INFO), c_uint64, c_uint64],
        )
        self._ps6000aGetAutoTriggerStatus = self._bind(
            "ps6000aGetAutoTriggerStatus",
            [c_int16, POINTER(PICO_AUTO_TRIGGER_STATUS_T), c_uint64, c_uint64],
        )
        self._ps6000aEnumerateUnits = self._bind(
            "ps6000aEnumerateUnits",
            [POINTER(c_int16), c_char_p, POINTER(c_int16)],
            # Finding no units is a valid enumeration result, not a failure.
            info=(PICO_STATUS.PICO_NOT_FOUND,),
        )
        self._ps6000aPingUnit = self._bind("ps6000aPingUnit", [c_int16])
        self._ps6000aGetAnalogueOffsetLimits = self._bind(
            "ps6000aGetAnalogueOffsetLimits",
            [
                c_int16,
                PICO_CONNECT_PROBE_RANGE_T,
                PICO_COUPLING_T,
                POINTER(c_double),
                POINTER(c_double),
            ],
        )
        self._ps6000aGetMinimumTimebaseStateless = self._bind(
            "ps6000aGetMinimumTimebaseStateless",
            [
                c_int16,
                PICO_CHANNEL_FLAGS_T,
                POINTER(c_uint32),
                POINTER(c_double),
                PICO_DEVICE_RESOLUTION_T,
            ],
        )
        self._ps6000aNearestSampleIntervalStateless = self._bind(
            "ps6000aNearestSampleIntervalStateless",
            [
                c_int16,
                PICO_CHANNEL_FLAGS_T,
                c_double,
                PICO_DEVICE_RESOLUTION_T,
                POINTER(c_uint32),
                POINTER(c_double),
            ],
        )
        self._ps6000aChannelCombinationsStateless = self._bind(
            "ps6000aChannelCombinationsStateless",
            [
                c_int16,
                POINTER(PICO_CHANNEL_FLAGS_T),
                POINTER(c_uint32),
                PICO_DEVICE_RESOLUTION_T,
                c_uint32,
            ],
        )
        self._ps6000aSetDeviceResolution = self._bind(
            "ps6000aSetDeviceResolution", [c_int16, PICO_DEVICE_RESOLUTION_T]
        )
        self._ps6000aGetDeviceResolution = self._bind(
            "ps6000aGetDeviceResolution",
            [c_int16, POINTER(PICO_DEVICE_RESOLUTION_T)],
        )
        self._ps6000aQueryOutputEdgeDetect = self._bind(
            "ps6000aQueryOutputEdgeDetect", [c_int16, POINTER(c_int16)]
        )
        self._ps6000aSetOutputEdgeDetect = self._bind(
            "ps6000aSetOutputEdgeDetect", [c_int16, c_int16]
        )
        self._ps6000aGetScalingValues = self._bind(
            "ps6000aGetScalingValues",
            [c_int16, POINTER(PICO_SCALING_FACTORS_VALUES), c_int16],
        )
        self._ps6000aGetAdcLimits = self._bind(
            "ps6000aGetAdcLimits",
            [
                c_int16,
                PICO_DEVICE_RESOLUTION_T,
                POINTER(c_int16),
                POINTER(c_int16),
            ],
        )
        self._ps6000aCheckForUpdate = self._bind(
            "ps6000aCheckForUpdate",
            [
                c_int16,
                POINTER(PICO_FIRMWARE_INFO),
                POINTER(c_int16),
                POINTER(c_uint16),
            ],
        )
        self._ps6000aStartFirmwareUpdate = self._bind(
            "ps6000aStartFirmwareUpdate", [c_int16, PicoUpdateFirmwareProgress]
        )
        self._ps6000aResetChannelsAndReportAllChannelsOvervoltageTripStatus = (
            self._bind(
                "ps6000aResetChannelsAndReportAllChannelsOvervoltageTripStatus",
                [c_int16, POINTER(PICO_CHANNEL_OVERVOLTAGE_TRIPPED), c_uint8],
            )
        )
        self._ps6000aReportAllChannelsOvervoltageTripStatus = self._bind(
            "ps6000aReportAllChannelsOvervoltageTripStatus",
            [c_int16, POINTER(PICO_CHANNEL_OVERVOLTAGE_TRIPPED), c_uint8],
        )
        self._ps6000aRunAutomaticOffsetAdjustment = self._bind(
            "ps6000aRunAutomaticOffsetAdjustment", [c_int16, PICO_CAL_TYPE_T]
        )
        self._ps6000aCommitCurrentAdjustmentSettingsToDevice = self._bind(
            "ps6000aCommitCurrentAdjustmentSettingsToDevice",
            [c_int16, PICO_CAL_TYPE_T],
        )
        self._ps6000aResetAdjustmentSettings = self._bind(
            "ps6000aResetAdjustmentSettings", [c_int16, PICO_CAL_TYPE_T]
        )
        self._ps6000aSetAdjustmentSettingDetails = self._bind(
            "ps6000aSetAdjustmentSettingDetails",
            [
                c_int16,
                PICO_CAL_TYPE_T,
                c_char_p,
                POINTER(c_int32),
                c_char_p,
                POINTER(c_int32),
            ],
        )
        self._ps6000aGetAdjustmentSettingDetails = self._bind(
            "ps6000aGetAdjustmentSettingDetails",
            [
                c_int16,
                PICO_CAL_TYPE_T,
                c_char_p,
                POINTER(c_int32),
                PICO_TEXT_FORMAT_T,
            ],
        )

        # ps6000aApiExperimental.h
        self._ps6000aSetDigitalPortInteractionCallback = self._bind(
            "ps6000aSetDigitalPortInteractionCallback",
            [c_int16, ps6000aDigitalPortInteractions],
        )
        self._ps6000aSetProbeInteractionCallback = self._bind(
            "ps6000aSetProbeInteractionCallback", [c_int16, PicoProbeInteractions]
        )
        self._ps6000aSetExternalReferenceInteractionCallback = self._bind(
            "ps6000aSetExternalReferenceInteractionCallback",
            [c_int16, PicoExternalReferenceInteractions],
        )
        self._ps6000aSetAWGOverrangeInteractionCallback = self._bind(
            "ps6000aSetAWGOverrangeInteractionCallback",
            [c_int16, PicoAWGOverrangeInteractions],
        )
        self._ps6000aSetTemperatureSensorInteractionCallback = self._bind(
            "ps6000aSetTemperatureSensorInteractionCallback",
            [c_int16, PicoTemperatureSensorInteractions],
        )
        self._ps6000aSetProbeUserActionCallback = self._bind(
            "ps6000aSetProbeUserActionCallback",
            [c_int16, PicoProbeUserAction, c_void_p],
        )

    def ps6000aOpenUnit(self, serial: str | None, resolution: PICO_DEVICE_RESOLUTION):
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        return self._ps6000aOpenUnit(byref(handle), ser, resolution), handle

    def ps6000aOpenUnitAsync(
        self, serial: str | None, resolution: PICO_DEVICE_RESOLUTION
    ) -> tuple[PICO_STATUS, bool]:
        """Start opening a unit; returns whether the open operation was started."""
        started = c_int16(0)
        ser = serial.encode() if serial is not None else None
        status = self._ps6000aOpenUnitAsync(byref(started), ser, resolution)
        return status, started.value != 0

    def ps6000aOpenUnitProgress(self) -> tuple[PICO_STATUS, c_int16, int, bool]:
        """Returns the status, handle, progress in percent, and completion flag."""
        handle = c_int16(0)
        progressPercent = c_int16(0)
        complete = c_int16(0)
        status = self._ps6000aOpenUnitProgress(
            byref(handle), byref(progressPercent), byref(complete)
        )
        return status, handle, progressPercent.value, complete.value != 0

    def ps6000aCloseUnit(self, handle: c_int16):
        return self._ps6000aCloseUnit(handle)

    def ps6000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(255)
        size = c_int16(0)
        status = self._ps6000aGetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = _decode(buf, size.value)
        else:
            infostr = ""
        return status, infostr

    def ps6000aGetAccessoryInfo(
        self, handle: c_int16, channel: PICO_CHANNEL, info: PICO_INFO
    ) -> tuple[PICO_STATUS, str]:
        buf = create_string_buffer(255)
        size = c_int16(0)
        status = self._ps6000aGetAccessoryInfo(
            handle, channel, buf, 255, byref(size), info
        )
        if status == PICO_STATUS.PICO_OK:
            infostr = _decode(buf, size.value)
        else:
            infostr = ""
        return status, infostr

    def ps6000aFlashLed(self, handle: c_int16, start: int) -> PICO_STATUS:
        """``start`` < 0 flashes indefinitely, 0 stops, > 0 flashes that often."""
        return self._ps6000aFlashLed(handle, start)

    def ps6000aSetAuxIoMode(
        self, handle: c_int16, auxIoMode: PICO_AUXIO_MODE
    ) -> PICO_STATUS:
        return self._ps6000aSetAuxIoMode(handle, auxIoMode)

    def ps6000aSetTriggerHoldoffCounterBySamples(
        self, handle: c_int16, samples: int
    ) -> PICO_STATUS:
        return self._ps6000aSetTriggerHoldoffCounterBySamples(handle, samples)

    def ps6000aGetTimebase(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ):
        timeIntervalNS = c_double(0)
        maxSamples = c_uint64(0)
        return (
            self._ps6000aGetTimebase(
                handle,
                timebase,
                noSamples,
                byref(timeIntervalNS),
                byref(maxSamples),
                segmentIndex,
            ),
            timeIntervalNS.value,
            maxSamples.value,
        )

    def ps6000aGetMinimumTimebaseStateless(
        self,
        handle: c_int16,
        enabledChannels: PICO_CHANNEL_FLAGS,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        return (
            self._ps6000aGetMinimumTimebaseStateless(
                handle,
                enabledChannels,
                byref(timebase),
                byref(timeInterval),
                resolution,
            ),
            timebase.value,
            timeInterval.value,
        )

    def ps6000aNearestSampleIntervalStateless(
        self,
        handle: c_int16,
        enabledChannels: PICO_CHANNEL_FLAGS,
        requiredInterval: float,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        return (
            self._ps6000aNearestSampleIntervalStateless(
                handle,
                enabledChannels,
                requiredInterval,
                resolution,
                byref(timebase),
                byref(timeInterval),
            ),
            timebase.value,
            timeInterval.value,
        )

    def ps6000aChannelCombinationsStateless(
        self,
        handle: c_int16,
        resolution: PICO_DEVICE_RESOLUTION,
        timebase: int,
        nChannelCombinations: int = 4096,
    ) -> tuple[PICO_STATUS, list[PICO_CHANNEL_FLAGS]]:
        """Returns the channel combinations usable with ``timebase``.

        ``nChannelCombinations`` is the size of the buffer for the result.
        """
        combinations = (PICO_CHANNEL_FLAGS_T * nChannelCombinations)()
        n = c_uint32(nChannelCombinations)
        status = self._ps6000aChannelCombinationsStateless(
            handle, combinations, byref(n), resolution, timebase
        )
        count = min(n.value, nChannelCombinations)
        return status, [PICO_CHANNEL_FLAGS(c) for c in combinations[:count]]

    def ps6000aSetChannelOn(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        coupling: PICO_COUPLING,
        range: PICO_CONNECT_PROBE_RANGE,
        analog_offset: float,
        bandwidth: PICO_BANDWIDTH_LIMITER,
    ):
        return self._ps6000aSetChannelOn(
            handle, channel, coupling, range, analog_offset, bandwidth
        )

    def ps6000aSetChannelOff(self, handle: c_int16, channel: PICO_CHANNEL):
        return self._ps6000aSetChannelOff(handle, channel)

    def ps6000aSetDigitalPortOn(
        self,
        handle: c_int16,
        port: PICO_CHANNEL,
        logicThresholds: list[int],
        hysteresis: PICO_DIGITAL_PORT_HYSTERESIS,
    ):
        logicThresholdLevel = _array(c_int16, logicThresholds)
        return self._ps6000aSetDigitalPortOn(
            handle, port, logicThresholdLevel, len(logicThresholds), hysteresis
        )

    def ps6000aSetDigitalPortOff(self, handle: c_int16, port: PICO_CHANNEL):
        return self._ps6000aSetDigitalPortOff(handle, port)

    def ps6000aGetAdcLimits(self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION):
        minCount = c_int16(0)
        maxCount = c_int16(0)
        return (
            self._ps6000aGetAdcLimits(
                handle, resolution, byref(minCount), byref(maxCount)
            ),
            minCount.value,
            maxCount.value,
        )

    def ps6000aSigGenWaveform(
        self,
        handle: c_int16,
        waveType: PICO_WAVE_TYPE,
        buffer: Sequence[int] | None = None,
    ) -> PICO_STATUS:
        """``buffer`` holds the arbitrary waveform samples (only for PICO_ARBITRARY)."""
        samples = _array(c_int16, buffer) if buffer is not None else None
        return self._ps6000aSigGenWaveform(
            handle, waveType, samples, len(buffer) if buffer is not None else 0
        )

    def ps6000aSigGenRange(
        self, handle: c_int16, peakToPeakVolts: float, offsetVolts: float
    ) -> PICO_STATUS:
        return self._ps6000aSigGenRange(handle, peakToPeakVolts, offsetVolts)

    def ps6000aSigGenWaveformDutyCycle(
        self, handle: c_int16, dutyCyclePercent: float
    ) -> PICO_STATUS:
        return self._ps6000aSigGenWaveformDutyCycle(handle, dutyCyclePercent)

    def ps6000aSigGenTrigger(
        self,
        handle: c_int16,
        triggerType: PICO_SIGGEN_TRIG_TYPE,
        triggerSource: PICO_SIGGEN_TRIG_SOURCE,
        cycles: int,
        autoTriggerPicoSeconds: int,
    ) -> PICO_STATUS:
        return self._ps6000aSigGenTrigger(
            handle, triggerType, triggerSource, cycles, autoTriggerPicoSeconds
        )

    def ps6000aSigGenFilter(
        self, handle: c_int16, filterState: PICO_SIGGEN_FILTER_STATE
    ) -> PICO_STATUS:
        return self._ps6000aSigGenFilter(handle, filterState)

    def ps6000aSigGenFrequency(
        self, handle: c_int16, frequencyHz: float
    ) -> PICO_STATUS:
        return self._ps6000aSigGenFrequency(handle, frequencyHz)

    def ps6000aSigGenFrequencySweep(
        self,
        handle: c_int16,
        stopFrequencyHz: float,
        frequencyIncrement: float,
        dwellTimeSeconds: float,
        sweepType: PICO_SWEEP_TYPE,
    ) -> PICO_STATUS:
        return self._ps6000aSigGenFrequencySweep(
            handle, stopFrequencyHz, frequencyIncrement, dwellTimeSeconds, sweepType
        )

    def ps6000aSigGenPhase(self, handle: c_int16, deltaPhase: int) -> PICO_STATUS:
        return self._ps6000aSigGenPhase(handle, deltaPhase)

    def ps6000aSigGenPhaseSweep(
        self,
        handle: c_int16,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PICO_SWEEP_TYPE,
    ) -> PICO_STATUS:
        return self._ps6000aSigGenPhaseSweep(
            handle, stopDeltaPhase, deltaPhaseIncrement, dwellCount, sweepType
        )

    def ps6000aSigGenClockManual(
        self, handle: c_int16, dacClockFrequency: float, prescaleRatio: int
    ) -> PICO_STATUS:
        return self._ps6000aSigGenClockManual(handle, dacClockFrequency, prescaleRatio)

    def ps6000aSigGenSoftwareTriggerControl(
        self, handle: c_int16, triggerState: PICO_SIGGEN_TRIG_TYPE
    ) -> PICO_STATUS:
        return self._ps6000aSigGenSoftwareTriggerControl(handle, triggerState)

    def ps6000aSigGenApply(
        self,
        handle: c_int16,
        sigGenEnabled: bool,
        sweepEnabled: bool,
        triggerEnabled: bool,
        automaticClockOptimisationEnabled: bool,
        overrideAutomaticClockAndPrescale: bool,
    ) -> tuple[PICO_STATUS, float, float, float, float]:
        """Returns the status, frequency, stop frequency, increment and dwell time."""
        frequency = c_double(0)
        stopFrequency = c_double(0)
        frequencyIncrement = c_double(0)
        dwellTime = c_double(0)
        status = self._ps6000aSigGenApply(
            handle,
            sigGenEnabled,
            sweepEnabled,
            triggerEnabled,
            automaticClockOptimisationEnabled,
            overrideAutomaticClockAndPrescale,
            byref(frequency),
            byref(stopFrequency),
            byref(frequencyIncrement),
            byref(dwellTime),
        )
        return (
            status,
            frequency.value,
            stopFrequency.value,
            frequencyIncrement.value,
            dwellTime.value,
        )

    def ps6000aSigGenLimits(
        self, handle: c_int16, parameter: PICO_SIGGEN_PARAMETER
    ) -> tuple[PICO_STATUS, float, float, float]:
        """Returns the status, minimum, maximum, and step of ``parameter``."""
        minimum = c_double(0)
        maximum = c_double(0)
        step = c_double(0)
        status = self._ps6000aSigGenLimits(
            handle, parameter, byref(minimum), byref(maximum), byref(step)
        )
        return status, minimum.value, maximum.value, step.value

    def ps6000aSigGenFrequencyLimits(
        self,
        handle: c_int16,
        waveType: PICO_WAVE_TYPE,
        numSamples: int,
        startFrequency: float,
        sweepEnabled: bool,
        manualDacClockFrequency: float | None = None,
        manualPrescaleRatio: int | None = None,
    ) -> tuple[PICO_STATUS, float, float, float, float, float]:
        """Returns the status, max. stop frequency, min./max. frequency step and
        min./max. dwell time."""
        numSamples_ = c_uint64(numSamples)
        startFrequency_ = c_double(startFrequency)
        dacClock = (
            byref(c_double(manualDacClockFrequency))
            if manualDacClockFrequency is not None
            else None
        )
        prescale = (
            byref(c_uint64(manualPrescaleRatio))
            if manualPrescaleRatio is not None
            else None
        )
        maxStopFrequency = c_double(0)
        minFrequencyStep = c_double(0)
        maxFrequencyStep = c_double(0)
        minDwellTime = c_double(0)
        maxDwellTime = c_double(0)
        status = self._ps6000aSigGenFrequencyLimits(
            handle,
            waveType,
            byref(numSamples_),
            byref(startFrequency_),
            sweepEnabled,
            dacClock,
            prescale,
            byref(maxStopFrequency),
            byref(minFrequencyStep),
            byref(maxFrequencyStep),
            byref(minDwellTime),
            byref(maxDwellTime),
        )
        return (
            status,
            maxStopFrequency.value,
            minFrequencyStep.value,
            maxFrequencyStep.value,
            minDwellTime.value,
            maxDwellTime.value,
        )

    def ps6000aSigGenPause(self, handle: c_int16) -> PICO_STATUS:
        return self._ps6000aSigGenPause(handle)

    def ps6000aSigGenRestart(self, handle: c_int16) -> PICO_STATUS:
        return self._ps6000aSigGenRestart(handle)

    def ps6000aSetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PICO_CHANNEL,
        threshold: int,
        direction: PICO_THRESHOLD_DIRECTION,
        delay: int,
        autoTriggerUS: int,
    ):
        assert autoTriggerUS >= 0
        return self._ps6000aSetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTriggerUS,
        )

    def ps6000aTriggerWithinPreTriggerSamples(
        self, handle: c_int16, state: PICO_TRIGGER_WITHIN_PRE_TRIGGER
    ) -> PICO_STATUS:
        return self._ps6000aTriggerWithinPreTriggerSamples(handle, state)

    def ps6000aSetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PICO_TRIGGER_CHANNEL_PROPERTIES],
        auxOutputEnable: bool,
        autoTriggerMicroSeconds: int,
    ) -> PICO_STATUS:
        """``auxOutputEnable`` is ignored by the driver (see ps6000aSetAuxIoMode)."""
        return self._ps6000aSetTriggerChannelProperties(
            handle,
            _array(PICO_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            auxOutputEnable,
            autoTriggerMicroSeconds,
        )

    def ps6000aSetTriggerChannelConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PICO_CONDITION],
        action: PICO_ACTION,
    ) -> PICO_STATUS:
        return self._ps6000aSetTriggerChannelConditions(
            handle, _array(PICO_CONDITION, conditions), len(conditions), action
        )

    def ps6000aSetTriggerChannelDirections(
        self, handle: c_int16, directions: Sequence[PICO_DIRECTION]
    ) -> PICO_STATUS:
        return self._ps6000aSetTriggerChannelDirections(
            handle, _array(PICO_DIRECTION, directions), len(directions)
        )

    def ps6000aSetTriggerDelay(self, handle: c_int16, delay: int) -> PICO_STATUS:
        return self._ps6000aSetTriggerDelay(handle, delay)

    def ps6000aSetPulseWidthQualifierProperties(
        self, handle: c_int16, lower: int, upper: int, type: PICO_PULSE_WIDTH_TYPE
    ) -> PICO_STATUS:
        return self._ps6000aSetPulseWidthQualifierProperties(handle, lower, upper, type)

    def ps6000aSetPulseWidthQualifierConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PICO_CONDITION],
        action: PICO_ACTION,
    ) -> PICO_STATUS:
        return self._ps6000aSetPulseWidthQualifierConditions(
            handle, _array(PICO_CONDITION, conditions), len(conditions), action
        )

    def ps6000aSetPulseWidthQualifierDirections(
        self, handle: c_int16, directions: Sequence[PICO_DIRECTION]
    ) -> PICO_STATUS:
        return self._ps6000aSetPulseWidthQualifierDirections(
            handle, _array(PICO_DIRECTION, directions), len(directions)
        )

    def ps6000aSetTriggerDigitalPortProperties(
        self,
        handle: c_int16,
        port: PICO_CHANNEL,
        directions: Sequence[PICO_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> PICO_STATUS:
        return self._ps6000aSetTriggerDigitalPortProperties(
            handle,
            port,
            _array(PICO_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def ps6000aSetPulseWidthDigitalPortProperties(
        self,
        handle: c_int16,
        port: PICO_CHANNEL,
        directions: Sequence[PICO_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> PICO_STATUS:
        return self._ps6000aSetPulseWidthDigitalPortProperties(
            handle,
            port,
            _array(PICO_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def ps6000aGetTriggerTimeOffset(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, PICO_TIME_UNITS]:
        time = c_int64(0)
        timeUnits = PICO_TIME_UNITS_T(0)
        status = self._ps6000aGetTriggerTimeOffset(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return status, time.value, PICO_TIME_UNITS(timeUnits.value)

    def ps6000aGetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[PICO_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * nsegments)()
        timeUnits = (PICO_TIME_UNITS_T * nsegments)()
        status = self._ps6000aGetValuesTriggerTimeOffsetBulk(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return status, list(times), [PICO_TIME_UNITS(u) for u in timeUnits]

    def ps6000aQueryMaxSegmentsBySamples(
        self,
        handle: c_int16,
        nsamples: int,
        nchannels: int,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        maxSegments = c_uint64(0)
        return (
            self._ps6000aQueryMaxSegmentsBySamples(
                handle, nsamples, nchannels, byref(maxSegments), resolution
            ),
            maxSegments.value,
        )

    def ps6000aMemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_uint64(0)
        return (
            self._ps6000aMemorySegments(handle, nsegments, byref(maxSamples)),
            maxSamples.value,
        )

    def ps6000aMemorySegmentsBySamples(self, handle: c_int16, nsamples: int):
        assert nsamples > 0
        maxSegments = c_uint64(0)
        return (
            self._ps6000aMemorySegmentsBySamples(handle, nsamples, byref(maxSegments)),
            maxSegments.value,
        )

    def ps6000aGetMaximumAvailableMemory(
        self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION
    ) -> tuple[PICO_STATUS, int]:
        nMaxSamples = c_uint64(0)
        status = self._ps6000aGetMaximumAvailableMemory(
            handle, byref(nMaxSamples), resolution
        )
        return status, nMaxSamples.value

    def ps6000aGetScopeState(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, PICO_SCOPE_STATE]:
        scopeState = PICO_SCOPE_STATE_T(0)
        status = self._ps6000aGetScopeState(handle, byref(scopeState))
        return status, PICO_SCOPE_STATE(scopeState.value)

    def ps6000aSetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return self._ps6000aSetNoOfCaptures(handle, ncaptures)

    def ps6000aGetNoOfCaptures(self, handle: c_int16) -> tuple[PICO_STATUS, int]:
        nCaptures = c_uint64(0)
        status = self._ps6000aGetNoOfCaptures(handle, byref(nCaptures))
        return status, nCaptures.value

    def ps6000aGetNoOfProcessedCaptures(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, int]:
        nProcessedCaptures = c_uint64(0)
        status = self._ps6000aGetNoOfProcessedCaptures(
            handle, byref(nProcessedCaptures)
        )
        return status, nProcessedCaptures.value

    def ps6000aRunBlock(
        self,
        handle: c_int16,
        preSamples: int,
        postSamples: int,
        timebase: int,
        segment: int,
        callback: Callable[[int, PICO_STATUS], None] | None,
    ):
        assert preSamples >= 0
        assert postSamples >= 0
        timeInd = c_double(0)
        # A NULL function pointer; ctypes rejects None here.
        lpReady = ps6000aBlockReady()
        if callback is not None:

            def cbwrapper(handle: int, status: int, _: int | None) -> None:
                callback(handle, PICO_STATUS(status))

            lpReady = ps6000aBlockReady(cbwrapper)
        status = self._with_callback(
            self._callback_key("ps6000aRunBlock", handle),
            lpReady,
            lambda: self._ps6000aRunBlock(
                handle,
                preSamples,
                postSamples,
                timebase,
                byref(timeInd),
                segment,
                lpReady,
                None,
            ),
        )
        return status, timeInd.value

    def ps6000aIsReady(self, handle: c_int16):
        ready = c_int16(0)
        return self._ps6000aIsReady(handle, byref(ready)), ready.value == 1

    def ps6000aRunStreaming(
        self,
        handle: c_int16,
        sampleInterval: float,
        sampleIntervalTimeUnits: PICO_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
    ) -> tuple[PICO_STATUS, float]:
        """Returns the status and the actual sample interval."""
        interval = c_double(sampleInterval)
        status = self._ps6000aRunStreaming(
            handle,
            byref(interval),
            sampleIntervalTimeUnits,
            maxPreTriggerSamples,
            maxPostTriggerSamples,
            autoStop,
            downSampleRatio,
            downSampleRatioMode,
        )
        return status, interval.value

    def ps6000aGetStreamingLatestValues(
        self,
        handle: c_int16,
        streamingDataInfo: Sequence[PICO_STREAMING_DATA_INFO],
    ) -> tuple[
        PICO_STATUS,
        list[PICO_STREAMING_DATA_INFO],
        PICO_STREAMING_DATA_TRIGGER_INFO,
    ]:
        """Returns the status, the updated ``streamingDataInfo`` and trigger info.

        A status of PICO_WAITING_FOR_DATA_BUFFERS is informational: new buffers
        have to be set before the driver continues.
        """
        infos = (PICO_STREAMING_DATA_INFO * len(streamingDataInfo))(*streamingDataInfo)
        triggerInfo = PICO_STREAMING_DATA_TRIGGER_INFO()
        status = self._ps6000aGetStreamingLatestValues(
            handle, infos, len(streamingDataInfo), byref(triggerInfo)
        )
        return status, list(infos), triggerInfo

    def ps6000aNoOfStreamingValues(self, handle: c_int16) -> tuple[PICO_STATUS, int]:
        noOfValues = c_uint64(0)
        status = self._ps6000aNoOfStreamingValues(handle, byref(noOfValues))
        return status, noOfValues.value

    def ps6000aSetDataBuffer(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        buffer: "DataBuffer",
        nsamples: int,
        datatype: PICO_DATA_TYPE,
        waveform: int,
        downsampleMode: PICO_RATIO_MODE,
        action: PICO_ACTION,
    ):
        assert nsamples >= 0
        return self._ps6000aSetDataBuffer(
            handle,
            channel,
            buffer,
            nsamples,
            datatype,
            waveform,
            downsampleMode,
            action,
        )

    def ps6000aSetDataBuffers(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        bufferMax: "DataBuffer",
        bufferMin: "DataBuffer",
        nSamples: int,
        dataType: PICO_DATA_TYPE,
        waveform: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        action: PICO_ACTION,
    ) -> PICO_STATUS:
        return self._ps6000aSetDataBuffers(
            handle,
            channel,
            bufferMax,
            bufferMin,
            nSamples,
            dataType,
            waveform,
            downSampleRatioMode,
            action,
        )

    def ps6000aGetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int, PICO_CHANNEL_FLAGS]:
        """Returns the status, the number of samples retrieved, and the overflows."""
        noOfSamples_ = c_uint64(noOfSamples)
        overflow = c_int16(0)
        status = self._ps6000aGetValues(
            handle,
            startIndex,
            byref(noOfSamples_),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return status, noOfSamples_.value, PICO_CHANNEL_FLAGS(overflow.value)

    def ps6000aGetValuesBulk(
        self,
        handle: c_int16,
        startindex: int,
        nosamples: int,
        fromSegment: int,
        toSegment: int,
        downsampleRatio: int,
        downsampleMode: PICO_RATIO_MODE,
    ):
        assert startindex >= 0
        assert nosamples > 0
        assert fromSegment <= toSegment
        nosamples_ = c_uint64(nosamples)
        nsegments = (toSegment - fromSegment) + 1
        overflow = (c_int16 * nsegments)()
        return (
            self._ps6000aGetValuesBulk(
                handle,
                startindex,
                byref(nosamples_),
                fromSegment,
                toSegment,
                downsampleRatio,
                downsampleMode,
                overflow,
            ),
            nosamples_.value,
            [PICO_CHANNEL_FLAGS(f) for f in overflow],
        )

    def _data_ready(
        self,
        callback: Callable[[int, PICO_STATUS, int, PICO_CHANNEL_FLAGS], None],
    ) -> Any:
        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: int | None
        ) -> None:
            callback(
                handle, PICO_STATUS(status), noOfSamples, PICO_CHANNEL_FLAGS(overflow)
            )

        return ps6000aDataReady(cbwrapper)

    def ps6000aGetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        segmentIndex: int,
        callback: Callable[[int, PICO_STATUS, int, PICO_CHANNEL_FLAGS], None],
    ) -> PICO_STATUS:
        """``callback(handle, status, noOfSamples, overflow)`` is called when done."""
        lpDataReady = self._data_ready(callback)
        return self._with_callback(
            self._callback_key("ps6000aGetValuesAsync", handle),
            lpDataReady,
            lambda: self._ps6000aGetValuesAsync(
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

    def ps6000aGetValuesBulkAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        fromSegmentIndex: int,
        toSegmentIndex: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        callback: Callable[[int, PICO_STATUS, int, PICO_CHANNEL_FLAGS], None],
    ) -> PICO_STATUS:
        """``callback(handle, status, noOfSamples, overflow)`` is called when done."""
        lpDataReady = self._data_ready(callback)
        return self._with_callback(
            self._callback_key("ps6000aGetValuesBulkAsync", handle),
            lpDataReady,
            lambda: self._ps6000aGetValuesBulkAsync(
                handle,
                startIndex,
                noOfSamples,
                fromSegmentIndex,
                toSegmentIndex,
                downSampleRatio,
                downSampleRatioMode,
                lpDataReady,
                None,
            ),
        )

    def ps6000aGetValuesOverlapped(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[PICO_STATUS, c_uint64, "Array[c_int16]"]:
        """Set up the data retrieval to happen after the next capture.

        The driver fills in the number of samples and the per-segment overflow
        flags only once the capture is complete, so they are returned as the
        ctypes objects the driver writes to (read ``.value`` / the elements
        later). They are kept alive by this wrapper until replaced.
        """
        assert fromSegmentIndex <= toSegmentIndex
        nsegments = (toSegmentIndex - fromSegmentIndex) + 1
        noOfSamples_ = c_uint64(noOfSamples)
        overflow = (c_int16 * nsegments)()
        status = self._with_callback(
            self._callback_key("ps6000aGetValuesOverlapped", handle),
            (noOfSamples_, overflow),
            lambda: self._ps6000aGetValuesOverlapped(
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

    def ps6000aStopUsingGetValuesOverlapped(self, handle: c_int16) -> PICO_STATUS:
        return self._ps6000aStopUsingGetValuesOverlapped(handle)

    def ps6000aStop(self, handle: c_int16) -> PICO_STATUS:
        return self._ps6000aStop(handle)

    def ps6000aGetTriggerInfo(
        self, handle: c_int16, firstSegmentIndex: int, segmentCount: int
    ) -> tuple[PICO_STATUS, list[PICO_TRIGGER_INFO]]:
        assert segmentCount > 0
        triggerInfo = (PICO_TRIGGER_INFO * segmentCount)()
        status = self._ps6000aGetTriggerInfo(
            handle, triggerInfo, firstSegmentIndex, segmentCount
        )
        return status, list(triggerInfo)

    def ps6000aGetAutoTriggerStatus(
        self, handle: c_int16, firstSegmentIndex: int, segmentCount: int
    ) -> tuple[PICO_STATUS, list[PICO_AUTO_TRIGGER_STATUS]]:
        assert segmentCount > 0
        autoTriggerStatus = (PICO_AUTO_TRIGGER_STATUS_T * segmentCount)()
        status = self._ps6000aGetAutoTriggerStatus(
            handle, autoTriggerStatus, firstSegmentIndex, segmentCount
        )
        return status, [PICO_AUTO_TRIGGER_STATUS(s) for s in autoTriggerStatus]

    def ps6000aEnumerateUnits(self) -> tuple[PICO_STATUS, int, list[str]]:
        """Returns the status, the number of units, and their serial numbers."""
        count = c_int16(0)
        serials = create_string_buffer(4096)
        serialLth = c_int16(len(serials))
        status = self._ps6000aEnumerateUnits(byref(count), serials, byref(serialLth))
        text = serials.value.decode("utf-8")
        return status, count.value, [s for s in text.split(",") if s]

    def ps6000aPingUnit(self, handle: c_int16) -> PICO_STATUS:
        return self._ps6000aPingUnit(handle)

    def ps6000aGetAnalogueOffsetLimits(
        self,
        handle: c_int16,
        range: PICO_CONNECT_PROBE_RANGE,
        coupling: PICO_COUPLING,
    ) -> tuple[PICO_STATUS, float, float]:
        """Returns the status, the maximum and the minimum analogue offset."""
        maximumVoltage = c_double(0)
        minimumVoltage = c_double(0)
        status = self._ps6000aGetAnalogueOffsetLimits(
            handle, range, coupling, byref(maximumVoltage), byref(minimumVoltage)
        )
        return status, maximumVoltage.value, minimumVoltage.value

    def ps6000aSetDeviceResolution(
        self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION
    ) -> PICO_STATUS:
        return self._ps6000aSetDeviceResolution(handle, resolution)

    def ps6000aGetDeviceResolution(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, PICO_DEVICE_RESOLUTION]:
        resolution = PICO_DEVICE_RESOLUTION_T(0)
        status = self._ps6000aGetDeviceResolution(handle, byref(resolution))
        return status, PICO_DEVICE_RESOLUTION(resolution.value)

    def ps6000aQueryOutputEdgeDetect(self, handle: c_int16) -> tuple[PICO_STATUS, bool]:
        state = c_int16(0)
        status = self._ps6000aQueryOutputEdgeDetect(handle, byref(state))
        return status, state.value != 0

    def ps6000aSetOutputEdgeDetect(self, handle: c_int16, state: bool) -> PICO_STATUS:
        return self._ps6000aSetOutputEdgeDetect(handle, state)

    def ps6000aGetScalingValues(
        self, handle: c_int16, nChannels: int
    ) -> tuple[PICO_STATUS, list[PICO_SCALING_FACTORS_VALUES]]:
        """Returns the scaling values of the first ``nChannels`` channels."""
        assert nChannels > 0
        scalingValues = (PICO_SCALING_FACTORS_VALUES * nChannels)()
        for i, values in enumerate(scalingValues):
            values.channel = PICO_CHANNEL.PICO_CHANNEL_A + i
        status = self._ps6000aGetScalingValues(handle, scalingValues, nChannels)
        return status, list(scalingValues)

    def ps6000aCheckForUpdate(
        self, handle: c_int16, nFirmwareInfos: int = 16
    ) -> tuple[PICO_STATUS, list[PICO_FIRMWARE_INFO], int]:
        """Returns the status, the firmware infos, and the updates-required flags.

        ``nFirmwareInfos`` is the size of the buffer for the firmware infos.
        """
        firmwareInfos = (PICO_FIRMWARE_INFO * nFirmwareInfos)()
        n = c_int16(nFirmwareInfos)
        updatesRequired = c_uint16(0)
        status = self._ps6000aCheckForUpdate(
            handle, firmwareInfos, byref(n), byref(updatesRequired)
        )
        count = max(0, min(n.value, nFirmwareInfos))
        return status, list(firmwareInfos[:count]), updatesRequired.value

    def ps6000aStartFirmwareUpdate(
        self, handle: c_int16, progress: Callable[[int, int], None] | None
    ) -> PICO_STATUS:
        """``progress(handle, percent)`` is called while the update is running."""
        cfunc = PicoUpdateFirmwareProgress()
        if progress is not None:

            def cbwrapper(handle: int, percent: int) -> None:
                progress(handle, percent)

            cfunc = PicoUpdateFirmwareProgress(cbwrapper)
        return self._with_callback(
            self._callback_key("ps6000aStartFirmwareUpdate", handle),
            cfunc,
            lambda: self._ps6000aStartFirmwareUpdate(handle, cfunc),
        )

    def ps6000aResetChannelsAndReportAllChannelsOvervoltageTripStatus(
        self, handle: c_int16, nChannelTrippedStatus: int
    ) -> tuple[PICO_STATUS, list[PICO_CHANNEL_OVERVOLTAGE_TRIPPED]]:
        assert 0 < nChannelTrippedStatus < 256
        tripped = (PICO_CHANNEL_OVERVOLTAGE_TRIPPED * nChannelTrippedStatus)()
        status = self._ps6000aResetChannelsAndReportAllChannelsOvervoltageTripStatus(
            handle, tripped, nChannelTrippedStatus
        )
        return status, list(tripped)

    def ps6000aReportAllChannelsOvervoltageTripStatus(
        self, handle: c_int16, nChannelTrippedStatus: int
    ) -> tuple[PICO_STATUS, list[PICO_CHANNEL_OVERVOLTAGE_TRIPPED]]:
        assert 0 < nChannelTrippedStatus < 256
        tripped = (PICO_CHANNEL_OVERVOLTAGE_TRIPPED * nChannelTrippedStatus)()
        status = self._ps6000aReportAllChannelsOvervoltageTripStatus(
            handle, tripped, nChannelTrippedStatus
        )
        return status, list(tripped)

    def ps6000aRunAutomaticOffsetAdjustment(
        self, handle: c_int16, calType: PICO_CAL_TYPE
    ) -> PICO_STATUS:
        return self._ps6000aRunAutomaticOffsetAdjustment(handle, calType)

    def ps6000aCommitCurrentAdjustmentSettingsToDevice(
        self, handle: c_int16, calType: PICO_CAL_TYPE
    ) -> PICO_STATUS:
        return self._ps6000aCommitCurrentAdjustmentSettingsToDevice(handle, calType)

    def ps6000aResetAdjustmentSettings(
        self, handle: c_int16, calType: PICO_CAL_TYPE
    ) -> PICO_STATUS:
        return self._ps6000aResetAdjustmentSettings(handle, calType)

    def ps6000aSetAdjustmentSettingDetails(
        self,
        handle: c_int16,
        calType: PICO_CAL_TYPE,
        nameString: str | None,
        addressString: str | None,
    ) -> PICO_STATUS:
        """Set the name and/or address; pass None to leave one unchanged."""
        name = nameString.encode() if nameString is not None else None
        address = addressString.encode() if addressString is not None else None
        # The lengths include the NUL terminator.
        nameLength = byref(c_int32(len(name) + 1)) if name is not None else None
        addressLength = (
            byref(c_int32(len(address) + 1)) if address is not None else None
        )
        return self._ps6000aSetAdjustmentSettingDetails(
            handle, calType, name, nameLength, address, addressLength
        )

    def ps6000aGetAdjustmentSettingDetails(
        self,
        handle: c_int16,
        calType: PICO_CAL_TYPE,
        textFormat: PICO_TEXT_FORMAT = PICO_TEXT_FORMAT.PICO_JSON_DATA,
    ) -> tuple[PICO_STATUS, str]:
        """Returns the status and the adjustment setting details (JSON)."""
        stringLength = c_int32(0)
        # Query the required length first; errors are reported by the second call.
        with errstate(all="ignore"):
            _ = self._ps6000aGetAdjustmentSettingDetails(
                handle, calType, None, byref(stringLength), textFormat
            )
        buf = create_string_buffer(max(stringLength.value, 1))
        stringLength = c_int32(len(buf))
        status = self._ps6000aGetAdjustmentSettingDetails(
            handle, calType, buf, byref(stringLength), textFormat
        )
        return status, buf.value.decode("utf-8")

    # ps6000aApiExperimental.h

    def ps6000aSetDigitalPortInteractionCallback(
        self,
        handle: c_int16,
        callback: Callable[
            [int, PICO_STATUS, list[PICO_DIGITAL_PORT_INTERACTIONS]], None
        ]
        | None,
    ) -> PICO_STATUS:
        """``callback(handle, status, ports)`` is called on MSO pod changes.

        ``ports`` are copies, valid beyond the callback.
        """
        cfunc = ps6000aDigitalPortInteractions()
        if callback is not None:

            def cbwrapper(handle: int, status: int, ports: Any, nPorts: int) -> None:
                copies = (
                    [
                        PICO_DIGITAL_PORT_INTERACTIONS.from_buffer_copy(ports[i])
                        for i in range(nPorts)
                    ]
                    if ports
                    else []
                )
                callback(handle, PICO_STATUS(status), copies)

            cfunc = ps6000aDigitalPortInteractions(cbwrapper)
        return self._with_callback(
            self._callback_key("ps6000aSetDigitalPortInteractionCallback", handle),
            cfunc,
            lambda: self._ps6000aSetDigitalPortInteractionCallback(handle, cfunc),
        )

    def ps6000aSetProbeInteractionCallback(
        self,
        handle: c_int16,
        callback: Callable[[int, PICO_STATUS, list[PICO_USER_PROBE_INTERACTIONS]], None]
        | None,
    ) -> PICO_STATUS:
        """``callback(handle, status, probes)`` is called on probe changes.

        ``probes`` are copies, valid beyond the callback.
        """
        cfunc = PicoProbeInteractions()
        if callback is not None:

            def cbwrapper(handle: int, status: int, probes: Any, nProbes: int) -> None:
                copies = (
                    [
                        PICO_USER_PROBE_INTERACTIONS.from_buffer_copy(probes[i])
                        for i in range(nProbes)
                    ]
                    if probes
                    else []
                )
                callback(handle, PICO_STATUS(status), copies)

            cfunc = PicoProbeInteractions(cbwrapper)
        return self._with_callback(
            self._callback_key("ps6000aSetProbeInteractionCallback", handle),
            cfunc,
            lambda: self._ps6000aSetProbeInteractionCallback(handle, cfunc),
        )

    def ps6000aSetExternalReferenceInteractionCallback(
        self,
        handle: c_int16,
        callback: Callable[[int, PICO_STATUS, PICO_CLOCK_REFERENCE], None] | None,
    ):
        cfunc = PicoExternalReferenceInteractions()
        if callback is not None:

            def cbwrapper(handle: int, status: int, reference: int) -> None:
                callback(handle, PICO_STATUS(status), PICO_CLOCK_REFERENCE(reference))

            cfunc = PicoExternalReferenceInteractions(cbwrapper)
        return self._with_callback(
            self._callback_key(
                "ps6000aSetExternalReferenceInteractionCallback", handle
            ),
            cfunc,
            lambda: self._ps6000aSetExternalReferenceInteractionCallback(handle, cfunc),
        )

    def ps6000aSetAWGOverrangeInteractionCallback(
        self,
        handle: c_int16,
        callback: Callable[[int, PICO_STATUS], None] | None,
    ) -> PICO_STATUS:
        cfunc = PicoAWGOverrangeInteractions()
        if callback is not None:

            def cbwrapper(handle: int, status: int) -> None:
                callback(handle, PICO_STATUS(status))

            cfunc = PicoAWGOverrangeInteractions(cbwrapper)
        return self._with_callback(
            self._callback_key("ps6000aSetAWGOverrangeInteractionCallback", handle),
            cfunc,
            lambda: self._ps6000aSetAWGOverrangeInteractionCallback(handle, cfunc),
        )

    def ps6000aSetTemperatureSensorInteractionCallback(
        self,
        handle: c_int16,
        callback: Callable[[int, PICO_TEMPERATURE_REFERENCE], None] | None,
    ) -> PICO_STATUS:
        cfunc = PicoTemperatureSensorInteractions()
        if callback is not None:

            def cbwrapper(handle: int, temperatureStatus: int) -> None:
                callback(handle, PICO_TEMPERATURE_REFERENCE(temperatureStatus))

            cfunc = PicoTemperatureSensorInteractions(cbwrapper)
        return self._with_callback(
            self._callback_key(
                "ps6000aSetTemperatureSensorInteractionCallback", handle
            ),
            cfunc,
            lambda: self._ps6000aSetTemperatureSensorInteractionCallback(handle, cfunc),
        )

    def ps6000aSetProbeUserActionCallback(
        self,
        handle: c_int16,
        callback: Callable[
            [
                int,
                PICO_STATUS,
                PICO_CHANNEL,
                PICO_CONNECT_PROBE,
                PICO_PROBE_USER_ACTION,
                PICO_PROBE_BUTTON_PRESS_PARAMETER | None,
            ],
            None,
        ]
        | None,
    ) -> PICO_STATUS:
        """``callback(handle, status, channel, probe, action, actionParameter)``.

        ``actionParameter`` is a copy of the action's parameter struct (a
        PICO_PROBE_BUTTON_PRESS_PARAMETER for PICO_PROBE_BUTTON_PRESS), or None.
        Requires a probe interaction callback to be set first.
        """
        cfunc = PicoProbeUserAction()
        if callback is not None:

            def cbwrapper(
                handle: int,
                status: int,
                channel: int,
                probe: int,
                action: int,
                pActionParameter: int | None,
                _: int | None,
            ) -> None:
                parameter = None
                if pActionParameter and (
                    action == PICO_PROBE_USER_ACTION.PICO_PROBE_BUTTON_PRESS
                ):
                    parameter = PICO_PROBE_BUTTON_PRESS_PARAMETER.from_buffer_copy(
                        PICO_PROBE_BUTTON_PRESS_PARAMETER.from_address(pActionParameter)
                    )
                callback(
                    handle,
                    PICO_STATUS(status),
                    PICO_CHANNEL(channel),
                    PICO_CONNECT_PROBE(probe),
                    PICO_PROBE_USER_ACTION(action),
                    parameter,
                )

            cfunc = PicoProbeUserAction(cbwrapper)
        return self._with_callback(
            self._callback_key("ps6000aSetProbeUserActionCallback", handle),
            cfunc,
            lambda: self._ps6000aSetProbeUserActionCallback(handle, cfunc, None),
        )


__all__ = (
    "PICO_PROBE_BUTTON_PRESS_PARAMETER",
    "PICO_PROBE_BUTTON_PRESS_TYPE",
    "PICO_PROBE_BUTTON_PRESS_TYPE_T",
    "PICO_PROBE_USER_ACTION",
    "PICO_PROBE_USER_ACTION_T",
    "PicoProbeUserAction",
    "PicoScope6000aWrapper",
    "ps6000aBlockReady",
    "ps6000aDataReady",
    "ps6000aDigitalPortInteractions",
    "ps6000aProbeInteractions",
)
