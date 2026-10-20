# pycosdk

Yet another wrapper for the [PicoSDK](https://www.picotech.com/downloads).

`pycosdk` is a thin, fully type-annotated `ctypes` binding to Pico Technology's
PicoScope driver libraries. It stays deliberately close to the C API: method
names mirror the driver functions, and the enums and structs are transcribed
from the SDK headers as `IntEnum`/`IntFlag` types and typed dataclasses (see
[Structs](#structs)).

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

Methods return the function's output parameters: nothing, a single value, or a
tuple in the order of the C parameters. A failed call raises a
`StatusException` instead of returning its `PICO_STATUS`. Only the few
functions whose status carries information (e.g. the power source reported when
opening a unit) return it, as their last output; see
[Status handling](#status-handling).

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

handle, status = scope.ps6000aOpenUnit(None, PICO_DEVICE_RESOLUTION.PICO_DR_8BIT)

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

scope, status = PicoScope6000aDevice.ps6000aOpenUnit(
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

Every status other than `PICO_OK` falls into one of three categories:

| Category  | Statuses                                                          | Handling                                              |
| --------- | ----------------------------------------------------------------- | ----------------------------------------------------- |
| `error`   | everything not covered below                                      | always raises `StatusException`                       |
| `warning` | `PICO_WARNING_*` and `PICO_SHOTS_SWEEPS_WARNING`                   | configurable, default `"warn"` (emit a `StatusWarning`) |
| `info`    | statuses a specific function uses to report a non-error condition | configurable, default `"ignore"`                      |

The `info` statuses are documented in the programmer's guides as not being
failures, and the functions reporting them return the status as their last
output:

| Functions                                                                           | Statuses                                                                                          |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `OpenUnit`, `OpenUnitAsync`, `OpenUnitProgress` of ps3000a and ps5000a                | power source (`PICO_POWER_SUPPLY_NOT_CONNECTED`, `PICO_USB3_0_DEVICE_NON_USB3_0_PORT`, ...)        |
| `ChangePowerSource`, `CurrentPowerSource`, `PingUnit` of ps3000a and ps5000a; `ps5000aSetDeviceResolution`; `ps6000PingUnit` | power source                                                   |
| `OpenUnit`, `OpenUnitAsync`, `OpenUnitProgress` of ps6000a; `psospaOpenUnit`        | `PICO_USB3_0_DEVICE_NON_USB3_0_PORT`, `PICO_FIRMWARE_UPDATE_REQUIRED_TO_USE_DEVICE_WITH_THIS_DRIVER` |
| `GetStreamingLatestValues` of ps2000a, ps3000a, ps5000, ps5000a and ps6000          | `PICO_BUSY` (no new data yet, poll again)                                                         |
| `GetStreamingLatestValues` of ps6000a and psospa                                    | `PICO_WAITING_FOR_DATA_BUFFERS` (set new buffers; the returned data is valid)                     |

`EnumerateUnits` treats `PICO_NOT_FOUND` as a valid result (no units, count 0)
without returning it.

If the power supply of a ps3000a or ps5000a is connected or disconnected while
it is running, the next call raises a `StatusException` with the new power
status; catch it and call `ChangePowerSource` to continue.

Like NumPy's `seterr`/`errstate`, the configuration of the `warning` and `info`
categories is global rather than per wrapper instance:

```python
import pycosdk

# Process-wide; returns the previous settings.
old = pycosdk.seterr(warning="raise", info="warn")
pycosdk.seterr(**old)

# Temporarily, as context manager or decorator. Overrides are local to the
# current thread / asyncio task.
with pycosdk.errstate(warning="ignore"):
    scope.ps6000aSetAuxIoMode(handle, ...)

try:
    scope.ps6000aSetChannelOn(handle, ...)
except pycosdk.StatusException as e:
    print(e.function, e.status)
```

The legacy drivers `ps2000` and `ps3000` predate `PICO_STATUS`: a failed call
raises a `ResultException`, and a return value is only returned where it means
more than success (e.g. a handle or a number of values).

Callbacks registered with the driver (e.g. via `RunBlock` or the
`Set*InteractionCallback` functions) receive the status as a parameter and are
not subject to this configuration. The wrappers keep references to the
callback objects handed to the driver, so passing a lambda is safe.

## Structs

The C structs are typed dataclasses (subclasses of `CStruct`) with the C field
names. Fields are converted to fitting Python types: enum fields to their enum,
flags to `bool`, char arrays to `str`, nested structs to their dataclass. Methods
take and return these dataclasses (lists of them for C arrays) and convert to and
from the C struct, which is available as `c_type`, themselves:

```python
from pycosdk import PICO_CHANNEL, PICO_CONDITION, PICO_TRIGGER_STATE

conditions = [
    PICO_CONDITION(
        source=PICO_CHANNEL.PICO_CHANNEL_A,
        condition=PICO_TRIGGER_STATE.PICO_CONDITION_TRUE,
    )
]
```

A misspelled or missing field is a `TypeError` (and caught by type checkers),
unlike with a plain `ctypes.Structure`. Values returned by the driver are
copies: in/out arrays, e.g. the `streamingDataInfo` of
`ps6000aGetStreamingLatestValues`, come back as new lists.

## Buffers

Sample buffers and arbitrary waveforms take any object supporting Python's
buffer protocol, such as a numpy array, `array.array` or a ctypes array, so
`pycosdk` works with numpy without depending on it. Buffers are passed to the
driver without copying and checked first: they must be C-contiguous, hold
elements of the type the driver expects (e.g. `int16` samples), hold at least
as many elements as passed to the driver, and be writable if the driver writes
to them. Waveforms may also be plain sequences of ints.

```python
import numpy as np

samples = np.empty((nSegments, nSamples), dtype=np.int16)
for segment in range(nSegments):
    scope.ps6000aSetDataBuffer(
        PICO_CHANNEL.PICO_CHANNEL_A,
        samples[segment],  # each row is one segment's buffer
        nSamples,
        PICO_DATA_TYPE.PICO_INT16_T,
        segment,
        PICO_RATIO_MODE.PICO_RATIO_MODE_RAW,
        PICO_ACTION.PICO_ADD,
    )
```

The driver writes to such buffers after the call that set them, so the wrapper
keeps them alive (and numpy from resizing them) until they are replaced, set to
`None`, cleared with `PICO_CLEAR_ALL`, or the unit is closed. A raw address (an
`int` or `c_void_p`) is passed on unchecked and must be kept valid by the
caller.

## Type checking

The package ships a `py.typed` marker, so annotations are visible to `mypy`,
`pyright`, and friends.

## License

MIT License — see [LICENSE](LICENSE).
