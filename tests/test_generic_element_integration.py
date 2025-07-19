"""
Integration tests for GenericElement with Parameter and Geometry synchronization.

Tests focus on ensuring that geometry properties automatically sync with
underlying parameters without requiring explicit synchronization.
"""

import pytest

from pymcore.generic_element import GenericElement
from pymcore.types import Unit, ValueType
from pymcore.unit_converter import UnitConversionError


class TestGenericElementIntegration:
    """Integration tests for GenericElement parameter management."""

    def test_parameter_operations_with_unit_conversion(self):
        """Test basic parameter operations with automatic unit conversion."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(
            "height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER
        )

        # Set parameter with unit conversion (12m -> mm)
        element.set_value("height", 12.0, unit=Unit.METER)

        # Retrieve in original unit
        height_mm = element.value_by("height")
        assert height_mm is not None
        assert height_mm.value == 12000.0

        # Retrieve with unit conversion (mm -> m)
        height_m = element.value_by("height", default=0.0)
        assert height_m is not None
        assert height_m.value == 12000.00

    def test_parameter_sync_with_geometry_descriptor(self):
        """Test that geometry descriptors automatically sync with parameters."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(
            "height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER
        )
        # Set height parameter directly
        element.set_value("height", 15000.0, Unit.MILLIMETER)

        # Access through geometry property should return same value
        geometry = element.get_geometry()
        assert geometry.height == 15000.0

        # Change through geometry should update parameter
        geometry.height = 18000.0
        param_value = element.value_by("height")
        assert param_value is not None
        assert param_value.value == 18000.0

    def test_invalid_unit_conversion_raises_exception(self):
        """Test that invalid unit conversions raise proper exceptions."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(
            "height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER
        )

        # Try to set length parameter with mass unit
        with pytest.raises(UnitConversionError):
            element.set_value("height", 100.0, Unit.KILOGRAM)

    def test_parameter_metadata_storage(self):
        """Test that parameter metadata (units, types) is properly stored."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(
            "height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER
        )

        # Set parameter with metadata
        element.set_value("height", 12000.0, Unit.MILLIMETER)

        # Retrieve metadata
        metadata = element.definition_by("height")
        assert metadata is not None
        assert metadata.name == "height"
        assert metadata.unit == Unit.MILLIMETER
        assert metadata.value_type == ValueType.FLOAT

    def test_element_serialization_roundtrip(self):
        """Test that elements can be serialized and deserialized correctly."""
        original = GenericElement("pole_001", "pole")
        original.define_parameter(
            "height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER
        )
        original.define_parameter(
            "diameter", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER
        )
        original.define_parameter(
            "material", value_type=ValueType.STRING, unit=Unit.NONE
        )
        original.set_value("height", 12000.0, Unit.MILLIMETER)
        original.set_value("diameter", 300.0, Unit.MILLIMETER)
        original.set_value("material", "steel", Unit.NONE)

        # Serialize to dict
        data = original.to_dict()

        # Deserialize from dict
        restored = GenericElement.from_dict(data)

        # Verify all parameters are preserved
        assert restored.element_id == "pole_001"
        assert restored.element_type == "pole"
        param_value = restored.value_by("height")
        assert param_value is not None
        assert param_value.value == 12000.0
        param_value = restored.value_by("diameter")
        assert param_value is not None
        assert param_value.value == 300.0
        param_value = restored.value_by("material")
        assert param_value is not None
        assert param_value.value == "steel"

        # Verify metadata is preserved
        definition = restored.definition_by("height")
        assert definition is not None
        assert definition.unit == Unit.MILLIMETER
        assert definition.value_type == ValueType.FLOAT

    def test_geometry_container_automatic_creation(self):
        """Test that geometry container is automatically created when needed."""
        element = GenericElement("foundation_001", "foundation")
        element.define_parameter(
            "width", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER
        )
        element.define_parameter(
            "length", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER
        )
        element.define_parameter("depth", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)

        # Setting geometric parameters should auto-create geometry
        element.set_value("width", 2000.0, Unit.MILLIMETER)
        element.set_value("length", 3000.0, Unit.MILLIMETER)
        element.set_value("depth", 1500.0, Unit.MILLIMETER)

        # Geometry should be automatically available
        geometry = element.get_geometry()
        assert geometry is not None
        assert geometry.width == 2000.0
        assert geometry.length == 3000.0
        assert geometry.depth == 1500.0

        # Changes through geometry should reflect in parameters
        geometry.width = 2500.0
        width_param = element.value_by("width")
        assert width_param is not None
        assert width_param.value == 2500.0
