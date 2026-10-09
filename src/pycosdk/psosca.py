from collections.abc import Callable, Sequence
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

from ._base import CALLBACK_FUNCTYPE, PicoScopeWrapperBase
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
    PicoUsbPowerDetails,
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
    _library_name = "psospa"

    def __init__(self, library_path: str | None = None):
        super().__init__(library_path)

        # The device opened fine, but is connected to a USB 2.0 port.
        self._psospaOpenUnit = self._bind(
            "psospaOpenUnit",
            [
                POINTER(c_int16),
                c_char_p,
                PICO_DEVICE_RESOLUTION_T,
                POINTER(PICO_USB_POWER_DETAILS),
            ],
            info={PICO_STATUS.PICO_USB3_0_DEVICE_NON_USB3_0_PORT},
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
            [c_int16, POINTER(PICO_TRIGGER_CHANNEL_PROPERTIES), c_int16, c_uint32],
        )
        self._psospaSetTriggerChannelConditions = self._bind(
            "psospaSetTriggerChannelConditions",
            [c_int16, POINTER(PICO_CONDITION), c_int16, PICO_ACTION_T],
        )
        self._psospaSetTriggerChannelDirections = self._bind(
            "psospaSetTriggerChannelDirections",
            [c_int16, POINTER(PICO_DIRECTION), c_int16],
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
            [c_int16, POINTER(PICO_CONDITION), c_int16, PICO_ACTION_T],
        )
        self._psospaSetPulseWidthQualifierDirections = self._bind(
            "psospaSetPulseWidthQualifierDirections",
            [c_int16, POINTER(PICO_DIRECTION), c_int16],
        )
        self._psospaSetTriggerDigitalPortProperties = self._bind(
            "psospaSetTriggerDigitalPortProperties",
            [
                c_int16,
                PICO_CHANNEL_T,
                POINTER(PICO_DIGITAL_CHANNEL_DIRECTIONS),
                c_int16,
            ],
        )
        self._psospaSetPulseWidthDigitalPortProperties = self._bind(
            "psospaSetPulseWidthDigitalPortProperties",
            [
                c_int16,
                PICO_CHANNEL_T,
                POINTER(PICO_DIGITAL_CHANNEL_DIRECTIONS),
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
                POINTER(PICO_STREAMING_DATA_INFO),
                c_uint64,
                POINTER(PICO_STREAMING_DATA_TRIGGER_INFO),
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
            [c_int16, POINTER(PICO_TRIGGER_INFO), c_uint64, c_uint64],
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
            [c_int16, POINTER(PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES), c_int16],
        )
        self._psospaGetAdcLimits = self._bind(
            "psospaGetAdcLimits",
            [c_int16, PICO_DEVICE_RESOLUTION_T, POINTER(c_int16), POINTER(c_int16)],
        )
        self._psospaCheckForUpdate = self._bind(
            "psospaCheckForUpdate",
            [
                c_int16,
                POINTER(PICO_FIRMWARE_INFO),
                POINTER(c_int16),
                POINTER(c_uint16),
            ],
        )
        self._psospaStartFirmwareUpdate = self._bind(
            "psospaStartFirmwareUpdate", [c_int16, PicoUpdateFirmwareProgress]
        )
        self._psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus = self._bind(
            "psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus",
            [c_int16, POINTER(PICO_CHANNEL_OVERVOLTAGE_TRIPPED), c_uint8],
        )
        self._psospaReportAllChannelsOvervoltageTripStatus = self._bind(
            "psospaReportAllChannelsOvervoltageTripStatus",
            [c_int16, POINTER(PICO_CHANNEL_OVERVOLTAGE_TRIPPED), c_uint8],
        )
        self._psospaSetLedColours = self._bind(
            "psospaSetLedColours",
            [c_int16, POINTER(PICO_LED_COLOUR_PROPERTIES), c_uint32],
        )
        self._psospaSetLedBrightness = self._bind(
            "psospaSetLedBrightness", [c_int16, c_uint8]
        )
        self._psospaSetLedStates = self._bind(
            "psospaSetLedStates",
            [c_int16, POINTER(PICO_LED_STATE_PROPERTIES), c_uint32],
        )
        self._psospaSetAuxIoMode = self._bind(
            "psospaSetAuxIoMode", [c_int16, PICO_AUXIO_MODE_T]
        )

    def psospaOpenUnit(self, serial: str | None, resolution: PICO_DEVICE_RESOLUTION):
        handle = c_int16(0)
        ser = serial.encode() if serial is not None else None
        usbpwrdet = PICO_USB_POWER_DETAILS()
        return (
            self._psospaOpenUnit(byref(handle), ser, resolution, byref(usbpwrdet)),
            handle,
            PicoUsbPowerDetails.from_struct(usbpwrdet),
        )

    def psospaCloseUnit(self, handle: c_int16):
        return self._psospaCloseUnit(handle)

    def psospaGetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._psospaGetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return status, infostr

    def psospaGetVariantDetails(
        self, variantName: str, textFormat: PICO_TEXT_FORMAT
    ) -> tuple[PICO_STATUS, str]:
        name = variantName.encode()
        length = c_int32(0)
        # The first call only queries the required buffer size.
        status = self._psospaGetVariantDetails(
            name, len(name), None, byref(length), textFormat
        )
        if status != PICO_STATUS.PICO_OK:
            return status, ""
        buf = create_string_buffer(length.value + 1)
        status = self._psospaGetVariantDetails(
            name, len(name), buf, byref(length), textFormat
        )
        return status, buf.value.decode("utf-8")

    def psospaMemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_uint64(0)
        return (
            self._psospaMemorySegments(handle, nsegments, byref(maxSamples)),
            maxSamples.value,
        )

    def psospaMemorySegmentsBySamples(self, handle: c_int16, nsamples: int):
        assert nsamples > 0
        maxSegments = c_uint64(0)
        return (
            self._psospaMemorySegmentsBySamples(handle, nsamples, byref(maxSegments)),
            maxSegments.value,
        )

    def psospaGetMaximumAvailableMemory(
        self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION
    ) -> tuple[PICO_STATUS, int]:
        nMaxSamples = c_uint64(0)
        return (
            self._psospaGetMaximumAvailableMemory(
                handle, byref(nMaxSamples), resolution
            ),
            nMaxSamples.value,
        )

    def psospaQueryMaxSegmentsBySamples(
        self,
        handle: c_int16,
        nsamples: int,
        nchannels: int,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        maxSegments = c_uint64(0)
        return (
            self._psospaQueryMaxSegmentsBySamples(
                handle, nsamples, nchannels, byref(maxSegments), resolution
            ),
            maxSegments.value,
        )

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
    ):
        return self._psospaSetChannelOn(
            handle,
            channel,
            coupling,
            _range_value(rangeMin),
            _range_value(rangeMax),
            rangeType,
            analog_offset,
            bandwidth,
        )

    def psospaSetChannelOff(self, handle: c_int16, channel: PICO_CHANNEL):
        return self._psospaSetChannelOff(handle, channel)

    def psospaSetDigitalPortOn(
        self, handle: c_int16, port: PICO_CHANNEL, logicThreshold: float
    ):
        return self._psospaSetDigitalPortOn(handle, port, logicThreshold)

    def psospaSetDigitalPortOff(self, handle: c_int16, port: PICO_CHANNEL):
        return self._psospaSetDigitalPortOff(handle, port)

    def psospaGetTimebase(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ):
        timeIntervalNS = c_double(0)
        maxSamples = c_uint64(0)
        return (
            self._psospaGetTimebase(
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

    def psospaSigGenWaveform(
        self, handle: c_int16, waveType: PICO_WAVE_TYPE, buffer: Sequence[int] | None
    ) -> PICO_STATUS:
        if buffer is None:
            return self._psospaSigGenWaveform(handle, waveType, None, 0)
        buf = (c_int16 * len(buffer))(*buffer)
        return self._psospaSigGenWaveform(handle, waveType, buf, len(buffer))

    def psospaSigGenRange(
        self, handle: c_int16, peakToPeakVolts: float, offsetVolts: float
    ) -> PICO_STATUS:
        return self._psospaSigGenRange(handle, peakToPeakVolts, offsetVolts)

    def psospaSigGenWaveformDutyCycle(
        self, handle: c_int16, dutyCyclePercent: float
    ) -> PICO_STATUS:
        return self._psospaSigGenWaveformDutyCycle(handle, dutyCyclePercent)

    def psospaSigGenTrigger(
        self,
        handle: c_int16,
        triggerType: PICO_SIGGEN_TRIG_TYPE,
        triggerSource: PICO_SIGGEN_TRIG_SOURCE,
        cycles: int,
        autoTriggerPicoSeconds: int,
    ) -> PICO_STATUS:
        return self._psospaSigGenTrigger(
            handle, triggerType, triggerSource, cycles, autoTriggerPicoSeconds
        )

    def psospaSigGenFrequency(self, handle: c_int16, frequencyHz: float) -> PICO_STATUS:
        return self._psospaSigGenFrequency(handle, frequencyHz)

    def psospaSigGenFrequencySweep(
        self,
        handle: c_int16,
        stopFrequencyHz: float,
        frequencyIncrement: float,
        dwellTimeSeconds: float,
        sweepType: PICO_SWEEP_TYPE,
    ) -> PICO_STATUS:
        return self._psospaSigGenFrequencySweep(
            handle, stopFrequencyHz, frequencyIncrement, dwellTimeSeconds, sweepType
        )

    def psospaSigGenPhase(self, handle: c_int16, deltaPhase: int) -> PICO_STATUS:
        return self._psospaSigGenPhase(handle, deltaPhase)

    def psospaSigGenPhaseSweep(
        self,
        handle: c_int16,
        stopDeltaPhase: int,
        deltaPhaseIncrement: int,
        dwellCount: int,
        sweepType: PICO_SWEEP_TYPE,
    ) -> PICO_STATUS:
        return self._psospaSigGenPhaseSweep(
            handle, stopDeltaPhase, deltaPhaseIncrement, dwellCount, sweepType
        )

    def psospaSigGenSoftwareTriggerControl(
        self, handle: c_int16, triggerState: PICO_SIGGEN_TRIG_TYPE
    ) -> PICO_STATUS:
        return self._psospaSigGenSoftwareTriggerControl(handle, triggerState)

    def psospaSigGenApply(
        self,
        handle: c_int16,
        sigGenEnabled: bool,
        sweepEnabled: bool,
        triggerEnabled: bool,
    ) -> tuple[PICO_STATUS, float, float, float, float]:
        frequency = c_double(0)
        stopFrequency = c_double(0)
        frequencyIncrement = c_double(0)
        dwellTime = c_double(0)
        return (
            self._psospaSigGenApply(
                handle,
                1 if sigGenEnabled else 0,
                1 if sweepEnabled else 0,
                1 if triggerEnabled else 0,
                byref(frequency),
                byref(stopFrequency),
                byref(frequencyIncrement),
                byref(dwellTime),
            ),
            frequency.value,
            stopFrequency.value,
            frequencyIncrement.value,
            dwellTime.value,
        )

    def psospaSigGenLimits(
        self, handle: c_int16, parameter: PICO_SIGGEN_PARAMETER
    ) -> tuple[PICO_STATUS, float, float, float]:
        minimumPermissibleValue = c_double(0)
        maximumPermissibleValue = c_double(0)
        step = c_double(0)
        return (
            self._psospaSigGenLimits(
                handle,
                parameter,
                byref(minimumPermissibleValue),
                byref(maximumPermissibleValue),
                byref(step),
            ),
            minimumPermissibleValue.value,
            maximumPermissibleValue.value,
            step.value,
        )

    def psospaSigGenFrequencyLimits(
        self, handle: c_int16, waveType: PICO_WAVE_TYPE, numSamples: int
    ) -> tuple[PICO_STATUS, float, float, float, float, float, float]:
        numSamples_ = c_uint64(numSamples)
        minFrequency = c_double(0)
        maxFrequency = c_double(0)
        minFrequencyStep = c_double(0)
        maxFrequencyStep = c_double(0)
        minDwellTime = c_double(0)
        maxDwellTime = c_double(0)
        return (
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
            ),
            minFrequency.value,
            maxFrequency.value,
            minFrequencyStep.value,
            maxFrequencyStep.value,
            minDwellTime.value,
            maxDwellTime.value,
        )

    def psospaSigGenPause(self, handle: c_int16) -> PICO_STATUS:
        return self._psospaSigGenPause(handle)

    def psospaSigGenRestart(self, handle: c_int16) -> PICO_STATUS:
        return self._psospaSigGenRestart(handle)

    def psospaSetSimpleTrigger(
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
        return self._psospaSetSimpleTrigger(
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
    ) -> PICO_STATUS:
        return self._psospaTriggerWithinPreTriggerSamples(handle, state)

    def psospaSetTriggerChannelProperties(
        self,
        handle: c_int16,
        channelProperties: Sequence[PICO_TRIGGER_CHANNEL_PROPERTIES],
        autoTriggerMicroSeconds: int,
    ) -> PICO_STATUS:
        n = len(channelProperties)
        props = (PICO_TRIGGER_CHANNEL_PROPERTIES * n)(*channelProperties)
        return self._psospaSetTriggerChannelProperties(
            handle, props, n, autoTriggerMicroSeconds
        )

    def psospaSetTriggerChannelConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PICO_CONDITION],
        action: PICO_ACTION,
    ) -> PICO_STATUS:
        n = len(conditions)
        conds = (PICO_CONDITION * n)(*conditions)
        return self._psospaSetTriggerChannelConditions(handle, conds, n, action)

    def psospaSetTriggerChannelDirections(
        self, handle: c_int16, directions: Sequence[PICO_DIRECTION]
    ) -> PICO_STATUS:
        n = len(directions)
        dirs = (PICO_DIRECTION * n)(*directions)
        return self._psospaSetTriggerChannelDirections(handle, dirs, n)

    def psospaSetTriggerDelay(self, handle: c_int16, delay: int) -> PICO_STATUS:
        return self._psospaSetTriggerDelay(handle, delay)

    def psospaSetTriggerHoldoffCounterBySamples(
        self, handle: c_int16, holdoffSamples: int
    ) -> PICO_STATUS:
        return self._psospaSetTriggerHoldoffCounterBySamples(handle, holdoffSamples)

    def psospaSetPulseWidthQualifierProperties(
        self, handle: c_int16, lower: int, upper: int, type: PICO_PULSE_WIDTH_TYPE
    ) -> PICO_STATUS:
        return self._psospaSetPulseWidthQualifierProperties(handle, lower, upper, type)

    def psospaSetPulseWidthQualifierConditions(
        self,
        handle: c_int16,
        conditions: Sequence[PICO_CONDITION],
        action: PICO_ACTION,
    ) -> PICO_STATUS:
        n = len(conditions)
        conds = (PICO_CONDITION * n)(*conditions)
        return self._psospaSetPulseWidthQualifierConditions(handle, conds, n, action)

    def psospaSetPulseWidthQualifierDirections(
        self, handle: c_int16, directions: Sequence[PICO_DIRECTION]
    ) -> PICO_STATUS:
        n = len(directions)
        dirs = (PICO_DIRECTION * n)(*directions)
        return self._psospaSetPulseWidthQualifierDirections(handle, dirs, n)

    def psospaSetTriggerDigitalPortProperties(
        self,
        handle: c_int16,
        port: PICO_CHANNEL,
        directions: Sequence[PICO_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> PICO_STATUS:
        n = len(directions)
        dirs = (PICO_DIGITAL_CHANNEL_DIRECTIONS * n)(*directions)
        return self._psospaSetTriggerDigitalPortProperties(handle, port, dirs, n)

    def psospaSetPulseWidthDigitalPortProperties(
        self,
        handle: c_int16,
        port: PICO_CHANNEL,
        directions: Sequence[PICO_DIGITAL_CHANNEL_DIRECTIONS],
    ) -> PICO_STATUS:
        n = len(directions)
        dirs = (PICO_DIGITAL_CHANNEL_DIRECTIONS * n)(*directions)
        return self._psospaSetPulseWidthDigitalPortProperties(handle, port, dirs, n)

    def psospaGetTriggerTimeOffset(
        self, handle: c_int16, segmentIndex: int
    ) -> tuple[PICO_STATUS, int, PICO_TIME_UNITS]:
        time = c_int64(0)
        timeUnits = PICO_TIME_UNITS_T(0)
        return (
            self._psospaGetTriggerTimeOffset(
                handle, byref(time), byref(timeUnits), segmentIndex
            ),
            time.value,
            PICO_TIME_UNITS(timeUnits.value),
        )

    def psospaGetValuesTriggerTimeOffsetBulk(
        self, handle: c_int16, fromSegmentIndex: int, toSegmentIndex: int
    ) -> tuple[PICO_STATUS, list[int], list[PICO_TIME_UNITS]]:
        assert fromSegmentIndex <= toSegmentIndex
        n = (toSegmentIndex - fromSegmentIndex) + 1
        times = (c_int64 * n)()
        timeUnits = (PICO_TIME_UNITS_T * n)()
        return (
            self._psospaGetValuesTriggerTimeOffsetBulk(
                handle, times, timeUnits, fromSegmentIndex, toSegmentIndex
            ),
            list(times),
            [PICO_TIME_UNITS(u) for u in timeUnits],
        )

    def psospaSetDataBuffer(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        buffer: c_void_p,
        nsamples: int,
        datatype: PICO_DATA_TYPE,
        waveform: int,
        downsampleMode: PICO_RATIO_MODE,
        action: PICO_ACTION,
    ):
        assert nsamples > 0
        return self._psospaSetDataBuffer(
            handle,
            channel,
            buffer,
            nsamples,
            datatype,
            waveform,
            downsampleMode,
            action,
        )

    def psospaSetDataBuffers(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        bufferMax: c_void_p | int | None,
        bufferMin: c_void_p | int | None,
        nSamples: int,
        dataType: PICO_DATA_TYPE,
        waveform: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        action: PICO_ACTION,
    ) -> PICO_STATUS:
        return self._psospaSetDataBuffers(
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

    def psospaRunBlock(
        self,
        handle: c_int16,
        preSamples: int,
        postSamples: int,
        timebase: int,
        segment: int,
        callback: Callable[[c_int16, PICO_STATUS], None] | None = None,
    ):
        assert preSamples >= 0
        assert postSamples >= 0
        timeInd = c_double(0)
        lpReady = psospaBlockReady()  # NULL; ctypes rejects None here
        if callback is not None:

            def cbwrapper(handle: c_int16, status: int, _: int | None):
                callback(handle, PICO_STATUS(status))

            lpReady = psospaBlockReady(cbwrapper)
        status = self._with_callback(
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
        return status, float(timeInd.value)

    def psospaIsReady(self, handle: c_int16):
        ready = c_int16(0)
        return self._psospaIsReady(handle, byref(ready)), ready.value == 1

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
    ) -> tuple[PICO_STATUS, float]:
        sampleInterval_ = c_double(sampleInterval)
        return (
            self._psospaRunStreaming(
                handle,
                byref(sampleInterval_),
                sampleIntervalTimeUnits,
                maxPreTriggerSamples,
                maxPostTriggerSamples,
                1 if autoStop else 0,
                downSampleRatio,
                downSampleRatioMode,
            ),
            sampleInterval_.value,
        )

    def psospaGetStreamingLatestValues(
        self,
        handle: c_int16,
        streamingDataInfo: Sequence[PICO_STREAMING_DATA_INFO],
    ) -> tuple[
        PICO_STATUS,
        list[PICO_STREAMING_DATA_INFO],
        PICO_STREAMING_DATA_TRIGGER_INFO,
    ]:
        n = len(streamingDataInfo)
        infos = (PICO_STREAMING_DATA_INFO * n)(*streamingDataInfo)
        triggerInfo = PICO_STREAMING_DATA_TRIGGER_INFO()
        return (
            self._psospaGetStreamingLatestValues(handle, infos, n, byref(triggerInfo)),
            list(infos),
            triggerInfo,
        )

    def psospaNoOfStreamingValues(self, handle: c_int16) -> tuple[PICO_STATUS, int]:
        noOfValues = c_uint64(0)
        return (
            self._psospaNoOfStreamingValues(handle, byref(noOfValues)),
            noOfValues.value,
        )

    def psospaGetValues(
        self,
        handle: c_int16,
        startIndex: int,
        noOfSamples: int,
        downSampleRatio: int,
        downSampleRatioMode: PICO_RATIO_MODE,
        segmentIndex: int,
    ) -> tuple[PICO_STATUS, int, PICO_CHANNEL_FLAGS]:
        noOfSamples_ = c_uint64(noOfSamples)
        overflow = c_int16(0)
        return (
            self._psospaGetValues(
                handle,
                startIndex,
                byref(noOfSamples_),
                downSampleRatio,
                downSampleRatioMode,
                segmentIndex,
                byref(overflow),
            ),
            noOfSamples_.value,
            PICO_CHANNEL_FLAGS(overflow.value),
        )

    def psospaGetValuesBulk(
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
        overflow = (c_int16 * nsegments)(0)
        return (
            self._psospaGetValuesBulk(
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
        self, callback: Callable[[int, PICO_STATUS, int, PICO_CHANNEL_FLAGS], None]
    ):
        def cbwrapper(
            handle: int, status: int, noOfSamples: int, overflow: int, _: int | None
        ):
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
    ) -> PICO_STATUS:
        """``lpDataReady(handle, status, noOfSamples, overflow)`` is called once the
        data has been written to the buffers set up with psospaSetDataBuffer(s)."""
        cb = self._data_ready(lpDataReady)
        return self._with_callback(
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
    ) -> PICO_STATUS:
        """See :meth:`psospaGetValuesAsync` for the callback signature."""
        cb = self._data_ready(lpDataReady)
        return self._with_callback(
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
    ) -> tuple[PICO_STATUS, c_uint64, Array[c_int16]]:
        """Set up data retrieval during the next psospaRunBlock.

        The driver fills the returned ``noOfSamples`` and ``overflow`` ctypes
        objects once the capture has completed, so they are returned as is
        (read ``noOfSamples.value`` and ``overflow[i]`` afterwards). The wrapper
        keeps them alive until they are replaced by a later call.
        """
        assert fromSegmentIndex <= toSegmentIndex
        noOfSamples_ = c_uint64(noOfSamples)
        overflow = (c_int16 * ((toSegmentIndex - fromSegmentIndex) + 1))()
        status = self._with_callback(
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
        return status, noOfSamples_, overflow

    def psospaStopUsingGetValuesOverlapped(self, handle: c_int16) -> PICO_STATUS:
        return self._psospaStopUsingGetValuesOverlapped(handle)

    def psospaGetNoOfCaptures(self, handle: c_int16) -> tuple[PICO_STATUS, int]:
        nCaptures = c_uint64(0)
        return self._psospaGetNoOfCaptures(handle, byref(nCaptures)), nCaptures.value

    def psospaGetNoOfProcessedCaptures(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, int]:
        nProcessedCaptures = c_uint64(0)
        return (
            self._psospaGetNoOfProcessedCaptures(handle, byref(nProcessedCaptures)),
            nProcessedCaptures.value,
        )

    def psospaStop(self, handle: c_int16) -> PICO_STATUS:
        return self._psospaStop(handle)

    def psospaSetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return self._psospaSetNoOfCaptures(handle, ncaptures)

    def psospaGetTriggerInfo(
        self, handle: c_int16, firstSegmentIndex: int, segmentCount: int
    ) -> tuple[PICO_STATUS, list[PICO_TRIGGER_INFO]]:
        assert segmentCount > 0
        triggerInfo = (PICO_TRIGGER_INFO * segmentCount)()
        return (
            self._psospaGetTriggerInfo(
                handle, triggerInfo, firstSegmentIndex, segmentCount
            ),
            list(triggerInfo),
        )

    def psospaEnumerateUnits(self) -> tuple[PICO_STATUS, int, list[str]]:
        count = c_int16(0)
        serials = create_string_buffer(_ENUMERATE_BUFFER_SIZE)
        serialLth = c_int16(_ENUMERATE_BUFFER_SIZE)
        status = self._psospaEnumerateUnits(byref(count), serials, byref(serialLth))
        serialstr = serials.value.decode("utf-8")
        return status, count.value, [s for s in serialstr.split(",") if s]

    def psospaPingUnit(self, handle: c_int16) -> PICO_STATUS:
        return self._psospaPingUnit(handle)

    def psospaGetAnalogueOffsetLimits(
        self,
        handle: c_int16,
        rangeMin: float,
        rangeMax: float,
        rangeType: PICO_PROBE_RANGE_INFO,
        coupling: PICO_COUPLING,
    ) -> tuple[PICO_STATUS, float, float]:
        """Returns ``(status, maximumVoltage, minimumVoltage)``."""
        maximumVoltage = c_double(0)
        minimumVoltage = c_double(0)
        return (
            self._psospaGetAnalogueOffsetLimits(
                handle,
                _range_value(rangeMin),
                _range_value(rangeMax),
                rangeType,
                coupling,
                byref(maximumVoltage),
                byref(minimumVoltage),
            ),
            maximumVoltage.value,
            minimumVoltage.value,
        )

    def psospaGetMinimumTimebaseStateless(
        self,
        handle: c_int16,
        enabledChannels: PICO_CHANNEL_FLAGS,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        return (
            self._psospaGetMinimumTimebaseStateless(
                handle,
                enabledChannels,
                byref(timebase),
                byref(timeInterval),
                resolution,
            ),
            timebase.value,
            float(timeInterval.value),
        )

    def psospaNearestSampleIntervalStateless(
        self,
        handle: c_int16,
        enabledChannels: PICO_CHANNEL_FLAGS,
        timeIntervalRequested: float,
        roundFaster: bool,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        return (
            self._psospaNearestSampleIntervalStateless(
                handle,
                enabledChannels,
                timeIntervalRequested,
                1 if roundFaster else 0,
                resolution,
                byref(timebase),
                byref(timeInterval),
            ),
            timebase.value,
            float(timeInterval.value),
        )

    def psospaSetDeviceResolution(
        self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION
    ) -> PICO_STATUS:
        return self._psospaSetDeviceResolution(handle, resolution)

    def psospaGetDeviceResolution(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, PICO_DEVICE_RESOLUTION]:
        resolution = PICO_DEVICE_RESOLUTION_T(0)
        return (
            self._psospaGetDeviceResolution(handle, byref(resolution)),
            PICO_DEVICE_RESOLUTION(resolution.value),
        )

    def psospaQueryOutputEdgeDetect(self, handle: c_int16) -> tuple[PICO_STATUS, bool]:
        state = c_int16(0)
        return self._psospaQueryOutputEdgeDetect(handle, byref(state)), state.value != 0

    def psospaSetOutputEdgeDetect(self, handle: c_int16, state: bool) -> PICO_STATUS:
        return self._psospaSetOutputEdgeDetect(handle, 1 if state else 0)

    def psospaGetScalingValues(
        self,
        handle: c_int16,
        scalingValues: Sequence[PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES],
    ) -> tuple[PICO_STATUS, list[PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES]]:
        """``scalingValues`` select channel and range; the filled-in copies are
        returned."""
        n = len(scalingValues)
        values = (PICO_SCALING_FACTORS_FOR_RANGE_TYPES_VALUES * n)(*scalingValues)
        return self._psospaGetScalingValues(handle, values, n), list(values)

    def psospaGetAdcLimits(
        self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION
    ) -> tuple[PICO_STATUS, int, int]:
        minValue = c_int16(0)
        maxValue = c_int16(0)
        return (
            self._psospaGetAdcLimits(
                handle, resolution, byref(minValue), byref(maxValue)
            ),
            minValue.value,
            maxValue.value,
        )

    def psospaCheckForUpdate(
        self, handle: c_int16
    ) -> tuple[PICO_STATUS, list[PICO_FIRMWARE_INFO], bool]:
        firmwareInfos = (PICO_FIRMWARE_INFO * _MAX_FIRMWARE_INFOS)()
        nFirmwareInfos = c_int16(_MAX_FIRMWARE_INFOS)
        updatesRequired = c_uint16(0)
        status = self._psospaCheckForUpdate(
            handle, firmwareInfos, byref(nFirmwareInfos), byref(updatesRequired)
        )
        n = max(0, min(nFirmwareInfos.value, _MAX_FIRMWARE_INFOS))
        return status, list(firmwareInfos[:n]), updatesRequired.value != 0

    def psospaStartFirmwareUpdate(
        self, handle: c_int16, progress: Callable[[int, int], None] | None
    ) -> PICO_STATUS:
        """``progress(handle, progressPercent)`` is called during the update."""
        cb = PicoUpdateFirmwareProgress()  # NULL; ctypes rejects None here
        if progress is not None:

            def cbwrapper(handle: int, percent: int):
                progress(handle, percent)

            cb = PicoUpdateFirmwareProgress(cbwrapper)
        return self._with_callback(
            self._callback_key("psospaStartFirmwareUpdate", handle),
            cb,
            lambda: self._psospaStartFirmwareUpdate(handle, cb),
        )

    def psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus(
        self, handle: c_int16, nChannelTrippedStatus: int
    ) -> tuple[PICO_STATUS, list[PICO_CHANNEL_OVERVOLTAGE_TRIPPED]]:
        tripped = (PICO_CHANNEL_OVERVOLTAGE_TRIPPED * nChannelTrippedStatus)()
        return (
            self._psospaResetChannelsAndReportAllChannelsOvervoltageTripStatus(
                handle, tripped, nChannelTrippedStatus
            ),
            list(tripped),
        )

    def psospaReportAllChannelsOvervoltageTripStatus(
        self, handle: c_int16, nChannelTrippedStatus: int
    ) -> tuple[PICO_STATUS, list[PICO_CHANNEL_OVERVOLTAGE_TRIPPED]]:
        tripped = (PICO_CHANNEL_OVERVOLTAGE_TRIPPED * nChannelTrippedStatus)()
        return (
            self._psospaReportAllChannelsOvervoltageTripStatus(
                handle, tripped, nChannelTrippedStatus
            ),
            list(tripped),
        )

    def psospaSetLedColours(
        self,
        handle: c_int16,
        colourProperties: Sequence[PICO_LED_COLOUR_PROPERTIES],
    ) -> PICO_STATUS:
        n = len(colourProperties)
        props = (PICO_LED_COLOUR_PROPERTIES * n)(*colourProperties)
        return self._psospaSetLedColours(handle, props, n)

    def psospaSetLedBrightness(self, handle: c_int16, brightness: int) -> PICO_STATUS:
        return self._psospaSetLedBrightness(handle, brightness)

    def psospaSetLedStates(
        self,
        handle: c_int16,
        stateProperties: Sequence[PICO_LED_STATE_PROPERTIES],
    ) -> PICO_STATUS:
        n = len(stateProperties)
        props = (PICO_LED_STATE_PROPERTIES * n)(*stateProperties)
        return self._psospaSetLedStates(handle, props, n)

    def psospaSetAuxIoMode(
        self, handle: c_int16, auxIoMode: PICO_AUXIO_MODE
    ) -> PICO_STATUS:
        return self._psospaSetAuxIoMode(handle, auxIoMode)


__all__ = (
    "PicoScope3000eWrapper",
    "psospaBlockReady",
    "psospaDataReady",
)
