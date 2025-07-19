"""
Type definitions for PyM Core.

Defines value types and units used in railway infrastructure modeling.
"""
from enum import Enum


class ValueType(Enum):
    """Value types for railway infrastructure parameters."""
    
    FLOAT = "float"
    INTEGER = "integer"
    STRING = "string"
    BOOLEAN = "boolean"
    
    def is_compatible_with_unit(self, unit_type: 'UnitType') -> bool:
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
        if unit_type == UnitType.NONE:
            return True
            
        numeric_units = {
            UnitType.MILLIMETER, UnitType.METER, UnitType.KILOMETER,
            UnitType.KILOGRAM, UnitType.TON,
            UnitType.PERCENTAGE,
            UnitType.DEGREES
        }
        
        if self in (ValueType.FLOAT, ValueType.INTEGER):
            return unit_type in numeric_units
        
        return False


class UnitType(Enum):
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
    
    def get_unit_category(self) -> str:
        """
        Get the category of this unit for conversion compatibility.
        
        Returns
        -------
        str
            Unit category name
        """
        length_units = {UnitType.MILLIMETER, UnitType.METER, UnitType.KILOMETER}
        mass_units = {UnitType.KILOGRAM, UnitType.TON}
        angular_units = {UnitType.DEGREES}
        dimensionless_units = {UnitType.PERCENTAGE, UnitType.NONE}
        
        if self in length_units:
            return "length"
        elif self in mass_units:
            return "mass"
        elif self in angular_units:
            return "angular"
        elif self in dimensionless_units:
            return "dimensionless"
        else:
            return "unknown"
    
    def is_compatible_with(self, other: 'UnitType') -> bool:
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