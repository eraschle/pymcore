"""
Integration tests for Unit Conversion System.

Tests focus on realistic railway infrastructure scenarios
and error handling for incompatible conversions.
"""
import pytest
from src.pymcore.types import ValueType, UnitType
from src.pymcore.unit_converter import UnitConverter, UnitConversionError


class TestUnitConversionIntegration:
    """Integration tests for unit conversion in railway context."""

    def test_length_conversions_railway_scale(self):
        """Test length conversions typical for railway infrastructure."""
        converter = UnitConverter()
        
        # Pole height: 12m -> mm
        result = converter.convert(12.0, UnitType.METER, UnitType.MILLIMETER)
        assert result == 12000.0
        
        # Track gauge: 1435mm -> m
        result = converter.convert(1435.0, UnitType.MILLIMETER, UnitType.METER)
        assert result == 1.435
        
        # Foundation depth: 2500mm -> m
        result = converter.convert(2500.0, UnitType.MILLIMETER, UnitType.METER)
        assert result == 2.5

    def test_incompatible_unit_conversion_raises_exception(self):
        """Test that incompatible conversions raise proper exceptions."""
        converter = UnitConverter()
        
        # Cannot convert length to mass
        with pytest.raises(UnitConversionError) as exc_info:
            converter.convert(100.0, UnitType.MILLIMETER, UnitType.KILOGRAM)
        
        assert "Cannot convert from MILLIMETER to KILOGRAM" in str(exc_info.value)
        
        # Cannot convert mass to percentage
        with pytest.raises(UnitConversionError) as exc_info:
            converter.convert(50.0, UnitType.KILOGRAM, UnitType.PERCENTAGE)

    def test_same_unit_conversion_returns_original_value(self):
        """Test that converting to same unit returns original value."""
        converter = UnitConverter()
        
        original_value = 1435.0
        result = converter.convert(original_value, UnitType.MILLIMETER, UnitType.MILLIMETER)
        assert result == original_value

    def test_value_type_compatibility_with_units(self):
        """Test that ValueTypes work correctly with unit conversions."""
        # This will test the integration between ValueType and UnitType
        assert ValueType.FLOAT.is_compatible_with_unit(UnitType.MILLIMETER)
        assert ValueType.INTEGER.is_compatible_with_unit(UnitType.MILLIMETER)
        assert not ValueType.STRING.is_compatible_with_unit(UnitType.MILLIMETER)
        assert ValueType.STRING.is_compatible_with_unit(UnitType.NONE)

    def test_railway_specific_unit_combinations(self):
        """Test unit combinations specific to railway infrastructure."""
        converter = UnitConverter()
        
        # Load capacity: tons to kg
        result = converter.convert(5.0, UnitType.TON, UnitType.KILOGRAM)
        assert result == 5000.0
        
        # Gradient: percentage stays percentage
        result = converter.convert(2.5, UnitType.PERCENTAGE, UnitType.PERCENTAGE)
        assert result == 2.5