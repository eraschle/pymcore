"""
Integration tests for HybridParameterInterface.

Tests focus on unified ENUM and Plugin parameter access with proper exception
handling for conflicting configurations.
"""

from enum import Enum

import pytest
from pymcore.generic_element import GenericElement
from pymcore.hybrid_parameter_interface import (
    HybridParameterInterface,
    ParameterConfigurationError,
)
from pymcore.parameter_registry import ParameterMapping, ParameterRegistry
from pymcore.types import Unit, ValueType


class ParameterRole(Enum):
    """Railway infrastructure parameter roles for testing."""

    PRIMARY_HEIGHT = "primary_height"
    PRIMARY_LENGTH = "primary_length"
    DIAMETER = "diameter"
    MATERIAL_TYPE = "material_type"
    GAUGE = "gauge"


class TestHybridParameterInterfaceIntegration:
    """Integration tests for hybrid parameter interface system."""

    def test_enum_mode_parameter_access(self):
        """Test parameter access using ENUM mode only."""
        from pymcore.generic_element import ParameterMetadata

        element = GenericElement("pole_001", "pole")
        element.define_parameter(name="height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)
        element.define_parameter(name="diameter", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT)
        element.define_parameter(name="material", unit=Unit.NONE, value_type=ValueType.STRING)

        pole_mapping = ParameterMapping("pole")
        pole_mapping.add_parameter(
            ParameterRole.PRIMARY_HEIGHT,
            ParameterMetadata("height", Unit.MILLIMETER, ValueType.FLOAT),
        )
        pole_mapping.add_parameter(
            ParameterRole.DIAMETER,
            ParameterMetadata("diameter", Unit.MILLIMETER, ValueType.FLOAT),
        )
        pole_mapping.add_parameter(
            ParameterRole.MATERIAL_TYPE,
            ParameterMetadata("material", Unit.NONE, ValueType.STRING),
        )

        # Create interface with ENUM mapping only
        interface = HybridParameterInterface(element=element, mapping_name="pole", enum_mapping=pole_mapping)
        interface._resolve_enum_parameter(ParameterRole.PRIMARY_HEIGHT)

        # Set values using ENUM
        interface.set_value(ParameterRole.PRIMARY_HEIGHT, 12000.0)
        interface.set_value(ParameterRole.DIAMETER, 300.0)
        interface.set_value(ParameterRole.MATERIAL_TYPE, "steel")

        # Get values using ENUM
        param_value = interface.get_value(ParameterRole.PRIMARY_HEIGHT)
        assert param_value is not None
        assert param_value == 12000.0

        param_value = interface.get_value(ParameterRole.DIAMETER)
        assert param_value is not None
        assert param_value == 300.0

        param_value = interface.get_value(ParameterRole.MATERIAL_TYPE)
        assert param_value is not None
        assert param_value == "steel"

        # Verify values are stored in element with correct parameter names
        param_value = element.value_by("height")
        assert param_value is not None
        assert param_value.value == 12000.0

        param_value = element.value_by("diameter")
        assert param_value is not None
        assert param_value.value == 300.0

        param_value = element.value_by("material")
        assert param_value is not None
        assert param_value.value == "steel"

    def test_plugin_mode_parameter_access(self):
        """Test parameter access using Plugin/Registry mode only."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(name="primary_height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)
        element.define_parameter(name="diameter", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)
        element.define_parameter(name="material_type", value_type=ValueType.STRING, unit=Unit.NONE)

        # Create registry with parameter definitions
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        # Create interface with registry only
        interface = HybridParameterInterface(element=element, mapping_name="pole", registry=registry)

        # Set values using string keys (Plugin mode)
        interface.set_value("primary_height", 15000.0)
        interface.set_value("diameter", 350.0)
        interface.set_value("material_type", "aluminum")

        # Get values using string keys
        param_value = interface.get_value("primary_height")
        assert param_value is not None
        assert param_value == 15000.0
        param_value = interface.get_value("diameter")
        assert param_value is not None
        assert param_value == 350.0
        param_value = interface.get_value("material_type")
        assert param_value is not None
        assert param_value == "aluminum"

        # Verify values are stored in element with semantic keys
        param_value = element.value_by("primary_height")
        assert param_value is not None
        assert param_value.value == 15000.0
        param_value = element.value_by("diameter")
        assert param_value is not None
        assert param_value.value == 350
        param_value = element.value_by("material_type")
        assert param_value is not None
        assert param_value.value == "aluminum"

    def test_conflicting_configuration_raises_exception(self):
        """Test that providing both enum_mapping and registry raises exception."""
        element = GenericElement("pole_001", "pole")

        # Create both mapping and registry
        from pymcore.generic_element import ParameterMetadata
        from pymcore.types import ValueType

        pole_mapping = ParameterMapping("pole")
        pole_mapping.add_parameter(
            ParameterRole.PRIMARY_HEIGHT,
            ParameterMetadata("height", Unit.MILLIMETER, ValueType.FLOAT),
        )

        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        # Providing both should raise exception
        with pytest.raises(ParameterConfigurationError) as exc_info:
            HybridParameterInterface(
                element=element,
                mapping_name="pole",
                enum_mapping=pole_mapping,
                registry=registry,
            )

        assert "Cannot provide both enum_mapping and registry" in str(exc_info.value)

    def test_no_configuration_raises_exception(self):
        """Test that providing neither enum_mapping nor registry raises exception."""
        element = GenericElement("pole_001", "pole")

        # Providing neither should raise exception
        with pytest.raises(ParameterConfigurationError) as exc_info:
            HybridParameterInterface(element=element, mapping_name="pole")

        assert "Must provide either enum_mapping or registry" in str(exc_info.value)

    def test_smart_dispatcher_enum_vs_string(self):
        """Test that interface correctly dispatches ENUM vs string access."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(name="primary_height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)
        element.define_parameter(name="diameter", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)

        # Use registry for both ENUM and string access
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        interface = HybridParameterInterface(element=element, mapping_name="pole", registry=registry)
        registry.register_from_enum(ParameterRole)
        # Set using ENUM
        interface.set_value(ParameterRole.PRIMARY_HEIGHT, 12000.0)

        # Get using both ENUM and string - should return same value
        enum_value = interface.get_value(ParameterRole.PRIMARY_HEIGHT)
        string_value = interface.get_value("primary_height")

        assert enum_value == string_value == 12000.0

        # Set using string
        interface.set_value("diameter", 300.0)

        # Get using both string and ENUM - should return same value
        string_value = interface.get_value("diameter")
        enum_value = interface.get_value(ParameterRole.DIAMETER)

        assert string_value == enum_value == 300.0

    def test_unit_conversion_through_interface(self):
        """Test that unit conversion works through the interface."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(name="primary_height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)

        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        interface = HybridParameterInterface(element=element, mapping_name="pole", registry=registry)

        # Set height in meters (will be stored in first-used unit)
        interface.set_value_with_unit("primary_height", 12.0, Unit.METER)

        # Get value (stored in METER since that was first unit used)
        height_m = interface.get_value("primary_height")
        assert height_m == 12.0

        height_mm = interface.get_value_with_unit("primary_height", Unit.METER)
        assert height_mm == 12.0 / 1000

    def test_parameter_validation_through_interface(self):
        """Test parameter validation through the interface."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(name="primary_height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)

        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        interface = HybridParameterInterface(element=element, mapping_name="pole", registry=registry)

        # Valid numeric value should work
        interface.set_value("primary_height", 12000.0)
        assert interface.validate_value("primary_height", 15000.0)

        # Invalid value type should fail validation
        assert not interface.validate_value("primary_height", "not_a_number")

        # String parameter should accept strings
        assert interface.validate_value("material_type", "steel")

    def test_default_value_handling(self):
        """Test proper handling of default values."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(name="primary_height", value_type=ValueType.FLOAT, unit=Unit.MILLIMETER)

        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        interface = HybridParameterInterface(element=element, mapping_name="pole", registry=registry)

        # Get non-existent parameter with default
        value = interface.get_value("non_existent", default=999.0)
        assert value == 999.0

        # Get non-existent parameter without default (should return None)
        value = interface.get_value("non_existent")
        assert value is None

    def test_interface_serialization_roundtrip(self):
        """Test that interface state can be serialized and restored."""
        element = GenericElement("pole_001", "pole")
        element.define_parameter(name="primary_height", unit=Unit.MILLIMETER, value_type=ValueType.FLOAT)
        element.define_parameter(name="material_type", unit=Unit.NONE, value_type=ValueType.STRING)

        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        interface = HybridParameterInterface(element=element, mapping_name="pole", registry=registry)

        # Set some values
        interface.set_value("primary_height", 12000.0)
        interface.set_value("material_type", "steel")

        # Serialize interface configuration
        config_data = interface.get_configuration()

        # Create new interface from configuration
        new_element = GenericElement.from_dict(element.to_dict())
        new_interface = HybridParameterInterface.from_configuration(element=new_element, config_data=config_data)

        # Verify values are preserved
        assert new_interface.get_value("primary_height") == 12000.0
        assert new_interface.get_value("material_type") == "steel"
