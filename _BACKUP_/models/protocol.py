from enum import StrEnum
from typing import Any, Protocol


class ValueType(StrEnum):
    """Enumeration for value types of parameters."""

    UNKNOWN = "unknown"
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"


class IPymParameter(Protocol):
    @property
    def name(self) -> str:
        """Return the name of the parameter."""
        ...

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the parameter."""
        ...

    @property
    def value_type(self) -> type[Any]:
        """Return the type of the parameter value."""
        ...

    @value_type.setter
    def value_type(self, value: type[Any]) -> None:
        """Set the type of the parameter value."""
        ...


class IPymModel(Protocol):
    def parameters(self) -> dict[str, str]:
        """Return the parameters of the model."""
        ...
