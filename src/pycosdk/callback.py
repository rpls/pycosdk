from ctypes import POINTER, c_int16, c_uint16, c_uint32, c_uint64, c_void_p

from ._base import CALLBACK_FUNCTYPE
from .deviceenums import (
    PICO_CLOCK_REFERENCE_T,
    PICO_READ_SELECTION_T,
    PICO_TEMPERATURE_REFERENCE_T,
)
from .devicestructs import PICO_USER_PROBE_INTERACTIONS
from .status import PICO_STATUS_T

PicoUpdateFirmwareProgress = CALLBACK_FUNCTYPE(None, c_int16, c_uint16)

PicoProbeInteractions = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, POINTER(PICO_USER_PROBE_INTERACTIONS), c_uint32
)

PicoDataReadyUsingReads = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_READ_SELECTION_T, PICO_STATUS_T, c_uint64, c_uint64, c_void_p
)

PicoExternalReferenceInteractions = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_STATUS_T, PICO_CLOCK_REFERENCE_T
)

PicoAWGOverrangeInteractions = CALLBACK_FUNCTYPE(None, c_int16, PICO_STATUS_T)

PicoTemperatureSensorInteractions = CALLBACK_FUNCTYPE(
    None, c_int16, PICO_TEMPERATURE_REFERENCE_T
)

__all__ = (
    "PicoAWGOverrangeInteractions",
    "PicoDataReadyUsingReads",
    "PicoExternalReferenceInteractions",
    "PicoProbeInteractions",
    "PicoTemperatureSensorInteractions",
    "PicoUpdateFirmwareProgress",
)
