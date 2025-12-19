import sys
from ctypes import (
    CFUNCTYPE,
    POINTER,
    LibraryLoader,
    byref,
    c_char_p,
    c_double,
    c_int16,
    c_int32,
    c_uint32,
    c_uint64,
    c_void_p,
    create_string_buffer,
)
from ctypes.util import find_library
from typing import Any, Callable

from .connectprobe import PICO_CONNECT_PROBE_RANGE, PICO_CONNECT_PROBE_RANGE_T
from .deviceenums import (
    PICO_ACTION,
    PICO_ACTION_T,
    PICO_BANDWIDTH_LIMITER,
    PICO_BANDWIDTH_LIMITER_T,
    PICO_CHANNEL,
    PICO_CHANNEL_FLAGS,
    PICO_CHANNEL_FLAGS_T,
    PICO_CHANNEL_T,
    PICO_CLOCK_REFERENCE,
    PICO_CLOCK_REFERENCE_T,
    PICO_COUPLING,
    PICO_COUPLING_T,
    PICO_DATA_TYPE,
    PICO_DATA_TYPE_T,
    PICO_DEVICE_RESOLUTION,
    PICO_DEVICE_RESOLUTION_T,
    PICO_DIGITAL_PORT_HYSTERESIS,
    PICO_DIGITAL_PORT_HYSTERESIS_T,
    PICO_RATIO_MODE,
    PICO_RATIO_MODE_T,
    PICO_THRESHOLD_DIRECTION,
    PICO_THRESHOLD_DIRECTION_T,
)
from .devicestructs import PICO_TRIGGER_INFO, PICO_USER_PROBE_INTERACTIONS
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T

ps6000aBlockReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)
ps6000aDataReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_uint64, c_int16, c_void_p)
ps6000aProbeInteractions = CFUNCTYPE(
    None, c_int16, PICO_STATUS_T, POINTER(PICO_USER_PROBE_INTERACTIONS), c_uint32
)
PicoExternalReferenceInterations = CFUNCTYPE(
    None, c_int16, PICO_STATUS_T, PICO_CLOCK_REFERENCE_T
)


class PicoScope6000aWrapper:
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

        self._ps6000aOpenUnit = getattr(self.lib, "ps6000aOpenUnit")
        self._ps6000aOpenUnit.resType = PICO_STATUS_T
        self._ps6000aOpenUnit.argTypes = [
            POINTER(c_int16),
            c_char_p,
            PICO_DEVICE_RESOLUTION_T,
        ]

        self._ps6000aCloseUnit = getattr(self.lib, "ps6000aCloseUnit")
        self._ps6000aCloseUnit.resType = PICO_STATUS_T
        self._ps6000aCloseUnit.argTypes = [c_int16]

        self._ps6000aGetUnitInfo = getattr(self.lib, "ps6000aGetUnitInfo")
        self._ps6000aGetUnitInfo.resType = PICO_STATUS_T
        self._ps6000aGetUnitInfo.argTypes = [
            c_int16,
            c_char_p,
            c_int16,
            POINTER(c_int16),
            PICO_INFO_T,
        ]

        self._ps6000aMemorySegments = getattr(self.lib, "ps6000aMemorySegments")
        self._ps6000aMemorySegments.resType = PICO_STATUS_T
        self._ps6000aMemorySegments.argTypes = [c_int16, c_uint64, POINTER(c_uint64)]

        self._ps6000aMemorySegmentsBySamples = getattr(
            self.lib, "ps6000aMemorySegmentsBySamples"
        )
        self._ps6000aMemorySegmentsBySamples.resType = PICO_STATUS_T
        self._ps6000aMemorySegmentsBySamples.argTypes = [
            c_int16,
            c_uint64,
            POINTER(c_uint64),
        ]

        self._ps6000aQueryMaxSegmentsBySamples = getattr(
            self.lib, "ps6000aQueryMaxSegmentsBySamples"
        )
        self._ps6000aQueryMaxSegmentsBySamples.resType = PICO_STATUS_T
        self._ps6000aQueryMaxSegmentsBySamples.argTypes = [
            c_int16,
            c_uint64,
            c_uint32,
            POINTER(c_uint64),
            PICO_DEVICE_RESOLUTION_T,
        ]

        self._ps6000aSetNoOfCaptures = getattr(self.lib, "ps6000aSetNoOfCaptures")
        self._ps6000aSetNoOfCaptures.resType = PICO_STATUS_T
        self._ps6000aSetNoOfCaptures.argTypes = [c_int16, c_uint64]

        self._ps6000aSetChannelOn = getattr(self.lib, "ps6000aSetChannelOn")
        self._ps6000aSetChannelOn.resType = PICO_STATUS_T
        self._ps6000aSetChannelOn.argTypes = [
            c_int16,
            PICO_CHANNEL_T,
            PICO_COUPLING_T,
            PICO_CONNECT_PROBE_RANGE_T,
            c_double,
            PICO_BANDWIDTH_LIMITER_T,
        ]

        self._ps6000aSetChannelOff = getattr(self.lib, "ps6000aSetChannelOff")
        self._ps6000aSetChannelOff.resType = PICO_STATUS_T
        self._ps6000aSetChannelOff.argTypes = [c_int16, PICO_CHANNEL_T]

        self._ps6000aSetDigitalPortOff = getattr(self.lib, "ps6000aSetDigitalPortOff")
        self._ps6000aSetDigitalPortOff.resType = PICO_STATUS_T
        self._ps6000aSetDigitalPortOff.argTypes = [c_int16, PICO_CHANNEL_T]

        self._ps6000aSetDigitalPortOn = getattr(self.lib, "ps6000aSetDigitalPortOn")
        self._ps6000aSetDigitalPortOn.resType = PICO_STATUS_T
        self._ps6000aSetDigitalPortOn.argTypes = [
            c_int16,
            PICO_CHANNEL_T,
            POINTER(c_int16),
            c_int16,
            PICO_DIGITAL_PORT_HYSTERESIS_T,
        ]

        self._ps6000aGetTimebase = getattr(self.lib, "ps6000aGetTimebase")
        self._ps6000aGetTimebase.resType = PICO_STATUS_T
        self._ps6000aGetTimebase.argTypes = [
            c_int16,
            c_uint32,
            c_uint64,
            POINTER(c_double),
            POINTER(c_uint64),
            c_uint64,
        ]

        self._ps6000aGetMinimumTimebaseStateless = getattr(
            self.lib, "ps6000aGetMinimumTimebaseStateless"
        )
        self._ps6000aGetMinimumTimebaseStateless.resType = PICO_STATUS_T
        self._ps6000aGetMinimumTimebaseStateless.argTypes = [
            c_int16,
            PICO_CHANNEL_FLAGS_T,
            POINTER(c_int32),
            POINTER(c_double),
            PICO_DEVICE_RESOLUTION_T,
        ]

        self._ps6000aNearestSampleIntervalStateless = getattr(
            self.lib, "ps6000aNearestSampleIntervalStateless"
        )
        self._ps6000aNearestSampleIntervalStateless.resType = PICO_STATUS_T
        self._ps6000aNearestSampleIntervalStateless.argTypes = [
            c_int16,
            PICO_CHANNEL_FLAGS_T,
            c_double,
            PICO_DEVICE_RESOLUTION_T,
            POINTER(c_uint32),
            POINTER(c_double),
        ]

        self._ps6000aChannelCombinationsStateless = getattr(
            self.lib, "ps6000aChannelCombinationsStateless"
        )
        self._ps6000aChannelCombinationsStateless.resType = PICO_STATUS_T
        self._ps6000aChannelCombinationsStateless.argTypes = [
            c_int16,
            POINTER(PICO_CHANNEL_FLAGS_T),
            POINTER(c_uint32),
            PICO_DEVICE_RESOLUTION_T,
            c_uint32,
        ]

        self._ps6000aSetSimpleTrigger = getattr(self.lib, "ps6000aSetSimpleTrigger")
        self._ps6000aSetSimpleTrigger.resType = PICO_STATUS_T
        self._ps6000aSetSimpleTrigger.argTypes = [
            c_int16,
            c_int16,
            PICO_CHANNEL_T,
            c_int16,
            PICO_THRESHOLD_DIRECTION_T,
            c_uint64,
            c_uint32,
        ]

        self._ps6000aSetTriggerDelay = getattr(self.lib, "ps6000aSetTriggerDelay")
        self._ps6000aSetTriggerDelay.resType = PICO_STATUS_T
        self._ps6000aSetTriggerDelay.argTypes = [c_int16, c_uint64]

        self._ps6000aSetDataBuffer = getattr(self.lib, "ps6000aSetDataBuffer")
        self._ps6000aSetDataBuffer.resType = PICO_STATUS_T
        self._ps6000aSetDataBuffer.argTypes = [
            c_int16,
            PICO_CHANNEL_T,
            c_void_p,
            c_int32,
            PICO_DATA_TYPE_T,
            c_uint64,
            PICO_RATIO_MODE_T,
            PICO_ACTION_T,
        ]

        self._ps6000aRunBlock = getattr(self.lib, "ps6000aRunBlock")
        self._ps6000aRunBlock.resType = PICO_STATUS_T
        self._ps6000aRunBlock.argTypes = [
            c_int16,
            c_uint64,
            c_uint64,
            c_uint32,
            POINTER(c_double),
            c_uint64,
            ps6000aBlockReady,
            c_void_p,
        ]
        self._lpReady: Any | None = None

        self._ps6000aIsReady = getattr(self.lib, "ps6000aIsReady")
        self._ps6000aIsReady.resType = PICO_STATUS_T
        self._ps6000aIsReady.argTypes = [c_int16, POINTER(c_int16)]

        self._ps6000aGetValues = getattr(self.lib, "ps6000aGetValues")
        self._ps6000aGetValues.resType = PICO_STATUS_T
        self._ps6000aGetValues.argTypes = [
            c_int16,
            c_uint64,
            POINTER(c_uint64),
            c_uint64,
            PICO_RATIO_MODE_T,
            c_uint64,
            POINTER(c_int16),
        ]

        self._ps6000aGetValuesBulk = getattr(self.lib, "ps6000aGetValuesBulk")
        self._ps6000aGetValuesBulk.resType = PICO_STATUS_T
        self._ps6000aGetValuesBulk.argTypes = [
            c_int16,
            c_uint64,
            POINTER(c_uint64),
            c_uint64,
            c_uint64,
            c_uint64,
            PICO_RATIO_MODE_T,
            POINTER(c_int16),
        ]

        self._ps6000aGetTriggerInfo = getattr(self.lib, "ps6000aGetTriggerInfo")
        self._ps6000aGetTriggerInfo.resType = PICO_STATUS_T
        self._ps6000aGetTriggerInfo.argTypes = [
            c_int16,
            POINTER(PICO_TRIGGER_INFO),
            c_uint64,
            c_uint64,
        ]

        self._ps6000aSetDeviceResolution = getattr(
            self.lib, "ps6000aSetDeviceResolution"
        )
        self._ps6000aSetDeviceResolution.resType = PICO_STATUS_T
        self._ps6000aSetDeviceResolution.argTypes = [c_int16, PICO_DEVICE_RESOLUTION_T]

        self._ps6000aGetDeviceResolution = getattr(
            self.lib, "ps6000aGetDeviceResolution"
        )
        self._ps6000aGetDeviceResolution.resType = PICO_STATUS_T
        self._ps6000aGetDeviceResolution.argTypes = [c_int16, PICO_DEVICE_RESOLUTION_T]

        self._ps6000aGetAdcLimits = getattr(self.lib, "ps6000aGetAdcLimits")
        self._ps6000aGetAdcLimits.resType = PICO_STATUS_T
        self._ps6000aGetAdcLimits.argTypes = [
            c_int16,
            PICO_DEVICE_RESOLUTION_T,
            POINTER(c_int16),
            POINTER(c_int16),
        ]

        self._ps6000aStop = getattr(self.lib, "ps6000aStop")
        self._ps6000aStop.resType = PICO_STATUS_T
        self._ps6000aStop.argTypes = [c_int16]

        self._ps6000aSetExternalReferenceInteractionCallback = getattr(
            self.lib, "ps6000aSetExternalReferenceInteractionCallback"
        )
        self._ps6000aSetExternalReferenceInteractionCallback.resType = PICO_STATUS_T
        self._ps6000aSetExternalReferenceInteractionCallback.argTypes = [
            c_int16,
            PicoExternalReferenceInterations,
        ]
        self._extrefcb: Any | None = None

    def ps6000aOpenUnit(self, serial: str | None, resolution: PICO_DEVICE_RESOLUTION):
        handle = c_int16(0)
        ser = c_char_p(serial.encode()) if serial is not None else 0
        return (
            PICO_STATUS(self._ps6000aOpenUnit(byref(handle), ser, resolution)),
            handle,
        )

    def ps6000aCloseUnit(self, handle: c_int16):
        return PICO_STATUS(self._ps6000aCloseUnit(handle))

    def ps6000aGetTimebase(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ):
        timeIntervalNS = c_double(0)
        maxSamples = c_uint64(0)
        return (
            PICO_STATUS(
                self._ps6000aGetTimebase(
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

    def ps6000aGetMinimumTimebaseStateless(
        self,
        handle: c_int16,
        enabledChannels: PICO_CHANNEL_FLAGS,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        return (
            PICO_STATUS(
                self._ps6000aGetMinimumTimebaseStateless(
                    handle,
                    enabledChannels,
                    byref(timebase),
                    byref(timeInterval),
                    resolution,
                )
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
            PICO_STATUS(
                self._ps6000aNearestSampleIntervalStateless(
                    handle,
                    enabledChannels,
                    c_double(requiredInterval),
                    resolution,
                    byref(timebase),
                    byref(timeInterval),
                )
            ),
            timebase.value,
            timeInterval.value,
        )

    def ps6000aSetChannelOn(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        coupling: PICO_COUPLING,
        range: PICO_CONNECT_PROBE_RANGE,
        analog_offset: float,
        bandwidth: PICO_BANDWIDTH_LIMITER,
    ):
        return PICO_STATUS(
            self._ps6000aSetChannelOn(
                handle, channel, coupling, range, c_double(analog_offset), bandwidth
            )
        )

    def ps6000aSetChannelOff(self, handle: c_int16, channel: PICO_CHANNEL):
        return PICO_STATUS(self._ps6000aSetChannelOff(handle, channel))

    def ps6000aSetDigitalPortOn(
        self,
        handle: c_int16,
        port: PICO_CHANNEL,
        logicThresholds: list[int],
        hysteresis: PICO_DIGITAL_PORT_HYSTERESIS,
    ):
        logicThresholdLevel = (c_int16 * len(logicThresholds))(*logicThresholds)
        return PICO_STATUS(
            self._ps6000aSetDigitalPortOn(
                handle, port, logicThresholdLevel, len(logicThresholds), hysteresis
            )
        )

    def ps6000aSetDigitalPortOff(self, handle: c_int16, port: PICO_CHANNEL):
        return PICO_STATUS(self._ps6000aSetDigitalPortOff(handle, port))

    def ps6000aGetAdcLimits(self, handle: c_int16, resolution: PICO_DEVICE_RESOLUTION):
        minCount = c_int16(0)
        maxCount = c_int16(0)
        return (
            PICO_STATUS(
                self._ps6000aGetAdcLimits(
                    handle, resolution, byref(minCount), byref(maxCount)
                )
            ),
            minCount.value,
            maxCount.value,
        )

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
        return PICO_STATUS(
            self._ps6000aSetSimpleTrigger(
                handle,
                1 if enable else 0,
                source,
                threshold,
                direction,
                delay,
                autoTriggerUS,
            )
        )

    def ps6000aQueryMaxSegmentsBySamples(
        self,
        handle: c_int16,
        nsamples: int,
        nchannels: int,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        maxSegments = c_uint64(0)
        return (
            PICO_STATUS(
                self._ps6000aQueryMaxSegmentsBySamples(
                    handle, nsamples, nchannels, byref(maxSegments), resolution
                )
            ),
            maxSegments.value,
        )

    def ps6000aMemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_uint64(0)
        return (
            PICO_STATUS(
                self._ps6000aMemorySegments(handle, nsegments, byref(maxSamples))
            ),
            maxSamples.value,
        )

    def ps6000aMemorySegmentsBySamples(self, handle: c_int16, nsamples: int):
        assert nsamples > 0
        maxSegments = c_uint64(0)
        return (
            PICO_STATUS(
                self._ps6000aMemorySegmentsBySamples(
                    handle, nsamples, byref(maxSegments)
                )
            ),
            maxSegments.value,
        )

    def ps6000aSetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return PICO_STATUS(self._ps6000aSetNoOfCaptures(handle, ncaptures))

    def ps6000aRunBlock(
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
        timeInd = c_double(0)
        self._lpReady = None
        if callback is not None:

            def cbwrapper(handle: c_int16, status: PICO_STATUS_T, _: c_void_p):
                callback(handle, PICO_STATUS(status))

            self._lpReady = ps6000aBlockReady(cbwrapper)
        return (
            PICO_STATUS(
                self._ps6000aRunBlock(
                    handle,
                    preSamples,
                    postSamples,
                    timebase,
                    byref(timeInd),
                    segment,
                    self._lpReady,
                    None,
                )
            ),
            timeInd.value,
        )

    def ps6000aIsReady(self, handle: c_int16):
        ready = c_int16(0)
        return PICO_STATUS(self._ps6000aIsReady(handle, byref(ready))), ready.value == 1

    def ps6000aSetDataBuffer(
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
        return PICO_STATUS(
            self._ps6000aSetDataBuffer(
                handle,
                channel,
                buffer,
                nsamples,
                datatype,
                waveform,
                downsampleMode,
                action,
            )
        )

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
        overflow = (c_int16 * nsegments)(0)
        return (
            PICO_STATUS(
                self._ps6000aGetValuesBulk(
                    handle,
                    startindex,
                    byref(nosamples_),
                    fromSegment,
                    toSegment,
                    downsampleRatio,
                    downsampleMode,
                    overflow,
                )
            ),
            nosamples_.value,
            [PICO_CHANNEL_FLAGS(f) for f in overflow],
        )

    def ps6000aGetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._ps6000aGetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return PICO_STATUS(status), infostr

    def ps6000aSetExternalReferenceInteractionCallback(
        self,
        handle: c_int16,
        callback: Callable[[c_int16, PICO_STATUS, PICO_CLOCK_REFERENCE], None],
    ):
        def cbwrapper(
            handle: c_int16, status: PICO_STATUS_T, reference: PICO_CLOCK_REFERENCE_T
        ):
            callback(handle, PICO_STATUS(status), PICO_CLOCK_REFERENCE(reference))

        # We need to keep a reference
        self._extrefcb = PicoExternalReferenceInterations(cbwrapper)
        return PICO_STATUS(
            self._ps6000aSetExternalReferenceInteractionCallback(handle, self._extrefcb)
        )
