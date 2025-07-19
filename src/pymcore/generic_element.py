"""
Generic element implementation for PyM Core.

Provides universal container with parameter management and geometry synchronization.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .geometry import ElementGeometry
from .types import Unit, ValueType
from .unit_converter import UnitConversionError, UnitConverter

log = logging.getLogger(__name__)


class ParameterNotDefinedError(Exception):
    """Raised when trying to set a parameter that is not defined."""

    pass


@dataclass
class ParameterMetadata:
    """
    Metadata for parameters in GenericElement.

    Stores unit, value type, and actual value for each parameter.
    Used to manage parameter serialization and deserialization.
    """

    name: str
    unit: Unit
    value_type: ValueType
    role: Enum | None = None


class ParameterValue(BaseModel):
    """
    Value object for parameter value in GenericElement.

    Contains the parameter name, value, and unit.
    Used to encapsulate parameter data for serialization.
    """

    parameter: ParameterMetadata
    value: Any = Field(..., alias="value")

    @property
    def name(self) -> str:
        """Get the name of the parameter."""
        return self.parameter.name

    @property
    def value_type(self) -> ValueType:
        """Get the value type of the parameter."""
        return self.parameter.value_type

    @property
    def unit(self) -> Unit:
        """Get the unit of the parameter."""
        return self.parameter.unit

    def model_post_init(self, __context):
        """Initialize after Pydantic model creation."""
        self._unit_converter = UnitConverter()

    def set_value(self, new_value: Any, input_unit: Unit | None = None) -> None:
        """
        Set parameter value with optional unit conversion.
        if input_unit is not provided, the unit of the parameter is used.

        Parameters
        ----------
        new_value : Any
            New value to set
        input_unit : UnitType
            Unit of the input value
        """
        is_value_type, as_value_type = self.value_type.get_convert_function()
        if is_value_type(new_value):
            new_value = as_value_type(new_value)

        converted_value = None
        input_unit = input_unit or self.parameter.unit
        if self.parameter.unit.is_compatible_with(input_unit):
            try:
                converted_value = self._unit_converter.convert(new_value, input_unit, self.unit)
            except UnitConversionError as e:
                log.warning(f"Unit conversion failed for parameter {self.name}: {e}")
                raise e
        if self.value_type.is_compatible_with_unit(input_unit):
            log.info(f"Converting {new_value} from {input_unit} to {self.unit}")
            converted_value = self._unit_converter.convert(new_value, input_unit, self.unit)
        else:
            raise TypeError(f"Value {converted_value} is not of type {input_unit}")  # type: ignore
        self.value = as_value_type(converted_value)  # type: ignore

    def get_value(self, target_unit: Unit | None = None) -> Any:
        """
        Get parameter value with optional unit conversion.

        Parameters
        ----------
        target_unit : UnitType | None
            Unit to convert the value to

        Returns
        -------
        Any
            Parameter value (possibly converted)
        """
        if target_unit is None or target_unit == self.unit:
            return self.value

        try:
            return self._unit_converter.convert(self.value, self.unit, target_unit)
        except UnitConversionError as e:
            log.warning(f"Unit conversion failed for parameter {self.name}: {e}")
            return self.value

    def convert_to(self, target_unit: Unit | None, default_value: Any) -> Any:
        """
        Return the value of the parameter, converting it to the target unit if specified.
        if target_unit is None, the value is returned in the parameter's unit.

        Parameters
        ----------
        target_unit : UnitType | None
            Unit to convert the value to

        Returns
        -------
        float
            Parameter value (possibly converted)

        """
        if target_unit is None:
            if self.unit == Unit.NONE:
                log.warning(f"Parameter {self.name} has no unit defined, returning raw value")
            else:
                log.info(f"Returning value of parameter {self.name} in its own unit: {self.unit}")
            return self.value
        try:
            return self._unit_converter.convert(self.value, self.unit, target_unit)
        except UnitConversionError as e:
            log.warning(f"Unit conversion failed for parameter {self.name}: {e}")
            return default_value


class GenericElement:
    """
    Universal container for infrastructure elements.

    Provides parameter management with automatic unit conversion
    and synchronized geometry access through descriptors.
    """

    def __init__(self, element_id: str, element_type: str):
        """
        Initialize a generic element.

        Parameters
        ----------
        element_id : str
            Unique identifier for this element
        element_type : str
            Type of the element (e.g., "pole", "foundation")
        """
        self.element_id = element_id
        self.element_type = element_type
        self._parameter_definitions: dict[str, ParameterMetadata] = {}
        self._param_values: dict[str, ParameterValue] = {}
        self._containers: dict[str, Any] = {}
        self._unit_converter = UnitConverter()
        self._geometry: ElementGeometry | None = None

    def get_parameter_definitions(self) -> list[ParameterMetadata]:
        """
        Get all parameter definitions for this element.

        Returns
        -------
        dict[str, ParameterMetadata]
            Dictionary of parameter definitions
        """
        return list(self._parameter_definitions.values())

    def definition_by(self, name: str) -> ParameterMetadata | None:
        """
        Get parameter definition by name.

        Parameters
        ----------
        name : str
            Parameter name

        Returns
        -------
        ParameterMetadata | None
            Parameter definition or None if not found
        """
        return self._parameter_definitions.get(name)

    def define_parameter(self, name: str, value_type: ValueType, unit: Unit) -> None:
        """
        Define a parameter for this element.

        Parameters
        ----------
        name : str
            Parameter name
        unit : UnitType
            Unit of the parameter
        value_type : ValueType
            Type of the parameter value
        """
        metadata = ParameterMetadata(name=name, unit=unit, value_type=value_type)
        self._parameter_definitions[name] = metadata

    def set_value(self, name: str, value: Any, unit: Unit | None) -> None:
        """
        Set a parameter value with and convert it to the parameter's unit.

        Parameters
        ----------
        name : str
            Parameter name
        value : Any
            Parameter value
        unit : UnitType
            Unit of the input value

        Raises
        ------
        UnitConversionError
            If unit conversion is not possible
        """
        existing_value = self.value_by(name)
        if existing_value is None:
            existing_value = self._create_value_from_definition(name, value)
        if existing_value and name not in self._param_values:
            self._param_values[name] = existing_value
        elif existing_value is None:
            return None
        unit = unit or existing_value.unit
        existing_value.set_value(value, unit)
        self._update_geometry_if_needed(name, value)

    def _create_value_from_definition(
        self, param_name: str, default: Any | None = None
    ) -> ParameterValue | None:
        """
        Get a parameter value object by name.

        Parameters
        ----------
        parameter_name : str
            Parameter name
        default : Any | None
            Default value to return if parameter not found

        Returns
        -------
        ParameterValue | None
            Parameter value object or None if not found
        """
        defintion = self._parameter_definitions.get(param_name)
        if defintion is None:
            return None
        return ParameterValue(parameter=defintion, value=default)

    def value_by(self, param_name: str, default: Any | None = None) -> ParameterValue | None:
        """
        Get a parameter value object by name.

        Parameters
        ----------
        parameter_name : str
            Parameter name
        default : Any | None
            Default value to return if parameter not found

        Returns
        -------
        ParameterValue | None
            Parameter value object or None if not found
        """
        parameter = self._param_values.get(param_name, default)
        return parameter

    def has_value(self, name: str) -> bool:
        """
        Check if parameter exists.

        Parameters
        ----------
        name : str
            Parameter name

        Returns
        -------
        bool
            True if parameter exists
        """
        return name in self._param_values

    def get_geometry(self) -> ElementGeometry:
        """
        Get geometry container with synchronized parameter access.

        Returns
        -------
        ElementGeometry
            Geometry container linked to this element's parameters
        """
        if self._geometry is None:
            self._geometry = ElementGeometry(self)
        return self._geometry

    def add_container(self, container_type: str, container_data: Any) -> None:
        """
        Add a container to this element.

        Parameters
        ----------
        container_type : str
            Type identifier for the container
        container_data : Any
            Container data (typically from container.serialize())
        """
        self._containers[container_type] = container_data

    def get_container(self, container_type: str) -> Any | None:
        """
        Get container data by type.

        Parameters
        ----------
        container_type : str
            Type identifier for the container

        Returns
        -------
        Any | None
            Container data if found, None otherwise
        """
        return self._containers.get(container_type)

    def has_container(self, container_type: str) -> bool:
        """
        Check if element has a container of the given type.

        Parameters
        ----------
        container_type : str
            Type identifier for the container

        Returns
        -------
        bool
            True if container exists
        """
        return container_type in self._containers

    def remove_container(self, container_type: str) -> bool:
        """
        Remove a container from this element.

        Parameters
        ----------
        container_type : str
            Type identifier for the container

        Returns
        -------
        bool
            True if container was removed, False if not found
        """
        if container_type in self._containers:
            del self._containers[container_type]
            return True
        return False

    def get_container_types(self) -> list[str]:
        """
        Get list of all container types in this element.

        Returns
        -------
        list[str]
            List of container type identifiers
        """
        return list(self._containers.keys())

    def _infer_value_type(self, value: Any) -> ValueType:
        """Infer ValueType from actual value."""
        if isinstance(value, bool):
            return ValueType.BOOLEAN
        elif isinstance(value, int):
            return ValueType.INTEGER
        elif isinstance(value, float):
            return ValueType.FLOAT
        elif isinstance(value, str):
            return ValueType.STRING
        else:
            return ValueType.STRING  # fallback

    def _update_geometry_if_needed(self, parameter_name: str, value: Any) -> None:
        """Update geometry if this parameter affects geometry."""
        # Only update if geometry already exists (lazy creation)
        if self._geometry is not None:
            self._geometry._sync_from_parameters()

    def to_dict(self, for_json: bool = False) -> dict[str, Any]:
        """
        Serialize element to dictionary.

        Parameters
        ----------
        for_json : bool
            If True, serialize enums as strings for JSON compatibility

        Returns
        -------
        dict[str, Any]
            Serialized element data
        """
        parameters = {}
        parameter_metadata = {}

        for name, param_obj in self._param_values.items():
            parameters[name] = param_obj.value

            if for_json:
                parameter_metadata[name] = {
                    "unit": param_obj.unit.value,
                    "value_type": param_obj.value_type.value,
                    "value": param_obj.value,
                }
            else:
                parameter_metadata[name] = {
                    "unit": param_obj.unit,
                    "value_type": param_obj.value_type,
                    "value": param_obj.value,
                }

        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "parameters": parameters,
            "parameter_metadata": parameter_metadata,
            "containers": self._containers.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GenericElement:
        """
        Deserialize element from dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            Serialized element data

        Returns
        -------
        GenericElement
            Restored element instance
        """
        element = cls(data["element_id"], data["element_type"])
        element._containers = data.get("containers", {}).copy()

        # Reconstruct ParameterValue objects
        parameters = data.get("parameters", {})
        metadata = data.get("parameter_metadata", {})

        for name, value in parameters.items():
            param_metadata = metadata.get(name, {})

            # Handle enum conversion from JSON
            unit = param_metadata.get("unit", Unit.NONE)
            value_type = param_metadata.get("value_type", ValueType.FLOAT)

            if isinstance(unit, str):
                unit = Unit(unit)
            if isinstance(value_type, str):
                value_type = ValueType(value_type)

            # Create ParameterValue object
            metadata_obj = ParameterMetadata(name=name, unit=unit, value_type=value_type)
            element._parameter_definitions[name] = metadata_obj
            param_obj = ParameterValue(parameter=metadata_obj, value=value)
            element._param_values[name] = param_obj

        return element
