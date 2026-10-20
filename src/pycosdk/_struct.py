"""Typed dataclasses for C structs, see :class:`CStruct`."""

import dataclasses
from collections.abc import Callable, Iterable, Sequence
from ctypes import Array, Structure, sizeof
from enum import Enum
from typing import (
    Annotated,
    Any,
    ClassVar,
    Self,
    dataclass_transform,
    get_args,
    get_origin,
    get_type_hints,
)

_Converter = Callable[[Any], Any]


def _identity(value: Any) -> Any:
    return value


def _string_converters(ctype: type[Array[Any]]) -> tuple[_Converter, _Converter]:
    """Convert between ``str`` and a fixed-size, NUL padded char array."""
    size = sizeof(ctype)

    def to_c(value: str) -> Array[Any]:
        data = value.encode()
        if len(data) > size:
            raise ValueError(f"{value!r} does not fit into {size} bytes")
        return ctype.from_buffer_copy(data.ljust(size, b"\0"))

    def from_c(raw: Array[Any]) -> str:
        return bytes(raw).split(b"\0", 1)[0].decode(errors="replace")

    return to_c, from_c


def _converters(pytype: Any, ctype: Any) -> tuple[_Converter, _Converter]:
    """Converters of a field's Python value to its C value and back."""
    if isinstance(pytype, type):
        if issubclass(pytype, CStruct):
            return (lambda value: value.to_c()), pytype.from_c
        if issubclass(pytype, Enum):
            return int, pytype
        if pytype is bool:
            return int, bool
        if pytype is str:
            return _string_converters(ctype)
    return _identity, _identity


def _field_types(owner: type, name: str, hint: Any) -> tuple[Any, Any]:
    """Split a field annotation into its Python type and its ctypes type."""
    if get_origin(hint) is Annotated:
        pytype, ctype, *_ = get_args(hint)
        return pytype, ctype
    if isinstance(hint, type) and issubclass(hint, CStruct):
        return hint, hint.c_type
    raise TypeError(
        f"{owner.__name__}.{name}: annotate as Annotated[<python type>, <ctypes type>]"
    )


@dataclass_transform()
class CStruct:
    """Base of typed dataclasses mirroring a C struct.

    Each field is annotated as ``Annotated[<python type>, <ctypes type>]``, e.g.
    ``Annotated[PICO_CHANNEL, PICO_CHANNEL_T]``; a nested struct is annotated with
    its ``CStruct`` class. Subclasses become dataclasses, and :attr:`c_type` is
    the matching :class:`ctypes.Structure`, packed to ``pack`` bytes (``None``
    for the platform default)::

        class PICO_CONDITION(CStruct):
            source: Annotated[PICO_CHANNEL, PICO_CHANNEL_T]
            condition: Annotated[PICO_TRIGGER_STATE, PICO_TRIGGER_STATE_T]

    Converting from C turns enum fields into their enum, ``bool`` fields into
    ``bool``, ``str`` fields (char arrays) into the NUL terminated string, and
    nested structs into their ``CStruct``. All other values are passed as is.
    """

    c_type: ClassVar[type[Structure]]
    _converters: ClassVar[tuple[tuple[str, _Converter, _Converter], ...]]

    @classmethod
    def __init_subclass__(cls, *, pack: int | None = 1, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        dataclasses.dataclass(cls)
        hints = get_type_hints(cls, include_extras=True)
        fields: list[tuple[str, Any]] = []
        converters: list[tuple[str, _Converter, _Converter]] = []
        for field in dataclasses.fields(cls):  # type: ignore[arg-type]
            pytype, ctype = _field_types(cls, field.name, hints[field.name])
            fields.append((field.name, ctype))
            converters.append((field.name, *_converters(pytype, ctype)))
        namespace: dict[str, Any] = {"_fields_": fields, "__module__": cls.__module__}
        if pack is not None:
            namespace["_pack_"] = pack
        cls.c_type = type(cls.__name__, (Structure,), namespace)
        cls._converters = tuple(converters)

    def to_c(self) -> Structure:
        """Return the C struct holding this struct's values."""
        return self.c_type(
            *(to_c(getattr(self, name)) for name, to_c, _ in self._converters)
        )

    @classmethod
    def from_c(cls, raw: Structure) -> Self:
        """Return the values of the C struct ``raw`` (copied, not referencing it)."""
        return cls(
            **{name: from_c(getattr(raw, name)) for name, _, from_c in cls._converters}
        )

    @classmethod
    def to_c_array(cls, items: Sequence[Self]) -> Array[Structure]:
        """Return ``items`` as a C array of :attr:`c_type`."""
        return (cls.c_type * len(items))(*(item.to_c() for item in items))

    @classmethod
    def from_c_array(cls, raw: Iterable[Structure]) -> list[Self]:
        """Return the values of the C structs in ``raw``."""
        return [cls.from_c(item) for item in raw]


def c_array(ctype: Any, items: Sequence[Any]) -> Any:
    """Return ``items`` as ctypes array, or None (NULL) if there are none.

    ``ctype`` is a ctypes type, or a :class:`CStruct` for an array of its C struct.
    The drivers document NULL (with a count of 0) as the way to pass no
    conditions, directions, properties, etc.
    """
    if len(items) == 0:
        return None
    if isinstance(ctype, type) and issubclass(ctype, CStruct):
        return ctype.to_c_array(items)
    return (ctype * len(items))(*items)


__all__ = ("CStruct", "c_array")
