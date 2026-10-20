from ctypes import c_int16, c_uint16
from typing import Annotated, final

from ._struct import CStruct
from .status import PICO_INFO, PICO_INFO_T


@final
class PICO_VERSION(CStruct):
    major_: Annotated[int, c_int16]
    minor_: Annotated[int, c_int16]
    revision_: Annotated[int, c_int16]
    build_: Annotated[int, c_int16]


@final
class PICO_FIRMWARE_INFO(CStruct):
    firmwareType: Annotated[PICO_INFO, PICO_INFO_T]
    currentVersion: PICO_VERSION
    updateVersion: PICO_VERSION
    updateRequired: Annotated[bool, c_uint16]


__all__ = (
    "PICO_FIRMWARE_INFO",
    "PICO_VERSION",
)
