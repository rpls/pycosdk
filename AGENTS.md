# AGENTS.md

## General Rule

- Do not run any tests unless explicitly asked to do.

## Python Coding rules

- Use modern type hints wherever possible, e.g., avoid `List[type]` and use `list[type]`, avoid `Optional[type]` and use `type | None`.
- Try to keep the Python compatabilty at a 3.11 floor, if not possible, explain why and ask if the floor should be raised.
- Use the `uv` package manager for everything and run things through `uv`.
- Lint/type-check with `uv run ruff format src/`, `uv run ruff check src/` and `uv run mypy src/`.

## Project Structure

All code lives in `src/pycosdk/`:

- `_base.py`: `PicoScopeWrapperBase` (library loading, `_bind`, callback keep-alive), `CALLBACK_FUNCTYPE`, `POWER_SOURCE_STATUSES`.
- `statusconfig.py`: `seterr`/`geterr`/`errstate` and `check_status` (status → error/warning/info handling).
- `exceptions.py`: `StatusException`, `StatusWarning`, `MissingLibraryException`, `MissingFunctionException`.
- `status.py` (`PicoStatus.h`), `deviceenums.py` (`PicoDeviceEnums.h`), `devicestructs.py` (`PicoDeviceStructs.h`), `connectprobe.py` (`PicoConnectProbes.h`), `callback.py` (`PicoCallback.h`), `version.py` (`PicoVersion.h`): types shared by the newer drivers.
- One module per driver, each with its driver-specific enums/structs/constants, callback types and the wrapper class:
  - `ps3000a.py`, `ps5000a.py`, `ps6000.py`: legacy drivers, mostly own `PS<model>_*` types.
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

- Enums are `IntEnum`/`IntFlag` plus a `<NAME>_T` ctypes alias (`c_int32`, or `c_uint32` where the C type is unsigned). Structs are `ctypes.Structure`; keep `_pack_ = 1` where the header uses `#pragma pack(push, 1)`.
- Bind every driver function in `__init__` via `self._<Fn> = self._bind("<Fn>", [argtypes], info=...)`. `_bind` sets `restype`, `argtypes` and an `errcheck`, so the bound callable returns an already checked `PICO_STATUS`. Never set `restype`/`argtypes` by hand (note the lowercase spelling).
- `argtypes` must match the C prototype exactly. Sample/AWG data buffers use `c_void_p` so ctypes arrays, numpy `.ctypes.data` and ints work.
- `info=` lists statuses that are not errors *for that function* (e.g. power-source statuses from `OpenUnit`). Add a short comment explaining why. `PICO_WARNING_*` is handled globally, don't list it.
- Public method names and parameter names mirror the C API. Return the status alone, or `(status, out1, ...)` with outputs converted to Python values. Don't change existing signatures or return shapes.
- Outputs the driver writes *after* the call returns (`GetValuesOverlapped*`) are returned as ctypes objects and kept alive via `_with_callback`.

## Callbacks

- Define callback types with `CALLBACK_FUNCTYPE` (`__stdcall` on Windows), not `CFUNCTYPE`.
- The driver calls callbacks later from its own threads, so the ctypes callback object must stay referenced: register it through `self._with_callback(self._callback_key("<Fn>", handle), cfunc, lambda: self._<Fn>(...))`. Never store it in a local only.
- ctypes rejects `None` for a callback-typed argument; pass a NULL instance (e.g. `ps6000aBlockReady()`) instead.
- Wrap user callables to convert raw ints to `PICO_STATUS`/enums. Copy struct arrays passed into a callback, since they are only valid during the call. `pParameter` is not exposed; pass `None`.
