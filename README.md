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

| Driver    | Wrapper class           | Device class           |
| --------- | ----------------------- | ---------------------- |
| `ps2000`  | `PicoScope2000Wrapper`  | `PicoScope2000Device`  |
| `ps2000a` | `PicoScope2000aWrapper` | `PicoScope2000aDevice` |
| `ps3000`  | `PicoScope3000Wrapper`  | `PicoScope3000Device`  |
| `ps3000a` | `PicoScope3000aWrapper` | `PicoScope3000aDevice` |
| `ps5000`  | `PicoScope5000Wrapper`  | `PicoScope5000Device`  |
| `ps5000a` | `PicoScope5000aWrapper` | `PicoScope5000aDevice` |
| `ps6000`  | `PicoScope6000Wrapper`  | `PicoScope6000Device`  |
| `ps6000a` | `PicoScope6000aWrapper` | `PicoScope6000aDevice` |
| `psospa`  | `PicoScope3000eWrapper` | `PicoScope3000eDevice` |

Each wrapper binds every function declared in the corresponding SDK header
(for `ps6000a` including `ps6000aApiExperimental.h`). Functions that the
installed driver does not export raise `MissingFunctionException` when called,
so an older driver version does not prevent the wrapper from loading.

## Usage

Importing `pycosdk` does not load any driver library. Get a wrapper with
`instance()`: the first call loads the corresponding shared library, later calls
return the same wrapper. Pass an explicit `library_path` to the first call if
the library is not on the default search path; otherwise a
`MissingLibraryException` is raised when the library cannot be found. Once
loaded, asking for a different `library_path` raises a `RuntimeError`.

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

scope = PicoScope6000aWrapper.instance()

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

## Device wrappers

A device class bundles an opened unit with the driver's shared wrapper. It
offers every function of the wrapper that takes a handle as a method with the
handle filled in, and the functions without one (opening and enumerating units)
as classmethods. The open functions return a device instead of a handle;
everything else keeps the wrapper's arguments and return values. A device is a
context manager that closes the unit on exit, and `close()` may be called more
than once. Once closed, calling a method that needs the handle raises a
`ValueError`.

```python
from pycosdk import (
    PICO_BANDWIDTH_LIMITER,
    PICO_CHANNEL,
    PICO_CONNECT_PROBE_RANGE,
    PICO_COUPLING,
    PICO_DEVICE_RESOLUTION,
    PicoScope6000aDevice,
)

status, scope = PicoScope6000aDevice.ps6000aOpenUnit(
    None, PICO_DEVICE_RESOLUTION.PICO_DR_8BIT
)
with scope:
    scope.ps6000aSetChannelOn(
        PICO_CHANNEL.PICO_CHANNEL_A,
        PICO_COUPLING.PICO_DC_50OHM,
        PICO_CONNECT_PROBE_RANGE.PICO_X1_PROBE_1V,
        0.0,
        PICO_BANDWIDTH_LIMITER.PICO_BW_FULL,
    )
```

To use a custom library path, call the wrapper's `instance(library_path)`
before using the device class. A unit opened through the wrapper can be wrapped
as a device with `PicoScope6000aDevice(handle)`.

### Why device methods keep the driver prefix

The device methods are named `scope.ps6000aSetChannelOn(...)` rather than
`scope.SetChannelOn(...)` on purpose. The drivers share many function names, but
often not their arguments, argument types or semantics. For example,
`SetChannel` takes a `dc` flag for the ps2000, ps3000 and ps5000, a coupling and
an analogue offset for the ps2000a, ps3000a and ps5000a, an additional
bandwidth limit for the ps6000, and the ps6000a and psospa split it into
`SetChannelOn`/`SetChannelOff`. Even where the arguments match, enum values may
differ (e.g. the ratio modes of the ps5000 and ps6000).

Without the prefix, code written for one device would seem to work with another
after only changing the device class, and fail (or silently misbehave) in many
places at runtime. A type checker catches some, but not all, of these mistakes,
and not everyone uses one. With the prefix, switching devices means touching
every call, which forces the user (or their coding assistant) to look at what
needs to change for the new device.

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
