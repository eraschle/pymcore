"""
Generic element implementation for PyM Core.

Provides universal container with parameter management and geometry synchronization.
"""
from typing import Any, Dict, Optional
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
        self._parameters: Dict[str, Any] = {}
        self._parameter_metadata: Dict[str, Dict[str, Any]] = {}
        self._containers: Dict[str, Any] = {}
        self._unit_converter = UnitConverter()
        self._geometry: Optional[ElementGeometry] = None
    
    def set_parameter(
        self, 
        name: str, 
        value: Any, 
        unit: UnitType = UnitType.NONE,
        target_unit: Optional[UnitType] = None,
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
        return_unit: Optional[UnitType] = None
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
    
    def get_parameter_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get metadata for a parameter.
        
        Parameters
        ----------
        name : str
            Parameter name
            
        Returns
        -------
        Dict[str, Any]
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
    
    def get_geometry(self) -> 'ElementGeometry':
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
    
    def _update_geometry_if_needed(self, parameter_name: str, value: Any) -> None:
        """Update geometry if this parameter affects geometry."""
        # Only update if geometry already exists (lazy creation)
        if self._geometry is not None:
            self._geometry._sync_from_parameters()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize element to dictionary.
        
        Returns
        -------
        Dict[str, Any]
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
    def from_dict(cls, data: Dict[str, Any]) -> 'GenericElement':
        """
        Deserialize element from dictionary.
        
        Parameters
        ----------
        data : Dict[str, Any]
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