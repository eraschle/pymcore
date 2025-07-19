"""
Type definitions for PyM Core.

Defines value types and units used in railway infrastructure modeling.
"""

from collections.abc import Callable
from enum import Enum
from typing import Any


class ValueType(Enum):
    """Value types for railway infrastructure parameters."""

    FLOAT = "float"
    INTEGER = "integer"
    STRING = "string"
    BOOLEAN = "boolean"

    def get_convert_function(self) -> tuple[Callable[[Any], bool], Callable[[Any], Any]]:
        """
        Check if this value type is compatible with given unit type.

        Parameters
        ----------
        unit_type : UnitType
            The unit type to check compatibility with

        Returns
        -------
        bool
            True if compatible, False otherwise
        """

        from pymcore import as_bool, as_float, as_int, as_str, is_bool, is_float, is_int, is_str

        if self == ValueType.STRING:
            return (is_str, as_str)
        if self == ValueType.INTEGER:
            return (is_int, as_int)
        if self == ValueType.FLOAT:
            return (is_float, as_float)
        if self == ValueType.BOOLEAN:
            return (is_bool, as_bool)
        raise ValueError(f"Unsupported value type: {self.value}")

    def is_compatible_with_unit(self, unit_type: "Unit") -> bool:
        """
        Check if this value type is compatible with given unit type.

        Parameters
        ----------
        unit_type : UnitType
            The unit type to check compatibility with

        Returns
        -------
        bool
            True if compatible, False otherwise
        """
        if unit_type == Unit.NONE:
            return True

        numeric_units = {
            Unit.MILLIMETER,
            Unit.METER,
            Unit.KILOMETER,
            Unit.KILOGRAM,
            Unit.TON,
            Unit.PERCENTAGE,
            Unit.DEGREES,
        }

        if self in (ValueType.FLOAT, ValueType.INTEGER):
            return unit_type in numeric_units

        return False


class UnitType(Enum):
    UNKNOWN = "unknown"
    NONE = "none"
    LENGTH = "length"
    MASS = "mass"
    ANGULAR = "angular"


class Unit(Enum):
    """Units used in railway infrastructure."""

    # Length units
    MILLIMETER = "mm"
    METER = "m"
    KILOMETER = "km"

    # Mass units
    KILOGRAM = "kg"
    TON = "t"

    # Angular units
    DEGREES = "deg"

    # Dimensionless
    PERCENTAGE = "%"
    NONE = ""

    def get_unit_category(self) -> UnitType:
        """
        Get the category of this unit for conversion compatibility.

        Returns
        -------
        str
            Unit category name
        """
        length_units = {Unit.MILLIMETER, Unit.METER, Unit.KILOMETER}
        mass_units = {Unit.KILOGRAM, Unit.TON}
        angular_units = {Unit.DEGREES}
        dimensionless_units = {Unit.PERCENTAGE, Unit.NONE}

        if self in length_units:
            return UnitType.LENGTH
        elif self in mass_units:
            return UnitType.MASS
        elif self in angular_units:
            return UnitType.ANGULAR
        elif self in dimensionless_units:
            return UnitType.NONE
        else:
            return UnitType.UNKNOWN

    def is_compatible_with(self, other: "Unit") -> bool:
        """
        Check if this unit can be converted to another unit.

        Parameters
        ----------
        other : UnitType
            Target unit type

        Returns
        -------
        bool
            True if conversion is possible
        """
        return self.get_unit_category() == other.get_unit_category()
