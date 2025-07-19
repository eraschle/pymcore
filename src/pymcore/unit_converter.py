"""
Unit conversion system for PyM Core.

Provides safe unit conversions with error handling for incompatible types.
"""
from typing import Dict
from .types import UnitType


class UnitConversionError(Exception):
    """Raised when unit conversion is not possible."""
    pass


class UnitConverter:
    """
    Handles unit conversions for railway infrastructure parameters.
    
    Supports conversions within compatible unit categories and raises
    exceptions for incompatible conversions.
    """
    
    def __init__(self):
        """Initialize the unit converter with conversion factors."""
        # Conversion factors to base units (meter for length, kg for mass)
        self._to_base_factors: Dict[UnitType, float] = {
            # Length units (base: meter)
            UnitType.MILLIMETER: 0.001,
            UnitType.METER: 1.0,
            UnitType.KILOMETER: 1000.0,
            
            # Mass units (base: kilogram)
            UnitType.KILOGRAM: 1.0,
            UnitType.TON: 1000.0,
            
            # Angular units (base: degrees)
            UnitType.DEGREES: 1.0,
            
            # Dimensionless (no conversion needed)
            UnitType.PERCENTAGE: 1.0,
            UnitType.NONE: 1.0
        }
    
    def convert(self, value: float, from_unit: UnitType, to_unit: UnitType) -> float:
        """
        Convert a value from one unit to another.
        
        Parameters
        ----------
        value : float
            The value to convert
        from_unit : UnitType
            Source unit
        to_unit : UnitType
            Target unit
            
        Returns
        -------
        float
            Converted value
            
        Raises
        ------
        UnitConversionError
            If units are not compatible for conversion
        """
        # Same unit - no conversion needed
        if from_unit == to_unit:
            return value
            
        # Check compatibility
        if not from_unit.is_compatible_with(to_unit):
            raise UnitConversionError(
                f"Cannot convert from {from_unit.name} to {to_unit.name}: "
                f"incompatible unit categories ({from_unit.get_unit_category()} vs {to_unit.get_unit_category()})"
            )
        
        # Get conversion factors
        from_factor = self._to_base_factors.get(from_unit)
        to_factor = self._to_base_factors.get(to_unit)
        
        if from_factor is None or to_factor is None:
            raise UnitConversionError(
                f"No conversion factor available for {from_unit.name} or {to_unit.name}"
            )
        
        # Convert: value -> base unit -> target unit
        base_value = value * from_factor
        result = base_value / to_factor
        
        return result
    
    def get_supported_conversions(self, unit: UnitType) -> list[UnitType]:
        """
        Get all units that the given unit can be converted to.
        
        Parameters
        ----------
        unit : UnitType
            Source unit
            
        Returns
        -------
        list[UnitType]
            List of compatible target units
        """
        category = unit.get_unit_category()
        compatible_units = []
        
        for other_unit in UnitType:
            if other_unit.get_unit_category() == category:
                compatible_units.append(other_unit)
                
        return compatible_units