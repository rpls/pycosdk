from ctypes import Structure, c_int16
from typing import final

from .status import PICO_INFO_T


@final
class PICO_VERSION(Structure):
    _fields_ = [
        ("major_", c_int16),
        ("minor_", c_int16),
        ("revision_", c_int16),
        ("build_", c_int16),
    ]


@final
class PICO_FIRMWARE_INFO(Structure):
    _fields_ = [
        ("firmwareType", PICO_INFO_T),
        ("currentVersion", PICO_VERSION),
        ("updateVersion", PICO_VERSION),
        ("updateRequired", c_int16),
    ]


__all__ = (
    "PICO_VERSION",
    "PICO_FIRMWARE_INFO",
)
