# pycosdk

Yet another wrapper for the [PicoSDK](https://www.picotech.com/downloads).

`pycosdk` is a thin, fully type-annotated `ctypes` binding to Pico Technology's
PicoScope driver libraries. It stays deliberately close to the C API: method
names mirror the driver functions, and the enums and structs are transcribed
from the SDK headers as `IntEnum`/`IntFlag` and `ctypes.Structure` types.

## Requirements

- Python 3.11+
- The **PicoSDK drivers, installed separately**. `pycosdk` does not bundle or
  install them — it locates the shared libraries at runtime via
  `ctypes.util.find_library`. Download them from
  [picotech.com/downloads](https://www.picotech.com/downloads).

## Installation

```sh
pip install pycosdk
```

## Supported drivers

| Driver    | Wrapper class            |
| --------- | ------------------------ |
| `ps3000a` | `PicoScope3000aWrapper`  |
| `ps5000a` | `PicoScope5000aWrapper`  |
| `ps6000`  | `PicoScope6000Wrapper`   |
| `ps6000a` | `PicoScope6000aWrapper`  |
| `psospa`  | `PicoScope3000eWrapper`  |

Coverage is not exhaustive — each wrapper binds the subset of the driver API
that has been needed so far.

## Usage

Instantiating a wrapper loads the corresponding shared library. Pass an
explicit `library_path` if it is not on the default search path; otherwise a
`MissingLibraryException` is raised when the library cannot be found.

Methods return the driver's `PICO_STATUS` as an enum member, followed by any
output parameters. Statuses are returned, not raised — check them yourself.

```python
from pycosdk import (
    PICO_BANDWIDTH_LIMITER,
    PICO_CHANNEL,
    PICO_CONNECT_PROBE_RANGE,
    PICO_COUPLING,
    PICO_DEVICE_RESOLUTION,
    PICO_STATUS,
    PicoScope6000aWrapper,
)

scope = PicoScope6000aWrapper()

status, handle = scope.ps6000aOpenUnit(None, PICO_DEVICE_RESOLUTION.PICO_DR_8BIT)
assert status == PICO_STATUS.PICO_OK

status = scope.ps6000aSetChannelOn(
    handle,
    PICO_CHANNEL.PICO_CHANNEL_A,
    PICO_COUPLING.PICO_DC_50OHM,
    PICO_CONNECT_PROBE_RANGE.PICO_X1_PROBE_1V,
    0.0,
    PICO_BANDWIDTH_LIMITER.PICO_BW_FULL,
)

scope.ps6000aCloseUnit(handle)
```

## Type checking

The package ships a `py.typed` marker, so annotations are visible to `mypy`,
`pyright`, and friends.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
