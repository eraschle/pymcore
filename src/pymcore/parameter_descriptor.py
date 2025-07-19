"""
Parameter descriptor definitions for PyM Core.

Provides structured parameter definitions for the registry system.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Type
from .types import ValueType, Unit


@dataclass(frozen=True)
class ParameterDescriptor:
    """
    Descriptor for parameter definitions in the registry system.

    Defines the semantic meaning, type, and validation rules for parameters.
    """

    semantic_key: str
    """Semantic identifier that matches ENUM values for migration."""

    data_type: Type
    """Python type for this parameter (int, float, str, bool)."""

    unit: Unit = Unit.NONE
    """Unit of measurement for this parameter."""

    required: bool = True
    """Whether this parameter is required for the element type."""

    default_value: object | None = None
    """Default value if parameter is not provided."""

    description: str | None = None
    """Human-readable description of the parameter."""

    def __post_init__(self):
        """Validate the parameter descriptor after creation."""
        # Convert data_type to ValueType for compatibility checking
        if self.data_type is float:
            value_type = ValueType.FLOAT
        elif self.data_type is int:
            value_type = ValueType.INTEGER
        elif self.data_type is str:
            value_type = ValueType.STRING
        elif self.data_type is bool:
            value_type = ValueType.BOOLEAN
        else:
            raise ValueError(f"Unsupported data type: {self.data_type}")

        # Validate unit compatibility
        if not value_type.is_compatible_with_unit(self.unit):
            raise ValueError(f"Data type {self.data_type.__name__} is not compatible with unit {self.unit.name}")
