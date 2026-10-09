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
  `ctypes.util.find_library`. On macOS, it additionally looks in the SDK's
  default install location `/Library/Frameworks/PicoSDK.framework/Libraries`,
  so setting `DYLD_LIBRARY_PATH` is not needed. Download them from
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

Each wrapper binds every function declared in the corresponding SDK header
(for `ps6000a` including `ps6000aApiExperimental.h`). Functions that the
installed driver does not export raise `MissingFunctionException` when called,
so an older driver version does not prevent the wrapper from loading.

## Usage

Instantiating a wrapper loads the corresponding shared library. Pass an
explicit `library_path` if it is not on the default search path; otherwise a
`MissingLibraryException` is raised when the library cannot be found.

Methods return the driver's `PICO_STATUS` as an enum member, followed by any
output parameters. By default, a status other than `PICO_OK` raises a
`StatusException` (see [Status handling](#status-handling)).

```python
from pycosdk import (
    PICO_BANDWIDTH_LIMITER,
    PICO_CHANNEL,
    PICO_CONNECT_PROBE_RANGE,
    PICO_COUPLING,
    PICO_DEVICE_RESOLUTION,
    PicoScope6000aWrapper,
)

scope = PicoScope6000aWrapper()

status, handle = scope.ps6000aOpenUnit(None, PICO_DEVICE_RESOLUTION.PICO_DR_8BIT)

scope.ps6000aSetChannelOn(
    handle,
    PICO_CHANNEL.PICO_CHANNEL_A,
    PICO_COUPLING.PICO_DC_50OHM,
    PICO_CONNECT_PROBE_RANGE.PICO_X1_PROBE_1V,
    0.0,
    PICO_BANDWIDTH_LIMITER.PICO_BW_FULL,
)

scope.ps6000aCloseUnit(handle)
```

## Status handling

Non-OK statuses fall into three categories, each handled by one of the actions
`"raise"` (raise `StatusException`), `"warn"` (emit a `StatusWarning`) or
`"ignore"`. Unless a method raises, it still returns the status.

| Category  | Statuses                                                        | Default    |
| --------- | --------------------------------------------------------------- | ---------- |
| `error`   | everything not covered below                                    | `"raise"`  |
| `warning` | `PICO_WARNING_*` and `PICO_SHOTS_SWEEPS_WARNING`                 | `"warn"`   |
| `info`    | statuses a specific function uses to report a non-error condition | `"ignore"` |

Examples for `info` statuses are the power-source statuses returned by
`ps3000aOpenUnit` or `ps5000aCurrentPowerSource` (e.g.
`PICO_POWER_SUPPLY_NOT_CONNECTED`) and `PICO_WAITING_FOR_DATA_BUFFERS` from
`ps6000aGetStreamingLatestValues`.

Like NumPy's `seterr`/`errstate`, the configuration is global rather than per
wrapper instance:

```python
import pycosdk

# Process-wide; returns the previous settings.
old = pycosdk.seterr(error="warn", info="warn")
pycosdk.seterr(**old)

# Temporarily, as context manager or decorator. Overrides are local to the
# current thread / asyncio task.
with pycosdk.errstate(error="ignore"):
    status = scope.ps6000aStop(handle)

try:
    scope.ps6000aSetChannelOn(handle, ...)
except pycosdk.StatusException as e:
    print(e.function, e.status)
```

Callbacks registered with the driver (e.g. via `RunBlock` or the
`Set*InteractionCallback` functions) receive the status as a parameter and are
not subject to this configuration. The wrappers keep references to the
callback objects handed to the driver, so passing a lambda is safe.

## Type checking

The package ships a `py.typed` marker, so annotations are visible to `mypy`,
`pyright`, and friends.

## License

MIT License — see [LICENSE](LICENSE).
