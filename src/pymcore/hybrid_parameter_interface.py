"""
Hybrid Parameter Interface for PyM Core.

Provides unified interface for ENUM and Plugin parameter access with
automatic dispatching and proper exception handling for conflicts.
"""

from __future__ import annotations
from typing import Any
from enum import Enum

from .generic_element import GenericElement
from .parameter_registry import ParameterRegistry, ParameterMapping
from .types import UnitType, ValueType


class ParameterConfigurationError(Exception):
    """Raised when parameter interface configuration is invalid."""

    pass


class HybridParameterInterface:
    """
    Unified interface for ENUM and Plugin parameter access.

    Automatically dispatches between ENUM and string-based parameter access
    based on the type of the key provided. Ensures only one configuration
    mode is active to prevent conflicts.
    """

    def __init__(
        self,
        element: GenericElement,
        mapping_name: str,
        enum_mapping: ParameterMapping | None = None,
        registry: ParameterRegistry | None = None,
    ):
        """
        Initialize hybrid parameter interface.

        Parameters
        ----------
        element : GenericElement
            The element this interface manages parameters for
        mapping_name : str
            Name/identifier for this parameter mapping
        enum_mapping : ParameterMapping, optional
            ENUM-based parameter mapping (legacy mode)
        registry : ParameterRegistry, optional
            Plugin-based parameter registry (new mode)

        Raises
        ------
        ParameterConfigurationError
            If both or neither configuration options are provided
        """
        # Validate configuration - exactly one mode must be provided
        if enum_mapping is not None and registry is not None:
            raise ParameterConfigurationError(
                "Cannot provide both enum_mapping and registry. Use either ENUM mode or Plugin mode, not both."
            )

        if enum_mapping is None and registry is None:
            raise ParameterConfigurationError(
                "Must provide either enum_mapping or registry. One configuration mode is required."
            )

        self._element = element
        self._mapping_name = mapping_name
        self._enum_mapping = enum_mapping
        self._registry = registry

        # Determine active mode
        self._is_enum_mode = enum_mapping is not None
        self._is_plugin_mode = registry is not None

    def set_value(self, role_or_key: Enum | str, value: Any) -> None:
        """
        Set parameter value using smart dispatching.

        Parameters
        ----------
        role_or_key : Enum | str
            ENUM role or string key for the parameter
        value : Any
            Value to set
        """
        if isinstance(role_or_key, Enum):
            self._set_enum_value(role_or_key, value)
        else:
            self._set_string_value(role_or_key, value)

    def get_value(self, role_or_key: Enum | str, default: Any = None) -> Any:
        """
        Get parameter value using smart dispatching.

        Parameters
        ----------
        role_or_key : Enum | str
            ENUM role or string key for the parameter
        default : Any
            Default value if parameter doesn't exist

        Returns
        -------
        Any
            Parameter value or default
        """
        if isinstance(role_or_key, Enum):
            return self._get_enum_value(role_or_key, default)
        else:
            return self._get_string_value(role_or_key, default)

    def set_value_with_unit(self, role_or_key: Enum | str, value: Any, unit: UnitType) -> None:
        """
        Set parameter value with explicit unit conversion.

        Parameters
        ----------
        role_or_key : Enum | str
            ENUM role or string key for the parameter
        value : Any
            Value to set
        unit : UnitType
            Unit of the input value
        """
        if isinstance(role_or_key, Enum):
            param_name, target_unit = self._resolve_enum_parameter(role_or_key)
        else:
            param_name, target_unit = self._resolve_string_parameter(role_or_key)

        # Determine value type
        value_type = self._infer_value_type(value)

        # Set with unit conversion
        self._element.set_parameter(param_name, value, unit, target_unit, value_type)

    def get_value_with_unit(self, role_or_key: Enum | str, unit: UnitType, default: Any = None) -> Any:
        """
        Get parameter value with unit conversion.

        Parameters
        ----------
        role_or_key : Enum | str
            ENUM role or string key for the parameter
        unit : UnitType
            Unit to convert the value to
        default : Any
            Default value if parameter doesn't exist

        Returns
        -------
        Any
            Parameter value converted to specified unit
        """
        if isinstance(role_or_key, Enum):
            param_name, _ = self._resolve_enum_parameter(role_or_key)
        else:
            param_name, _ = self._resolve_string_parameter(role_or_key)

        return self._element.get_parameter(param_name, default, unit)

    def validate_value(self, role_or_key: Enum | str, value: Any) -> bool:
        """
        Validate a parameter value.

        Parameters
        ----------
        role_or_key : Enum | str
            ENUM role or string key for the parameter
        value : Any
            Value to validate

        Returns
        -------
        bool
            True if value is valid for the parameter
        """
        if self._is_plugin_mode and self._registry:
            # Use registry validation
            semantic_key = role_or_key.value if isinstance(role_or_key, Enum) else role_or_key
            return self._registry.validate_parameter_value(semantic_key, value)
        else:
            # Basic type validation for ENUM mode
            try:
                if isinstance(role_or_key, Enum):
                    param_name, _ = self._resolve_enum_parameter(role_or_key)
                else:
                    param_name, _ = self._resolve_string_parameter(role_or_key)

                # Basic validation - if we can set it, it's valid
                self._infer_value_type(value)  # Will raise exception if invalid
                return True
            except Exception:
                return False

    def get_configuration(self) -> dict[str, Any]:
        """
        Get interface configuration for serialization.

        Returns
        -------
        dict[str, Any]
            Configuration data
        """
        config = {
            "mapping_name": self._mapping_name,
            "is_enum_mode": self._is_enum_mode,
            "is_plugin_mode": self._is_plugin_mode,
        }

        if self._is_plugin_mode and self._registry is not None:
            config["registry_data"] = self._registry.to_dict()

        # Note: ENUM mapping serialization would require additional work
        # For now, we focus on the Plugin mode which is the future direction

        return config

    @classmethod
    def from_configuration(cls, element: GenericElement, config_data: dict[str, Any]) -> HybridParameterInterface:
        """
        Create interface from configuration data.

        Parameters
        ----------
        element : GenericElement
            Element to manage parameters for
        config_data : dict[str, Any]
            Configuration data from get_configuration()

        Returns
        -------
        HybridParameterInterface
            Restored interface instance
        """
        mapping_name = config_data["mapping_name"]

        if config_data["is_plugin_mode"]:
            registry = ParameterRegistry.from_dict(config_data["registry_data"])
            return cls(element=element, mapping_name=mapping_name, registry=registry)
        else:
            # ENUM mode restoration would require additional implementation
            raise NotImplementedError("ENUM mapping restoration not yet implemented")

    def _set_enum_value(self, role: Enum, value: Any) -> None:
        """Set parameter value using ENUM role."""
        param_name, unit = self._resolve_enum_parameter(role)
        value_type = self._infer_value_type(value)

        self._element.set_parameter(param_name, value, unit, value_type=value_type)

    def _get_enum_value(self, role: Enum, default: Any = None) -> Any:
        """Get parameter value using ENUM role."""
        param_name, _ = self._resolve_enum_parameter(role)
        return self._element.get_parameter(param_name, default)

    def _set_string_value(self, key: str, value: Any) -> None:
        """Set parameter value using string key."""
        param_name, unit = self._resolve_string_parameter(key)
        value_type = self._infer_value_type(value)

        self._element.set_parameter(param_name, value, unit, value_type=value_type)

    def _get_string_value(self, key: str, default: Any = None) -> Any:
        """Get parameter value using string key."""
        param_name, _ = self._resolve_string_parameter(key)
        return self._element.get_parameter(param_name, default)

    def _resolve_enum_parameter(self, role: Enum) -> tuple[str, UnitType]:
        """Resolve ENUM role to parameter name and unit."""
        if self._is_enum_mode and self._enum_mapping:
            param_name = self._enum_mapping.get_parameter_name(role)
            unit = self._enum_mapping.get_parameter_unit(role)

            if param_name is None:
                raise ValueError(f"ENUM role {role} not found in mapping")

            return param_name, unit or UnitType.NONE
        else:
            # In plugin mode, use semantic key directly
            return role.value, UnitType.MILLIMETER  # Default assumption

    def _resolve_string_parameter(self, key: str) -> tuple[str, UnitType]:
        """Resolve string key to parameter name and unit."""
        if self._is_plugin_mode and self._registry:
            descriptor = self._registry.get_parameter(key)
            if descriptor:
                return key, descriptor.unit  # In plugin mode, key IS the parameter name
            else:
                # Parameter not in registry, use defaults
                return key, UnitType.NONE
        elif self._enum_mapping:
            # In ENUM mode, string keys map to whatever the ENUM mapping defines
            # Try to find a matching ENUM role with the same value
            for role in self._enum_mapping.get_all_roles():
                if role.value == key:
                    return self._resolve_enum_parameter(role)

        # If no matching ENUM role found, use string key directly with defaults
        return key, UnitType.NONE

    def _infer_value_type(self, value: Any) -> ValueType:
        """Infer ValueType from Python value."""
        if isinstance(value, bool):
            return ValueType.BOOLEAN
        elif isinstance(value, int):
            return ValueType.INTEGER
        elif isinstance(value, float):
            return ValueType.FLOAT
        elif isinstance(value, str):
            return ValueType.STRING
        else:
            return ValueType.STRING  # Default fallback
