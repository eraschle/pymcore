"""
Integration tests for HybridParameterInterface.

Tests focus on unified ENUM and Plugin parameter access with proper exception
handling for conflicting configurations.
"""
import pytest
from enum import Enum
from pymcore.hybrid_parameter_interface import HybridParameterInterface, ParameterConfigurationError
from pymcore.generic_element import GenericElement
from pymcore.parameter_registry import ParameterRegistry, ParameterMapping
from pymcore.parameter_descriptor import ParameterDescriptor
from pymcore.types import UnitType, ValueType


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
        element = GenericElement("pole_001", "pole")
        
        # Create ENUM mapping
        pole_mapping = ParameterMapping("pole")
        pole_mapping.add_parameter(ParameterRole.PRIMARY_HEIGHT, "height", UnitType.MILLIMETER)
        pole_mapping.add_parameter(ParameterRole.DIAMETER, "diameter", UnitType.MILLIMETER)
        pole_mapping.add_parameter(ParameterRole.MATERIAL_TYPE, "material", UnitType.NONE)
        
        # Create interface with ENUM mapping only
        interface = HybridParameterInterface(
            element=element,
            mapping_name="pole", 
            enum_mapping=pole_mapping
        )
        
        # Set values using ENUM
        interface.set_value(ParameterRole.PRIMARY_HEIGHT, 12000.0)
        interface.set_value(ParameterRole.DIAMETER, 300.0)
        interface.set_value(ParameterRole.MATERIAL_TYPE, "steel")
        
        # Get values using ENUM
        assert interface.get_value(ParameterRole.PRIMARY_HEIGHT) == 12000.0
        assert interface.get_value(ParameterRole.DIAMETER) == 300.0
        assert interface.get_value(ParameterRole.MATERIAL_TYPE) == "steel"
        
        # Verify values are stored in element with correct parameter names
        assert element.get_parameter("height") == 12000.0
        assert element.get_parameter("diameter") == 300.0
        assert element.get_parameter("material") == "steel"

    def test_plugin_mode_parameter_access(self):
        """Test parameter access using Plugin/Registry mode only."""
        element = GenericElement("pole_001", "pole")
        
        # Create registry with parameter definitions
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)
        
        # Create interface with registry only
        interface = HybridParameterInterface(
            element=element,
            mapping_name="pole",
            registry=registry
        )
        
        # Set values using string keys (Plugin mode)
        interface.set_value("primary_height", 15000.0)
        interface.set_value("diameter", 350.0)
        interface.set_value("material_type", "aluminum")
        
        # Get values using string keys
        assert interface.get_value("primary_height") == 15000.0
        assert interface.get_value("diameter") == 350.0
        assert interface.get_value("material_type") == "aluminum"
        
        # Verify values are stored in element with semantic keys
        assert element.get_parameter("primary_height") == 15000.0
        assert element.get_parameter("diameter") == 350.0
        assert element.get_parameter("material_type") == "aluminum"

    def test_conflicting_configuration_raises_exception(self):
        """Test that providing both enum_mapping and registry raises exception."""
        element = GenericElement("pole_001", "pole")
        
        # Create both mapping and registry
        pole_mapping = ParameterMapping("pole")
        pole_mapping.add_parameter(ParameterRole.PRIMARY_HEIGHT, "height", UnitType.MILLIMETER)
        
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)
        
        # Providing both should raise exception
        with pytest.raises(ParameterConfigurationError) as exc_info:
            HybridParameterInterface(
                element=element,
                mapping_name="pole",
                enum_mapping=pole_mapping,
                registry=registry
            )
        
        assert "Cannot provide both enum_mapping and registry" in str(exc_info.value)

    def test_no_configuration_raises_exception(self):
        """Test that providing neither enum_mapping nor registry raises exception."""
        element = GenericElement("pole_001", "pole")
        
        # Providing neither should raise exception
        with pytest.raises(ParameterConfigurationError) as exc_info:
            HybridParameterInterface(
                element=element,
                mapping_name="pole"
            )
        
        assert "Must provide either enum_mapping or registry" in str(exc_info.value)

    def test_smart_dispatcher_enum_vs_string(self):
        """Test that interface correctly dispatches ENUM vs string access."""
        element = GenericElement("pole_001", "pole")
        
        # Use registry for both ENUM and string access
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)
        
        interface = HybridParameterInterface(
            element=element,
            mapping_name="pole",
            registry=registry
        )
        
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
        
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)
        
        interface = HybridParameterInterface(
            element=element,
            mapping_name="pole",
            registry=registry
        )
        
        # Set height in meters (should be stored as mm)
        interface.set_value_with_unit("primary_height", 12.0, UnitType.METER)
        
        # Get as millimeters (default storage unit)
        height_mm = interface.get_value("primary_height")
        assert height_mm == 12000.0
        
        # Get with unit conversion back to meters
        height_m = interface.get_value_with_unit("primary_height", UnitType.METER)
        assert height_m == 12.0

    def test_parameter_validation_through_interface(self):
        """Test parameter validation through the interface."""
        element = GenericElement("pole_001", "pole")
        
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)
        
        interface = HybridParameterInterface(
            element=element,
            mapping_name="pole",
            registry=registry
        )
        
        # Valid numeric value should work
        interface.set_value("primary_height", 12000.0)
        assert interface.validate_value("primary_height", 15000.0) == True
        
        # Invalid value type should fail validation
        assert interface.validate_value("primary_height", "not_a_number") == False
        
        # String parameter should accept strings
        assert interface.validate_value("material_type", "steel") == True

    def test_default_value_handling(self):
        """Test proper handling of default values."""
        element = GenericElement("pole_001", "pole")
        
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)
        
        interface = HybridParameterInterface(
            element=element,
            mapping_name="pole",
            registry=registry
        )
        
        # Get non-existent parameter with default
        value = interface.get_value("non_existent", default=999.0)
        assert value == 999.0
        
        # Get non-existent parameter without default (should return None)
        value = interface.get_value("non_existent")
        assert value is None

    def test_interface_serialization_roundtrip(self):
        """Test that interface state can be serialized and restored."""
        element = GenericElement("pole_001", "pole")
        
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)
        
        interface = HybridParameterInterface(
            element=element,
            mapping_name="pole",
            registry=registry
        )
        
        # Set some values
        interface.set_value("primary_height", 12000.0)
        interface.set_value("material_type", "steel")
        
        # Serialize interface configuration
        config_data = interface.get_configuration()
        
        # Create new interface from configuration
        new_element = GenericElement.from_dict(element.to_dict())
        new_interface = HybridParameterInterface.from_configuration(
            element=new_element,
            config_data=config_data
        )
        
        # Verify values are preserved
        assert new_interface.get_value("primary_height") == 12000.0
        assert new_interface.get_value("material_type") == "steel"