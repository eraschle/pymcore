"""
Parameter registry system for PyM Core.

Provides unified parameter management bridging ENUM and Plugin systems
with automatic conversion and validation capabilities.
"""

from __future__ import annotations
from typing import Type, Any
from enum import Enum

from pymcore.generic_element import ParameterMetadata
from .parameter_descriptor import ParameterDescriptor
from .types import Unit


class ParameterMapping:
    """
    ENUM-based parameter mapping for backwards compatibility.

    Maps ENUM roles to parameter names and units for specific element types.
    """

    def __init__(self, element_type: str):
        """
        Initialize parameter mapping for an element type.

        Parameters
        ----------
        element_type : str
            Type of element this mapping applies to
        """
        self.element_type = element_type
        self._parameter_role: dict[Enum, ParameterMetadata] = {}

    def add_parameter(self, role: Enum, parameter: ParameterMetadata) -> None:
        """
        Add parameter mapping for an ENUM role.

        Parameters
        ----------
        role : Enum
            Parameter role from ENUM
        parameter_name : str
            Actual parameter name in element
        unit : UnitType
            Unit for this parameter
        """
        self._parameter_role[role] = parameter

    def get_parameter_name(self, role: Enum) -> str | None:
        """Get parameter name for ENUM role."""
        parmeter = self._parameter_role.get(role)
        return parmeter.name if parmeter else None

    def get_parameter_unit(self, role: Enum) -> Unit:
        """Get parameter unit for ENUM role."""
        parmeter = self._parameter_role.get(role)
        return parmeter.unit if parmeter else Unit.NONE

    def get_all_roles(self) -> list[Enum]:
        """Get all mapped ENUM roles."""
        return list(self._parameter_role.keys())


class ParameterRegistry:
    """
    Central registry for parameter definitions and mappings.

    Bridges ENUM-based and Plugin-based parameter systems with
    automatic conversion and validation capabilities.
    """

    def __init__(self):
        """Initialize empty parameter registry."""
        self._parameters: dict[str, ParameterDescriptor] = {}
        self._enum_mappings: dict[str, ParameterMapping] = {}
        self._parameter_categories: dict[str, list[str]] = {
            "geometric": [],
            "railway": [],
            "material": [],
        }

    def register_parameter(self, descriptor: ParameterDescriptor) -> None:
        """
        Register a parameter descriptor.

        Parameters
        ----------
        descriptor : ParameterDescriptor
            Parameter definition to register
        """
        self._parameters[descriptor.semantic_key] = descriptor
        self._categorize_parameter(descriptor)

    def register_from_enum(self, parameter_enum: Type[Enum]) -> None:
        """
        Auto-register parameters from an ENUM definition.

        Automatically infers types and units based on parameter names.

        Parameters
        ----------
        parameter_enum : Type[Enum]
            ENUM class containing parameter roles
        """
        for role in parameter_enum:
            # Infer parameter characteristics from name
            semantic_key = role.value
            data_type, unit, category = self._infer_parameter_characteristics(semantic_key)

            descriptor = ParameterDescriptor(
                semantic_key=semantic_key,
                data_type=data_type,
                unit=unit,
                required=True,
                description=f"Auto-generated from ENUM {parameter_enum.__name__}.{role.name}",
            )

            self.register_parameter(descriptor)

    def register_enum_mapping(self, mapping_name: str, enum_mapping: ParameterMapping) -> None:
        """
        Register an ENUM-based parameter mapping.

        Parameters
        ----------
        mapping_name : str
            Name for this mapping (typically element type)
        enum_mapping : ParameterMapping
            The mapping definition
        """
        self._enum_mappings[mapping_name] = enum_mapping

        # Auto-convert mapping to parameter descriptors
        for role in enum_mapping.get_all_roles():
            param_name = enum_mapping.get_parameter_name(role)
            param_unit = enum_mapping.get_parameter_unit(role)

            if param_name and role.value not in self._parameters:
                data_type = self._infer_type_from_unit(param_unit)

                descriptor = ParameterDescriptor(
                    semantic_key=role.value,
                    data_type=data_type,
                    unit=param_unit,
                    required=True,
                    description=f"From ENUM mapping {mapping_name}",
                )

                self.register_parameter(descriptor)

    def get_parameter(self, semantic_key: str) -> ParameterDescriptor | None:
        """
        Get parameter descriptor by semantic key.

        Parameters
        ----------
        semantic_key : str
            Semantic identifier for the parameter

        Returns
        -------
        ParameterDescriptor or None
            Parameter descriptor if found
        """
        return self._parameters.get(semantic_key)

    def get_enum_mapping(self, mapping_name: str) -> ParameterMapping | None:
        """
        Get ENUM mapping by name.

        Parameters
        ----------
        mapping_name : str
            Name of the mapping

        Returns
        -------
        ParameterMapping or None
            Mapping if found
        """
        return self._enum_mappings.get(mapping_name)

    def get_parameters_by_category(self, category: str) -> list[ParameterDescriptor]:
        """
        Get all parameters in a category.

        Parameters
        ----------
        category : str
            Category name ("geometric", "railway", "material")

        Returns
        -------
        list[ParameterDescriptor]
            Parameters in the category
        """
        param_keys = self._parameter_categories.get(category, [])
        return [self._parameters[key] for key in param_keys if key in self._parameters]

    def get_all_parameters(self) -> list[ParameterDescriptor]:
        """
        Get all registered parameters.

        Returns
        -------
        list[ParameterDescriptor]
            All registered parameter descriptors
        """
        return list(self._parameters.values())

    def validate_parameter_value(self, semantic_key: str, value: Any) -> bool:
        """
        Validate a parameter value against its descriptor.

        Parameters
        ----------
        semantic_key : str
            Parameter identifier
        value : Any
            Value to validate

        Returns
        -------
        bool
            True if value is valid for the parameter
        """
        descriptor = self.get_parameter(semantic_key)
        if descriptor is None:
            return False

        # Type validation
        try:
            if descriptor.data_type is float:
                float(value)
            elif descriptor.data_type is int:
                int(value)
            elif descriptor.data_type is str:
                str(value)
            elif descriptor.data_type is bool:
                bool(value)
            else:
                return False
            return True
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize registry to dictionary.

        Returns
        -------
        dict[str, Any]
            Serialized registry data
        """
        return {
            "parameters": {
                key: {
                    "semantic_key": desc.semantic_key,
                    "data_type": desc.data_type.__name__,
                    "unit": desc.unit.value,
                    "required": desc.required,
                    "default_value": desc.default_value,
                    "description": desc.description,
                }
                for key, desc in self._parameters.items()
            },
            "categories": self._parameter_categories.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParameterRegistry:
        """
        Restore registry from dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Serialized registry data

        Returns
        -------
        ParameterRegistry
            Restored registry instance
        """
        registry = cls()

        # Restore parameters
        for key, param_data in data.get("parameters", {}).items():
            # Convert type name back to type
            type_name = param_data["data_type"]
            if type_name == "float":
                data_type = float
            elif type_name == "int":
                data_type = int
            elif type_name == "str":
                data_type = str
            elif type_name == "bool":
                data_type = bool
            else:
                continue  # Skip unknown types

            # Convert unit value back to UnitType
            unit_value = param_data["unit"]
            unit = Unit(unit_value)

            descriptor = ParameterDescriptor(
                semantic_key=param_data["semantic_key"],
                data_type=data_type,
                unit=unit,
                required=param_data["required"],
                default_value=param_data["default_value"],
                description=param_data["description"],
            )

            registry.register_parameter(descriptor)

        # Restore categories
        registry._parameter_categories = data.get("categories", {}).copy()

        return registry

    def _infer_parameter_characteristics(self, semantic_key: str) -> tuple[Type, Unit, str]:
        """Infer parameter type, unit, and category from semantic key."""
        key_lower = semantic_key.lower()

        # Railway-specific patterns take precedence
        if any(rail in key_lower for rail in ["gauge", "rail", "track", "sleeper", "cantilever", "curve"]):
            if "spacing" in key_lower or "radius" in key_lower:
                return float, Unit.MILLIMETER, "railway"
            elif "profile" in key_lower:
                return str, Unit.NONE, "railway"
            else:
                return float, Unit.MILLIMETER, "railway"
        elif "capacity" in key_lower or "load" in key_lower:
            return float, Unit.KILOGRAM, "railway"
        elif any(mat in key_lower for mat in ["material", "concrete", "steel"]):
            return str, Unit.NONE, "material"
        elif any(dim in key_lower for dim in ["height", "width", "length", "depth", "diameter"]):
            return float, Unit.MILLIMETER, "geometric"
        else:
            # Default assumptions
            return float, Unit.MILLIMETER, "geometric"

    def _infer_type_from_unit(self, unit: Unit) -> Type:
        """Infer Python type from unit type."""
        if unit == Unit.NONE:
            return str
        else:
            return float

    def _categorize_parameter(self, descriptor: ParameterDescriptor) -> None:
        """Add parameter to appropriate category."""
        _, _, category = self._infer_parameter_characteristics(descriptor.semantic_key)

        if category in self._parameter_categories:
            if descriptor.semantic_key not in self._parameter_categories[category]:
                self._parameter_categories[category].append(descriptor.semantic_key)
