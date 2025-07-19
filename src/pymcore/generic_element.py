"""
Generic element implementation for PyM Core.

Provides universal container with parameter management and geometry synchronization.
"""
from __future__ import annotations
from typing import Any
from .types import ValueType, UnitType
from .unit_converter import UnitConverter, UnitConversionError
from .geometry import ElementGeometry


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
        self._parameters: dict[str, Any] = {}
        self._parameter_metadata: dict[str, dict[str, Any]] = {}
        self._containers: dict[str, Any] = {}
        self._unit_converter = UnitConverter()
        self._geometry: ElementGeometry | None = None
    
    def set_parameter(
        self, 
        name: str, 
        value: Any, 
        unit: UnitType = UnitType.NONE,
        target_unit: UnitType | None = None,
        value_type: ValueType = ValueType.FLOAT
    ) -> None:
        """
        Set a parameter with optional unit conversion.
        
        Parameters
        ----------
        name : str
            Parameter name
        value : Any
            Parameter value
        unit : UnitType
            Unit of the input value
        target_unit : UnitType, optional
            Target unit for storage (if different from input unit)
        value_type : ValueType
            Type of the parameter value
            
        Raises
        ------
        UnitConversionError
            If unit conversion is not possible
        """
        # Validate unit compatibility with value type
        if not value_type.is_compatible_with_unit(unit):
            raise UnitConversionError(
                f"Value type {value_type.name} is not compatible with unit {unit.name}"
            )
        
        # Perform unit conversion if needed
        stored_value = value
        stored_unit = unit
        
        if target_unit is not None and target_unit != unit:
            if not value_type.is_compatible_with_unit(target_unit):
                raise UnitConversionError(
                    f"Value type {value_type.name} is not compatible with target unit {target_unit.name}"
                )
            stored_value = self._unit_converter.convert(value, unit, target_unit)
            stored_unit = target_unit
        
        # Store parameter and metadata
        self._parameters[name] = stored_value
        self._parameter_metadata[name] = {
            "unit": stored_unit,
            "value_type": value_type,
            "value": stored_value
        }
        
        # Update geometry if this is a geometric parameter
        self._update_geometry_if_needed(name, stored_value)
    
    def get_parameter(
        self, 
        name: str, 
        default: Any = None,
        return_unit: UnitType | None = None
    ) -> Any:
        """
        Get a parameter value with optional unit conversion.
        
        Parameters
        ----------
        name : str
            Parameter name
        default : Any
            Default value if parameter doesn't exist
        return_unit : UnitType, optional
            Unit to convert the value to before returning
            
        Returns
        -------
        Any
            Parameter value (possibly converted)
        """
        if name not in self._parameters:
            return default
        
        value = self._parameters[name]
        
        # Convert unit if requested
        if return_unit is not None:
            metadata = self._parameter_metadata.get(name, {})
            stored_unit = metadata.get("unit", UnitType.NONE)
            
            if stored_unit != return_unit:
                value = self._unit_converter.convert(value, stored_unit, return_unit)
        
        return value
    
    def get_parameter_metadata(self, name: str) -> dict[str, Any]:
        """
        Get metadata for a parameter.
        
        Parameters
        ----------
        name : str
            Parameter name
            
        Returns
        -------
        dict[str, Any]
            Parameter metadata including unit, type, and value
        """
        return self._parameter_metadata.get(name, {}).copy()
    
    def has_parameter(self, name: str) -> bool:
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
        return name in self._parameters
    
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

    def _update_geometry_if_needed(self, parameter_name: str, value: Any) -> None:
        """Update geometry if this parameter affects geometry."""
        # Only update if geometry already exists (lazy creation)
        if self._geometry is not None:
            self._geometry._sync_from_parameters()
    
    def to_dict(self) -> dict[str, Any]:
        """
        Serialize element to dictionary.
        
        Returns
        -------
        dict[str, Any]
            Serialized element data
        """
        return {
            "element_id": self.element_id,
            "element_type": self.element_type,
            "parameters": self._parameters.copy(),
            "parameter_metadata": self._parameter_metadata.copy(),
            "containers": self._containers.copy()
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
        element._parameters = data.get("parameters", {}).copy()
        element._parameter_metadata = data.get("parameter_metadata", {}).copy()
        element._containers = data.get("containers", {}).copy()
        return element