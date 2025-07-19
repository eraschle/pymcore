"""
Integration tests for GenericElement with Parameter and Geometry synchronization.

Tests focus on ensuring that geometry properties automatically sync with
underlying parameters without requiring explicit synchronization.
"""

import pytest
from pymcore.generic_element import GenericElement
from pymcore.types import UnitType, ValueType
from pymcore.unit_converter import UnitConversionError


class TestGenericElementIntegration:
    """Integration tests for GenericElement parameter management."""

    def test_parameter_operations_with_unit_conversion(self):
        """Test basic parameter operations with automatic unit conversion."""
        element = GenericElement("pole_001", "pole")

        # Set parameter with unit conversion (12m -> mm)
        element.set_parameter("height", 12.0, UnitType.METER, target_unit=UnitType.MILLIMETER)

        # Retrieve in original unit
        height_mm = element.get_parameter("height")
        assert height_mm == 12000.0

        # Retrieve with unit conversion (mm -> m)
        height_m = element.get_parameter("height", return_unit=UnitType.METER)
        assert height_m == 12.0

    def test_parameter_sync_with_geometry_descriptor(self):
        """Test that geometry descriptors automatically sync with parameters."""
        element = GenericElement("pole_001", "pole")

        # Set height parameter directly
        element.set_parameter("height", 15000.0, UnitType.MILLIMETER)

        # Access through geometry property should return same value
        geometry = element.get_geometry()
        assert geometry.height == 15000.0

        # Change through geometry should update parameter
        geometry.height = 18000.0
        assert element.get_parameter("height") == 18000.0

    def test_invalid_unit_conversion_raises_exception(self):
        """Test that invalid unit conversions raise proper exceptions."""
        element = GenericElement("pole_001", "pole")

        # Try to set length parameter with mass unit
        with pytest.raises(UnitConversionError):
            element.set_parameter(
                "height", 100.0, UnitType.KILOGRAM, target_unit=UnitType.MILLIMETER
            )

    def test_parameter_metadata_storage(self):
        """Test that parameter metadata (units, types) is properly stored."""
        element = GenericElement("pole_001", "pole")

        # Set parameter with metadata
        element.set_parameter("height", 12000.0, UnitType.MILLIMETER, value_type=ValueType.FLOAT)

        # Retrieve metadata
        metadata = element.get_parameter_metadata("height")
        assert metadata["unit"] == UnitType.MILLIMETER
        assert metadata["value_type"] == ValueType.FLOAT
        assert metadata["value"] == 12000.0

    def test_element_serialization_roundtrip(self):
        """Test that elements can be serialized and deserialized correctly."""
        original = GenericElement("pole_001", "pole")
        original.set_parameter("height", 12000.0, UnitType.MILLIMETER)
        original.set_parameter("diameter", 300.0, UnitType.MILLIMETER)
        original.set_parameter("material", "steel", UnitType.NONE, value_type=ValueType.STRING)

        # Serialize to dict
        data = original.to_dict()

        # Deserialize from dict
        restored = GenericElement.from_dict(data)

        # Verify all parameters are preserved
        assert restored.element_id == "pole_001"
        assert restored.element_type == "pole"
        assert restored.get_parameter("height") == 12000.0
        assert restored.get_parameter("diameter") == 300.0
        assert restored.get_parameter("material") == "steel"

        # Verify metadata is preserved
        height_meta = restored.get_parameter_metadata("height")
        assert height_meta["unit"] == UnitType.MILLIMETER

    def test_geometry_container_automatic_creation(self):
        """Test that geometry container is automatically created when needed."""
        element = GenericElement("foundation_001", "foundation")

        # Setting geometric parameters should auto-create geometry
        element.set_parameter("width", 2000.0, UnitType.MILLIMETER)
        element.set_parameter("length", 3000.0, UnitType.MILLIMETER)
        element.set_parameter("depth", 1500.0, UnitType.MILLIMETER)

        # Geometry should be automatically available
        geometry = element.get_geometry()
        assert geometry is not None
        assert geometry.width == 2000.0
        assert geometry.length == 3000.0
        assert geometry.depth == 1500.0

        # Changes through geometry should reflect in parameters
        geometry.width = 2500.0
        assert element.get_parameter("width") == 2500.0
