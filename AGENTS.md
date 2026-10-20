# AGENTS.md

## General Rule

- Don't write any tests unless explicitly asked to do.
- Do not run any tests unless explicitly asked to do.

## Python Coding rules

- Use modern type hints wherever possible, e.g., avoid `List[type]` and use `list[type]`, avoid `Optional[type]` and use `type | None`.
- Try to keep the Python compatabilty at a 3.11 floor, if not possible, explain why and ask if the floor should be raised.
- Use the `uv` package manager for everything and run things through `uv`.
- Lint/type-check with `uv run ruff format src/`, `uv run ruff check src/` and `uv run mypy src/`.

## Project Structure

All code lives in `src/pycosdk/`:

- `_base.py`: `PicoScopeWrapperBase` (library loading, shared instance via `instance()`, `_bind`, callback keep-alive), `CALLBACK_FUNCTYPE`, `POWER_SOURCE_STATUSES`.
- `_struct.py`: `CStruct` (typed dataclass mirroring a C struct, with its `ctypes.Structure` as `c_type`) and `c_array` (input arrays, NULL when empty).
- `_device.py`: `PicoScopeDeviceBase` (an opened unit: handle, close, context manager) and the descriptors `handle_method`/`wrapper_function` exposing wrapper methods on device classes.
- `statusconfig.py`: `seterr`/`geterr`/`errstate` (warning/info handling; errors always raise), `check_status` (status → exception/warning) and `check_result` (legacy return values → `ResultException`).
- `exceptions.py`: `StatusException`/`StatusWarning` (`PICO_STATUS` drivers) and `ResultException` (legacy drivers), with the common bases `DriverException`/`DriverWarning`; `MissingLibraryException`, `MissingFunctionException`.
- `status.py` (`PicoStatus.h`), `deviceenums.py` (`PicoDeviceEnums.h`), `devicestructs.py` (`PicoDeviceStructs.h`), `connectprobe.py` (`PicoConnectProbes.h`), `callback.py` (`PicoCallback.h`), `version.py` (`PicoVersion.h`): types shared by the newer drivers.
- One module per driver, each with its driver-specific enums/structs/constants, callback types, the wrapper class and the device class:
  - `ps2000.py`, `ps3000.py`: pre-`PICO_STATUS` drivers, see `_bind_legacy` below; `ps3000.py` reuses private helpers from `ps2000.py`.
  - `ps2000a.py`, `ps3000a.py`, `ps5000.py`, `ps5000a.py`, `ps6000.py`: legacy drivers, mostly own `PS<model>_*` types.
  - `ps6000a.py`: also covers `ps6000aApiExperimental.h` / `PicoDeviceDefinitionsExperimental.h`.
  - `psosca.py`: driver `psospa`, class `PicoScope3000eWrapper` (file name differs from the driver name).
- `__init__.py`: re-exports wrappers, shared types and the `PS3000A_*` names; other driver-specific names are imported from their module.

## SDK Reference

The installed SDK (C headers and driver libraries) is the reference for the wrappers. Its location depends on the OS:

- Linux: usually under `/opt/picoscope`.
  - Headers: `include/lib<driver>/`, including a copy of the shared `Pico*.h` headers per driver (they differ slightly; the `libps6000a` copies are the most complete).
  - Libraries: `lib/lib<driver>.so`. The installer registers `/opt/picoscope/lib` with `ld.so.conf`, so `find_library` works.
- macOS: the installer places a framework at `/Library/Frameworks/PicoSDK.framework`.
  - Headers: `Headers/lib<driver>/`, with the shared `Pico*.h` headers in `Headers/shared/`.
  - Libraries: `Libraries/lib<driver>/lib<driver>.2.dylib`, one folder per driver. These folders are not on the dyld search path, so `find_driver_library` in `_base.py` falls back to them.
  - `ps6000` (legacy) is not part of the macOS SDK.
- Windows: location unknown/undocumented here; libraries are found via `find_library` (i.e. `PATH`).
- Check exported symbols with `nm -D --defined-only` (Linux) or `nm -gU` (macOS).
- Only wrap functions declared in the headers; the libraries export some undocumented extras. The SDK also contains drivers not (yet) wrapped here (e.g. `ps2000`, `ps2000a`, `ps4000a`, data loggers); ignore them unless asked.

## Wrapper Conventions

- Enums are `IntEnum`/`IntFlag` plus a `<NAME>_T` ctypes alias (`c_int32`, or `c_uint32` where the C type is unsigned).
- Structs are `CStruct` subclasses (`class X(CStruct):`, packed to 1 byte like the headers' `#pragma pack(1)`; `pack=None` where a header doesn't pack). Annotate each field as `Annotated[<python type>, <ctypes type>]` in C order with the C name: enum fields with their enum, 0/1 flags as `bool`, status fields as `PICO_STATUS`, char arrays as `str`, nested structs with their `CStruct` class. Output-only fields of structs that are also passed in get defaults.
- Struct arguments: argtypes `POINTER(X.c_type)`; input sequences via `c_array(X, items)`; outputs via `X.from_c(raw)` / `X.from_c_array(arr)`.
- Driver-specific names that the header leaves unprefixed (or misspells) get the driver prefix: `PS5000_` for types, constants and enum members, `ps2000` for callback types. Note the C name in a `# C: <name>` comment. Names from the shared `Pico*.h` headers keep their C names.
- Bind every driver function in `__init__` via `self._<Fn> = self._bind("<Fn>", [argtypes], info=...)`. `_bind` sets `restype`, `argtypes` and an `errcheck`, so the bound callable returns an already checked `PICO_STATUS`. Never set `restype`/`argtypes` by hand (note the lowercase spelling).
- `argtypes` must match the C prototype exactly. Sample/AWG data buffers use `c_void_p` so ctypes arrays, numpy `.ctypes.data` and ints work.
- `info=` lists statuses that are not errors *for that function* (e.g. power-source statuses from `OpenUnit`), as documented in the programmer's guide. Add a short comment explaining why. `PICO_WARNING_*` is handled globally, don't list it. Every other non-OK status raises `StatusException`.
- Public method names and parameter names mirror the C API. Methods don't return the status: they return `None`, their single output, or a tuple of the outputs in C parameter order, converted to Python values. A function with `info=` statuses returns its status as the last output (alone if it has no other outputs), because it carries information; exception: `EnumerateUnits` (`PICO_NOT_FOUND` just means a count of 0).
- Legacy drivers (`ps2000`, `ps3000`) predate `PICO_STATUS`: their snake_case functions return plain integers whose meaning differs per function. Bind them via `self._bind_legacy("<fn>", [argtypes], restype, failed=..., error_code=...)`, where `failed` is a predicate on the raw return value (`None` if the function cannot fail) and `error_code` looks up the driver error code (`get_unit_info(..., *_ERROR_CODE)`). Failures raise `ResultException`. Methods return the C return value (as a fitting Python type, e.g. `bool`, an enum, or the `c_int16` handle) followed by outputs, but only where it means more than success; a value that only signals success is not returned.
- Outputs the driver writes *after* the call returns (`GetValuesOverlapped*`) are returned as ctypes objects and kept alive via `_with_callback`.

## Device Classes

- Each driver module ends with a `PicoScope<model>Device(PicoScopeDeviceBase[<Wrapper>])` class that lists *every* public wrapper method, keeping the driver prefix in the name (a deliberate design decision, see the README). When adding a wrapper method, add it to the device class too:
  - Methods whose first parameter is `handle`: `<fn> = handle_method(<Wrapper>.<fn>)`; the close function gets `closes=True`.
  - Methods without a handle: `<fn> = wrapper_function(<Wrapper>.<fn>)`.
  - Open functions (`OpenUnit`, `OpenUnitProgress`, `open_unit`, ...) are classmethods returning `cls(handle)` in place of the handle (`None` while an async open is incomplete), keeping the other outputs and the status (if returned).
- Wrapper methods take the handle as `handle: c_int16`, otherwise `handle_method` does not type-check.

## Callbacks

- Define callback types with `CALLBACK_FUNCTYPE` (`__stdcall` on Windows), not `CFUNCTYPE`.
- The driver calls callbacks later from its own threads, so the ctypes callback object must stay referenced: register it through `self._with_callback(self._callback_key("<Fn>", handle), cfunc, lambda: self._<Fn>(...))`. Never store it in a local only.
- ctypes rejects `None` for a callback-typed argument; pass a NULL instance (e.g. `ps6000aBlockReady()`) instead.
- Wrap user callables to convert raw ints to `PICO_STATUS`/enums. Copy struct arrays passed into a callback, since they are only valid during the call. `pParameter` is not exposed; pass `None`.
