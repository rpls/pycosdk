from ctypes import CFUNCTYPE, POINTER, c_int16, c_uint16, c_uint32, c_uint64, c_void_p

from .deviceenums import (
    PICO_CLOCK_REFERENCE_T,
    PICO_READ_SELECTION_T,
    PICO_TEMPERATURE_REFERENCE_T,
)
from .devicestructs import PICO_USER_PROBE_INTERACTIONS
from .status import PICO_STATUS_T

PicoUpdateFirmwareProgress = CFUNCTYPE(None, c_int16, c_uint16)

PicoProbeInteractions = CFUNCTYPE(
    None, c_int16, PICO_STATUS_T, POINTER(PICO_USER_PROBE_INTERACTIONS), c_uint32
)

PicoDataReadyUsingReads = CFUNCTYPE(
    None, c_int16, PICO_READ_SELECTION_T, PICO_STATUS_T, c_uint64, c_uint64, c_void_p
)

PicoExternalReferenceInteractions = CFUNCTYPE(
    None, c_int16, PICO_STATUS_T, PICO_CLOCK_REFERENCE_T
)

PicoAWGOverrangeInteractions = CFUNCTYPE(None, c_int16, PICO_STATUS_T)

PicoTemperatureSensorInteractions = CFUNCTYPE(
    None, c_int16, PICO_TEMPERATURE_REFERENCE_T
)

__all__ = (
    "PicoUpdateFirmwareProgress",
    "PicoProbeInteractions",
    "PicoDataReadyUsingReads",
    "PicoExternalReferenceInteractions",
    "PicoAWGOverrangeInteractions",
    "PicoTemperatureSensorInteractions",
)
