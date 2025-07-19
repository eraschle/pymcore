"""
Integration tests for Unit Conversion System.

Tests focus on realistic railway infrastructure scenarios
and error handling for incompatible conversions.
"""

import pytest
from pymcore.types import ValueType, Unit
from pymcore.unit_converter import UnitConverter, UnitConversionError


class TestUnitConversionIntegration:
    """Integration tests for unit conversion in railway context."""

    def test_length_conversions_railway_scale(self):
        """Test length conversions typical for railway infrastructure."""
        converter = UnitConverter()

        # Pole height: 12m -> mm
        result = converter.convert(12.0, Unit.METER, Unit.MILLIMETER)
        assert result == 12000.0

        # Track gauge: 1435mm -> m
        result = converter.convert(1435.0, Unit.MILLIMETER, Unit.METER)
        assert result == 1.435

        # Foundation depth: 2500mm -> m
        result = converter.convert(2500.0, Unit.MILLIMETER, Unit.METER)
        assert result == 2.5

    def test_incompatible_unit_conversion_raises_exception(self):
        """Test that incompatible conversions raise proper exceptions."""
        converter = UnitConverter()

        # Cannot convert length to mass
        with pytest.raises(UnitConversionError) as exc_info:
            converter.convert(100.0, Unit.MILLIMETER, Unit.KILOGRAM)

        assert "Cannot convert from MILLIMETER to KILOGRAM" in str(exc_info.value)

        # Cannot convert mass to percentage
        with pytest.raises(UnitConversionError) as exc_info:
            converter.convert(50.0, Unit.KILOGRAM, Unit.PERCENTAGE)

    def test_same_unit_conversion_returns_original_value(self):
        """Test that converting to same unit returns original value."""
        converter = UnitConverter()

        original_value = 1435.0
        result = converter.convert(original_value, Unit.MILLIMETER, Unit.MILLIMETER)
        assert result == original_value

    def test_value_type_compatibility_with_units(self):
        """Test that ValueTypes work correctly with unit conversions."""
        # This will test the integration between ValueType and Unit
        assert ValueType.FLOAT.is_compatible_with_unit(Unit.MILLIMETER)
        assert ValueType.INTEGER.is_compatible_with_unit(Unit.MILLIMETER)
        assert not ValueType.STRING.is_compatible_with_unit(Unit.MILLIMETER)
        assert ValueType.STRING.is_compatible_with_unit(Unit.NONE)

    def test_railway_specific_unit_combinations(self):
        """Test unit combinations specific to railway infrastructure."""
        converter = UnitConverter()

        # Load capacity: tons to kg
        result = converter.convert(5.0, Unit.TON, Unit.KILOGRAM)
        assert result == 5000.0

        # Gradient: percentage stays percentage
        result = converter.convert(2.5, Unit.PERCENTAGE, Unit.PERCENTAGE)
        assert result == 2.5
