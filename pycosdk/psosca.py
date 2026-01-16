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
    c_int64,
    c_uint8,
    c_uint32,
    c_uint64,
    c_void_p,
    create_string_buffer,
)
from ctypes.util import find_library
from typing import Any, Callable

from .connectprobe import (
    PICO_PROBE_RANGE_INFO,
    PICO_PROBE_RANGE_INFO_T,
)
from .deviceenums import (
    PICO_ACTION,
    PICO_ACTION_T,
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
    PICO_RATIO_MODE,
    PICO_RATIO_MODE_T,
    PICO_THRESHOLD_DIRECTION,
    PICO_THRESHOLD_DIRECTION_T,
)
from .devicestructs import (
    PICO_TRIGGER_INFO,
    PICO_USB_POWER_DETAILS,
    PicoUsbPowerDetails,
)
from .status import PICO_INFO, PICO_INFO_T, PICO_STATUS, PICO_STATUS_T

psospaBlockReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_void_p)
psospaDataReady = CFUNCTYPE(None, c_int16, PICO_STATUS_T, c_uint64, c_int16, c_void_p)


class PicoScope3000eWrapper:
    def __init__(self, library_path: str | None = None):
        if library_path is None:
            library_path = find_library("psospa")
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

        self._psospaOpenUnit = getattr(self.lib, "psospaOpenUnit")
        self._psospaOpenUnit.resType = PICO_STATUS_T
        self._psospaOpenUnit.argTypes = [
            POINTER(c_int16),
            c_char_p,
            PICO_DEVICE_RESOLUTION_T,
            POINTER(PICO_USB_POWER_DETAILS),
        ]

        self._psospaCloseUnit = getattr(self.lib, "psospaCloseUnit")
        self._psospaCloseUnit.resType = PICO_STATUS_T
        self._psospaCloseUnit.argTypes = [c_int16]

        self._psospaGetUnitInfo = getattr(self.lib, "psospaGetUnitInfo")
        self._psospaGetUnitInfo.resType = PICO_STATUS_T
        self._psospaGetUnitInfo.argTypes = [
            c_int16,
            c_char_p,
            c_int16,
            POINTER(c_int16),
            PICO_INFO_T,
        ]

        self._psospaMemorySegments = getattr(self.lib, "psospaMemorySegments")
        self._psospaMemorySegments.resType = PICO_STATUS_T
        self._psospaMemorySegments.argTypes = [c_int16, c_uint64, POINTER(c_uint64)]

        self._psospaMemorySegmentsBySamples = getattr(
            self.lib, "psospaMemorySegmentsBySamples"
        )
        self._psospaMemorySegmentsBySamples.resType = PICO_STATUS_T
        self._psospaMemorySegmentsBySamples.argTypes = [
            c_int16,
            c_uint64,
            POINTER(c_uint64),
        ]

        self._psospaQueryMaxSegmentsBySamples = getattr(
            self.lib, "psospaQueryMaxSegmentsBySamples"
        )
        self._psospaQueryMaxSegmentsBySamples.resType = PICO_STATUS_T
        self._psospaQueryMaxSegmentsBySamples.argTypes = [
            c_int16,
            c_uint64,
            c_uint32,
            POINTER(c_uint64),
            PICO_DEVICE_RESOLUTION_T,
        ]

        self._psospaSetNoOfCaptures = getattr(self.lib, "psospaSetNoOfCaptures")
        self._psospaSetNoOfCaptures.resType = PICO_STATUS_T
        self._psospaSetNoOfCaptures.argTypes = [c_int16, c_uint64]

        self._psospaSetChannelOn = getattr(self.lib, "psospaSetChannelOn")
        self._psospaSetChannelOn.resType = PICO_STATUS_T
        self._psospaSetChannelOn.argTypes = [
            c_int16,
            PICO_CHANNEL_T,
            PICO_COUPLING_T,
            c_int64,
            c_int64,
            PICO_PROBE_RANGE_INFO_T,
            c_double,
            PICO_BANDWIDTH_LIMITER_T,
        ]

        self._psospaSetChannelOff = getattr(self.lib, "psospaSetChannelOff")
        self._psospaSetChannelOff.resType = PICO_STATUS_T
        self._psospaSetChannelOff.argTypes = [c_int16, PICO_CHANNEL_T]

        self._psospaSetDigitalPortOff = getattr(self.lib, "psospaSetDigitalPortOff")
        self._psospaSetDigitalPortOff.resType = PICO_STATUS_T
        self._psospaSetDigitalPortOff.argTypes = [c_int16, PICO_CHANNEL_T]

        self._psospaSetDigitalPortOn = getattr(self.lib, "psospaSetDigitalPortOn")
        self._psospaSetDigitalPortOn.resType = PICO_STATUS_T
        self._psospaSetDigitalPortOn.argTypes = [c_int16, PICO_CHANNEL_T, c_double]

        self._psospaGetTimebase = getattr(self.lib, "psospaGetTimebase")
        self._psospaGetTimebase.resType = PICO_STATUS_T
        self._psospaGetTimebase.argTypes = [
            c_int16,
            c_uint32,
            c_uint64,
            POINTER(c_double),
            POINTER(c_uint64),
            c_uint64,
        ]

        self._psospaGetMinimumTimebaseStateless = getattr(
            self.lib, "psospaGetMinimumTimebaseStateless"
        )
        self._psospaGetMinimumTimebaseStateless.resType = PICO_STATUS_T
        self._psospaGetMinimumTimebaseStateless.argTypes = [
            c_int16,
            PICO_CHANNEL_FLAGS_T,
            POINTER(c_int32),
            POINTER(c_double),
            PICO_DEVICE_RESOLUTION_T,
        ]

        self._psospaNearestSampleIntervalStateless = getattr(
            self.lib, "psospaNearestSampleIntervalStateless"
        )
        self._psospaNearestSampleIntervalStateless.resType = PICO_STATUS_T
        self._psospaNearestSampleIntervalStateless.argTypes = [
            c_int16,
            PICO_CHANNEL_FLAGS_T,
            c_double,
            c_uint8,
            PICO_DEVICE_RESOLUTION_T,
            POINTER(c_uint32),
            POINTER(c_double),
        ]

        self._psospaSetSimpleTrigger = getattr(self.lib, "psospaSetSimpleTrigger")
        self._psospaSetSimpleTrigger.resType = PICO_STATUS_T
        self._psospaSetSimpleTrigger.argTypes = [
            c_int16,
            c_int16,
            PICO_CHANNEL_T,
            c_int16,
            PICO_THRESHOLD_DIRECTION_T,
            c_uint64,
            c_uint32,
        ]

        self._psospaSetTriggerDelay = getattr(self.lib, "psospaSetTriggerDelay")
        self._psospaSetTriggerDelay.resType = PICO_STATUS_T
        self._psospaSetTriggerDelay.argTypes = [c_int16, c_uint64]

        self._psospaSetDataBuffer = getattr(self.lib, "psospaSetDataBuffer")
        self._psospaSetDataBuffer.resType = PICO_STATUS_T
        self._psospaSetDataBuffer.argTypes = [
            c_int16,
            PICO_CHANNEL_T,
            c_void_p,
            c_uint64,
            PICO_DATA_TYPE_T,
            c_uint64,
            PICO_RATIO_MODE_T,
            PICO_ACTION_T,
        ]

        self._psospaRunBlock = getattr(self.lib, "psospaRunBlock")
        self._psospaRunBlock.resType = PICO_STATUS_T
        self._psospaRunBlock.argTypes = [
            c_int16,
            c_uint64,
            c_uint64,
            c_uint32,
            POINTER(c_double),
            c_uint64,
            psospaBlockReady,
            c_void_p,
        ]
        self._lpReady: Any | None = None  # pyright: ignore[reportExplicitAny]

        self._psospaIsReady = getattr(self.lib, "psospaIsReady")
        self._psospaIsReady.resType = PICO_STATUS_T
        self._psospaIsReady.argTypes = [c_int16, POINTER(c_int16)]

        self._psospaGetValues = getattr(self.lib, "psospaGetValues")
        self._psospaGetValues.resType = PICO_STATUS_T
        self._psospaGetValues.argTypes = [
            c_int16,
            c_uint64,
            POINTER(c_uint64),
            c_uint64,
            PICO_RATIO_MODE_T,
            c_uint64,
            POINTER(c_int16),
        ]

        self._psospaGetValuesBulk = getattr(self.lib, "psospaGetValuesBulk")
        self._psospaGetValuesBulk.resType = PICO_STATUS_T
        self._psospaGetValuesBulk.argTypes = [
            c_int16,
            c_uint64,
            POINTER(c_uint64),
            c_uint64,
            c_uint64,
            c_uint64,
            PICO_RATIO_MODE_T,
            POINTER(c_int16),
        ]

        self._psospaGetTriggerInfo = getattr(self.lib, "psospaGetTriggerInfo")
        self._psospaGetTriggerInfo.resType = PICO_STATUS_T
        self._psospaGetTriggerInfo.argTypes = [
            c_int16,
            POINTER(PICO_TRIGGER_INFO),
            c_uint64,
            c_uint64,
        ]

        self._psospaSetDeviceResolution = getattr(self.lib, "psospaSetDeviceResolution")
        self._psospaSetDeviceResolution.resType = PICO_STATUS_T
        self._psospaSetDeviceResolution.argTypes = [c_int16, PICO_DEVICE_RESOLUTION_T]

        self._psospaGetDeviceResolution = getattr(self.lib, "psospaGetDeviceResolution")
        self._psospaGetDeviceResolution.resType = PICO_STATUS_T
        self._psospaGetDeviceResolution.argTypes = [
            c_int16,
            POINTER(PICO_DEVICE_RESOLUTION_T),
        ]

        self._psospaStop = getattr(self.lib, "psospaStop")
        self._psospaStop.resType = PICO_STATUS_T
        self._psospaStop.argTypes = [c_int16]

    def psospaOpenUnit(self, serial: str | None, resolution: PICO_DEVICE_RESOLUTION):
        handle = c_int16(0)
        ser = c_char_p(serial.encode()) if serial is not None else 0
        usbpwrdet = PICO_USB_POWER_DETAILS()
        return (
            PICO_STATUS(
                self._psospaOpenUnit(byref(handle), ser, resolution, byref(usbpwrdet))
            ),
            handle,
            PicoUsbPowerDetails(usbpwrdet),
        )

    def psospaCloseUnit(self, handle: c_int16):
        return PICO_STATUS(self._psospaCloseUnit(handle))

    def psospaGetTimebase(
        self, handle: c_int16, timebase: int, noSamples: int, segmentIndex: int
    ):
        timeIntervalNS = c_double(0)
        maxSamples = c_uint64(0)
        return (
            PICO_STATUS(
                self._psospaGetTimebase(
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

    def psospaGetMinimumTimebaseStateless(
        self,
        handle: c_int16,
        enabledChannels: PICO_CHANNEL_FLAGS,
        resolution: PICO_DEVICE_RESOLUTION,
    ):
        timebase = c_uint32(0)
        timeInterval = c_double(0)
        return (
            PICO_STATUS(
                self._psospaGetMinimumTimebaseStateless(
                    handle,
                    enabledChannels,
                    byref(timebase),
                    byref(timeInterval),
                    resolution,
                )
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
            PICO_STATUS(
                self._psospaNearestSampleIntervalStateless(
                    handle,
                    enabledChannels,
                    c_double(timeIntervalRequested),
                    1 if roundFaster else 0,
                    resolution,
                    byref(timebase),
                    byref(timeInterval),
                )
            ),
            timebase.value,
            float(timeInterval.value),
        )

    def psospaSetChannelOn(
        self,
        handle: c_int16,
        channel: PICO_CHANNEL,
        coupling: PICO_COUPLING,
        rangeMin: int | float,
        rangeMax: int | float,
        rangeType: PICO_PROBE_RANGE_INFO,
        analog_offset: float,
        bandwidth: PICO_BANDWIDTH_LIMITER,
    ):
        if isinstance(rangeMin, float):
            rangeMin = round(1e9 * rangeMin)
        if isinstance(rangeMax, float):
            rangeMax = round(1e9 * rangeMax)
        return PICO_STATUS(
            self._psospaSetChannelOn(
                handle,
                channel,
                coupling,
                rangeMin,
                rangeMax,
                rangeType,
                c_double(analog_offset),
                bandwidth,
            )
        )

    def psospaSetChannelOff(self, handle: c_int16, channel: PICO_CHANNEL):
        return PICO_STATUS(self._psospaSetChannelOff(handle, channel))

    def psospaSetDigitalPortOn(
        self, handle: c_int16, port: PICO_CHANNEL, logicThreshold: float
    ):
        return PICO_STATUS(self._psospaSetDigitalPortOn(handle, port, logicThreshold))

    def psospaSetDigitalPortOff(self, handle: c_int16, port: PICO_CHANNEL):
        return PICO_STATUS(self._psospaSetDigitalPortOff(handle, port))

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
        return PICO_STATUS(
            self._psospaSetSimpleTrigger(
                handle,
                1 if enable else 0,
                source,
                threshold,
                direction,
                delay,
                autoTriggerUS,
            )
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
            PICO_STATUS(
                self._psospaQueryMaxSegmentsBySamples(
                    handle, nsamples, nchannels, byref(maxSegments), resolution
                )
            ),
            maxSegments.value,
        )

    def psospaMemorySegments(self, handle: c_int16, nsegments: int):
        assert nsegments > 0
        maxSamples = c_uint64(0)
        return (
            PICO_STATUS(
                self._psospaMemorySegments(handle, nsegments, byref(maxSamples))
            ),
            maxSamples.value,
        )

    def psospaMemorySegmentsBySamples(self, handle: c_int16, nsamples: int):
        assert nsamples > 0
        maxSegments = c_uint64(0)
        return (
            PICO_STATUS(
                self._psospaMemorySegmentsBySamples(
                    handle, nsamples, byref(maxSegments)
                )
            ),
            maxSegments.value,
        )

    def psospaSetNoOfCaptures(self, handle: c_int16, ncaptures: int):
        assert ncaptures > 0
        return PICO_STATUS(self._psospaSetNoOfCaptures(handle, ncaptures))

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
        self._lpReady = None
        if callback is not None:

            def cbwrapper(handle: c_int16, status: PICO_STATUS_T, _: c_void_p):
                callback(handle, PICO_STATUS(status))

            self._lpReady = psospaBlockReady(cbwrapper)
        return (
            PICO_STATUS(
                self._psospaRunBlock(
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
            float(timeInd.value),
        )

    def psospaIsReady(self, handle: c_int16):
        ready = c_int16(0)
        return PICO_STATUS(self._psospaIsReady(handle, byref(ready))), ready.value == 1

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
        return PICO_STATUS(
            self._psospaSetDataBuffer(
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
            PICO_STATUS(
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
            ),
            nosamples_.value,
            [PICO_CHANNEL_FLAGS(f) for f in overflow],
        )

    def psospaGetUnitInfo(self, handle: c_int16, info: PICO_INFO):
        buf = create_string_buffer(bytes(255))
        size = c_int16(0)
        status = self._psospaGetUnitInfo(handle, buf, 255, byref(size), info)
        if status == PICO_STATUS.PICO_OK:
            infostr = buf.raw[: size.value - 1].decode("utf-8")
        else:
            infostr = ""
        return PICO_STATUS(status), infostr


__all__ = ("PicoScope3000eWrapper",)
