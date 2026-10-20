from collections.abc import Callable, Sequence
from _ctypes import CFuncPtr
from typing import Self, final
from ctypes import (
    POINTER,
    Array,
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

from ._device import PicoScopeDeviceBase, handle_method, wrapper_function
from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase
from ._buffer import (
    SAMPLE_TYPES,
    DataBuffer,
    InputValues,
    buffer_argument,
    input_argument,
)
from ._struct import c_array
from .callback import PicoUpdateFirmwareProgress
from .connectprobe import (
    PICO_PROBE_RANGE_INFO,
    PICO_PROBE_RANGE_INFO_T,
)
from .deviceenums import (
    PICO_ACTION,
    PICO_ACTION_T,
    PICO_AUXIO_MODE,
    PICO_AUXIO_MODE_T,
    PICO_BANDWIDTH_LIMITER,
    PICO_BANDWIDTH_LIMITER_T,
    PICO_CHANNEL,
    PICO_CHANNEL_FLAGS,
    PICO_CHANNEL_FLAGS_T,
    PICO_CHANNEL_T,
    PICO_COUPLING,
    PICO_COUPLING_T,
    PICO_DATA_TYPE,
    PICO_DATA_TYPE_T,
    PICO_DEVICE_RESOLUTION,
    PICO_DEVICE_RESOLUTION_T,
    PICO_PULSE_WIDTH_TYPE,
    PICO_PULSE_WIDTH_TYPE_T,
    PICO_RATIO_MODE,
    PICO_RATIO_MODE_T,
    PICO_SIGGEN_PARAMETER,
    PICO_SIGGEN_PARAMETER_T,
    PICO_SIGGEN_TRIG_SOURCE,
    PICO_SIGGEN_TRIG_SOURCE_T,
    PICO_SIGGEN_TRIG_TYPE,
    PICO_SIGGEN_TRIG_TYPE_T,
    PICO_SWEEP_TYPE,
    PICO_SWEEP_TYPE_T,
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
    PICO_DIRECTION,
    PICO_LED_COLOUR_PROPERTIES,
    PICO_LED_STATE_PROPERTIES,
    PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES,
    PICO_STREAMING_DATA_INFO,
    PICO_STREAMING_DATA_TRIGGER_INFO,
    PICO_TRIGGER_CHANNEL_PROPERTIES,
    PICO_TRIGGER_INFO,
    PICO_USB_POWER_DETAILS,
)
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T
from .version import PICO_FIRMWARE_INFO

psospaBlockReady = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)
psospaDataReady = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, c_uint64, c_int16, c_void_p
)

# Upper bound of firmware components reported by psospaCheckForUpdate.
_MAX_FIRMWARE_INFOS = 16
# Size of the buffer receiving the serial numbers in psospaEnumerateUnits.
_ENUMERATE_BUFFER_SIZE = 4096


def _range_value(value: float) -> int:
    # Ranges are given in nano-units (e.g. nV); floats are taken as base units.
    if isinstance(value, float):
        return round(1e9 * value)
    return value


class PicoScope3000eWrapper(PicoScopeWrapperBase):
    # TODO: Rename the parameters that differ from the C prototypes:
    # GetMinimumTimebaseStateless/NearestSampleIntervalStateless (enabledChannels
    # -> enabledChannelFlags), GetValuesBulk (startindex, nosamples, fromSegment,
    # toSegment, downsampleRatio, downsampleMode), MemorySegments (nsegments),
    # MemorySegmentsBySamples (nsamples), QueryMaxSegmentsBySamples (nsamples,
    # nchannels -> nChannelEnabled), RunBlock (preSamples, postSamples, segment,
    # callback -> noOfPreTriggerSamples, noOfPostTriggerSamples, segmentIndex,
    # lpReady), SetChannelOn (analog_offset), SetDataBuffer (nsamples, datatype,
    # downsampleMode), SetDigitalPortOn (logicThreshold ->
    # logicThresholdLevelVolts), SetNoOfCaptures (ncaptures) and SetSimpleTrigger
    # (autoTriggerUS -> autoTriggerMicroSeconds).
    _library_name = "psospa"

    def __init__(self, library_path: str | None = None) -> None:
        super().__init__(library_path)

        # The device opened fine, but is connected to a USB 2.0 port; or the handle
        # is valid, but all other calls fail until psospaStartFirmwareUpdate is
        # called (3000E guide).
        self._psospaOpenUnit = self._bind(
            "psospaOpenUnit",
            [
                POINTER(c_int16),
                c_char_p,
                PICO_DEVICE_RESOLUTION_T,
                POINTER(PICO_USB_POWER_DETAILS.c_type),
            ],
            info={
                PICO_STATUS.PICO_USB3_0_DEVICE_NON_USB3_0_PORT,
                PICO_STATUS.PICO_FIRMWARE_UPDATE_REQUIRED_TO_USE_DEVICE_WITH_THIS_DRIVER,
            },
        )
        self._psospaGetUnitInfo = self._bind(
            "psospaGetUnitInfo",
            [c_int16, c_char_p, c_int16, POINTER(c_int16), PICO_INFO_T],
        )
        self._psospaGetVariantDetails = self._bind(
            "psospaGetVariantDetails",
            [c_char_p, c_int16, c_char_p, POINTER(c_int32), PICO_TEXT_FORMAT_T],
        )
        self._psospaCloseUnit = self._bind("psospaCloseUnit", [c_int16])
        self._psospaMemorySegments = self._bind(
            "psospaMemorySegments", [c_int16, c_uint64, POINTER(c_uint64)]
        )
        self._psospaMemorySegmentsBySamples = self._bind(
            "psospaMemorySegmentsBySamples", [c_int16, c_uint64, POINTER(c_uint64)]
        )
        self._psospaGetMaximumAvailableMemory = self._bind(
            "psospaGetMaximumAvailableMemory",
            [c_int16, POINTER(c_uint64), PICO_DEVICE_RESOLUTION_T],
        )
        self._psospaQueryMaxSegmentsBySamples = self._bind(
            "psospaQueryMaxSegmentsBySamples",
            [c_int16, c_uint64, c_uint32, POINTER(c_uint64), PICO_DEVICE_RESOLUTION_T],
        )
        self._psospaSetChannelOn = self._bind(
            "psospaSetChannelOn",
            [
                c_int16,
                PICO_CHANNEL_T,
                PICO_COUPLING_T,
                c_int64,
                c_int64,
                PICO_PROBE_RANGE_INFO_T,
                c_double,
                PICO_BANDWIDTH_LIMITER_T,
            ],
        )
        self._psospaSetChannelOff = self._bind(
            "psospaSetChannelOff", [c_int16, PICO_CHANNEL_T]
        )
        self._psospaSetDigitalPortOn = self._bind(
            "psospaSetDigitalPortOn", [c_int16, PICO_CHANNEL_T, c_double]
        )
        self._psospaSetDigitalPortOff = self._bind(
            "psospaSetDigitalPortOff", [c_int16, PICO_CHANNEL_T]
        )
        self._psospaGetTimebase = self._bind(
            "psospaGetTimebase",
            [
                c_int16,
                c_uint32,
                c_uint64,
                POINTER(c_double),
                POINTER(c_uint64),
                c_uint64,
            ],
        )
        self._psospaSigGenWaveform = self._bind(
            "psospaSigGenWaveform", [c_int16, PICO_WAVE_TYPE_T, c_void_p, c_uint64]
        )
        self._psospaSigGenRange = self._bind(
            "psospaSigGenRange", [c_int16, c_double, c_double]
        )
        self._psospaSigGenWaveformDutyCycle = self._bind(
            "psospaSigGenWaveformDutyCycle", [c_int16, c_double]
        )
        self._psospaSigGenTrigger = self._bind(
            "psospaSigGenTrigger",
            [
                c_int16,
                PICO_SIGGEN_TRIG_TYPE_T,
                PICO_SIGGEN_TRIG_SOURCE_T,
                c_uint64,
                c_uint64,
            ],
        )
        self._psospaSigGenFrequency = self._bind(
            "psospaSigGenFrequency", [c_int16, c_double]
        )
        self._psospaSigGenFrequencySweep = self._bind(
            "psospaSigGenFrequencySweep",
            [c_int16, c_double, c_double, c_double, PICO_SWEEP_TYPE_T],
        )
        self._psospaSigGenPhase = self._bind("psospaSigGenPhase", [c_int16, c_uint64])
        self._psospaSigGenPhaseSweep = self._bind(
            "psospaSigGenPhaseSweep",
            [c_int16, c_uint64, c_uint64, c_uint64, PICO_SWEEP_TYPE_T],
        )
        self._psospaSigGenSoftwareTriggerControl = self._bind(
            "psospaSigGenSoftwareTriggerControl", [c_int16, PICO_SIGGEN_TRIG_TYPE_T]
        )
        self._psospaSigGenApply = self._bind(
            "psospaSigGenApply",
            [
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
        self._psospaSigGenLimits = self._bind(
            "psospaSigGenLimits",
            [
                c_int16,
                PICO_SIGGEN_PARAMETER_T,
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
            ],
        )
        self._psospaSigGenFrequencyLimits = self._bind(
            "psospaSigGenFrequencyLimits",
            [
                c_int16,
                PICO_WAVE_TYPE_T,
                POINTER(c_uint64),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
                POINTER(c_double),
            ],
        )
        self._psospaSigGenPause = self._bind("psospaSigGenPause", [c_int16])
        self._psospaSigGenRestart = self._bind("psospaSigGenRestart", [c_int16])
        self._psospaSetSimpleTrigger = self._bind(
            "psospaSetSimpleTrigger",
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
        self._psospaTriggerWithinPreTriggerSamples = self._bind(
            "psospaTriggerWithinPreTriggerSamples",
            [c_int16, PICO_TRIGGER_WITHIN_PRE_TRIGGER_T],
        )
        self._psospaSetTriggerChannelProperties = self._bind(
            "psospaSetTriggerChannelProperties",
            [
                c_int16,
                POINTER(PICO_TRIGGER_CHANNEL_PROPERTIES.c_type),
                c_int16,
                c_uint32,
            ],
        )
        self._psospaSetTriggerChannelConditions = self._bind(
            "psospaSetTriggerChannelConditions",
            [c_int16, POINTER(PICO_CONDITION.c_type), c_int16, PICO_ACTION_T],
        )
        self._psospaSetTriggerChannelDirections = self._bind(
            "psospaSetTriggerChannelDirections",
            [c_int16, POINTER(PICO_DIRECTION.c_type), c_int16],
        )
        self._psospaSetTriggerDelay = self._bind(
            "psospaSetTriggerDelay", [c_int16, c_uint64]
        )
        self._psospaSetTriggerHoldoffCounterBySamples = self._bind(
            "psospaSetTriggerHoldoffCounterBySamples", [c_int16, c_uint64]
        )
        self._psospaSetPulseWidthQualifierProperties = self._bind(
            "psospaSetPulseWidthQualifierProperties",
            [c_int16, c_uint32, c_uint32, PICO_PULSE_WIDTH_TYPE_T],
        )
        self._psospaSetPulseWidthQualifierConditions = self._bind(
            "psospaSetPulseWidthQualifierConditions",
            [c_int16, POINTER(PICO_CONDITION.c_type), c_int16, PICO_ACTION_T],
        )
        self._psospaSetPulseWidthQualifierDirections = self._bind(
            "psospaSetPulseWidthQualifierDirections",
            [c_int16, POINTER(PICO_DIRECTION.c_type), c_int16],
        )
        self._psospaSetTriggerDigitalPortProperties = self._bind(
            "psospaSetTriggerDigitalPortProperties",
            [
                c_int16,
                PICO_CHANNEL_T,
                POINTER(PICO_DIGITAL_CHANNEL_DIRECTIONS.c_type),
                c_int16,
            ],
        )
        self._psospaSetPulseWidthDigitalPortProperties = self._bind(
            "psospaSetPulseWidthDigitalPortProperties",
            [
                c_int16,
                PICO_CHANNEL_T,
                POINTER(PICO_DIGITAL_CHANNEL_DIRECTIONS.c_type),
                c_int16,
            ],
        )
        self._psospaGetTriggerTimeOffset = self._bind(
            "psospaGetTriggerTimeOffset",
            [c_int16, POINTER(c_int64), POINTER(PICO_TIME_UNITS_T), c_uint64],
        )
        self._psospaGetValuesTriggerTimeOffsetBulk = self._bind(
            "psospaGetValuesTriggerTimeOffsetBulk",
            [
                c_int16,
                POINTER(c_int64),
                POINTER(PICO_TIME_UNITS_T),
                c_uint64,
                c_uint64,
            ],
        )
        self._psospaSetDataBuffer = self._bind(
            "psospaSetDataBuffer",
            [
                c_int16,
                PICO_CHANNEL_T,
                c_void_p,
                c_uint64,
                PICO_DATA_TYPE_T,
                c_uint64,
                PICO_RATIO_MODE_T,
                PICO_ACTION_T,
            ],
        )
        self._psospaSetDataBuffers = self._bind(
            "psospaSetDataBuffers",
            [
                c_int16,
                PICO_CHANNEL_T,
                c_void_p,
                c_void_p,
                c_uint64,
                PICO_DATA_TYPE_T,
                c_uint64,
                PICO_RATIO_MODE_T,
                PICO_ACTION_T,
            ],
        )
        self._psospaRunBlock = self._bind(
            "psospaRunBlock",
            [
                c_int16,
                c_uint64,
                c_uint64,
                c_uint32,
                POINTER(c_double),
                c_uint64,
                psospaBlockReady,
                c_void_p,
            ],
        )
        self._psospaIsReady = self._bind("psospaIsReady", [c_int16, POINTER(c_int16)])
        self._psospaRunStreaming = self._bind(
            "psospaRunStreaming",
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
        # The driver needs new data buffers before it can hand out more data;
        # this is part of the regular streaming flow, not a failure.
        self._psospaGetStreamingLatestValues = self._bind(
            "psospaGetStreamingLatestValues",
            [
                c_int16,
                POINTER(PICO_STREAMING_DATA_INFO.c_type),
                c_uint64,
                POINTER(PICO_STREAMING_DATA_TRIGGER_INFO.c_type),
            ],
            info={PICO_STATUS.PICO_WAITING_FOR_DATA_BUFFERS},
        )
        self._psospaNoOfStreamingValues = self._bind(
            "psospaNoOfStreamingValues", [c_int16, POINTER(c_uint64)]
        )
        self._psospaGetValues = self._bind(
            "psospaGetValues",
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
        self._psospaGetValuesBulk = self._bind(
            "psospaGetValuesBulk",
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
        # lpDataReady is declared as PICO_POINTER, but is a psospaDataReady.
        self._psospaGetValuesAsync = self._bind(
            "psospaGetValuesAsync",
            [
                c_int16,
                c_uint64,
                c_uint64,
                c_uint64,
                PICO_RATIO_MODE_T,
                c_uint64,
                psospaDataReady,
                c_void_p,
            ],
        )
        self._psospaGetValuesBulkAsync = self._bind(
            "psospaGetValuesBulkAsync",
            [
                c_int16,
                c_uint64,
                c_uint64,
                c_uint64,
                c_uint64,
                c_uint64,
                PICO_RATIO_MODE_T,
                psospaDataReady,
                c_void_p,
            ],
        )
        self._psospaGetValuesOverlapped = self._bind(
            "psospaGetValuesOverlapped",
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
        self._psospaStopUsingGetValuesOverlapped = self._bind(
            "psospaStopUsingGetValuesOverlapped", [c_int16]
        )
        self._psospaGetNoOfCaptures = self._bind(
            "psospaGetNoOfCaptures", [c_int16, POINTER(c_uint64)]
        )
        self._psospaGetNoOfProcessedCaptures = self._bind(
            "psospaGetNoOfProcessedCaptures", [c_int16, POINTER(c_uint64)]
        )
        self._psospaStop = self._bind("psospaStop", [c_int16])
        self._psospaSetNoOfCaptures = self._bind(
            "psospaSetNoOfCaptures", [c_int16, c_uint64]
        )
        self._psospaGetTriggerInfo = self._bind(
            "psospaGetTriggerInfo",
            [c_int16, POINTER(PICO_TRIGGER_INFO.c_type), c_uint64, c_uint64],
        )
        # No connected unit is a valid enumeration result.
        self._psospaEnumerateUnits = self._bind(
            "psospaEnumerateUnits",
            [POINTER(c_int16), c_char_p, POINTER(c_int16)],
            info={PICO_STATUS.PICO_NOT_FOUND},
        )
        self._psospaPingUnit = self._bind("psospaPingUnit", [c_int16])
        self._psospaGetAnalogueOffsetLimits = self._bind(
            "psospaGetAnalogueOffsetLimits",
            [
                c_int16,
                c_int64,
                c_int64,
                PICO_PROBE_RANGE_INFO_T,
                PICO_COUPLING_T,
                POINTER(c_double),
                POINTER(c_double),
            ],
        )
        self._psospaGetMinimumTimebaseStateless = self._bind(
            "psospaGetMinimumTimebaseStateless",
            [
                c_int16,
                PICO_CHANNEL_FLAGS_T,
                POINTER(c_uint32),
                POINTER(c_double),
                PICO_DEVICE_RESOLUTION_T,
            ],
        )
        self._psospaNearestSampleIntervalStateless = self._bind(
            "psospaNearestSampleIntervalStateless",
            [
                c_int16,
                PICO_CHANNEL_FLAGS_T,
                c_double,
                c_uint8,
                PICO_DEVICE_RESOLUTION_T,
                POINTER(c_uint32),
                POINTER(c_double),
            ],
        )
        self._psospaSetDeviceResolution = self._bind(
            "psospaSetDeviceResolution", [c_int16, PICO_DEVICE_RESOLUTION_T]
        )
        self._psospaGetDeviceResolution = self._bind(
            "psospaGetDeviceResolution", [c_int16, POINTER(PICO_DEVICE_RESOLUTION_T)]
        )
        self._psospaQueryOutputEdgeDetect = self._bind(
            "psospaQueryOutputEdgeDetect", [c_int16, POINTER(c_int16)]
        )
        self._psospaSetOutputEdgeDetect = self._bind(
            "psospaSetOutputEdgeDetect", [c_int16, c_int16]
        )
        self._psospaGetScalingValues = self._bind(
            "psospaGetScalingValues",
            [
                c_int16,
                POINTER(PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES.c_type),
                c_int16,
            ],
        )
        self._psospaGetAdcLimits = self._bind(
            "psospaGetAdcLimits",
            [c_int16, PICO_DEVICE_RESOLUTION_T, POINTER(c_int16), POINTER(c_int16)],
        )
        self._psospaCheckForUpdate = self._bind(
            "psospaCheckForUpdate",
            [
                c_int16,
                POINTER(PICO_FIRMWARE_INFO.c_type),
                POINTER(c_int16),
                POINTER(c_uint16),
            ],
        )
        # The guide documents PICO_FIRMWARE_UP_TO_DATE as the result of a
        # successful update (or of one that was not needed).
        self._psospaStartFirmwareUpdate = self._bind(
            "psospaStartFirmwareUpdate",
            [c_int16, PicoUpdateFirmwareProgress],
            info={PICO_STATUS.PICO_FIRMWARE_UP_TO_DATE},
        )
        self._psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus = self._bind(
            "psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus",
            [c_int16, POINTER(PICO_CHANNEL_OVERVOLTAGE_TRIPPED.c_type), c_uint8],
        )
        self._psospaReportAllChannelsOvervoltageTripStatus = self._bind(
            "psospaReportAllChannelsOvervoltageTripStatus",
            [c_int16, POINTER(PICO_CHANNEL_OVERVOLTAGE_TRIPPED.c_type), c_uint8],
        )
        self._psospaSetLedColours = self._bind(
            "psospaSetLedColours",
            [c_int16, POINTER(PICO_LED_COLOUR_PROPERTIES.c_type), c_uint32],
        )
        self._psospaSetLedBrightness = self._bind(
            "psospaSetLedBrightness", [c_int16, c_uint8]
        )
        self._psospaSetLedStates = self._bind(
            "psospaSetLedStates",
            [c_int16, POINTER(PICO_LED_STATE_PROPERTIES.c_type), c_uint32],
        )
        self._psospaSetAuxIoMode = self._bind(
            "psospaSetAuxIoMode", [c_int16, PICO_AUXIO_MODE_T]
        )
        # TODO: Wrap the functions the psospa guide documents for driver 1.0.178+
        # once the SDK headers declare them (up to 1.0.158, headers and library
        # lack them): psospaGetAutoTriggerStatus, psospaRunAutomaticOffsetAdjustment,
        # psospaCommitCurrentAdjustmentSettingsToDevice, psospaResetAdjustmentSettings,
        # psospaSetAdjustmentSettingDetails and psospaGetAdjustmentSettingDetails.
        # The ps6000a wrappers of the same functions can serve as a template.

    def psospaOpenUnit(
        self, serial: str | None, resolution: PICO_DEVICE_RESOLUTION
    ) -> tuple[c_int16, PICO_USB_POWER_DETAILS, PICO_STATUS]:
        """Returns the handle, the USB power details and the status.

        The status is PICO_OK, PICO_USB3_0_DEVICE_NON_USB3_0_PORT, or
        PICO_FIRMWARE_UPDATE_REQUIRED_TO_USE_DEVICE_WITH_THIS_DRIVER (all other
        calls fail until psospaStartFirmwareUpdate is called).
        """
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        usbpwrdet = PICO_USB_POWER_DETAILS.c_type()
        status = self._psospaOpenUnit(byref(handle), ser, resolution, byref(usbpwrdet))
        return handle, PICO_USB_POWER_DETAILS.from_c(usbpwrdet), status

    def psospaCloseUnit(self, handle: c_int16) -> None:
        self._psospaCloseUnit(handle)
        self._release_buffers(handle)

    def psospaGetUnitInfo(self, handle: c_int16, info: PICO_INFO) -> str:
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        self._psospaGetUnitInfo(handle, buf, 255, byref(size), info)
        return buf.raw[: size.value - 1].decode("utf-8")

    def psospaGetVariantDetails(
        self, variantName: str, textFormat: PICO_TEXT_FORMAT
    ) -> str:
        name = variantName.encode()
        length = c_int32(0)
        # The first call only queries the required buffer size.
        self._psospaGetVariantDetails(name, len(name), None, byref(length), textFormat)
        buf = create_string_buffer(length.value + 1)
        self._psospaGetVariantDetails(name, len(name), buf, byref(length), textFormat)
        return buf.value.decode("utf-8")

    def psospaMemorySegments(self, handle: c_int16, nsegments: int) -> int:
        assert nsegments > 0
        maxSamples = c_uint64(0)
        self._psospaMemorySegments(handle, nsegments, byref(maxSamples))
        return maxSamples.value

    def psospaMemorySegmentsBySamples(self, handle: c_int16, nsamples: int) -> int:
        assert nsamples > 0
        maxSegments = c_uint64(0)
        self._psospaMemorySegmentsBySamples(handle, nsamples, byref(maxSegments))
        return maxSegments.value

    def psospaGetMaximumAvailableMemory(
        self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION
    ) -> int:
        nMaxSamples = c_uint64(0)
        self._psospaGetMaximumAvailableMemory(handle, byref(nMaxSamples), resolution)
        return nMaxSamples.value

    def psospaQueryMaxSegmentsBySamples(
        self,
        handle: c_int16,
        nsamples: int,
        nchannels: int,
        resolution: PICO_DEVICE_RESOLUTION,
    ) -> int:
        maxSegments = c_uint64(0)
        self._psospaQueryMaxSegmentsBySamples(
            handle, nsamples, nchannels, byref(maxSegments), resolution
        )
        return maxSegments.value

    def psospaSetChannelOn(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        coupling: PICO_COUPLING,
        rangeMin: float,
        rangeMax: float,
        rangeType: PICO_PROBE_RANGE_INFO,
        analog_offset: float,
        bandwidth: PICO_BANDWIDTH_LIMITER,
    ) -> None:
        self._psospaSetChannelOn(
            handle,
            channel,
            coupling,
            _range_value(rangeMin),
            _range_value(rangeMax),
            rangeType,
            analog_offset,
            bandwidth,
        )

    def psospaSetChannelOff(self, handle: c_int16, channel: PICO_CHANNEL) -> None:
        self._psospaSetChannelOff(handle, channel)

    def psospaSetDigitalPortOn(
        self, handle: c_int16, port: PICO_CHANNEL, logicThreshold: float
    ) -> None:
        self._psospaSetDigitalPortOn(handle, port, logicThreshold)

    def psospaSetDigitalPortOff(self, handle: c_int16, port: PICO_CHANNEL) -> None:
        self._psospaSetDigitalPortOff(handle, port)

    def psospaGetTimebase(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ) -> tuple[float, int]:
        timeIntervalNS = c_double(0)
        maxSamples = c_uint64(0)
        self._psospaGetTimebase(
            handle,
            timebase,
            noSamples,
            byref(timeIntervalNS),
            byref(maxSamples),
            segmentIndex,
        )
        return timeIntervalNS.value, maxSamples.value

    def psospaSigGenWaveform(
        self, handle: c_int16, waveType: PICO_WAVE_TYPE, buffer: InputValues | None
    ) -> None:
        """``buffer`` holds the int16 arbitrary waveform samples (only for PICO_ARBITRARY).

        It is a sequence of ints or a buffer of int16 (e.g. a numpy array with
        ``dtype=np.int16``), which is passed without copying.
        """
        samples, bufferLength = (
            input_argument(buffer, c_int16, "buffer")
            if buffer is not None
            else (None, 0)
        )
        self._psospaSigGenWaveform(handle, waveType, samples, bufferLength)

    def psospaSigGenRange(
        self, handle: c_int16, peakToPeakVolts: float, offsetVolts: float
    ) -> None:
        self._psospaSigGenRange(handle, peakToPeakVolts, offsetVolts)

    def psospaSigGenWaveformDutyCycle(
        self, handle: c_int16, dutyCyclePercent: float
    ) -> None:
        self._psospaSigGenWaveformDutyCycle(handle, dutyCyclePercent)

    def psospaSigGenTrigger(
        self,
        handle: c_int16,
        triggerType: PICO_SIGGEN_TRIG_TYPE,
        triggerSource: PICO_SIGGEN_TRIG_SOURCE,
        cycles: int,
        autoTriggerPicoSeconds: int,
    ) -> None:
        self._psospaSigGenTrigger(
            handle, triggerType, triggerSource, cycles, autoTriggerPicoSeconds
        )

    def psospaSigGenFrequency(self, handle: c_int16, frequencyHz: float) -> None:
        self._psospaSigGenFrequency(handle, frequencyHz)

    def psospaSigGenFrequencySweep(
        self,
        handle: c_int16,
        stopFrequencyHz: float,
        frequencyIncrement: float,
        dwellTimeSeconds: float,
        sweepType: PICO_SWEEP_TYPE,
    ) -> None:
        self._psospaSigGenFrequencySweep(
            handle, stopFrequencyHz, frequencyIncrement, dwellTimeSeconds, sweepType
        )

    def psospaSigGenPhase(self, handle: c_int16, deltaPhase: int) -> None:
        self._psospaSigGenPhase(handle, deltaPhase)

    def psospaSigGenPhaseSweep(
        self,
        handle: c_int16,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PICO_SWEEP_TYPE,
    ) -> None:
        self._psospaSigGenPhaseSweep(
            handle, stopDeltaPhase, deltaPhaseIncrement, dwellCount, sweepType
        )

    def psospaSigGenSoftwareTriggerControl(
        self, handle: c_int16, triggerState: PICO_SIGGEN_TRIG_TYPE
    ) -> None:
        self._psospaSigGenSoftwareTriggerControl(handle, triggerState)

    def psospaSigGenApply(
        self,
        handle: c_int16,
        sigGenEnabled: bool,
        sweepEnabled: bool,
        triggerEnabled: bool,
    ) -> tuple[float, float, float, float]:
        frequency = c_double(0)
        stopFrequency = c_double(0)
        frequencyIncrement = c_double(0)
        dwellTime = c_double(0)
        self._psospaSigGenApply(
            handle,
            1 if sigGenEnabled else 0,
            1 if sweepEnabled else 0,
            1 if triggerEnabled else 0,
            byref(frequency),
            byref(stopFrequency),
            byref(frequencyIncrement),
            byref(dwellTime),
        )
        return (
            frequency.value,
            stopFrequency.value,
            frequencyIncrement.value,
            dwellTime.value,
        )

    def psospaSigGenLimits(
        self, handle: c_int16, parameter: PICO_SIGGEN_PARAMETER
    ) -> tuple[float, float, float]:
        minimumPermissibleValue = c_double(0)
        maximumPermissibleValue = c_double(0)
        step = c_double(0)
        self._psospaSigGenLimits(
            handle,
            parameter,
            byref(minimumPermissibleValue),
            byref(maximumPermissibleValue),
            byref(step),
        )
        return minimumPermissibleValue.value, maximumPermissibleValue.value, step.value

    def psospaSigGenFrequencyLimits(
        self, handle: c_int16, waveType: PICO_WAVE_TYPE, numSamples: int
    ) -> tuple[float, float, float, float, float, float]:
        numSamples_ = c_uint64(numSamples)
        minFrequency = c_double(0)
        maxFrequency = c_double(0)
        minFrequencyStep = c_double(0)
        maxFrequencyStep = c_double(0)
        minDwellTime = c_double(0)
        maxDwellTime = c_double(0)
        self._psospaSigGenFrequencyLimits(
            handle,
            waveType,
            byref(numSamples_),
            byref(minFrequency),
            byref(maxFrequency),
            byref(minFrequencyStep),
            byref(maxFrequencyStep),
            byref(minDwellTime),
            byref(maxDwellTime),
        )
        return (
            minFrequency.value,
            maxFrequency.value,
            minFrequencyStep.value,
            maxFrequencyStep.value,
            minDwellTime.value,
            maxDwellTime.value,
        )

    def psospaSigGenPause(self, handle: c_int16) -> None:
        self._psospaSigGenPause(handle)

    def psospaSigGenRestart(self, handle: c_int16) -> None:
        self._psospaSigGenRestart(handle)

    def psospaSetSimpleTrigger(
        self,
        handle: c_int16,
        enable: bool,
        source: PICO_CHANNEL,
        threshold: int,
        direction: PICO_THRESHOLD_DIRECTION,
        delay: int,
        autoTriggerUS: int,
    ) -> None:
        assert autoTriggerUS >= 0
        self._psospaSetSimpleTrigger(
            handle,
            1 if enable else 0,
            source,
            threshold,
            direction,
            delay,
            autoTriggerUS,
        )

    def psospaTriggerWithinPreTriggerSamples(
        self, handle: c_int16, state: PICO_TRIGGER_WITHIN_PRE_TRIGGER
    ) -> None:
        self._psospaTriggerWithinPreTriggerSamples(handle, state)

    def psospaSetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PICO_TRIGGER_CHANNEL_PROPERTIES],
        autoTriggerMicroSeconds: int,
    ) -> None:
        self._psospaSetTriggerChannelProperties(
            handle,
            c_array(PICO_TRIGGER_CHANNEL_PROPERTIES, channelProperties),
            len(channelProperties),
            autoTriggerMicroSeconds,
        )

    def psospaSetTriggerChannelConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PICO_CONDITION],
        action: PICO_ACTION,
    ) -> None:
        self._psospaSetTriggerChannelConditions(
            handle, c_array(PICO_CONDITION, conditions), len(conditions), action
        )

    def psospaSetTriggerChannelDirections(
        self, handle: c_int16, directions: Sequence[PICO_DIRECTION]
    ) -> None:
        self._psospaSetTriggerChannelDirections(
            handle, c_array(PICO_DIRECTION, directions), len(directions)
        )

    def psospaSetTriggerDelay(self, handle: c_int16, delay: int) -> None:
        self._psospaSetTriggerDelay(handle, delay)

    def psospaSetTriggerHoldoffCounterBySamples(
        self, handle: c_int16, holdoffSamples: int
    ) -> None:
        self._psospaSetTriggerHoldoffCounterBySamples(handle, holdoffSamples)

    def psospaSetPulseWidthQualifierProperties(
        self, handle: c_int16, lower: int, upper: int, type: PICO_PULSE_WIDTH_TYPE
    ) -> None:
        self._psospaSetPulseWidthQualifierProperties(handle, lower, upper, type)

    def psospaSetPulseWidthQualifierConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PICO_CONDITION],
        action: PICO_ACTION,
    ) -> None:
        self._psospaSetPulseWidthQualifierConditions(
            handle, c_array(PICO_CONDITION, conditions), len(conditions), action
        )

    def psospaSetPulseWidthQualifierDirections(
        self, handle: c_int16, directions: Sequence[PICO_DIRECTION]
    ) -> None:
        self._psospaSetPulseWidthQualifierDirections(
            handle, c_array(PICO_DIRECTION, directions), len(directions)
        )

    def psospaSetTriggerDigitalPortProperties(
        self,
        handle: c_int16,
        port: PICO_CHANNEL,
        directions: Sequence[PICO_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> None:
        self._psospaSetTriggerDigitalPortProperties(
            handle,
            port,
            c_array(PICO_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def psospaSetPulseWidthDigitalPortProperties(
        self,
        handle: c_int16,
        port: PICO_CHANNEL,
        directions: Sequence[PICO_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> None:
        self._psospaSetPulseWidthDigitalPortProperties(
            handle,
            port,
            c_array(PICO_DIGITAL_CHANNEL_DIRECTIONS, directions),
            len(directions),
        )

    def psospaGetTriggerTimeOffset(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[int, PICO_TIME_UNITS]:
        time = c_int64(0)
        timeUnits = PICO_TIME_UNITS_T(0)
        self._psospaGetTriggerTimeOffset(
            handle, byref(time), byref(timeUnits), segmentIndex
        )
        return time.value, PICO_TIME_UNITS(timeUnits.value)

    def psospaGetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[list[int], list[PICO_TIME_UNITS]]:
        """Returns the time offsets and their units, one per segment.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        n = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * n)()
        timeUnits = (PICO_TIME_UNITS_T * n)()
        self._psospaGetValuesTriggerTimeOffsetBulk(
            handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
        )
        return list(times), [PICO_TIME_UNITS(u) for u in timeUnits]

    def psospaSetDataBuffer(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        buffer: DataBuffer,
        nsamples: int,
        datatype: PICO_DATA_TYPE,
        waveform: int,
        downsampleMode: PICO_RATIO_MODE,
        action: PICO_ACTION,
    ) -> None:
        """Set the buffer the driver writes the samples of ``channel`` to.

        ``buffer`` is a writable, C-contiguous buffer of at least ``nsamples``
        elements of ``datatype`` (e.g. ``np.empty(nsamples, np.int16)`` for
        ``PICO_INT16_T``), or None. The wrapper keeps it from being freed or
        resized until it is replaced, cleared (``PICO_CLEAR_ALL``, None) or the
        unit is closed. A raw address (int or ``c_void_p``) is passed unchecked
        and must be kept valid by the caller.
        """
        if nsamples < 0:
            raise ValueError("nsamples must not be negative")
        arg = buffer_argument(
            buffer, SAMPLE_TYPES[datatype], nsamples, writable=True, name="buffer"
        )
        self._psospaSetDataBuffer(
            handle,
            channel,
            arg,
            nsamples,
            datatype,
            waveform,
            downsampleMode,
            action,
        )
        self._keep_action_buffer(
            (handle.value, channel, waveform, downsampleMode, datatype), action, arg
        )

    def psospaSetDataBuffers(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        bufferMax: DataBuffer,
        bufferMin: DataBuffer,
        nSamples: int,
        dataType: PICO_DATA_TYPE,
        waveform: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        action: PICO_ACTION,
    ) -> None:
        """Like :meth:`psospaSetDataBuffer`, with buffers for the maxima and minima."""
        if nSamples < 0:
            raise ValueError("nSamples must not be negative")
        ctype = SAMPLE_TYPES[dataType]
        argMax = buffer_argument(
            bufferMax, ctype, nSamples, writable=True, name="bufferMax"
        )
        argMin = buffer_argument(
            bufferMin, ctype, nSamples, writable=True, name="bufferMin"
        )
        self._psospaSetDataBuffers(
            handle,
            channel,
            argMax,
            argMin,
            nSamples,
            dataType,
            waveform,
            downSampleRatioMode,
            action,
        )
        both = None if argMax is None and argMin is None else (argMax, argMin)
        self._keep_action_buffer(
            (handle.value, channel, waveform, downSampleRatioMode, dataType),
            action,
            both,
        )

    def psospaRunBlock(
        self,
        handle: c_int16,
        preSamples: int,
        postSamples: int,
        timebase: int,
        segment: int,
        callback: Callable[[c_int16, PICO_STATUS], None] | None = None,
    ) -> float:
        assert preSamples >= 0
        assert postSamples >= 0
        timeInd = c_double(0)
        lpReady = psospaBlockReady()  # NULL; ctypes rejects None here
        if callback is not None:

            def cbwrapper(handle: c_int16, status: int, _: int | None) -> None:
                callback(handle, PICO_STATUS(status))

            lpReady = psospaBlockReady(cbwrapper)
        self._with_callback(
            self._callback_key("psospaRunBlock", handle),
            lpReady,
            lambda: self._psospaRunBlock(
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
        return float(timeInd.value)

    def psospaIsReady(self, handle: c_int16) -> bool:
        ready = c_int16(0)
        self._psospaIsReady(handle, byref(ready))
        return ready.value == 1

    def psospaRunStreaming(
        self,
        handle: c_int16,
        sampleInterval: float,
        sampleIntervalTimeUnits: PICO_TIME_UNITS,
        maxPreTriggerSamples: int,
        maxPostTriggerSamples: int,
        autoStop: bool,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
    ) -> float:
        sampleInterval_ = c_double(sampleInterval)
        self._psospaRunStreaming(
            handle,
            byref(sampleInterval_),
            sampleIntervalTimeUnits,
            maxPreTriggerSamples,
            maxPostTriggerSamples,
            1 if autoStop else 0,
            downSampleRatio,
            downSampleRatioMode,
        )
        return sampleInterval_.value

    def psospaGetStreamingLatestValues(
        self,
        handle: c_int16,
        streamingDataInfo: Sequence[PICO_STREAMING_DATA_INFO],
    ) -> tuple[
        list[PICO_STREAMING_DATA_INFO],
        PICO_STREAMING_DATA_TRIGGER_INFO,
        PICO_STATUS,
    ]:
        """Returns the updated ``streamingDataInfo``, the trigger info and the status.

        A status of PICO_WAITING_FOR_DATA_BUFFERS is informational: new buffers
        have to be set before the driver continues.
        """
        n = len(streamingDataInfo)
        infos = PICO_STREAMING_DATA_INFO.to_c_array(streamingDataInfo)
        triggerInfo = PICO_STREAMING_DATA_TRIGGER_INFO.c_type()
        status = self._psospaGetStreamingLatestValues(
            handle, infos, n, byref(triggerInfo)
        )
        return (
            PICO_STREAMING_DATA_INFO.from_c_array(infos),
            PICO_STREAMING_DATA_TRIGGER_INFO.from_c(triggerInfo),
            status,
        )

    def psospaNoOfStreamingValues(self, handle: c_int16) -> int:
        noOfValues = c_uint64(0)
        self._psospaNoOfStreamingValues(handle, byref(noOfValues))
        return noOfValues.value

    def psospaGetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[int, PICO_CHANNEL_FLAGS]:
        noOfSamples_ = c_uint64(noOfSamples)
        overflow = c_int16(0)
        self._psospaGetValues(
            handle,
            startIndex,
            byref(noOfSamples_),
            downSampleRatio,
            downSampleRatioMode,
            segmentIndex,
            byref(overflow),
        )
        return noOfSamples_.value, PICO_CHANNEL_FLAGS(overflow.value)

    def psospaGetValuesBulk(
        self,
        handle: c_int16,
        startindex: int,
        nosamples: int,
        fromSegment: int,
        toSegment: int,
        downsampleRatio: int,
        downsampleMode: PICO_RATIO_MODE,
    ) -> tuple[int, list[PICO_CHANNEL_FLAGS]]:
        """Returns the number of samples and the overflow flags of each segment.

        The driver wraps around from the last segment to the first if
        ``toSegment < fromSegment``; the wrapper does not support this.
        """
        assert startindex >= 0
        assert nosamples > 0
        assert fromSegment <= toSegment
        nosamples_ = c_uint64(nosamples)
        nsegments = (toSegment - fromSegment) + 1
        overflow = (c_int16 * nsegments)(0)
        self._psospaGetValuesBulk(
            handle,
            startindex,
            byref(nosamples_),
            fromSegment,
            toSegment,
            downsampleRatio,
            downsampleMode,
            overflow,
        )
        return nosamples_.value, [PICO_CHANNEL_FLAGS(f) for f in overflow]

    def _data_ready(
        self, callback: Callable[[int, PICO_STATUS, int, PICO_CHANNEL_FLAGS], None]
    ) -> CFuncPtr:
        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: int | None
        ) -> None:
            callback(
                handle, PICO_STATUS(status), noOfSamples, PICO_CHANNEL_FLAGS(overflow)
            )

        return psospaDataReady(cbwrapper)

    def psospaGetValuesAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        segmentIndex: int,
        lpDataReady: Callable[[int, PICO_STATUS, int, PICO_CHANNEL_FLAGS], None],
    ) -> None:
        """``lpDataReady(handle, status, noOfSamples, overflow)`` is called once the
        data has been written to the buffers set up with psospaSetDataBuffer(s)."""
        cb = self._data_ready(lpDataReady)
        self._with_callback(
            self._callback_key("psospaGetValuesAsync", handle),
            cb,
            lambda: self._psospaGetValuesAsync(
                handle,
                startIndex,
                noOfSamples,
                downSampleRatio,
                downSampleRatioMode,
                segmentIndex,
                cb,
                None,
            ),
        )

    def psospaGetValuesBulkAsync(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        fromSegmentIndex: int,
        toSegmentIndex: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        lpDataReady: Callable[[int, PICO_STATUS, int, PICO_CHANNEL_FLAGS], None],
    ) -> None:
        """See :meth:`psospaGetValuesAsync` for the callback signature."""
        cb = self._data_ready(lpDataReady)
        self._with_callback(
            self._callback_key("psospaGetValuesBulkAsync", handle),
            cb,
            lambda: self._psospaGetValuesBulkAsync(
                handle,
                startIndex,
                noOfSamples,
                fromSegmentIndex,
                toSegmentIndex,
                downSampleRatio,
                downSampleRatioMode,
                cb,
                None,
            ),
        )

    def psospaGetValuesOverlapped(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        fromSegmentIndex: int,
        toSegmentIndex: int,
    ) -> tuple[c_uint64, Array[c_int16]]:
        """Set up data retrieval during the next psospaRunBlock.

        The driver fills the returned ``noOfSamples`` and ``overflow`` ctypes
        objects once the capture has completed, so they are returned as is
        (read ``noOfSamples.value`` and ``overflow[i]`` afterwards). The wrapper
        keeps them alive until they are replaced by a later call.

        The driver wraps around from the last segment to the first if
        ``toSegmentIndex < fromSegmentIndex``; the wrapper does not support this.
        """
        assert fromSegmentIndex <= toSegmentIndex
        noOfSamples_ = c_uint64(noOfSamples)
        overflow = (c_int16 * ((toSegmentIndex - fromSegmentIndex) + 1))()
        self._with_callback(
            self._callback_key("psospaGetValuesOverlapped", handle),
            (noOfSamples_, overflow),
            lambda: self._psospaGetValuesOverlapped(
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

    def psospaStopUsingGetValuesOverlapped(self, handle: c_int16) -> None:
        self._psospaStopUsingGetValuesOverlapped(handle)

    def psospaGetNoOfCaptures(self, handle: c_int16) -> int:
        nCaptures = c_uint64(0)
        self._psospaGetNoOfCaptures(handle, byref(nCaptures))
        return nCaptures.value

    def psospaGetNoOfProcessedCaptures(self, handle: c_int16) -> int:
        nProcessedCaptures = c_uint64(0)
        self._psospaGetNoOfProcessedCaptures(handle, byref(nProcessedCaptures))
        return nProcessedCaptures.value

    def psospaStop(self, handle: c_int16) -> None:
        self._psospaStop(handle)

    def psospaSetNoOfCaptures(self, handle: c_int16, ncaptures: int) -> None:
        assert ncaptures > 0
        self._psospaSetNoOfCaptures(handle, ncaptures)

    def psospaGetTriggerInfo(
        self, handle: c_int16, firstSegmentIndex: int, segmentCount: int
    ) -> list[PICO_TRIGGER_INFO]:
        assert segmentCount > 0
        triggerInfo = (PICO_TRIGGER_INFO.c_type * segmentCount)()
        self._psospaGetTriggerInfo(handle, triggerInfo, firstSegmentIndex, segmentCount)
        return PICO_TRIGGER_INFO.from_c_array(triggerInfo)

    def psospaEnumerateUnits(self) -> tuple[int, list[str]]:
        """Returns the number of units and their serial numbers."""
        count = c_int16(0)
        serials = create_string_buffer(_ENUMERATE_BUFFER_SIZE)
        serialLth = c_int16(_ENUMERATE_BUFFER_SIZE)
        self._psospaEnumerateUnits(byref(count), serials, byref(serialLth))
        serialstr = serials.value.decode("utf-8")
        return count.value, [s for s in serialstr.split(",") if s]

    def psospaPingUnit(self, handle: c_int16) -> None:
        self._psospaPingUnit(handle)

    def psospaGetAnalogueOffsetLimits(
        self,
        handle: c_int16,
        rangeMin: float,
        rangeMax: float,
        rangeType: PICO_PROBE_RANGE_INFO,
        coupling: PICO_COUPLING,
    ) -> tuple[float, float]:
        """Returns ``(maximumVoltage, minimumVoltage)``."""
        maximumVoltage = c_double(0)
        minimumVoltage = c_double(0)
        self._psospaGetAnalogueOffsetLimits(
            handle,
            _range_value(rangeMin),
            _range_value(rangeMax),
            rangeType,
            coupling,
            byref(maximumVoltage),
            byref(minimumVoltage),
        )
        return maximumVoltage.value, minimumVoltage.value

    def psospaGetMinimumTimebaseStateless(
        self,
        handle: c_int16,
        enabledChannels: PICO_CHANNEL_FLAGS,
        resolution: PICO_DEVICE_RESOLUTION,
    ) -> tuple[int, float]:
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        self._psospaGetMinimumTimebaseStateless(
            handle,
            enabledChannels,
            byref(timebase),
            byref(timeInterval),
            resolution,
        )
        return timebase.value, float(timeInterval.value)

    def psospaNearestSampleIntervalStateless(
        self,
        handle: c_int16,
        enabledChannels: PICO_CHANNEL_FLAGS,
        timeIntervalRequested: float,
        roundFaster: bool,
        resolution: PICO_DEVICE_RESOLUTION,
    ) -> tuple[int, float]:
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        self._psospaNearestSampleIntervalStateless(
            handle,
            enabledChannels,
            timeIntervalRequested,
            1 if roundFaster else 0,
            resolution,
            byref(timebase),
            byref(timeInterval),
        )
        return timebase.value, float(timeInterval.value)

    def psospaSetDeviceResolution(
        self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION
    ) -> None:
        self._psospaSetDeviceResolution(handle, resolution)

    def psospaGetDeviceResolution(self, handle: c_int16) -> PICO_DEVICE_RESOLUTION:
        resolution = PICO_DEVICE_RESOLUTION_T(0)
        self._psospaGetDeviceResolution(handle, byref(resolution))
        return PICO_DEVICE_RESOLUTION(resolution.value)

    def psospaQueryOutputEdgeDetect(self, handle: c_int16) -> bool:
        state = c_int16(0)
        self._psospaQueryOutputEdgeDetect(handle, byref(state))
        return state.value != 0

    def psospaSetOutputEdgeDetect(self, handle: c_int16, state: bool) -> None:
        self._psospaSetOutputEdgeDetect(handle, 1 if state else 0)

    def psospaGetScalingValues(
        self,
        handle: c_int16,
        scalingValues: Sequence[PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES],
    ) -> list[PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES]:
        """``scalingValues`` select channel and range; the filled-in copies are
        returned."""
        n = len(scalingValues)
        values = PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES.to_c_array(scalingValues)
        self._psospaGetScalingValues(handle, values, n)
        return PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES.from_c_array(values)

    def psospaGetAdcLimits(
        self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION
    ) -> tuple[int, int]:
        minValue = c_int16(0)
        maxValue = c_int16(0)
        self._psospaGetAdcLimits(handle, resolution, byref(minValue), byref(maxValue))
        return minValue.value, maxValue.value

    def psospaCheckForUpdate(
        self, handle: c_int16
    ) -> tuple[list[PICO_FIRMWARE_INFO], bool]:
        firmwareInfos = (PICO_FIRMWARE_INFO.c_type * _MAX_FIRMWARE_INFOS)()
        nFirmwareInfos = c_int16(_MAX_FIRMWARE_INFOS)
        updatesRequired = c_uint16(0)
        self._psospaCheckForUpdate(
            handle, firmwareInfos, byref(nFirmwareInfos), byref(updatesRequired)
        )
        n = max(0, min(nFirmwareInfos.value, _MAX_FIRMWARE_INFOS))
        return (
            PICO_FIRMWARE_INFO.from_c_array(firmwareInfos[:n]),
            updatesRequired.value != 0,
        )

    def psospaStartFirmwareUpdate(
        self, handle: c_int16, progress: Callable[[int, int], None] | None
    ) -> PICO_STATUS:
        """``progress(handle, progressPercent)`` is called during the update.

        Returns the status, PICO_FIRMWARE_UP_TO_DATE once the firmware has been
        updated or did not need an update.
        """
        cb = PicoUpdateFirmwareProgress()  # NULL; ctypes rejects None here
        if progress is not None:

            def cbwrapper(handle: int, percent: int) -> None:
                progress(handle, percent)

            cb = PicoUpdateFirmwareProgress(cbwrapper)
        return self._with_callback(
            self._callback_key("psospaStartFirmwareUpdate", handle),
            cb,
            lambda: self._psospaStartFirmwareUpdate(handle, cb),
            accepted=lambda status: (
                status in (PICO_STATUS.PICO_OK, PICO_STATUS.PICO_FIRMWARE_UP_TO_DATE)
            ),
        )

    def psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus(
        self, handle: c_int16, nChannelTrippedStatus: int
    ) -> list[PICO_CHANNEL_OVERVOLTAGE_TRIPPED]:
        tripped = (PICO_CHANNEL_OVERVOLTAGE_TRIPPED.c_type * nChannelTrippedStatus)()
        self._psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus(
            handle, tripped, nChannelTrippedStatus
        )
        return PICO_CHANNEL_OVERVOLTAGE_TRIPPED.from_c_array(tripped)

    def psospaReportAllChannelsOvervoltageTripStatus(
        self, handle: c_int16, nChannelTrippedStatus: int
    ) -> list[PICO_CHANNEL_OVERVOLTAGE_TRIPPED]:
        tripped = (PICO_CHANNEL_OVERVOLTAGE_TRIPPED.c_type * nChannelTrippedStatus)()
        self._psospaReportAllChannelsOvervoltageTripStatus(
            handle, tripped, nChannelTrippedStatus
        )
        return PICO_CHANNEL_OVERVOLTAGE_TRIPPED.from_c_array(tripped)

    def psospaSetLedColours(
        self,
        handle: c_int16,
        colourProperties: Sequence[PICO_LED_COLOUR_PROPERTIES],
    ) -> None:
        n = len(colourProperties)
        props = PICO_LED_COLOUR_PROPERTIES.to_c_array(colourProperties)
        self._psospaSetLedColours(handle, props, n)

    def psospaSetLedBrightness(self, handle: c_int16, brightness: int) -> None:
        self._psospaSetLedBrightness(handle, brightness)

    def psospaSetLedStates(
        self,
        handle: c_int16,
        stateProperties: Sequence[PICO_LED_STATE_PROPERTIES],
    ) -> None:
        n = len(stateProperties)
        props = PICO_LED_STATE_PROPERTIES.to_c_array(stateProperties)
        self._psospaSetLedStates(handle, props, n)

    def psospaSetAuxIoMode(self, handle: c_int16, auxIoMode: PICO_AUXIO_MODE) -> None:
        self._psospaSetAuxIoMode(handle, auxIoMode)


@final
class PicoScope3000eDevice(PicoScopeDeviceBase[PicoScope3000eWrapper]):
    """An opened psospa unit; the functions of :class:`PicoScope3000eWrapper` with its handle.

    See :class:`~pycosdk.PicoScopeDeviceBase`.
    """

    _wrapper_type = PicoScope3000eWrapper

    @classmethod
    def psospaOpenUnit(
        cls, serial: str | None, resolution: PICO_DEVICE_RESOLUTION
    ) -> tuple[Self, PICO_USB_POWER_DETAILS, PICO_STATUS]:
        """Like :meth:`PicoScope3000eWrapper.psospaOpenUnit`, returning a device instead of the handle."""
        handle, usbPowerDetails, status = cls.shared_wrapper().psospaOpenUnit(
            serial, resolution
        )
        return cls(handle), usbPowerDetails, status

    psospaGetVariantDetails = wrapper_function(
        PicoScope3000eWrapper.psospaGetVariantDetails
    )
    psospaEnumerateUnits = wrapper_function(PicoScope3000eWrapper.psospaEnumerateUnits)

    psospaCloseUnit = handle_method(PicoScope3000eWrapper.psospaCloseUnit, closes=True)
    psospaGetUnitInfo = handle_method(PicoScope3000eWrapper.psospaGetUnitInfo)
    psospaMemorySegments = handle_method(PicoScope3000eWrapper.psospaMemorySegments)
    psospaMemorySegmentsBySamples = handle_method(
        PicoScope3000eWrapper.psospaMemorySegmentsBySamples
    )
    psospaGetMaximumAvailableMemory = handle_method(
        PicoScope3000eWrapper.psospaGetMaximumAvailableMemory
    )
    psospaQueryMaxSegmentsBySamples = handle_method(
        PicoScope3000eWrapper.psospaQueryMaxSegmentsBySamples
    )
    psospaSetChannelOn = handle_method(PicoScope3000eWrapper.psospaSetChannelOn)
    psospaSetChannelOff = handle_method(PicoScope3000eWrapper.psospaSetChannelOff)
    psospaSetDigitalPortOn = handle_method(PicoScope3000eWrapper.psospaSetDigitalPortOn)
    psospaSetDigitalPortOff = handle_method(
        PicoScope3000eWrapper.psospaSetDigitalPortOff
    )
    psospaGetTimebase = handle_method(PicoScope3000eWrapper.psospaGetTimebase)
    psospaSigGenWaveform = handle_method(PicoScope3000eWrapper.psospaSigGenWaveform)
    psospaSigGenRange = handle_method(PicoScope3000eWrapper.psospaSigGenRange)
    psospaSigGenWaveformDutyCycle = handle_method(
        PicoScope3000eWrapper.psospaSigGenWaveformDutyCycle
    )
    psospaSigGenTrigger = handle_method(PicoScope3000eWrapper.psospaSigGenTrigger)
    psospaSigGenFrequency = handle_method(PicoScope3000eWrapper.psospaSigGenFrequency)
    psospaSigGenFrequencySweep = handle_method(
        PicoScope3000eWrapper.psospaSigGenFrequencySweep
    )
    psospaSigGenPhase = handle_method(PicoScope3000eWrapper.psospaSigGenPhase)
    psospaSigGenPhaseSweep = handle_method(PicoScope3000eWrapper.psospaSigGenPhaseSweep)
    psospaSigGenSoftwareTriggerControl = handle_method(
        PicoScope3000eWrapper.psospaSigGenSoftwareTriggerControl
    )
    psospaSigGenApply = handle_method(PicoScope3000eWrapper.psospaSigGenApply)
    psospaSigGenLimits = handle_method(PicoScope3000eWrapper.psospaSigGenLimits)
    psospaSigGenFrequencyLimits = handle_method(
        PicoScope3000eWrapper.psospaSigGenFrequencyLimits
    )
    psospaSigGenPause = handle_method(PicoScope3000eWrapper.psospaSigGenPause)
    psospaSigGenRestart = handle_method(PicoScope3000eWrapper.psospaSigGenRestart)
    psospaSetSimpleTrigger = handle_method(PicoScope3000eWrapper.psospaSetSimpleTrigger)
    psospaTriggerWithinPreTriggerSamples = handle_method(
        PicoScope3000eWrapper.psospaTriggerWithinPreTriggerSamples
    )
    psospaSetTriggerChannelProperties = handle_method(
        PicoScope3000eWrapper.psospaSetTriggerChannelProperties
    )
    psospaSetTriggerChannelConditions = handle_method(
        PicoScope3000eWrapper.psospaSetTriggerChannelConditions
    )
    psospaSetTriggerChannelDirections = handle_method(
        PicoScope3000eWrapper.psospaSetTriggerChannelDirections
    )
    psospaSetTriggerDelay = handle_method(PicoScope3000eWrapper.psospaSetTriggerDelay)
    psospaSetTriggerHoldoffCounterBySamples = handle_method(
        PicoScope3000eWrapper.psospaSetTriggerHoldoffCounterBySamples
    )
    psospaSetPulseWidthQualifierProperties = handle_method(
        PicoScope3000eWrapper.psospaSetPulseWidthQualifierProperties
    )
    psospaSetPulseWidthQualifierConditions = handle_method(
        PicoScope3000eWrapper.psospaSetPulseWidthQualifierConditions
    )
    psospaSetPulseWidthQualifierDirections = handle_method(
        PicoScope3000eWrapper.psospaSetPulseWidthQualifierDirections
    )
    psospaSetTriggerDigitalPortProperties = handle_method(
        PicoScope3000eWrapper.psospaSetTriggerDigitalPortProperties
    )
    psospaSetPulseWidthDigitalPortProperties = handle_method(
        PicoScope3000eWrapper.psospaSetPulseWidthDigitalPortProperties
    )
    psospaGetTriggerTimeOffset = handle_method(
        PicoScope3000eWrapper.psospaGetTriggerTimeOffset
    )
    psospaGetValuesTriggerTimeOffsetBulk = handle_method(
        PicoScope3000eWrapper.psospaGetValuesTriggerTimeOffsetBulk
    )
    psospaSetDataBuffer = handle_method(PicoScope3000eWrapper.psospaSetDataBuffer)
    psospaSetDataBuffers = handle_method(PicoScope3000eWrapper.psospaSetDataBuffers)
    psospaRunBlock = handle_method(PicoScope3000eWrapper.psospaRunBlock)
    psospaIsReady = handle_method(PicoScope3000eWrapper.psospaIsReady)
    psospaRunStreaming = handle_method(PicoScope3000eWrapper.psospaRunStreaming)
    psospaGetStreamingLatestValues = handle_method(
        PicoScope3000eWrapper.psospaGetStreamingLatestValues
    )
    psospaNoOfStreamingValues = handle_method(
        PicoScope3000eWrapper.psospaNoOfStreamingValues
    )
    psospaGetValues = handle_method(PicoScope3000eWrapper.psospaGetValues)
    psospaGetValuesBulk = handle_method(PicoScope3000eWrapper.psospaGetValuesBulk)
    psospaGetValuesAsync = handle_method(PicoScope3000eWrapper.psospaGetValuesAsync)
    psospaGetValuesBulkAsync = handle_method(
        PicoScope3000eWrapper.psospaGetValuesBulkAsync
    )
    psospaGetValuesOverlapped = handle_method(
        PicoScope3000eWrapper.psospaGetValuesOverlapped
    )
    psospaStopUsingGetValuesOverlapped = handle_method(
        PicoScope3000eWrapper.psospaStopUsingGetValuesOverlapped
    )
    psospaGetNoOfCaptures = handle_method(PicoScope3000eWrapper.psospaGetNoOfCaptures)
    psospaGetNoOfProcessedCaptures = handle_method(
        PicoScope3000eWrapper.psospaGetNoOfProcessedCaptures
    )
    psospaStop = handle_method(PicoScope3000eWrapper.psospaStop)
    psospaSetNoOfCaptures = handle_method(PicoScope3000eWrapper.psospaSetNoOfCaptures)
    psospaGetTriggerInfo = handle_method(PicoScope3000eWrapper.psospaGetTriggerInfo)
    psospaPingUnit = handle_method(PicoScope3000eWrapper.psospaPingUnit)
    psospaGetAnalogueOffsetLimits = handle_method(
        PicoScope3000eWrapper.psospaGetAnalogueOffsetLimits
    )
    psospaGetMinimumTimebaseStateless = handle_method(
        PicoScope3000eWrapper.psospaGetMinimumTimebaseStateless
    )
    psospaNearestSampleIntervalStateless = handle_method(
        PicoScope3000eWrapper.psospaNearestSampleIntervalStateless
    )
    psospaSetDeviceResolution = handle_method(
        PicoScope3000eWrapper.psospaSetDeviceResolution
    )
    psospaGetDeviceResolution = handle_method(
        PicoScope3000eWrapper.psospaGetDeviceResolution
    )
    psospaQueryOutputEdgeDetect = handle_method(
        PicoScope3000eWrapper.psospaQueryOutputEdgeDetect
    )
    psospaSetOutputEdgeDetect = handle_method(
        PicoScope3000eWrapper.psospaSetOutputEdgeDetect
    )
    psospaGetScalingValues = handle_method(PicoScope3000eWrapper.psospaGetScalingValues)
    psospaGetAdcLimits = handle_method(PicoScope3000eWrapper.psospaGetAdcLimits)
    psospaCheckForUpdate = handle_method(PicoScope3000eWrapper.psospaCheckForUpdate)
    psospaStartFirmwareUpdate = handle_method(
        PicoScope3000eWrapper.psospaStartFirmwareUpdate
    )
    psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus = handle_method(
        PicoScope3000eWrapper.psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus
    )
    psospaReportAllChannelsOvervoltageTripStatus = handle_method(
        PicoScope3000eWrapper.psospaReportAllChannelsOvervoltageTripStatus
    )
    psospaSetLedColours = handle_method(PicoScope3000eWrapper.psospaSetLedColours)
    psospaSetLedBrightness = handle_method(PicoScope3000eWrapper.psospaSetLedBrightness)
    psospaSetLedStates = handle_method(PicoScope3000eWrapper.psospaSetLedStates)
    psospaSetAuxIoMode = handle_method(PicoScope3000eWrapper.psospaSetAuxIoMode)


__all__ = (
    "PicoScope3000eWrapper",
    "PicoScope3000eDevice",
    "psospaBlockReady",
    "psospaDataReady",
)
