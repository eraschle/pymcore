"""
Integration tests for ParameterRegistry System.

Tests focus on ENUM to Plugin parameter conversion and registry management
for railway infrastructure parameters.
"""

from enum import Enum
from pymcore.parameter_registry import ParameterRegistry, ParameterMapping
from pymcore.parameter_descriptor import ParameterDescriptor
from pymcore.types import UnitType


class ParameterRole(Enum):
    """Railway infrastructure parameter roles for testing."""

    # Geometric dimensions
    PRIMARY_HEIGHT = "primary_height"
    PRIMARY_LENGTH = "primary_length"
    PRIMARY_WIDTH = "primary_width"
    DIAMETER = "diameter"

    # Railway-specific
    GAUGE = "gauge"
    RAIL_PROFILE = "rail_profile"
    CURVE_RADIUS = "curve_radius"
    LOAD_CAPACITY = "load_capacity"
    FOUNDATION_DEPTH = "foundation_depth"
    SLEEPER_SPACING = "sleeper_spacing"

    # Materials
    MATERIAL_TYPE = "material_type"
    CONCRETE_GRADE = "concrete_grade"


class TestParameterRegistryIntegration:
    """Integration tests for parameter registry system."""

    def test_enum_to_plugin_auto_conversion(self):
        """Test automatic conversion from ENUM to Plugin descriptors."""
        registry = ParameterRegistry()

        # Register ENUM with default conversions
        registry.register_from_enum(ParameterRole)

        # Verify numeric parameters get appropriate defaults
        height_desc = registry.get_parameter("primary_height")
        assert height_desc is not None
        assert height_desc.semantic_key == "primary_height"
        assert height_desc.data_type is float
        assert height_desc.unit == UnitType.MILLIMETER  # Default for dimensions

        # Verify string parameters
        material_desc = registry.get_parameter("material_type")
        assert material_desc is not None
        assert material_desc.data_type is str
        assert material_desc.unit == UnitType.NONE

    def test_custom_parameter_descriptor_registration(self):
        """Test registration of custom parameter descriptors."""
        registry = ParameterRegistry()

        # Register custom descriptor
        custom_desc = ParameterDescriptor(
            semantic_key="custom_load",
            data_type=float,
            unit=UnitType.KILOGRAM,
            required=False,
            default_value=0.0,
            description="Custom load parameter",
        )

        registry.register_parameter(custom_desc)

        # Verify registration
        retrieved = registry.get_parameter("custom_load")
        assert retrieved == custom_desc
        assert retrieved is not None
        assert retrieved.default_value == 0.0
        assert not retrieved.required

    def test_enum_mapping_system(self):
        """Test ENUM-based parameter mapping system."""
        registry = ParameterRegistry()

        # Create mapping for pole elements
        pole_mapping = ParameterMapping("pole")
        pole_mapping.add_parameter(ParameterRole.PRIMARY_HEIGHT, "height", UnitType.MILLIMETER)
        pole_mapping.add_parameter(ParameterRole.DIAMETER, "diameter", UnitType.MILLIMETER)
        pole_mapping.add_parameter(ParameterRole.MATERIAL_TYPE, "material", UnitType.NONE)

        # Register mapping
        registry.register_enum_mapping("pole", pole_mapping)

        # Verify mapping retrieval
        retrieved_mapping = registry.get_enum_mapping("pole")
        assert retrieved_mapping is not None
        assert retrieved_mapping.element_type == "pole"

        # Test parameter resolution through mapping
        height_param = retrieved_mapping.get_parameter_name(ParameterRole.PRIMARY_HEIGHT)
        assert height_param == "height"

        height_unit = retrieved_mapping.get_parameter_unit(ParameterRole.PRIMARY_HEIGHT)
        assert height_unit == UnitType.MILLIMETER

    def test_registry_parameter_lookup_integration(self):
        """Test integrated parameter lookup across ENUM and Plugin systems."""
        registry = ParameterRegistry()

        # Register both ENUM and custom parameters
        registry.register_from_enum(ParameterRole)

        custom_desc = ParameterDescriptor(
            semantic_key="special_coating", data_type=str, unit=UnitType.NONE, required=False
        )
        registry.register_parameter(custom_desc)

        # Test lookup of ENUM-derived parameter
        enum_param = registry.get_parameter("primary_height")
        assert enum_param is not None
        assert enum_param.semantic_key == "primary_height"

        # Test lookup of custom parameter
        custom_param = registry.get_parameter("special_coating")
        assert custom_param is not None
        assert custom_param.semantic_key == "special_coating"

        # Test non-existent parameter
        missing_param = registry.get_parameter("non_existent")
        assert missing_param is None

    def test_parameter_validation_through_registry(self):
        """Test parameter validation using registry definitions."""
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        # Valid parameter should pass validation
        assert registry.validate_parameter_value("primary_height", 12000.0)

        # Invalid type should fail validation
        assert not registry.validate_parameter_value("primary_height", "not_a_number")

        # String parameter should accept string
        assert registry.validate_parameter_value("material_type", "steel")

    def test_railway_specific_parameter_categories(self):
        """Test that railway-specific parameters are properly categorized."""
        registry = ParameterRegistry()
        registry.register_from_enum(ParameterRole)

        # Test geometric parameters
        geometric_params = registry.get_parameters_by_category("geometric")
        expected_geometric = {"primary_height", "primary_length", "primary_width", "diameter"}

        geometric_keys = {p.semantic_key for p in geometric_params}
        assert expected_geometric.issubset(geometric_keys)

        # Test railway-specific parameters
        railway_params = registry.get_parameters_by_category("railway")
        expected_railway = {"gauge", "rail_profile", "curve_radius", "sleeper_spacing"}

        railway_keys = {p.semantic_key for p in railway_params}
        assert expected_railway.issubset(railway_keys)

    def test_registry_serialization_roundtrip(self):
        """Test that registry can be serialized and restored."""
        original_registry = ParameterRegistry()
        original_registry.register_from_enum(ParameterRole)

        # Serialize registry
        registry_data = original_registry.to_dict()

        # Restore registry
        restored_registry = ParameterRegistry.from_dict(registry_data)

        # Verify all parameters are preserved
        original_params = original_registry.get_all_parameters()
        restored_params = restored_registry.get_all_parameters()

        assert len(original_params) == len(restored_params)

        for param in original_params:
            restored_param = restored_registry.get_parameter(param.semantic_key)
            assert restored_param is not None
            assert restored_param.semantic_key == param.semantic_key
            assert restored_param.data_type == param.data_type
            assert restored_param.unit == param.unit
